import socket
import struct
import threading
import time
import io
import subprocess
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageColor
import numpy as np
import cv2

# Cozmo constants
COZMO_IP = "172.31.1.1"
COZMO_PORT = 5551

# Command IDs (placeholders, replace with actual AST IDs)
CMD_PING = 0x04
CMD_SYNC_TIME = 0x0A
CMD_DRIVE_WHEELS = 0x1B
CMD_MOVE_LIFT = 0x23
CMD_MOVE_HEAD = 0x25
CMD_DISPLAY_IMAGE = 0x96
CMD_SET_BACKPACK_LIGHTS = 0x03
CMD_ENABLE_CAMERA = 0x12
CMD_PLAY_AUDIO = 0x3C
CMD_STOP_AUDIO = 0x3D
CMD_SET_VOLUME = 0x40

# Globals
sock = None
seq = 0
running = False
ping_thread = None
recv_thread = None
_seq_lock = threading.Lock()
_latest_frame = None  # latest camera frame (BGR numpy array)

# Sequence number generator
def _next_seq():
    global seq
    with _seq_lock:
        seq = (seq + 1) & 0xFFFF
        return seq

# Frame builder
def build_frame(cmd_id, payload=b""):
    # Correct header: <HHH> = uint16 seq, uint16 length, uint16 cmd
    header = struct.pack("<HHH", _next_seq(), len(payload)+6, cmd_id)
    return header + payload

# Connect to Cozmo
def connect():
    global sock, running, ping_thread, recv_thread
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    sock.connect((COZMO_IP, COZMO_PORT))
    running = True

    def keepalive():
        while running:
            try:
                sock.send(build_frame(CMD_PING))
            except Exception:
                break
            time.sleep(0.2)

    def recv_loop():
        global _latest_frame
        while running:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception:
                continue
            # parse image chunks and update _latest_frame if needed
            if len(data) > 10:
                # very simplified JPEG detection (placeholder)
                start = data.find(b"\xFF\xD8")
                end = data.find(b"\xFF\xD9", start+2)
                if start != -1 and end != -1:
                    img_bytes = data[start:end+2]
                    try:
                        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                        _latest_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    except Exception:
                        pass

    ping_thread = threading.Thread(target=keepalive, daemon=True)
    ping_thread.start()
    recv_thread = threading.Thread(target=recv_loop, daemon=True)
    recv_thread.start()

    # Sync time
    now = time.time()
    sec = int(now)
    nsec = int((now - sec) * 1e9)
    sock.send(build_frame(CMD_SYNC_TIME, struct.pack("<II", sec, nsec)))

    # Enable camera (enable=1, res=4, fps=30)
    sock.send(build_frame(CMD_ENABLE_CAMERA, struct.pack("<BBB", 1, 4, 30)))

# Disconnect
def disconnect():
    global running, sock
    running = False
    if sock:
        try:
            sock.close()
        except Exception:
            pass
        sock = None

# Drive commands with optional duration
def drive(lspeed, rspeed, duration=None):
    payload = struct.pack("<ffff", lspeed, rspeed, 1000.0, 1000.0)
    sock.send(build_frame(CMD_DRIVE_WHEELS, payload))
    if duration:
        time.sleep(duration)
        stop()

def stop():
    payload = struct.pack("<ffff", 0.0, 0.0, 1000.0, 1000.0)
    sock.send(build_frame(CMD_DRIVE_WHEELS, payload))

def forward(duration=1.0): drive(50.0, 50.0, duration)
def back(duration=1.0): drive(-50.0, -50.0, duration)
def left(duration=1.0): drive(-30.0, 30.0, duration)
def right(duration=1.0): drive(30.0, -30.0, duration)

def liftup(): sock.send(build_frame(CMD_MOVE_LIFT, struct.pack("<f", 5.0)))
def liftdown(): sock.send(build_frame(CMD_MOVE_LIFT, struct.pack("<f", -5.0)))
def headup(): sock.send(build_frame(CMD_MOVE_HEAD, struct.pack("<f", 5.0)))
def headdown(): sock.send(build_frame(CMD_MOVE_HEAD, struct.pack("<f", -5.0)))

