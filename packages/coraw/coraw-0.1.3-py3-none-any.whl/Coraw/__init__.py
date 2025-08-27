from .coraw import (
    co,
    connect,
    connect_robust,
    ping,
    stop_ping,
    # alias for older "stop" name:
    # (stop will be exported below via __all__ as well)
    disconnect,
    close,
    forward,
    back,
    left,
    right,
    stop_move,
    headup,
    headdown,
    liftup,
    liftdown,
    backlight,
    Img,
    draw,
    stopface,
    resumeface,
    paudio,
    saudio,
    setvol,
    tts,
    wait,
    bind,
    camera,
    camerargb,
    tkint,
)

# provide backwards-compatible alias `stop` -> `stop_ping`
try:
    from .coraw import stop_ping as stop
except Exception:
    # fallback no-op if stop_ping not present
    def stop():
        raise RuntimeError("stop not available (stop_ping missing in coraw).")

__all__ = [
    "co",
    "connect",
    "connect_robust",
    "ping",
    "stop",        # classic alias
    "stop_ping",
    "disconnect",
    "close",
    "forward",
    "back",
    "left",
    "right",
    "stop_move",
    "headup",
    "headdown",
    "liftup",
    "liftdown",
    "backlight",
    "Img",
    "draw",
    "stopface",
    "resumeface",
    "paudio",
    "saudio",
    "setvol",
    "tts",
    "wait",
    "bind",
    "camera",
    "camerargb",
    "tkint",
]
