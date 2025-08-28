import pycozmo
import time
import subprocess
import io
import wave
import numpy as np

class Cozmo:
    def __init__(self):
        self.cli = pycozmo.Client()
        self.cli.start()
        self.cli.connect()
        self.cli.wait_for_robot()

    def disconnect(self):
        self.cli.disconnect()
        self.cli.stop()

    # ---------------- Movement ----------------
    def forward(self, duration=1.0, speed=50.0):
        self.cli.drive_wheels(lwheel_speed=speed, rwheel_speed=speed)
        time.sleep(duration)
        self.cli.stop_all_motors()

    def back(self, duration=1.0, speed=50.0):
        self.cli.drive_wheels(lwheel_speed=-speed, rwheel_speed=-speed)
        time.sleep(duration)
        self.cli.stop_all_motors()

    def left(self, duration=0.5, speed=30.0):
        self.cli.drive_wheels(lwheel_speed=-speed, rwheel_speed=speed)
        time.sleep(duration)
        self.cli.stop_all_motors()

    def right(self, duration=0.5, speed=30.0):
        self.cli.drive_wheels(lwheel_speed=speed, rwheel_speed=-speed)
        time.sleep(duration)
        self.cli.stop_all_motors()

    def stop(self):
        self.cli.stop_all_motors()

    # ---------------- Head & Lift ----------------
    def liftup(self):
        self.cli.move_lift(5.0)

    def liftdown(self):
        self.cli.move_lift(-5.0)

    def headup(self):
        self.cli.move_head(5.0)

    def headdown(self):
        self.cli.move_head(-5.0)

    # ---------------- Audio ----------------
    def tts(self, text):
        wav = subprocess.check_output(["espeak", "-w", "/dev/stdout", text])
        with io.BytesIO(wav) as f:
            wf = wave.open(f, "rb")
            frames = wf.readframes(wf.getnframes())
            # Pycozmo expects 16 kHz mono, convert if needed
            self.cli.send_audio(frames)

    # ---------------- Cube Dock (stub) ----------------
    def cubedock(self, cube_id=1):
        # Use pycozmo’s world state / object detection
        print(f"[TODO] Docking with cube {cube_id} not yet implemented.")
