from setuptools import setup, find_packages

setup(
    name="coraw",
    version="0.1.2",
    description="Simplest cozmo raw data sender",
    author="Alan",
    author_email="dipdoptrip@gmail.com",
    url="https://github.com/yourname/coraw",
    packages=find_packages(),
    install_requires=[
        "pynput",
        "inputs",
        "opencv-python",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
