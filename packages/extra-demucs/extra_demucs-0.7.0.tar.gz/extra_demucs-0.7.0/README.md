<div align="center">
  <a href="https://pypi.org/project/extra-demucs" target="_blank"><img src="https://img.shields.io/pypi/v/extra-demucs?label=PyPI%20Version&color=limegreen" /></a>
  <a href="https://pypi.org/project/extra-demucs" target="_blank"><img src="https://img.shields.io/pypi/pyversions/extra-demucs?color=limegreen" /></a>
  <a href="https://github.com/mohammadmansour200/extra-demucs/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/pypi/l/extra-demucs?color=limegreen" /></a>
  <a href="https://pepy.tech/project/extra-demucs" target="_blank"><img src="https://static.pepy.tech/badge/extra-demucs" /></a>
  <a href="https://baseet.netlify.app/ai" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" /></a>
</div>

`extra_demucs`: Extended [Demucs](https://github.com/facebookresearch/demucs) with yt-dlp media downloading and Video
Music removal

## Features

- 🎧 **Vocal isolation** using Demucs (`--two-stems vocals`)
- 📥 **Media download** from URLs (e.g., YouTube) using `yt-dlp`
- 📁 Works with both **audio** and **video** files
- ✅ Local + remote (URL) input support

## Get started

*Make sure you have [ffmpeg](https://www.ffmpeg.org/download.html) installed.*

```bash
sudo apt install ffmpeg
```

Download package:
> Requires Python 3.9+

```bash
pip install extra-demucs
```

## Usage

```bash
from extra_demucs.separate import extra_separator

extra_separator(
    files=[
        "https://www.youtube.com/watch?v=123",
        "local_audio.mp3"
    ],
    download_format="audio",   # or "video"
    quality="medium",     # "low", "medium", "high"
    output_dir="outputs"
)

```
