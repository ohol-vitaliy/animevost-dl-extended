destination="$HOME/.local/bin"
 
if ! [ -d "$destination" ]; then
    mkdir -p "$destination"
    export PATH="$destination/:$PATH"
fi
 
wget -P "$destination/" "https://raw.githubusercontent.com/ohol-vitaliy/animevost-dl-extended/master/animevost-dl.py"
chmod +x "$destination/animevost-dl.py"
yes | pip3 install requests python-slugify
