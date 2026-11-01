#!/usr/bin/env python3
"""Waybar modules for the TV on HDMI: two clouds, shown only while it is plugged in.

  tv.py display [toggle]  second screen <-> mirror of the laptop screen
  tv.py audio [toggle]    sound on the TV <-> laptop speakers
"""
import glob
import json
import os
import subprocess
import sys

MODE_FILE = os.path.expanduser("~/.config/hypr/display-mode")
DISPLAY_MODE = os.path.expanduser("~/.local/bin/display-mode")

ICONS = {
    "extend": "\U000F0163",  # cloud outline
    "mirror": "\U000F063F",  # cloud sync
    "tv": "\U000F0160",      # cloud check
    "laptop": "\U000F0164",  # cloud off
}


def hdmi_connected():
    for path in glob.glob("/sys/class/drm/card*-HDMI-*/status"):
        with open(path) as f:
            if f.read().strip() == "connected":
                return True
    return False


def pactl(*args):
    return subprocess.run(["pactl", *args], capture_output=True, text=True).stdout


def sinks():
    """Names of the HDMI sink and the first non-HDMI sink."""
    hdmi = laptop = None
    for line in pactl("list", "sinks", "short").splitlines():
        name = line.split("\t")[1]
        if "hdmi" in name:
            hdmi = hdmi or name
        else:
            laptop = laptop or name
    return hdmi, laptop


def display(toggle):
    if toggle:
        subprocess.run([DISPLAY_MODE, "toggle"])
    try:
        with open(MODE_FILE) as f:
            mode = f.read().strip()
    except OSError:
        mode = "extend"
    if mode == "mirror":
        return mode, "Телевизор дублирует экран\n<small>Клик — второй экран</small>"
    return "extend", "Телевизор — второй экран\n<small>Клик — дублировать</small>"


def audio(toggle):
    hdmi, laptop = sinks()
    if not hdmi:
        return None, None
    on_tv = pactl("get-default-sink").strip() == hdmi
    if toggle and laptop:
        target = laptop if on_tv else hdmi
        pactl("set-default-sink", target)
        # Move streams that are already playing, not only new ones.
        for line in pactl("list", "sink-inputs", "short").splitlines():
            pactl("move-sink-input", line.split("\t")[0], target)
        on_tv = not on_tv
    if on_tv:
        return "tv", "Звук на телевизоре\n<small>Клик — на ноутбук</small>"
    return "laptop", "Звук на ноутбуке\n<small>Клик — на телевизор</small>"


def main():
    module = sys.argv[1] if len(sys.argv) > 1 else "display"
    toggle = "toggle" in sys.argv[2:]
    state = tip = None
    if hdmi_connected():
        state, tip = (audio if module == "audio" else display)(toggle)
    if state is None:
        out = {"text": "", "tooltip": "", "class": "off"}  # empty text hides the module
    else:
        out = {"text": ICONS[state], "tooltip": tip, "class": state}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
