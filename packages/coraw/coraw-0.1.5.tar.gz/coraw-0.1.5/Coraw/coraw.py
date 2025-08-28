import socket
import struct
import threading
import time
import subprocess
import io
from PIL import Image, ImageGrab
import tkinter as tk
from tkinter import colorchooser
import cv2
import numpy as np

COZMO_IP = "172.31.1.1"
COZMO_PORT = 5551

# === Protocol / Frame utilities ===
_seq_lock = threading.Lock()
_seq = 0

def _next_seq():
    global _seq
    with _seq_lock:
        _seq = (_seq + 1) % 0xFFFF
        return _seq

def build_frame(cmd_id, payload=b''):
    length = 6 + len(payload)
    header = struct.pack("<HHH", _next_seq(), length, cmd_id)
    return header + payload

# === Client ===
class CozmoClient:
    def __init__(self, ip=COZMO_IP, port=COZMO_PORT):
        self.addr = (ip, port)
        self.sock = None
        self.running = False
        self.recv_thread = None
        self._latest_frame = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect(self.addr)
        self.running = True
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
        print("Connected to Cozmo")

    def disconnect(self):
        self.running = False
        if self.sock:
            self.sock.close()
        print("Disconnected")

    def send(self, cmd_id, payload=b''):
        frame = build_frame(cmd_id, payload)
        self.sock.send(frame)

    def _recv_loop(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                # Simple camera frame parsing
                start = data.find(b'\xFF\xD8')
                end = data.find(b'\xFF\xD9', start+2)
                if start != -1 and end != -1:
                    jpg = data[start:end+2]
                    self._latest_frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
            except Exception:
                continue

# === Robot Commands ===
class Cozmo:
    def __init__(self, client):
        self.client = client

    # Movement
    def drive(self, lspeed, rspeed, laccel=1000.0, raccel=1000.0, duration=None):
        payload = struct.pack("<ffff", lspeed, rspeed, laccel, raccel)
        self.client.send(0x32, payload)
        if duration:
            time.sleep(duration)
            self.stop()

    def forward(self, duration=None): self.drive(50.0, 50.0, duration=duration)
    def back(self, duration=None): self.drive(-50.0, -50.0, duration=duration)
    def left(self, duration=None): self.drive(-50.0, 50.0, duration=duration)
    def right(self, duration=None): self.drive(50.0, -50.0, duration=duration)
    def stop(self): self.client.send(0x3B)

    # Lift / Head
    def liftup(self, speed=1.0): self.client.send(0x34, struct.pack("<f", speed))
    def liftdown(self, speed=1.0): self.client.send(0x34, struct.pack("<f", -speed))
    def headup(self, speed=1.0): self.client.send(0x35, struct.pack("<f", speed))
    def headdown(self, speed=1.0): self.client.send(0x35, struct.pack("<f", -speed))

    # Procedural Face commands
    def stopface(self): print("Face generation stopped")
    def resume(self): print("Face generation resumed")

    # Audio
    def paudio(self, audio_bytes): self.client.send(0x8E, audio_bytes)
    def saudio(self): self.client.send(0x8F)
    def setvol(self, level): self.client.send(0x64, struct.pack("<H", level))
    def tts(self, text):
        wav = subprocess.check_output(["espeak", "--stdout", text])
        # strip header (not ideal, ensure 16kHz mono)
        payload = wav[44:]
        self.client.send(0x8E, payload)

    # Cube Docking
    def cubedock(self, cube_id):
        print(f"Attempting to dock cube {cube_id}")
        if self.client._latest_frame is None:
            print("No camera frame yet")
            return
        frame = self.client._latest_frame
        # Dummy ORB detection (for illustration)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create()
        kp, des = orb.detectAndCompute(gray, None)
        print(f"Detected {len(kp)} keypoints")
        # Move forward for example
        self.forward(1.0)
        self.liftup(1.0)

    # Display / Draw
    def draw(self):
        def submit():
            ps = canvas.postscript(colormode="mono")
            img = Image.open(io.BytesIO(ps.encode("latin-1")))
            rgb565 = ((np.array(img)[:,:,0]>>3)<<11)|((np.array(img)[:,:,1]>>2)<<5)|((np.array(img)[:,:,2]>>3))
            payload = rgb565.astype(">u2").tobytes()
            self.client.send(0x36, payload)
        root = tk.Tk()
        canvas = tk.Canvas(root, width=32, height=32, bg="black")
        canvas.pack()
        tk.Button(root, text="Send", command=submit).pack()
        threading.Thread(target=root.mainloop).start()

    # Backlight
    def backlight(self):
        def pick_color():
            color = colorchooser.askcolor()[0]
            if color:
                r,g,b = map(int, color)
                payload = struct.pack("<BBBBBBBBB", r,g,b, r,g,b, r,g,b)
                self.client.send(0x35, payload)
        root = tk.Tk()
        tk.Button(root, text="Pick color", command=pick_color).pack()
        threading.Thread(target=root.mainloop).start()

# === Example Usage ===
if __name__ == "__main__":
    client = CozmoClient()
    client.connect()
    robot = Cozmo(client)

    robot.forward(1.0)
    robot.left(0.5)
    robot.liftup()
    robot.headdown()
    robot.tts("Hello Cozmo")
    robot.backlight()
    robot.draw()
    robot.cubedock("1")

    time.sleep(5)
    robot.stop()
    client.disconnect()
