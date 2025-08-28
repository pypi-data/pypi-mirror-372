#!/usr/bin/python3

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

def image_on_video(video_path, image_path, position=(0,0), output_path="output.mp4"):
    """
    Overlays an image on every frame of a video.

    Args:
        video_path (str): Path to the original video file.
        image_path (str): Path to the image to overlay (supports PNG transparency).
        position (tuple): (x, y) position in pixels where the image will be placed on the video.
        output_path (str): Path for the resulting video with the overlay.

    Returns:
        None
    """
    # Carrega o vídeo
    video = VideoFileClip(video_path)

    # Carrega a imagem e define duração igual ao vídeo
    overlay = ImageClip(image_path).set_duration(video.duration).set_pos(position)

    # Cria vídeo final com overlay
    final = CompositeVideoClip([video, overlay])

    # Salva vídeo final
    final.write_videofile(output_path, fps=video.fps)

# Exemplo de uso
if __name__ == "__main__":
    image_on_video( video_path="scatter_path.mp4",
                    image_path="logo.png",
                    position=(50,50),
                    output_path="scatter_with_logo.mp4" )

