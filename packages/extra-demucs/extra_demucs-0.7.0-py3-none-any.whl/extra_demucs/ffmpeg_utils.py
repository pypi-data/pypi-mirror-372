import os
import shutil
import subprocess


class FFMPEGUtils:
    """
    FFmpeg utils used in separation.

    When created, FFMPEG binary path will be checked,
    raising exception if not found. Such path could be inferred using
    `FFMPEG_PATH` environment variable.
    """

    def __init__(self) -> None:
        """
        Default constructor, ensure FFMPEG binaries are available.

        Raises:
            ValueError:
                If ffmpeg or ffprobe is not found.
        """
        for binary in ("ffmpeg", "ffprobe"):
            if shutil.which(binary) is None:
                raise Exception("ffmpeg_utils:{} binary not found".format(binary))

    def replace_video_audio(self, input_video_path: str, input_audio_path: str, final_output_path: str):
        try:
            subprocess.run([
                "ffmpeg",
                "-y",
                "-loglevel", "quiet",
                "-an",
                "-i", input_video_path,
                "-i", input_audio_path,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "copy",
                final_output_path, ], check=True)
        except Exception as e:
            raise Exception(
                "ffmpeg_utils:An error occurred with ffmpeg (see ffmpeg output below)\n\n{}".format(
                    e
                )
            )

    def is_video(self, path: str) -> bool:
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                 '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True, check=True
            )
            return 'video' in result.stdout
        except Exception as e:
            return False

    def duration(self, path: str) -> float:
        # --- Use ffprobe to get the metadata of the audio file ---
        try:
            result = subprocess.run(
                ['ffprobe', "-v",
                 "error",
                 "-select_streams",
                 "v:0",
                 "-show_entries",
                 "format=duration",
                 "-of",
                 "default=noprint_wrappers=1:nokey=1", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            raise Exception(
                "ffmpeg_utils:An error occurred with ffprobe (see ffprobe output below)\n\n{}".format(
                    e
                )
            )

        # --- Extract the duration from the metadata ---
        return float(result.stdout)

    def chunk(self, input_path: str, input_file_index: int, output_dir: str, duration_to_process: int, offset: int,
              segment_duration: int, chunk_ext: str) -> str:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        final_output_path = os.path.join(
            output_dir,
            f"{input_file_index}_demucschunk_{offset // segment_duration}.{'mp3' if chunk_ext is None else chunk_ext}"
        )

        try:
            subprocess.run([
                "ffmpeg",
                "-y",
                "-loglevel", "quiet",
                "-ss", str(offset),
                "-t", str(duration_to_process),
                "-i", input_path,
                "-vn",
                final_output_path, ], check=True)
        except Exception as e:
            raise Exception(
                "ffmpeg_utils:An error occurred with ffmpeg (see ffmpeg output below)\n\n{}".format(
                    e
                )
            )
        return final_output_path

    def merge(
            self, segment_files: list, output_dir: str, output_name: str, output_ext: str
    ):
        # --- Create a temporary text file to list all audio files to merge ---
        with open(os.path.join(output_dir, "file_list.txt"), "w") as file_list:
            for segment in segment_files:
                filename_from_path, ext_from_path = os.path.splitext(os.path.basename(segment))
                demucs_segment_path = os.path.join(output_dir, f"{filename_from_path}_vocals.wav")
                file_list.write(f"file '{demucs_segment_path}'\n")

        # --- Use ffmpeg to merge the files ---
        try:
            subprocess.run([
                "ffmpeg",
                "-y",
                "-loglevel", "quiet",
                "-f", "concat",
                "-safe", "0",
                "-i", os.path.join(output_dir, "file_list.txt"),
                os.path.join(output_dir, f"{output_name}.{'mp3' if output_ext is None else output_ext}")
            ]
                , check=True)
        except Exception as e:
            raise Exception(
                "ffmpeg_utils:An error occurred with ffmpeg (see ffmpeg output below)\n\n{}".format(
                    e
                )
            )

    def convert_to_audio_format(self, output_dir: str, output_name: str, audio_format: str):
        processed_demucs_file_path = os.path.join(output_dir, f"{output_name}.wav")
        final_output_file_path = os.path.join(output_dir,
                                              f"{output_name}.{'mp3' if audio_format is None else audio_format}")
        try:
            subprocess.run([
                "ffmpeg",
                "-y",
                "-loglevel", "quiet",
                "-i", processed_demucs_file_path,
                final_output_file_path
            ]
                , check=True)
        except Exception as e:
            raise Exception(
                "ffmpeg_utils:An error occurred with ffmpeg (see ffmpeg output below)\n\n{}".format(
                    e
                )
            )
