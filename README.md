# dotfiles

Настройки рабочего стола Arch Linux + Hyprland в теме [Tokyo Night](https://github.com/enkia/tokyo-night-vscode-theme).

| Что | Где в репозитории | Куда ставится |
|---|---|---|
| Hyprland (конфиг на Lua), hyprlock, hypridle, hyprpaper | `config/hypr/` | `~/.config/hypr/` |
| Waybar: «островки», модуль с подсказкой горячих клавиш | `config/waybar/` | `~/.config/waybar/` |
| Rofi | `config/rofi/` | `~/.config/rofi/` |
| Уведомления dunst | `config/dunst/` | `~/.config/dunst/` |
| Скрипты: скриншоты, история буфера, живые обои | `local/bin/` | `~/.local/bin/` |
| Обои (обычные и живые), фон экрана блокировки | `wallpapers/` | `~/Pictures/wallpapers/` |
| Тема GRUB | `system/grub/` | `/boot/grub/themes/tokyonight/` |
| Тема экрана входа SDDM | `system/sddm/` | `/usr/share/sddm/themes/tokyonight/` |

## Установка

```sh
sudo pacman -S --needed - < packages.txt
yay -S mpvpaper            # живые обои (AUR)
./install.sh               # пользовательские настройки
./install.sh --system      # плюс темы GRUB и SDDM
```

Заменяемые файлы сохраняются рядом с суффиксом `.orig`.

## Горячие клавиши

| Клавиши | Действие |
|---|---|
| Super + Q | терминал (kitty) |
| Super + R | запуск приложений (rofi) |
| Super + Tab | список окон |
| Super + V | история буфера обмена |
| Super + E | файловый менеджер (Dolphin) |
| Super + B | браузер |
| Super + L | заблокировать экран |
| PrtSc / Shift + PrtSc | скриншот области / всего экрана |
| Super + Space | раскладка us/ru |

Полный список — в подсказке к значку облака на Waybar: он читается прямо из `hyprland.lua`.

## Обои

- `noire-night.png`, `noire-night-live.mp4` — сцена **Noire Night 4K** для Wallpaper Engine,
  [Steam Workshop, id 3562656216](https://steamcommunity.com/sharedfiles/filedetails/?id=3562656216),
  скачана с [vsthemes.org](https://vsthemes.org/). Права на изображение принадлежат его автору.
  Видео проигрывает `live-wallpaper` через mpvpaper; если mpvpaper нет — ставится статичная картинка через hyprpaper.
- `noire-night-live.lua` — часы поверх живых обоев, как в оригинальной сцене. Нужны шрифты
  **Anurati** и **Quicksand Bold** в `~/.local/share/fonts/` (в репозиторий не входят); без них mpv подставит другой шрифт.
- `tokyonight.png` — фон экрана блокировки, простой градиент.
