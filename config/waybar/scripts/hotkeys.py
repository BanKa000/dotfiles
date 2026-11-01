#!/usr/bin/env python3
"""Waybar module: cloud icon whose tooltip lists Hyprland keybindings.

Binds are read from ~/.config/hypr/hyprland.lua on every run,
so the tooltip follows config changes automatically.
"""
import html
import json
import os
import re

CONFIG = os.path.expanduser("~/.config/hypr/hyprland.lua")
ICON = "󰅟"

COLORS = {"head": "#7aa2f7", "key": "#bb9af7", "text": "#a9b1d6", "dim": "#565f89"}
GROUPS = ["Приложения", "Окна", "Рабочие столы", "Система", "Мультимедиа", "Прочее"]

KEY_NAMES = {
    "SUPER": "Super", "SHIFT": "Shift", "CTRL": "Ctrl", "CONTROL": "Ctrl", "ALT": "Alt",
    "left": "←", "right": "→", "up": "↑", "down": "↓", "Tab": "Tab", "Print": "PrtSc",
    "mouse_down": "Колесо ↓", "mouse_up": "Колесо ↑",
    "mouse:272": "ЛКМ", "mouse:273": "ПКМ", "mouse:274": "СКМ",
    "XF86AudioRaiseVolume": "Громк+", "XF86AudioLowerVolume": "Громк−",
    "XF86AudioMute": "Mute", "XF86AudioMicMute": "MicMute",
    "XF86MonBrightnessUp": "Ярк+", "XF86MonBrightnessDown": "Ярк−",
    "XF86AudioNext": "Next", "XF86AudioPrev": "Prev",
    "XF86AudioPlay": "Play", "XF86AudioPause": "Pause",
}

# (regex on the dispatcher call, group, description); first match wins
RULES = [
    (r"exec_cmd\(terminal\)", "Приложения", "Терминал ({terminal})"),
    (r"exec_cmd\(fileManager\)", "Приложения", "Файловый менеджер ({fileManager})"),
    (r"exec_cmd\(browser\)", "Приложения", "Браузер ({browser})"),
    (r"exec_cmd\(menu\)", "Приложения", "Запуск приложений"),
    (r"rofi -show window", "Окна", "Список окон"),
    (r"clipboard-menu", "Приложения", "История буфера обмена"),
    (r"screenshot area", "Система", "Скриншот области"),
    (r"screenshot screen", "Система", "Скриншот экрана"),
    (r"lock-session|hyprlock", "Система", "Заблокировать экран"),
    (r"hyprshutdown|exit\(\)", "Система", "Выйти из Hyprland"),
    (r"window\.close", "Окна", "Закрыть окно"),
    (r"window\.float", "Окна", "Плавающее окно вкл/выкл"),
    (r"window\.fullscreen", "Окна", "Полный экран"),
    (r"window\.pseudo", "Окна", "Псевдотайлинг"),
    (r"togglesplit", "Окна", "Сменить направление разделения"),
    (r"window\.drag", "Окна", "Перетащить окно"),
    (r"window\.resize", "Окна", "Изменить размер окна"),
    (r"focus\(\{\s*direction", "Окна", "Переместить фокус"),
    (r"toggle_special", "Рабочие столы", "Показать скрытый стол"),
    (r"window\.move\(\{\s*workspace\s*=\s*\"special", "Рабочие столы", "Окно → скрытый стол"),
    (r"window\.move\(\{\s*workspace", "Рабочие столы", "Окно → стол N"),
    (r"focus\(\{\s*workspace\s*=\s*\"e\+1", "Рабочие столы", "Следующий стол"),
    (r"focus\(\{\s*workspace\s*=\s*\"e-1", "Рабочие столы", "Предыдущий стол"),
    (r"focus\(\{\s*workspace", "Рабочие столы", "Перейти на стол N"),
    (r"set-volume.*\+", "Мультимедиа", "Громкость +5%"),
    (r"set-volume.*-", "Мультимедиа", "Громкость −5%"),
    (r"SOURCE@ toggle", "Мультимедиа", "Выкл/вкл микрофон"),
    (r"set-mute", "Мультимедиа", "Выкл/вкл звук"),
    (r"brightnessctl.*\+", "Мультимедиа", "Яркость +5%"),
    (r"brightnessctl.*-", "Мультимедиа", "Яркость −5%"),
    (r"playerctl next", "Мультимедиа", "Следующий трек"),
    (r"playerctl previous", "Мультимедиа", "Предыдущий трек"),
    (r"playerctl play-pause", "Мультимедиа", "Пауза/воспроизведение"),
]

