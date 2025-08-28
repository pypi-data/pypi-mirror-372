#!/usr/bin/python3

"""
viz3dvideo.audio
================

Subpackage for audio processing.

Provides functions to add audio tracks to existing videos.

Available functions:

- add_to_video(video_path, audio_path, start_time=0, output_path="output.mp4")

Example::

    from viz3dvideo.audio import add_to_video
    
    add_to_video("video.mp4", "audio.mp3", start_time=5)
"""

from .add import add_to_video
