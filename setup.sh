destination="$HOME/.local/bin"
 
if ! [ -d "$destination" ]; then
    mkdir -p "$destination"
    echo 'export PATH="'"$destination"':$PATH"' >> $HOME/.bashrc
    source "$HOME/.bashrc"
fi
 
wget -P "$destination/" "https://raw.githubusercontent.com/ohol-vitaliy/animevost-dl-extended/master/animevost-dl.py"
mv "$destination/animevost-dl.py" "$destination/animevost-dl"
chmod +x "$destination/animevost-dl"
yes | pip3 install requests python-slugify
