#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import interp1d

def animate_path(   X, Y, Z, W, camera_points,
                    output_path="animate_path.mp4",
                    pixel_size=(1920, 1080),
                    dpi=200,
                    colormap='viridis',
                    frames=360,
                    fps=30,
                    cb_enable=False,
                    cb_title="W",
                    s=40  ):
    """
    Creates and saves a 3D scatter animation following a camera path
    defined by `camera_points`.

    Args:
        X, Y, Z (array-like): 1D arrays of point coordinates.
        W (array-like): 1D array of values used to color the points.
        camera_points (list of tuple): List of (elev, azim) tuples defining the camera path.
        frames (int, optional): Total number of frames. Default is 360.
        pixel_size (tuple, optional): Figure size in pixels (width, height). Default is (1920, 1080).
        dpi (int, optional): Figure resolution in dots per inch. Default is 100.
        colormap (str, optional): Matplotlib colormap for coloring. Default is 'viridis'.
        output_path (str, optional): Output file name. Default is 'animate_scatter_path.mp4'.
        fps (int, optional): Frames per second for the video. Default is 30.
        cb_enable (bool, optional): Enable colorbar. Default is False.
        cb_title (str, optional): Colorbar title. Default is "W".
        s (int, optional): Size of scatter points. Default is 40.

    Returns:
        None
    """
    # --- Calcula figsize ---
    width, height = pixel_size
    figsize = (width / dpi, height / dpi)

    # --- Cria figura ---
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')

    # Scatter inicial
    scatter = ax.scatter(X, Y, Z, c=W, cmap=colormap, s=s)

    # Barra de cores
    if cb_enable:
        fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=10, label=cb_title)

    # --- Interpolação do caminho da câmera ---
    camera_points = np.array(camera_points)
    n_points = len(camera_points)
    t_original = np.linspace(0, 1, n_points)
    t_interp = np.linspace(0, 1, frames)

    elev_interp = interp1d(t_original, camera_points[:,0], kind='cubic')(t_interp)
    azim_interp = interp1d(t_original, camera_points[:,1], kind='cubic')(t_interp)

    # --- Função de atualização ---
    def update(frame):
        ax.view_init(elev=elev_interp[frame], azim=azim_interp[frame])
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

    # Exemplo com pontos aleatórios
    n = 100
    X = np.random.uniform(-5, 5, n)
    Y = np.random.uniform(-5, 5, n)
    Z = np.random.uniform(-5, 5, n)
    W = np.sqrt(X**2 + Y**2 + Z**2)  # valor usado para cor

    # Lista de pontos de câmera pelos quais a animação deve passar
    camera_points = [(30, 0), (45, 90), (60, 180), (30, 270), (30, 360)]

    animate_path(X, Y, Z, W, camera_points, frames=1440, fps=30, cb_enable=True)

