#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def animate_rotate( X, Y, Z, W,
                    output_path="animate_rotate.mp4",
                    pixel_size=(1920, 1080),
                    dpi=200,
                    colormap='viridis',
                    frames=360,
                    fps=30,
                    cb_enable=False,
                    cb_title="W",
                    elev=30,
                    interval=0.5,
                    s=40 ):
    """
    Creates and saves a 3D rotating scatter plot animation.

    Args:
        X (array-like): Coordinates X of the points (1D arrays).
        Y (array-like): Coordinates Y of the points (1D arrays).
        Z (array-like): Coordinates Z of the points (1D arrays).
        W (array-like): Values used to color the points.
        output_path (str, optional): Output video file. Default 'animate_rotate.mp4'.
        pixel_size (tuple, optional): Size of video in pixels. Default (1920, 1080).
        dpi (int, optional): Dots per inch. Default 100.
        colormap (str, optional): Matplotlib colormap for coloring. Default 'viridis'.
        elev (float, optional): Initial elevation angle. Default 30.
        frames (int, optional): Number of frames. Default 360.
        interval (float, optional): Angle interval between frames in degrees. Default is 1.0.
        fps (int, optional): Frames per second. Default 30.
        s (int, optional): Scatter point size. Default 40.
        cb_enable (bool, optional): Enable colorbar. Default False.
        cb_title (str, optional): Title of colorbar. Default "W".

    Returns:
        None
    """

    width, height = pixel_size
    figsize = (width / dpi, height / dpi)  # tamanho em polegadas
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')

    # Scatter inicial
    scatter = ax.scatter(X, Y, Z, c=W, cmap=colormap, s=s)

    # Barra de cores
    if cb_enable:
        fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=10, label=cb_title)

    def update(fr):
        ax.view_init(elev=elev, azim=fr*interval)
        return scatter,

    def progresso(frame_number, total_frames):
        print(f"Renderizando frame {frame_number+1}/{total_frames}", end='\r')

    ani = FuncAnimation(fig, update, frames=frames, blit=False)

    ani.save(
        output_path,
        writer='ffmpeg',
        fps=fps,
        dpi=dpi,
        progress_callback=progresso
    )
    print(f"\nVídeo salvo em {width}x{height} pixels como '{output_path}'")


if __name__ == "__main__":
    plt.style.use('dark_background')

    # Exemplo com dados sintéticos
    n = 100
    X = np.random.uniform(-5, 5, n)
    Y = np.random.uniform(-5, 5, n)
    Z = np.random.uniform(-5, 5, n)
    W = np.sqrt(X**2 + Y**2 + Z**2)  # coloração por distância à origem

    animate_rotate(X, Y, Z, W, pixel_size=(1920, 1080), frames=720, interval=0.5, cb_enable=True)

