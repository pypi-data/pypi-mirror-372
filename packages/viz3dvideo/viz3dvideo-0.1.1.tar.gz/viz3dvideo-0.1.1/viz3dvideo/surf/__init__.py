#!/usr/bin/python3

"""
viz3dvideo.surf
===============

Subpackage for 3D surface visualizations.

Provides functions to animate 3D surfaces (Z = f(X, Y)). You can
either rotate the camera around the surface or follow a custom camera path.

Available functions:

- animate_rotate(X, Y, Z, ...) : Create a rotating 3D surface animation.
- animate_path(X, Y, Z, camera_points, ...) : Animate a surface following a camera path.

Example usage::

    from viz3dvideo.surf import animate_path
    
    animate_path(X, Y, Z, camera_points=[(30,0),(45,90)])
"""

from .rotate import animate_rotate
from .path   import animate_path

