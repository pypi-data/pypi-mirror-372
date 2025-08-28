#!/usr/bin/python3

from moviepy.editor import VideoFileClip, AudioFileClip

def add_to_video(video_path, audio_path, start_time=0, output_path="output.mp4"):
    """
    Adds an audio track to a video starting at a specified time. 
    If the audio duration plus the start time exceeds the video duration,
    the audio is truncated to match the video length.

    Args:
        video_path (str): Path to the original video file.
        audio_path (str): Path to the audio file (e.g., MP3).
        start_time (float): Time in seconds at which the audio should start. Default is 0.
        output_path (str): Path for the resulting video with audio.

    Returns:
        None
    """
    # Load video and audio
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Determine the effective audio duration
    max_audio_duration = max(0, video.duration - start_time)
    if audio.duration > max_audio_duration:
        audio = audio.subclip(0, max_audio_duration)

    # Set audio start time
    audio = audio.set_start(start_time)

    # Combine video and audio
    final_video = video.set_audio(audio)

    # Write output
    final_video.write_videofile(output_path, fps=video.fps, audio_codec='aac')


# Example usage
if __name__ == "__main__":
    add_to_video(
        video_path="scatter_path.mp4",
        audio_path="background.mp3",
        start_time=5,  # audio starts at 5 seconds
        output_path="scatter_with_audio.mp4"
    )

