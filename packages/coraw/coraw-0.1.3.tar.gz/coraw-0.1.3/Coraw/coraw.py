#!/usr/bin/env python3
# coraw.py -- Full Coraw module (PyCozmo wrapper) with Tkinter helpers, camera, draw GUI, wait, ping, bind, etc.

import time
import threading
import subprocess
import sys
from typing import Optional, Tuple

# Try pycozmo (optional)
try:
    import pycozmo
    from pycozmo.client import Client
except Exception:
    Client = None

# PIL for draw GUI
try:
    from PIL import Image, ImageDraw
except Exception:
    Image = None
    ImageDraw = None

# OpenCV + numpy for camera display (optional)
try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None

# Optional input libs for bind()
try:
    from pynput import keyboard as _pynput_keyboard
except Exception:
    _pynput_keyboard = None

try:
    from inputs import get_gamepad
except Exception:
    get_gamepad = None

# tkinter lazy import helper used by tkint / draw GUI
def _safe_tk():
    try:
        import tkinter as tk
        from tkinter import colorchooser, simpledialog
        return tk, colorchooser, simpledialog
    except Exception:
        return None, None, None

class CorawWrapper:
    def __init__(self, robot_addr: Optional[Tuple[str,int]] = None, auto_connect: bool = False):
        # robot_addr optionally (ip,port) for pycozmo Client
        if Client is None:
            self.client = None
            print("pycozmo not installed or failed to import.", file=sys.stderr)
        else:
            try:
                self.client = Client(robot_addr)
            except Exception as e:
                self.client = None
                print("Failed to create pycozmo Client:", e, file=sys.stderr)

        self._connected = False
        self._ping_thread = None
        self._pinging = False
        self._key_map = {}
        self._listener_started = False
        self.cam_color = True           # True => RGB, False => greyscale
        self._camera_thread = None
        self._camera_running = False

        if auto_connect:
            self.connect()

    # ----------------- Connection -----------------
    def connect(self, wait_for_robot: bool = True, timeout: float = 10.0):
        if self.client is None:
            print("No pycozmo client available.", file=sys.stderr)
            return False
        if self._connected:
            return True
        try:
            # start and connect
            self.client.start()
            self.client.connect()
            if wait_for_robot:
                try:
                    self.client.wait_for_robot(timeout=timeout)
                except Exception:
                    # some pycozmo versions use different wait semantics
                    pass
            self._connected = True
            return True
        except Exception as e:
            print("connect error:", e, file=sys.stderr)
            return False

    def disconnect(self):
        try:
            if self._connected and self.client:
                try: self.client.disconnect()
                except: pass
                try: self.client.stop()
                except: pass
        finally:
            self._connected = False

    # convenience robust connect with retries
    def connect_robust(self, retries=3, wait=2.0):
        for i in range(retries):
            if self.connect():
                return True
            time.sleep(wait)
        return False

    # ----------------- Ping / keepalive -----------------
    def ping(self):
        """Start a keepalive loop so the library/robot doesn't drop idle connections."""
        if self._pinging: return
        self._pinging = True
        def loop():
            while self._pinging:
                try:
                    if self.client and hasattr(self.client, "get_robot_state"):
                        try:
                            _ = self.client.get_robot_state()
                        except Exception:
                            pass
                    elif self.client:
                        try:
                            self.client.drive_wheels(lwheel_speed=0.0, rwheel_speed=0.0, duration=0.01)
                        except Exception:
                            pass
                except Exception:
                    pass
                time.sleep(0.5)
        self._ping_thread = threading.Thread(target=loop, daemon=True)
        self._ping_thread.start()

    def stop_ping(self):
        self._pinging = False
        self._ping_thread = None

    # ----------------- Movement -----------------
    def forward(self, duration: Optional[float]=None, speed: float=120.0):
        if not self.client: return
        try:
            self.client.drive_wheels(lwheel_speed=float(speed), rwheel_speed=float(speed), duration=(duration or 0.0))
            if duration and duration > 0:
                time.sleep(duration)
                self.stop_move()
        except Exception as e:
            print("forward error:", e, file=sys.stderr)

    def back(self, duration: Optional[float]=None, speed: float=120.0):
        if not self.client: return
        try:
            self.client.drive_wheels(lwheel_speed=-float(speed), rwheel_speed=-float(speed), duration=(duration or 0.0))
            if duration and duration > 0:
                time.sleep(duration)
                self.stop_move()
        except Exception as e:
            print("back error:", e, file=sys.stderr)

    def left(self, duration: Optional[float]=None, speed: float=60.0):
        if not self.client: return
        try:
            self.client.drive_wheels(lwheel_speed=-float(speed), rwheel_speed=float(speed), duration=(duration or 0.0))
            if duration and duration > 0:
                time.sleep(duration)
                self.stop_move()
        except Exception as e:
            print("left error:", e, file=sys.stderr)

    def right(self, duration: Optional[float]=None, speed: float=60.0):
        if not self.client: return
        try:
            self.client.drive_wheels(lwheel_speed=float(speed), rwheel_speed=-float(speed), duration=(duration or 0.0))
            if duration and duration > 0:
                time.sleep(duration)
                self.stop_move()
        except Exception as e:
            print("right error:", e, file=sys.stderr)

    def stop_move(self):
        if not self.client: return
        try:
            self.client.stop_all_motors()
        except Exception:
            pass

    # ----------------- Head / Lift -----------------
    def headup(self, duration: Optional[float]=None, radians: float=0.5):
        if not self.client: return
        try:
            self.client.set_head_angle(angle=float(radians))
            if duration:
                time.sleep(duration)
                try: self.client.set_head_angle(angle=0.0)
                except: pass
        except Exception as e:
            print("headup error:", e, file=sys.stderr)

    def headdown(self, duration: Optional[float]=None, radians: float=-0.5):
        self.headup(duration=duration, radians=radians)

    def liftup(self, duration: Optional[float]=None, mm: float=10.0):
        if not self.client: return
        try:
            self.client.set_lift_height(height_mm=float(mm))
            if duration:
                time.sleep(duration)
                try: self.client.set_lift_height(height_mm=0.0)
                except: pass
        except Exception as e:
            print("liftup error:", e, file=sys.stderr)

    def liftdown(self, duration: Optional[float]=None, mm: float=-10.0):
        self.liftup(duration=duration, mm=mm)

    # ----------------- Backpack LEDs -----------------
    def backlight(self, color):
        if not self.client: return
        if color is None: return
        try:
            if isinstance(color, (list, tuple)):
                r,g,b = map(int, color[:3])
            else:
                s = str(color)
                if s.startswith("#"): s = s[1:]
                if len(s) != 6: return
                r = int(s[0:2], 16); g = int(s[2:4], 16); b = int(s[4:6], 16)
            # convert 0-255 to 0-31 (5-bit)
            r5 = max(0, min(31, (r*31)//255))
            g5 = max(0, min(31, (g*31)//255))
            b5 = max(0, min(31, (b*31)//255))
            try:
                self.client.set_backpack_lights((r5, g5, b5))
            except Exception:
                try:
                    self.client.set_all_backpack_lights(r, g, b)
                except Exception:
                    pass
        except Exception as e:
            print("backlight error:", e, file=sys.stderr)

    # ----------------- Face / Display -----------------
    def Img(self, pil_image):
        if not self.client: return
        try:
            # pycozmo versions differ; try high level display_image or display_image_bytes
            if hasattr(self.client, "display_image"):
                self.client.display_image(pil_image)
            else:
                # fallback: try passing bytes if available
                try:
                    raw = pil_image.tobytes()
                    if hasattr(self.client, "display_image_bytes"):
                        self.client.display_image_bytes(raw)
                except Exception:
                    pass
        except Exception as e:
            print("Img error:", e, file=sys.stderr)

    def stopface(self):
        if not self.client: return
        try:
            if hasattr(self.client, "enable_procedural_face"):
                self.client.enable_procedural_face(False)
            elif hasattr(self.client, "anim_controller"):
                self.client.anim_controller.enable_procedural_face(False)
        except Exception:
            pass

    def resumeface(self):
        if not self.client: return
        try:
            if hasattr(self.client, "enable_procedural_face"):
                self.client.enable_procedural_face(True)
            elif hasattr(self.client, "anim_controller"):
                self.client.anim_controller.enable_procedural_face(True)
        except Exception:
            pass

    # ----------------- Audio / TTS -----------------
    def paudio(self, clip_id: int):
        if not self.client: return
        try:
            # older/newer pycozmo may vary
            if hasattr(self.client, "play_audio"):
                self.client.play_audio(clip_id)
            elif hasattr(self.client, "play_sound"):
                self.client.play_sound(clip_id)
        except Exception as e:
            print("paudio error:", e, file=sys.stderr)

    def saudio(self):
        if not self.client: return
        try:
            if hasattr(self.client, "stop_audio"):
                self.client.stop_audio()
            else:
                # fallback to stop_all_motors/stop
                try: self.client.stop()
                except: pass
        except Exception:
            pass

    def setvol(self, level: int):
        if not self.client: return
        try:
            if hasattr(self.client, "set_volume"):
                self.client.set_volume(level)
        except Exception as e:
            print("setvol error:", e, file=sys.stderr)

    def tts(self, text: str):
        if not isinstance(text, str): return
        try:
            subprocess.Popen(["espeak", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("espeak not installed", file=sys.stderr)

    # ----------------- Wait -----------------
    def wait(self, seconds):
        """Wait for given seconds. Example: co.wait(2)"""
        try:
            time.sleep(float(seconds))
        except Exception as e:
            print("wait error:", e, file=sys.stderr)

    # ----------------- Draw GUI -----------------
    def draw_gui(self, title="Cozmo Draw", width=128, height=64):
        tk, colorchooser, simpledialog = _safe_tk()
        if tk is None or Image is None:
            print("tkinter or PIL not available", file=sys.stderr)
            return
        scale = 4
        cw, ch = width*scale, height*scale
        root = tk.Tk()
        root.title(title)
        canvas = tk.Canvas(root, width=cw, height=ch, bg="black")
        canvas.pack()
        img = Image.new("RGB", (width, height), (0,0,0))
        draw = ImageDraw.Draw(img)
        drawing = {"down": False, "last": None}
        def s2i(x,y): return int(x/scale), int(y/scale)
        def on_down(e):
            drawing["down"] = True
            drawing["last"] = (e.x, e.y)
        def on_up(e):
            drawing["down"] = False
            drawing["last"] = None
        def on_move(e):
            if not drawing["down"]: return
            lx, ly = drawing["last"] or (e.x, e.y)
            canvas.create_line(lx, ly, e.x, e.y, fill="white", width=2)
            x1, y1 = s2i(lx, ly); x2, y2 = s2i(e.x, e.y)
            draw.line((x1, y1, x2, y2), fill=(255,255,255))
            drawing["last"] = (e.x, e.y)
        def send():
            try:
                self.Img(img)
            except Exception as e:
                print("send draw error:", e, file=sys.stderr)
        btn = tk.Button(root, text="Send to Cozmo", command=send)
        btn.pack(fill="x")
        canvas.bind("<ButtonPress-1>", on_down)
        canvas.bind("<ButtonRelease-1>", on_up)
        canvas.bind("<B1-Motion>", on_move)
        root.mainloop()

    # ----------------- Camera -----------------
    def _camera_loop(self):
        # Try to get frames from pycozmo client if available, else fallback to local webcam via OpenCV
        use_local_cam = False
        cap = None
        get_frame = None

        def pil_to_bgr(pil_img):
            arr = np.array(pil_img.convert("RGB"))
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            return bgr

        # try pycozmo hooks
        if self.client is not None:
            try:
                # try different common attributes that pycozmo versions provide
                if hasattr(self.client, "get_latest_image"):
                    get_frame = lambda: self.client.get_latest_image()
                elif hasattr(self.client, "world") and getattr(self.client.world, "latest_image", None) is not None:
                    get_frame = lambda: self.client.world.latest_image
                elif hasattr(self.client, "get_camera_frame"):
                    get_frame = lambda: self.client.get_camera_frame()
            except Exception:
                get_frame = None

        if get_frame is None:
            # fallback to local webcam
            if cv2 is None:
                print("No camera source available (need pycozmo image API or OpenCV).", file=sys.stderr)
                return
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("Local webcam not available.", file=sys.stderr)
                    return
                use_local_cam = True
            except Exception as e:
                print("webcam open error:", e, file=sys.stderr)
                return

        window_name = "Cozmo Camera"
        if cv2:
            try: cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            except Exception: pass

        self._camera_running = True
        while self._camera_running:
            frame = None
            try:
                if use_local_cam and cap is not None:
                    ret, frame = cap.read()
                    if not ret:
                        frame = None
                else:
                    imgobj = None
                    try:
                        imgobj = get_frame()
                    except Exception:
                        imgobj = None
                    if imgobj is None:
                        time.sleep(0.1)
                        continue
                    # if a PIL Image
                    if Image is not None and hasattr(imgobj, "convert"):
                        frame = pil_to_bgr(imgobj)
                    else:
                        # try decode bytes
                        try:
                            arr = np.frombuffer(imgobj, dtype=np.uint8)
                            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                        except Exception:
                            frame = None
                if frame is None:
                    time.sleep(0.05)
                    continue
                # camerargb flag: if False, convert to greyscale
                if not self.cam_color and cv2 is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if cv2 is not None:
                    cv2.imshow(window_name, frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            except Exception:
                time.sleep(0.05)
                continue

        self._camera_running = False
        if cap:
            try: cap.release()
            except: pass
        if cv2:
            try: cv2.destroyWindow(window_name)
            except: pass

    def camera(self):
        """Open camera window in background thread. Press 'q' to close."""
        if self._camera_running:
            return
        self._camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self._camera_thread.start()

    def camerargb(self, enable=True):
        """Enable/disable RGB (color). If disabled, camera window shows greyscale."""
        self.cam_color = bool(enable)

    # ----------------- Bindings -----------------
    def bind(self, action_name: str, *inputs):
        """Bind a method name (string) to keys/controller inputs."""
        self._key_map.setdefault(action_name, []).extend([str(i).lower() for i in inputs])
        self._start_listener()
        return self

    def _start_listener(self):
        if self._listener_started:
            return
        self._listener_started = True

        # keyboard listener (pynput)
        if _pynput_keyboard:
            def kb_thread():
                def on_press(key):
                    try:
                        k = None
                        if hasattr(key, "char") and key.char is not None:
                            k = key.char
                        elif hasattr(key, "name"):
                            k = key.name
                        if k is None:
                            return
                        k = str(k).lower()
                        for action, binds in list(self._key_map.items()):
                            if k in binds:
                                f = getattr(self, action, None)
                                if callable(f):
                                    try: f(duration=0.1)
                                    except TypeError: f()
                    except Exception:
                        pass
                listener = _pynput_keyboard.Listener(on_press=on_press)
                listener.daemon = True
                listener.start()
            threading.Thread(target=kb_thread, daemon=True).start()

        # controller listener (inputs)
        if get_gamepad:
            def gp_thread():
                while True:
                    try:
                        events = get_gamepad()
                        for e in events:
                            nm = e.code.lower()
                            for action, binds in self._key_map.items():
                                if nm in [b.lower() for b in binds]:
                                    f = getattr(self, action, None)
                                    if callable(f):
                                        try: f(duration=0.1)
                                        except TypeError: f()
                    except Exception:
                        pass
            threading.Thread(target=gp_thread, daemon=True).start()

    # ----------------- Tkinter helpers (tkint) -----------------
    def tkint(self, cmd, options=None):
        options = options or {}
        target = None
        if callable(cmd):
            target = cmd
            name = getattr(cmd, "__name__", "").lower()
        else:
            name = str(cmd).lower()

        tk, colorchooser, simpledialog = _safe_tk()
        if tk is None:
            print("tkinter not available", file=sys.stderr)
            return

        # backlight color picker
        if name in ("backlight", "backpack"):
            try:
                root = tk.Tk(); root.withdraw()
                color = colorchooser.askcolor(title=options.get("title", "Pick backpack color"))
                root.destroy()
                if color and color[1]:
                    self.backlight(color[1])
            except Exception as e:
                print("tkint backlight error:", e, file=sys.stderr)

        # tts window
        elif name in ("tts", "speak") or target is self.tts:
            def run_tts():
                r = tk.Tk(); r.title(options.get("title", "Cozmo TTS"))
                tk.Label(r, text="Enter text:").pack()
                txt = tk.Text(r, height=4, width=40); txt.pack()
                def send():
                    s = txt.get("1.0", "end").strip()
                    self.tts(s)
                tk.Button(r, text="Send", command=send).pack()
                r.mainloop()
            threading.Thread(target=run_tts, daemon=True).start()

        # draw GUI
        elif name in ("draw", "oled", "display", "img"):
            threading.Thread(target=self.draw_gui, args=(options.get("title", "Cozmo Draw"),), daemon=True).start()

        # camera window
        elif name == "camera":
            self.camera()

        # camerargb toggle UI
        elif name == "camerargb":
            def run_cam_ui():
                r = tk.Tk(); r.title("Camera RGB toggle")
                var = tk.BooleanVar(value=self.cam_color)
                def on_toggle(): self.camerargb(var.get())
                tk.Checkbutton(r, text="Enable color", variable=var, command=on_toggle).pack()
                r.mainloop()
            threading.Thread(target=run_cam_ui, daemon=True).start()

        else:
            print("tkint unknown command:", cmd)

    # ----------------- Close / cleanup -----------------
    def close(self):
        # stop camera if running
        try:
            self._camera_running = False
            if self._camera_thread:
                try: self._camera_thread.join(timeout=0.2)
                except: pass
        except Exception:
            pass
        self.disconnect()

# ----------------- single global instance & module-level wrappers -----------------
_co = CorawWrapper()
co = _co

def connect(*a, **k): return _co.connect(*a, **k)
def connect_robust(*a, **k): return _co.connect_robust(*a, **k)
def ping(): return _co.ping()
def stop_ping(): return _co.stop_ping()
def disconnect(): return _co.disconnect()
def close(): return _co.close()
def forward(duration=None, speed=120.0): return _co.forward(duration, speed)
def back(duration=None, speed=120.0): return _co.back(duration, speed)
def left(duration=None, speed=60.0): return _co.left(duration, speed)
def right(duration=None, speed=60.0): return _co.right(duration, speed)
def stop_move(): return _co.stop_move()
def headup(duration=None, radians=0.5): return _co.headup(duration, radians)
def headdown(duration=None, radians=-0.5): return _co.headdown(duration, radians)
def liftup(duration=None, mm=10.0): return _co.liftup(duration, mm)
def liftdown(duration=None, mm=-10.0): return _co.liftdown(duration, mm)
def backlight(color): return _co.backlight(color)
def Img(img): return _co.Img(img)
def stopface(): return _co.stopface()
def resumeface(): return _co.resumeface()
def paudio(clip_id): return _co.paudio(clip_id)
def saudio(): return _co.saudio()
def setvol(level): return _co.setvol(level)
def tts(text): return _co.tts(text)
def wait(seconds): return _co.wait(seconds)
def draw(title="Cozmo Draw"): return _co.draw_gui(title)
def bind(action, *inputs): return _co.bind(action, *inputs)
def camera(): return _co.camera()
def camerargb(enable=True): return _co.camerargb(enable)
def tkint(cmd, options=None): return _co.tkint(cmd, options)

# End of coraw.py
