"""
coraw: Raw Cozmo Wi-Fi Control Library

Provides low-level commands to control Cozmo over Wi-Fi, including:
- Movement: forward, back, left, right
- Lift and head: liftup, liftdown, headup, headdown
- Face control stubs: stopface, resumeface
- Audio: paudio, saudio, setvol, tts
- Cube docking: cubedock
- Draw to OLED: draw
- Backpack lights: backlight
- Connection management: connect, disconnect
"""

from .coraw import (
    connect,
    disconnect,
    forward,
    back,
    left,
    right,
    stop,
    liftup,
    liftdown,
    headup,
    headdown,
    stopface,
    resumeface,
    paudio,
    saudio,
    setvol,
    tts,
    draw,
    backlight,
    cubedock,
)

__all__ = [
    "connect",
    "disconnect",
    "forward",
    "back",
    "left",
    "right",
    "stop",
    "liftup",
    "liftdown",
    "headup",
    "headdown",
    "stopface",
    "resumeface",
    "paudio",
    "saudio",
    "setvol",
    "tts",
    "draw",
    "backlight",
    "cubedock",
]
