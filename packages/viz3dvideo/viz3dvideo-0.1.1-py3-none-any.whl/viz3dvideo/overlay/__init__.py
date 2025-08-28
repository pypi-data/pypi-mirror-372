#!/usr/bin/python3

"""
viz3dvideo.overlay
==================

Subpackage for overlaying images on videos.

Provides functions to overlay static images on every frame of a video.

Available functions:

- image_on_video(video_path, image_path, position=(0,0), output_path="output.mp4")

Example::

    from viz3dvideo.overlay import image_on_video
    
    image_on_video("video.mp4", "logo.png", position=(50,50))
"""

from .image import image_on_video
