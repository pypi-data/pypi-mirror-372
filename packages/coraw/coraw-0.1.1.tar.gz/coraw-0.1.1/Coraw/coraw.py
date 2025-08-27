#!/usr/bin/env python3
# coraw.py -- Cozmo UDP helper with keyboard/controller and built-in Tkinter GUI
# UPDATED: automatic Cozmo IP detection (looks for hostnames starting with "Cozmo_")

import socket, struct, threading, time, subprocess, sys, re, platform
import tkinter as tk
from tkinter import colorchooser

# Optional libraries
try:
    from pynput import keyboard as _pynput_keyboard
except Exception:
    _pynput_keyboard = None

try:
    from inputs import get_gamepad
except ImportError:
    get_gamepad = None
    print("Controller support requires 'inputs' library.")

try:
    import cv2
except ImportError:
    cv2 = None
    print("OpenCV not found; camera feed will not work.")

# CRC-16/X25
def crc16_x25(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8408 if crc & 1 else crc >> 1
    return (~crc) & 0xFFFF

def build_packet(msg_id, payload=b"", seq=0, ack=False):
    sync = b"\x55\xAA"
    length = struct.pack("<H", len(payload))
    mid = struct.pack("<H", msg_id)
    flags = b"\x01" if ack else b"\x00"
    seqb = struct.pack("B", seq)
    header = sync + length + mid + flags + seqb
    crc = struct.pack("<H", crc16_x25(header + payload))
    return header + payload + crc

# Message IDs
MSG_PING     = 0x0001
MSG_DRIVE    = 0x0380
MSG_TURN     = 0x0381
MSG_HEAD     = 0x03F2
MSG_LIFT     = 0x03F3
MSG_BACKPACK = 0x03F0
MSG_DISPLAY  = 0x03E8
MSG_FREEZE_FACE = 0x03E9
MSG_PLAY_AUDIO  = 0x0480
MSG_SET_VOLUME  = 0x0481
MSG_STOP_AUDIO  = 0x0482

# Controller mapping
_CONTROLLER_NAMES = {
    'ABS_Y_UP':'leftup','ABS_Y_DOWN':'leftdown','ABS_X_LEFT':'leftleft','ABS_X_RIGHT':'leftright','BTN_THUMBL':'leftpress',
    'ABS_RY_UP':'rightup','ABS_RY_DOWN':'rightdown','ABS_RX_LEFT':'rightleft','ABS_RX_RIGHT':'rightright','BTN_THUMBR':'rightpress',
    'BTN_TL':'L1','BTN_TL2':'L2','BTN_TR':'R1','BTN_TR2':'R2',
    'BTN_SOUTH':'Abutton','BTN_EAST':'Bbutton','BTN_NORTH':'Xbutton','BTN_WEST':'Ybutton'
}

# Helper to detect Cozmo on current Wi-Fi
def detect_cozmo_ip():
    """Detect Cozmo on current Wi-Fi by scanning ARP and doing a light reverse-lookup sweep.
    Returns the first IP whose hostname starts with 'Cozmo_' (case-insensitive) or None."""
    system = platform.system()

    # Try ARP table first (fast)
    try:
        output = subprocess.check_output("arp -a", shell=True, text=True, stderr=subprocess.DEVNULL)
        # Look for 'Cozmo_' in the ARP output lines (case-insensitive)
        m = re.findall(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*Cozmo_", output, flags=re.IGNORECASE)
        if m:
            return m[0]
    except Exception:
        pass

    # Determine local IP to derive subnet
    local_ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = None

    if not local_ip:
        return None

    parts = local_ip.split(".")
    if len(parts) != 4:
        return None
    base = ".".join(parts[:3])

    # Light sweep across the /24 (1..254). Use short timeouts.
    for i in range(1, 255):
        ip = f"{base}.{i}"
        try:
            if system == "Windows":
                # -n 1 (one echo), -w timeout in ms
                subprocess.run(["ping", "-n", "1", "-w", "200", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # -c 1 one packet, -W 1 timeout 1s
                subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # try reverse DNS; if it resolves and startswith Cozmo_ -> done
            try:
                host = socket.gethostbyaddr(ip)[0]
                if host.lower().startswith("cozmo_"):
                    return ip
            except Exception:
                continue
        except Exception:
            continue

    return None

class Coraw:
    def __init__(self, ip=None, port=5551):
        # If no IP provided, try to detect a Cozmo on the current network
        if ip is None:
            detected_ip = detect_cozmo_ip()
            if detected_ip:
                print(f"Detected Cozmo at {detected_ip}")
                ip = detected_ip
            else:
                ip = "172.31.1.24"  # fallback default
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except: pass
        self.seq = 0
        self._pinging = False
        self._ping_thread = None
        self._key_map = {}
        self._listener_started = False
        self.cam_color = True

    # Low-level send
    def send(self, msg_id, payload=b""):
        pkt = build_packet(msg_id, payload, self.seq)
        try:
            self.sock.sendto(pkt, (self.ip, self.port))
        except Exception as e:
            print("send error:", e, file=sys.stderr)
        self.seq = (self.seq + 1) % 256

    def close(self):
        try: self.sock.close()
        except: pass

    # Ping
    def ping(self):
        if self._pinging: return
        self._pinging = True
        def loop():
            while self._pinging:
                self.send(MSG_PING)
                time.sleep(0.2)
        self._ping_thread = threading.Thread(target=loop, daemon=True)
        self._ping_thread.start()
    def stop(self): self._pinging = False

    # Movement
    def forward(self,duration=None,speed=120.0):
        self.send(MSG_DRIVE, struct.pack("<ff", float(speed), float(speed)))
        if duration: time.sleep(duration); self.stop_move()
    def back(self,duration=None,speed=120.0):
        self.send(MSG_DRIVE, struct.pack("<ff", float(-speed), float(-speed)))
        if duration: time.sleep(duration); self.stop_move()
    def left(self,duration=None,rad=2.0):
        self.send(MSG_TURN, struct.pack("<ff", float(rad),0.0))
        if duration: time.sleep(duration); self.stop_move()
    def right(self,duration=None,rad=2.0):
        self.send(MSG_TURN, struct.pack("<ff", float(-rad),0.0))
        if duration: time.sleep(duration); self.stop_move()
    def stop_move(self): self.send(MSG_DRIVE, struct.pack("<ff",0.0,0.0))

    # Head/Lift
    def headup(self,duration=None,radians=0.5): self._head(radians,duration)
    def headdown(self,duration=None,radians=-0.5): self._head(radians,duration)
    def _head(self,r,duration):
        self.send(MSG_HEAD, struct.pack("<f",float(r)))
        if duration: time.sleep(duration); self.send(MSG_HEAD, struct.pack("<f",0.0))
    def liftup(self,duration=None,mm=10.0): self._lift(mm,duration)
    def liftdown(self,duration=None,mm=-10.0): self._lift(mm,duration)
    def _lift(self,mm,duration):
        self.send(MSG_LIFT, struct.pack("<f",float(mm)))
        if duration: time.sleep(duration); self.send(MSG_LIFT, struct.pack("<f",0.0))

    # Backpack
    def backlight(self,color):
        if color is None: return
        if isinstance(color,(list,tuple)) and len(color)>=3:
            r,g,b = map(int,color[:3])
        else:
            s = str(color)
            if s.startswith("#"): s = s[1:]
            if len(s) != 6: return
            r = int(s[0:2],16); g = int(s[2:4],16); b = int(s[4:6],16)
        r5 = max(0,min(31,(r*31)//255)); g5 = max(0,min(31,(g*31)//255)); b5 = max(0,min(31,(b*31)//255))
        value15 = (r5<<10)|(g5<<5)|b5
        self.send(MSG_BACKPACK, struct.pack("<H", value15))

    # OLED/Face
    def Img(self,raw_bytes): self.send(MSG_DISPLAY,raw_bytes)
    def stopface(self): self.send(MSG_FREEZE_FACE,b'\x00')
    def resumeface(self): self.send(MSG_FREEZE_FACE,b'\x01')

    # Audio/TTS
    def paudio(self,clip_id): self.send(MSG_PLAY_AUDIO,struct.pack("<H",int(clip_id)))
    def saudio(self): self.send(MSG_STOP_AUDIO)
    def setvol(self,level): self.send(MSG_SET_VOLUME, struct.pack("B",int(level)))
    def tts(self,text):
        if not isinstance(text,str): return
        try:
            subprocess.Popen(["espeak", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("Install espeak for TTS.", file=sys.stderr)

    # Wait
    def wait(self,seconds): time.sleep(float(seconds))

    # Camera
    def camera(self):
        if cv2 is None: return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened(): return
        while True:
            ret,frame = cap.read()
            if not ret: break
            cv2.imshow("Cozmo/Local Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cap.release(); cv2.destroyAllWindows()
    def camerargb(self,enable=True): self.cam_color = bool(enable)

    # Bind inputs
    def bind(self,action,*inputs):
        self._key_map.setdefault(action,[]).extend([str(i).lower() for i in inputs])
        self._start_listener()
        return self

    # Listener
    def _start_listener(self):
        if self._listener_started: return
        self._listener_started = True

        # Keyboard listener
        if _pynput_keyboard:
            def kb_thread():
                def on_press(key):
                    try:
                        k = None
                        if hasattr(key,"char") and key.char is not None: k = key.char
                        elif hasattr(key,"name"): k = key.name
                        if k is None: return
                        k = str(k).lower()
                        for action,binds in list(self._key_map.items()):
                            if k in binds:
                                f = getattr(self,action,None)
                                if callable(f):
                                    try: f(duration=0.1)
                                    except TypeError: f()
                    except: pass
                listener = _pynput_keyboard.Listener(on_press=on_press)
                listener.daemon = True
                listener.start()
            threading.Thread(target=kb_thread, daemon=True).start()

        # Controller listener
        if get_gamepad:
            def gp_thread():
                while True:
                    try:
                        events = get_gamepad()
                        for e in events:
                            name = _CONTROLLER_NAMES.get(e.code)
                            if name:
                                for action, binds in self._key_map.items():
                                    if name.lower() in [b.lower() for b in binds]:
                                        f = getattr(self,action,None)
                                        if callable(f):
                                            try: f(duration=0.1)
                                            except TypeError: f()
                    except: pass
            threading.Thread(target=gp_thread, daemon=True).start()

# Single global instance
_co = Coraw()
co = _co

# Convenience wrappers
def ping(): return _co.ping()
def stop(): return _co.stop()
def close(): return _co.close()
def forward(duration=None,speed=120.0): return _co.forward(duration,speed)
def back(duration=None,speed=120.0): return _co.back(duration,speed)
def left(duration=None,rad=2.0): return _co.left(duration,rad)
def right(duration=None,rad=2.0): return _co.right(duration,rad)
def stop_move(): return _co.stop_move()
def headup(duration=None,radians=0.5): return _co.headup(duration,radians)
def headdown(duration=None,radians=-0.5): return _co.headdown(duration,radians)
def liftup(duration=None,mm=10.0): return _co.liftup(duration,mm)
def liftdown(duration=None,mm=-10.0): return _co.liftdown(duration,mm)
def backlight(color): return _co.backlight(color)
def Img(raw_bytes): return _co.Img(raw_bytes)
def stopface(): return _co.stopface()
def resumeface(): return _co.resumeface()
def paudio(clip_id): return _co.paudio(clip_id)
def saudio(): return _co.saudio()
def setvol(level): return _co.setvol(level)
def tts(text): return _co.tts(text)
def wait(seconds): return _co.wait(seconds)
def bind(action,*inputs): return _co.bind(action,*inputs)
def camera(): return _co.camera()
def camerargb(enable=True): return _co.camerargb(enable)

# Tkinter helper
def tkint(cmd, options=None):
    options = options or {}
    target = None
    if callable(cmd):
        target = cmd
        name = getattr(cmd,"__name__","").lower()
    else:
        name = str(cmd).lower()
    # Backpack color picker
    if name in ("backlight","backpack"):
        try:
            root = tk.Tk(); root.withdraw()
            color = colorchooser.askcolor(title=options.get("title","Pick backpack color"))
            root.destroy()
            if color and color[1]: _co.backlight(color[1])
        except Exception:
            print("tkinter not available", file=sys.stderr)
    # TTS window
    elif name in ("tts","speak") or target is _co.tts:
        def run_tts_window():
            r = tk.Tk()
            r.title(options.get("title","Cozmo TTS"))
            tk.Label(r, text="Enter text:").pack()
            txt = tk.Text(r, height=4, width=40); txt.pack()
            def send():
                s = txt.get("1.0", "end").strip()
                _co.tts(s)
            tk.Button(r, text="Send", command=send).pack()
            r.mainloop()
        threading.Thread(target=run_tts_window, daemon=True).start()
    # Camera window
    elif name == "camera":
        threading.Thread(target=_co.camera, daemon=True).start()
    else:
        print("tkint unknown command:", cmd)
