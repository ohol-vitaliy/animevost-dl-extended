#!/usr/bin/python3
import argparse
import os

import requests
from slugify import slugify

MULTITHREAD = False

try:
    import multiprocessing as mp

    with mp.Pool(processes=4) as pool:
        pass
    MULTITHREAD = True
except ImportError:
    print("this device do not support multithreading")


API_URL = "https://api.animevost.org/v1/"
THREAD_COUNT = 4
CHUNK_SIZE = 32 * 1024


def _post_request(type, id):
    response = requests.post(
        API_URL + type,
        data={"id": id},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()


def _get_title(id):
    response = _post_request("info", id)

    if response.get("state", {}).get("status") != "ok":
        return None

    data = response.get("data", [])
    if not data:
        return None

    title = data[0].get("title")
    index_part = title.rfind(" [")

    return slugify(title[:index_part])


def _process_episode_info(episode):
    name = episode.get("name")
    if not name:
        return

    vod_urls = []
    std_vod = episode.get("std")
    hd_vod = episode.get("hd")
    if std_vod:
        vod_urls.append(std_vod)
    if hd_vod:
        vod_urls.append(hd_vod)
    if not vod_urls:
        return

    number_str = name.split(" ")[0]
    number = int(number_str) if number_str.isnumeric() else 1
    return (number, vod_urls)


def _get_playlist(id):
    response = _post_request("playlist", id)
    if MULTITHREAD:
        with mp.Pool(processes=THREAD_COUNT) as pool:
            playlist = pool.map(_process_episode_info, response)
        return playlist
    else:
        playlist = []
        for episode in response:
            playlist.append(_process_episode_info(episode))
        return sorted(playlist)


def _process_path(name, save_location, vod_url):
    file_name = name + os.path.splitext(vod_url)[1]
    return os.path.join(save_location, file_name)


def _download_video(name, vod_urls, save_location):
    name = f"{name:04}"
    file_path = _process_path(name, save_location, vod_urls[0])
    for vod_url in vod_urls:
        try:
            if os.path.exists(file_path):
                print(f"resuming {name}")
                mode = "ab"
                file_size = os.stat(file_path).st_size
                resume_header = {"Range": f"bytes={file_size}-"}
            else:
                print(f"downloading {name}")
                mode = "wb"
                resume_header = None

            with requests.get(vod_url, stream=True, headers=resume_header) as r:
                with open(file_path, mode) as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
            break
        except requests.HTTPError:
            print(f"Failed loading {vod_url}, retrying with lower quality")


def _get_id_from_url(web_url):
    full_name = web_url.split("/")[-1]
    id_str = full_name.split("-")[0]
    return int(id_str)


def download_playlist(url, path):
    id = _get_id_from_url(url)
    title = _get_title(id)

    save_location = os.path.join(path, title)
    if not (os.path.exists(save_location) and os.path.isdir(save_location)):
        os.mkdir(save_location)

    if MULTITHREAD:
        playlist = [tuple(list(i) + [save_location]) for i in _get_playlist(id)]
        with mp.Pool(processes=THREAD_COUNT) as pool:
            pool.starmap(_download_video, playlist)
    else:
        playlist = _get_playlist(id)
        print(f"\nPlaylist name: {title}\n")
        n_vods = len(playlist)
        for n, vod_urls in playlist:
            print(f"Downloading video {n} of {n_vods}")
            _download_video(n, vod_urls, save_location)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Download anime from animevost.org")
    parser.add_argument("--url", "-u", required=True, help="url of an anime")
    parser.add_argument(
        "--path", "-p", default=os.getcwd(), help="path where anime will be saved"
    )
    args = parser.parse_args()

    download_playlist(args.url, args.path)
