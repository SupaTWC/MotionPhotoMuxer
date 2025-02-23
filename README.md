MotionPhotoMuxer
================

Convert Apple Live Photos into Google Motion Photos commonly found on Android phones. This fork is meant for Windows use only.

# Windows Installation

This fork uses only 1 dependency 'pyexiv2' instead of 'py3exiv2' since it's way easier to install on Windows. https://github.com/LeoHsiao1/pyexiv2


Install Python (might need to install the 64 bit version)

Install Microsoft Visual C++ https://visualstudio.microsoft.com/downloads/#microsoft-visual-c-redistributable-for-visual-studio-2019
~~~
pip install pyexiv2
~~~

# Usage

~~~
usage: MotionPhotoMuxer.py [-h] [--verbose] [--dir DIR] [--recurse] [--photo PHOTO] [--video VIDEO]
In Command Prompt: python MotionPhotoMuxer.py [-h] [--verbose] [--dir DIR] [--recurse] [--photo PHOTO] [--video VIDEO
Merges a photo and video into a Microvideo-formatted Google Motion Photo

optional arguments:
  -h, --help     show this help message and exit
  --verbose      Show logging messages.
  --dir DIR      Process a directory for photos/videos. Takes precedence over --photo/--video
  --recurse      Recursively process a directory. Only applies if --dir is also provided, not working yet.
  --photo PHOTO  Path to the JPEG photo to add.
  --video VIDEO  Path to the MOV video to add.
~~~

A JPEG photo and MOV or MP4 video must be provided. The code only does simple
error checking to see if the file extensions are `.jpg|.jpeg` and `.mov|.mp4`
respectively, so if the actual photo/video encoding is something funky, things
may not work right.

This has been tested successfully on a couple photos taken on an iPhone 12 and
uploaded to Google Photos through a Pixel XL, but there hasn't been any
extensive testing done yet, so use at your own risk!

# Credit

This wouldn't have been possible without the excellent writeup on the process
of working with Motion Photos [here](https://medium.com/android-news/working-with-motion-photos-da0aa49b50c).
