#!/bin/sh
# Подставляет ядру EDID 1920x1080@60 для выхода, с которого EDID не читается.
#   ./install-edid.sh [ВЫХОД]           — включить (по умолчанию HDMI-A-1)
#   ./install-edid.sh --remove [ВЫХОД]  — убрать
# Когда это нужно — см. README.md рядом. Изменённые файлы сохраняются с суффиксом .orig.
set -e
cd "$(dirname "$0")"

EDID=forced-1080p.bin
FW=/usr/lib/firmware/edid/$EDID
MKINITCPIO=/etc/mkinitcpio.conf

remove=; [ "$1" = --remove ] && { remove=1; shift; }
param="drm.edid_firmware=${1:-HDMI-A-1}:edid/$EDID"

# Загрузка через UKI берёт параметры ядра из /etc/kernel/cmdline, иначе — из настроек GRUB.
if [ -f /etc/kernel/cmdline ] && grep -qs '^[^#]*_uki=' /etc/mkinitcpio.d/*.preset; then
    cmdline=/etc/kernel/cmdline
else
    cmdline=/etc/default/grub
fi

backup() { [ -e "$1.orig" ] || sudo cp -p "$1" "$1.orig"; }

backup "$cmdline"
backup "$MKINITCPIO"
sudo sed -i 's| *drm\.edid_firmware=[^ "]*||' "$cmdline"
sudo sed -i -e "/^FILES=/s|$FW||" -e '/^FILES=/s|  *| |g' -e 's|^FILES=( *\(.*[^ ]\) *)|FILES=(\1)|' \
    -e 's|^FILES=( *)|FILES=()|' "$MKINITCPIO"

if [ -z "$remove" ]; then
    sudo install -D -m 644 "$EDID" "$FW"
    if [ "$cmdline" = /etc/kernel/cmdline ]; then
        sudo sed -i "1s|\$| $param|" "$cmdline"
    else
        sudo sed -i "s|^GRUB_CMDLINE_LINUX_DEFAULT=\"\(.*\)\"|GRUB_CMDLINE_LINUX_DEFAULT=\"\1 $param\"|" "$cmdline"
    fi
    # amdgpu/i915 грузятся из initramfs (хук kms), поэтому EDID должен лежать и там.
    sudo sed -i -e "s|^FILES=()|FILES=($FW)|" -e "/^FILES=/{\|$FW|!s|)\$| $FW)|}" "$MKINITCPIO"
else
    sudo rm -f "$FW"
fi

sudo mkinitcpio -P
[ "$cmdline" = /etc/default/grub ] && sudo grub-mkconfig -o /boot/grub/grub.cfg

if [ -z "$remove" ]; then
    echo "EDID подставлен ($param). Перезагрузись с подключённым телевизором."
else
    echo "Подменённый EDID убран. Перезагрузись."
fi
