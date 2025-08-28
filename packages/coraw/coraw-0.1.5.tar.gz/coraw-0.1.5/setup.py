from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="coraw",
    version="0.1.5",
    description="Simplest Cozmo raw data sender",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alan",
    author_email="dipdoptrip@gmail.com",
    url="https://github.com/yourname/coraw",
    packages=find_packages(),
    install_requires=[
        "pynput",
        "inputs",
        "opencv-python",
        "Pillow",  # Needed for draw()
        "numpy"    # Needed for cubedock() / image processing
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