BIND = re.compile(r'^\s*(?:local\s+\w+\s*=\s*)?hl\.bind\((.*?),\s*hl\.dsp\.(.*)\)')
LOCAL_STR = re.compile(r'^\s*local\s+(\w+)\s*=\s*"([^"]*)"')


def eval_key(expr, variables):
    """Evaluate a Lua string concatenation like: mainMod .. " + SHIFT + " .. key"""
    parts = []
    for piece in expr.split(".."):
        piece = piece.strip()
        if piece.startswith('"') and piece.endswith('"'):
            parts.append(piece[1:-1])
        elif piece in variables:
            parts.append(variables[piece])
        else:
            parts.append("1…0")  # loop variable (workspace number)
    keys = [k.strip() for k in "".join(parts).split("+") if k.strip()]
    return " + ".join(KEY_NAMES.get(k, KEY_NAMES.get(k.upper(), k)) for k in keys)


def describe(action, variables):
    for pattern, group, text in RULES:
        if re.search(pattern, action):
            # Show program names, not paths: "~/.local/bin/fileman" → "fileman".
            names = {k: os.path.basename(v.split()[0]) if v else v for k, v in variables.items()}
            return group, text.format(**names) if "{" in text else text
    cmd = re.search(r'exec_cmd\("([^"]*)"\)', action)
    return "Прочее", cmd.group(1) if cmd else action.rstrip(")")


def parse():
    variables, binds = {}, []
    with open(CONFIG, encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("--"):
                continue
            if m := LOCAL_STR.match(line):
                variables[m.group(1)] = m.group(2)
                continue
            if m := BIND.match(line):
                group, text = describe(m.group(2), variables)
                binds.append((group, eval_key(m.group(1), variables), text))

    # Merge binds sharing one description, e.g. Super+← / Super+→ -> "Super + ← → ↑ ↓"
    merged = {}
    for group, key, text in binds:
        merged.setdefault((group, text), []).append(key)
    result = []
    for (group, text), keys in merged.items():
        if len(keys) > 1:
            prefixes = {k.rpartition(" + ")[0] for k in keys}
            if len(prefixes) == 1:
                prefix = prefixes.pop()
                tail = " ".join(k.rpartition(" + ")[2] for k in keys)
                keys = [f"{prefix} + {tail}" if prefix else tail.replace(" ", " / ")]
        result.append((group, " / ".join(keys), text))
    return result


def tooltip(binds):
    width = max((len(k) for _, k, _ in binds), default=0) + 2
    lines = []
    for group in GROUPS:
        rows = [(k, t) for g, k, t in binds if g == group]
        if not rows:
            continue
        if lines:
            lines.append("")
        lines.append(f"<span color='{COLORS['head']}'><b>{group}</b></span>")
        for key, text in rows:
            pad = " " * (width - len(key))
            lines.append(f"<span color='{COLORS['key']}'>{html.escape(key)}</span>{pad}"
                         f"<span color='{COLORS['text']}'>{html.escape(text)}</span>")
    return "\n".join(lines)


def main():
    try:
        binds = parse()
        out = {"text": ICON, "tooltip": tooltip(binds), "class": "hotkeys"}
    except OSError as e:
        out = {"text": ICON, "tooltip": f"Не удалось прочитать {CONFIG}: {html.escape(str(e))}",
               "class": "error"}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
