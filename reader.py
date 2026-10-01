from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np


@dataclass
class VideoInfo:
    path: str
    width: int
    height: int
    fps: float
    duration: float
    codec: str
    frame_count: int


class VideoReader:
    """Чтение видео через FFmpeg (без OpenCV).

    Пример:
        >>> with VideoReader("video.mp4") as vr:
        ...     for frame in vr.frames(start=5, end=10):
        ...         ...
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        if not Path(self.path).exists():
            raise FileNotFoundError(f"Файл не найден: {self.path}")
        self.info = self._probe()

    def _probe(self) -> VideoInfo:
        """Получить метаданные через ffprobe."""
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,codec_name,nb_frames,duration",
            "-of", "json", self.path,
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except FileNotFoundError as e:
            raise RuntimeError(
                "ffprobe не найден. Установите FFmpeg: https://ffmpeg.org"
            ) from e
        data = json.loads(out)["streams"][0]

        num, den = data["r_frame_rate"].split("/")
        fps = float(num) / float(den) if float(den) else 0.0

        duration = float(data.get("duration") or 0.0)
        nb = data.get("nb_frames")
        frame_count = int(nb) if nb and nb.isdigit() else int(duration * fps)

        return VideoInfo(
            path=self.path,
            width=int(data["width"]),
            height=int(data["height"]),
            fps=fps,
            duration=duration,
            codec=data.get("codec_name", "unknown"),
            frame_count=frame_count,
        )

    def frames(
        self,
        start: float = 0.0,
        end: float | None = None,
        size: tuple[int, int] | None = None,
    ) -> Iterator[np.ndarray]:
        """Генератор кадров в виде numpy-массивов (RGB).

        :param start: начало в секундах
        :param end: конец в секундах (None — до конца)
        :param size: (width, height) для ресайза
        """
        w, h = size if size else (self.info.width, self.info.height)

        cmd = ["ffmpeg", "-v", "error"]
        if start:
            cmd += ["-ss", str(start)]
        cmd += ["-i", self.path]
        if end is not None:
            cmd += ["-to", str(end - start)]
        cmd += [
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-vf", f"scale={w}:{h}",
            "-",
        ]

        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
        except FileNotFoundError as e:
            raise RuntimeError(
                "ffmpeg не найден. Установите FFmpeg: https://ffmpeg.org"
            ) from e

        frame_size = w * h * 3
        try:
            while True:
                raw = proc.stdout.read(frame_size)
                if len(raw) < frame_size:
                    break
                yield np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 3)
        finally:
            proc.stdout.close()
            proc.wait()

    def __enter__(self) -> "VideoReader":
        return self

    def __exit__(self, *args) -> None:
        # subprocess завершается в frames(), отдельного ресурса нет
        return None

    def __repr__(self) -> str:
        i = self.info
        return (
            f"VideoReader({self.path!r}, {i.width}x{i.height}, "
            f"{i.fps:.2f} fps, {i.duration:.2f}s, codec={i.codec})"
        )