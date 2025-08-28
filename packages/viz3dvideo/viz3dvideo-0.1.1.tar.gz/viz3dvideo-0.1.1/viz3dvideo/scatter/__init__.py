#!/usr/bin/python3

"""
viz3dvideo.scatter
==================

Subpackage for 3D scatter visualizations.

This subpackage provides functions to create animated 3D scatter plots
using Matplotlib. Animations can either rotate around the data or follow
a custom camera path.

Available functions:

- animate_rotate(X, Y, Z, W, ...) : Create a rotating 3D scatter plot animation.
- animate_path(X, Y, Z, W, camera_points, ...) : Animate a scatter plot following a camera path.

Example usage::

    from viz3dvideo.scatter import animate_rotate
    
    animate_rotate(X, Y, Z, W, frames=360, fps=30)

"""

from .rotate import animate_rotate
from .path   import animate_path


