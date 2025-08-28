#!/usr/bin/python3

"""
viz3dvideo: Visualization of 3D graphs as videos.

This package provides utilities to generate videos of 3D data visualizations
using Matplotlib and MoviePy.

Subpackages
-----------
- :mod:`viz3dvideo.surf`
    Create and animate 3D surface plots, either rotating around the object
    or following a custom camera path.
- :mod:`viz3dvideo.scatter`
    Create and animate 3D scatter plots with rotation or along a camera path.
- :mod:`viz3dvideo.overlay`
    Overlay images (e.g., logos) onto existing videos.
- :mod:`viz3dvideo.audio`
    Add audio tracks to videos, with control over start time and synchronization.

Examples
--------
Typical usage::

    from viz3dvideo import scatter, surf, overlay, audio
    
    # Animate a rotating 3D scatter
    scatter.animate_rotate(X, Y, Z, W, output_path="scatter.mp4")
    
    # Animate a surface along a camera path
    surf.animate_path(X, Y, Z, camera_points=[(30, 0), (45, 90)], output_path="surface.mp4")
    
    # Overlay a logo on a video
    overlay.image_on_video("surface.mp4", "logo.png", position=(50, 50))
    
    # Add background music
    audio.add_to_video("surface.mp4", "music.mp3", start_time=5)
"""

from . import surf
from . import scatter
from . import overlay
from . import audio
