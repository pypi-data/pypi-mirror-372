#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def animate_rotate( X, Y, Z, 
                    output_path="animate_rotate.mp4",
                    pixel_size=(1920, 1080), 
                    dpi=200, 
                    colormap='viridis',
                    frames=360, 
                    fps=30,
                    cb_enable=False,
                    cb_title="Z",
                    elev=30,
                    interval=0.5 ):
    """
    Creates and saves a 3D animation of the surface Z = f(X, Y).

    Args:
        X (array-like): 2D array of X coordinates of the surface.
        Y (array-like): 2D array of Y coordinates of the surface.
        Z (array-like): 2D array of Z values of the surface.
        output_path (str, optional): Output file name. Default is 'animate_rotate.mp4'.
        pixel_size (tuple, optional): Figure size in pixels (width, height). Default is (1920, 1080).
        dpi (int, optional): Figure resolution in dots per inch. Default is 100.
        colormap (str, optional): Colormap for the surface. Default is 'viridis'.
        elev (float, optional): Initial elevation of the camera. Default is 30.
        frames (int, optional): Total number of frames in the animation. Default is 360.
        interval (float, optional): Angle interval between frames in degrees. Default is 1.0.
        fps (int, optional): Frames per second for the video. Default is 30.
        cb_enable (bool, optional): Enable colorbar. Default False.
        cb_title (str, optional): Title of colorbar. Default "Z".

    Returns:
        None
    """
    width, height = pixel_size
    figsize = (width / dpi, height / dpi)  # calcula tamanho em polegadas
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')
    hd_surf = ax.plot_surface(X, Y, Z, cmap=colormap)
    
    # Barra de cores
    if cb_enable:
        fig.colorbar(hd_surf, ax=ax, shrink=0.5, aspect=10, label=cb_title)
    
    def update(fr):
        ax.view_init(elev=elev, azim=fr*interval)
        return []

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

    X = np.linspace(-5, 5, 100)
    Y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(X, Y)
    Z = np.sin(np.sqrt(X**2 + Y**2))
    
    animate_rotate(X, Y, Z, pixel_size=(1920, 1080), frames=720, interval=0.5, cb_enable=True)


