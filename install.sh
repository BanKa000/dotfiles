#!/bin/sh
# Раскладывает файлы по местам. Существующие файлы сохраняются рядом с суффиксом .orig.
#   ./install.sh          — только пользовательские настройки (~/.config, ~/.local/bin, обои)
#   ./install.sh --system — плюс темы GRUB и SDDM (нужен sudo)
set -e
cd "$(dirname "$0")"

put() { # put SRC DST [MODE]
    if [ -e "$2" ] && ! cmp -s "$1" "$2"; then cp -p "$2" "$2.orig"; fi
    install -D -m "${3:-644}" "$1" "$2"
}

for f in $(find config -type f); do
    mode=644; [ -x "$f" ] && mode=755
    put "$f" "$HOME/.$f" $mode
done
for f in local/bin/*; do put "$f" "$HOME/.local/bin/${f##*/}" 755; done
for f in wallpapers/*; do put "$f" "$HOME/Pictures/wallpapers/${f##*/}"; done
echo "Пользовательские настройки установлены."

[ "$1" = "--system" ] || exit 0

sudo cp -r system/grub/themes/tokyonight /boot/grub/themes/
if ! grep -q '^GRUB_THEME="/boot/grub/themes/tokyonight/theme.txt"' /etc/default/grub; then
    sudo cp -p /etc/default/grub /etc/default/grub.orig
    sudo sed -i -e '/^#\?GRUB_THEME=/d' /etc/default/grub
    echo 'GRUB_THEME="/boot/grub/themes/tokyonight/theme.txt"' | sudo tee -a /etc/default/grub >/dev/null
fi
sudo grub-mkconfig -o /boot/grub/grub.cfg

sudo cp -r system/sddm/themes/tokyonight /usr/share/sddm/themes/
sudo install -D -m 644 system/sddm/sddm.conf.d/theme.conf /etc/sddm.conf.d/theme.conf
echo "Темы GRUB и SDDM установлены."
