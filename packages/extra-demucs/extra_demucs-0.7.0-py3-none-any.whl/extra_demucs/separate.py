import os
import shutil

import validators
from demucs import separate

from extra_demucs.downloader import Downloader
from extra_demucs.ffmpeg_utils import FFMPEGUtils

video_audio_track_ext_map = {
    ".mp4": "aac",
    ".webm": "opus",
    ".3gp": "mp3",
    ".flv": "aac",
    ".mkv": "opus"
}


def extra_separator(
        files: list[str],
        download_format: str,
        quality: str,
        output_dir: str,
        segment_duration: int = 30,
        model: str = "htdemucs"
):
    """
    Separates vocals from a list of media files (audio/video), using Demucs, and replaces
    the audio track in video files with the extracted vocals if file was a video.

    This function supports both local files and remote URLs (e.g., YouTube links). It handles:
    - Downloading remote media using yt-dlp
    - Performing source separation using Demucs (vocal isolation)
    - For video: replacing the original audio with vocals using ffmpeg
    - Cleaning up intermediate files and keeping only the final output
    - Segmented processing in case of low-end devices

    Parameters:
        files (list[str]): List of file paths or URLs pointing to audio/video files.
        download_format (str): Either "audio" or "video". Determines post-processing behavior.
        quality (str): Quality level for yt-dlp downloading ("high", "low", "medium").
        output_dir (str): Path to directory where final results will be saved.
        segment_duration (int): Segment duration in seconds. Defaults to 30 minutes chunks (1800 seconds)
        model (str): Demucs model to be used

    Notes:
        - Requires `ffmpeg`, and internet access for remote URLs.
        - For audio files, only the isolated vocal track is kept in mp3 format.
        - For video files, a new `.mp4` is generated with vocals replacing original audio.
        - Temporary files are stored in a `tmp/` subfolder inside the output directory and deleted after completion.

    Example:
        extra_separator(
            files=["https://www.youtube.com/watch?v=123", "local_song.mp3"],
            media_type="audio",
            quality="medium",
            output_dir="output"
        )
    """
    abs_output_dir = os.path.abspath(output_dir)
    temp_output_dir = os.path.join(abs_output_dir, 'tmp')
    demucs_output_dir = os.path.join(abs_output_dir, model)

    ffmpeg_utils = FFMPEGUtils()

    processing_files_path = []
    processing_files_path_with_chunks = []

    # --- Preparing files for processing ---
    print("Preparing files...")

    if not files:
        raise Exception("Please provide files for processing")

    downloader = Downloader(
        output_dir=temp_output_dir,
        media_type=download_format,
        quality=quality
    )
    for index, url in enumerate(files):
        is_url = validators.url(url)
        if is_url:
            downloaded_file_name, downloaded_file_duration = downloader.download(url=url)
            downloaded_file_path = os.path.join(temp_output_dir, downloaded_file_name)

            if downloaded_file_duration is None:
                total_duration = ffmpeg_utils.duration(downloaded_file_path)
            else:
                total_duration = downloaded_file_duration

            processing_files_path.append(downloaded_file_path)
            processing_files_path_with_chunks.append(downloaded_file_path)
        else:
            total_duration = ffmpeg_utils.duration(os.path.abspath(url))
            processing_files_path.append(os.path.abspath(url))
            processing_files_path_with_chunks.append(os.path.abspath(url))

        if total_duration > segment_duration:
            file_chunks = []
            offset = 0
            while offset < total_duration:
                current_file = processing_files_path[index]
                current_file_ext = os.path.splitext(current_file)[1].lower()

                duration_to_process = min(segment_duration, total_duration - offset)

                chunk_ext = video_audio_track_ext_map.get(current_file_ext)

                output_path = ffmpeg_utils.chunk(input_path=current_file, input_file_index=index,
                                                 output_dir=temp_output_dir, duration_to_process=duration_to_process,
                                                 offset=offset, segment_duration=segment_duration, chunk_ext=chunk_ext)

                file_chunks.append(output_path)
                offset += segment_duration
            processing_files_path_with_chunks[index:index + 1] = file_chunks

    # --- Demucs model inference ---
    separate.main([
        "-n", model,
        "--two-stems", "vocals",
        "--filename", "{track}_{stem}.{ext}",
        "-o", abs_output_dir,
        *processing_files_path_with_chunks
    ])

    # --- Postprocess ---
    for file_index, original_file_path in enumerate(processing_files_path):
        original_file_name, original_file_ext = os.path.splitext(os.path.basename(original_file_path))
        vocal_output_name = f"{original_file_name}_vocals"
        vocal_output_path = os.path.join(demucs_output_dir, vocal_output_name)

        # --- Find chunks associated with the current file ---
        matching_chunk_paths = [
            chunk_path for chunk_path in processing_files_path_with_chunks
            if f"{file_index}_demucschunk" in chunk_path
        ]

        video_audio_track_ext = video_audio_track_ext_map.get(original_file_ext.lower())

        if matching_chunk_paths:
            ffmpeg_utils.merge(
                segment_files=matching_chunk_paths,
                output_dir=demucs_output_dir,
                output_name=vocal_output_name,
                output_ext=video_audio_track_ext
            )
        else:
            ffmpeg_utils.convert_to_audio_format(
                output_dir=demucs_output_dir,
                output_name=vocal_output_name,
                audio_format=video_audio_track_ext
            )

        is_original_file_video = ffmpeg_utils.is_video(original_file_path)
        if is_original_file_video and not video_audio_track_ext is None:
            print(f"Saving video in {abs_output_dir}")

            final_video_output_path = "{destination}{codec}".format(
                destination=os.path.join(abs_output_dir, vocal_output_name),
                codec=original_file_ext
            )

            audio_output_mp3_path = f"{vocal_output_path}.{video_audio_track_ext}"
            ffmpeg_utils.replace_video_audio(
                input_video_path=original_file_path,
                input_audio_path=audio_output_mp3_path,
                final_output_path=final_video_output_path
            )
        else:
            print(f"Saving audio in {abs_output_dir}")

            audio_output_mp3_path = f"{vocal_output_path}.mp3"
            final_audio_output_path = os.path.join(abs_output_dir, f"{vocal_output_name}.mp3")
            shutil.move(audio_output_mp3_path, final_audio_output_path)

    # --- Cleanup ---
    if os.path.exists(temp_output_dir):
        shutil.rmtree(temp_output_dir)
    if os.path.exists(demucs_output_dir):
        shutil.rmtree(demucs_output_dir)
