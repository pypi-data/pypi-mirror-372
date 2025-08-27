import os
from typing import Any

import yt_dlp

int_quality = {
    "high": "192",
    "medium": "128",
    "low": "96"
}


class Downloader:
    def __init__(self, output_dir: str, media_type: str, quality: str):
        self.output_dir = output_dir
        self.media_type = media_type
        self.quality = quality
        self.is_output_video = self.media_type == "video"

    def download(self, url: str) -> tuple[str, Any]:
        self._initialize_youtube_dl()

        self.youtube_dl.download(url)
        url_data = self.youtube_dl.extract_info(url, download=False)

        filename = f"{url_data['id']}.{url_data['ext']}"
        duration = float(url_data['duration']) or None
        return filename, duration

    def _initialize_youtube_dl(self) -> None:
        self.youtube_dl = yt_dlp.YoutubeDL(self._config())

    def _config(self) -> dict[str, Any]:
        config = {
            'ignoreerrors': True,
            'noplaylist': True,
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'verbose': False,
        }

        is_high_quality = self.quality == "high"

        if not self.is_output_video:
            config['format'] = f'bestaudio[abr>={int_quality[self.quality]}]/bestaudio'

        if self.is_output_video and not is_high_quality:
            config[
                'format'] = 'bestvideo[height<=720]+bestaudio' if self.quality == "medium" else 'bestvideo[height<=360]+bestaudio'

        return config
