"""
Coraw
=====

Simplest raw Wi-Fi control library for Anki Cozmo.
This package allows sending basic movement, lift, head,
audio, display, and cube docking commands directly.

Example:
--------
from coraw import Cozmo

robot = Cozmo()
robot.connect()
robot.forward(1.0)
robot.tts("Hello, world!")
robot.disconnect()
"""

from .coraw import Cozmo

__all__ = ["Cozmo"]
__version__ = "0.1.4"