# Stop/resume face stubs
def stopface(): print("[stub] stopface")
def resumeface(): print("[stub] resumeface")

# Audio
def paudio(filename):
    with open(filename, "rb") as f:
        data = f.read()
    sock.send(build_frame(CMD_PLAY_AUDIO, data))

def saudio():
    sock.send(build_frame(CMD_STOP_AUDIO))

def setvol(vol):
    payload = struct.pack("<B", max(0, min(100, vol)))
    sock.send(build_frame(CMD_SET_VOLUME, payload))

def tts(text):
    wav = subprocess.check_output(["espeak", "--stdout", text])
    f = io.BytesIO(wav)
    f.read(12)
    pcm = None
    while True:
        chunk_id = f.read(4)
        if not chunk_id:
            break
        chunk_size = struct.unpack("<I", f.read(4))[0]
        if chunk_id == b"fmt ":
            fmt = f.read(chunk_size)
            audio_fmt, channels, rate, _, _, bits = struct.unpack("<HHIIHH", fmt[:16])
            if audio_fmt != 1 or channels != 1 or rate != 16000 or bits != 16:
                raise RuntimeError("TTS WAV must be 16kHz mono PCM")
        elif chunk_id == b"data":
            pcm = f.read(chunk_size)
            break
        else:
            f.seek(chunk_size, 1)
    if pcm:
        sock.send(build_frame(CMD_PLAY_AUDIO, pcm))

# Draw on OLED
def draw():
    def send_img():
        ps = canvas.postscript(colormode="mono")
        img = Image.open(io.BytesIO(ps.encode("latin-1"))).resize((128,64)).convert("RGB")
        arr = np.array(img, dtype=np.uint8)
        rgb565 = (((arr[:,:,0]>>3)<<11) | ((arr[:,:,1]>>2)<<5) | (arr[:,:,2]>>3)).astype("<u2").byteswap()
        payload = rgb565.tobytes()
        sock.send(build_frame(CMD_DISPLAY_IMAGE, payload))
    root = tk.Tk()
    canvas = tk.Canvas(root, width=128, height=64, bg="white")
    canvas.pack()
    canvas.bind("<B1-Motion>", lambda e: canvas.create_line(e.x, e.y, e.x+1, e.y+1))
    tk.Button(root, text="Send", command=send_img).pack()
    root.mainloop()

# Backlight control
def backlight(color=None):
    if color is None:
        _, hexcolor = colorchooser.askcolor()
        color = hexcolor
    r,g,b = ImageColor.getrgb(color)
    payload = struct.pack("<BBBBBBBBB", r,g,b, r,g,b, r,g,b)
    sock.send(build_frame(CMD_SET_BACKPACK_LIGHTS, payload))

# Cube docking using camera & ORB template matching
def cubedock(template_id="1"):
    if _latest_frame is None:
        print("[cubedock] No camera frame available")
        return
    # Load cube template image
    template = cv2.imread(f"cube_{template_id}.png", cv2.IMREAD_COLOR)
    if template is None:
        print(f"[cubedock] Cube template cube_{template_id}.png not found")
        return
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), None)
    kp2, des2 = orb.detectAndCompute(cv2.cvtColor(_latest_frame, cv2.COLOR_BGR2GRAY), None)
    if des1 is None or des2 is None:
        print("[cubedock] No keypoints found")
        return
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    if not matches:
        print("[cubedock] No matches")
        return
    # Find centroid of matches
    pts = np.array([kp2[m.trainIdx].pt for m in matches])
    cx, cy = pts.mean(axis=0)
    # Move Cozmo toward cube
    # Very simplified: assume frame center is 128x96
    center_x, center_y = _latest_frame.shape[1]/2, _latest_frame.shape[0]/2
    dx = cx - center_x
    dy = cy - center_y
    if abs(dx) > 5:
        if dx > 0: right(0.2)
        else: left(0.2)
    if abs(dy) > 5:
        forward(0.5)
    stop()
    liftup()

if __name__ == "__main__":
    connect()
    print("Connected to Cozmo. Try commands: forward(), back(), draw(), backlight(), tts('hello')")
