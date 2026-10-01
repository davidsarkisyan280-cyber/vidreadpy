from __future__ import annotations

import shutil
import subprocess


def check_ffmpeg() -> bool:
    """Проверить, установлены ли ffmpeg и ffprobe."""
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def extract_audio(video: str, out: str = "audio.aac") -> str:
    """Извлечь аудиодорожку без перекодирования."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", video, "-vn", "-acodec", "copy", out],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


def clip(video: str, start: float, end: float, out: str = "clip.mp4") -> str:
    """Вырезать фрагмент без перекодирования."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", video,
            "-c", "copy",
            out,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out