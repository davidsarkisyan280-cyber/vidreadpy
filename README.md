# vidreadpy

Лёгкая библиотека для чтения видео на Python через FFmpeg. Без OpenCV.

## Требования
- Python 3.8+
- Установленные `ffmpeg` и `ffprobe` в `PATH`

Установка FFmpeg:
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: скачать с https://ffmpeg.org и добавить в PATH

## Установка
```bash
pip install git+https://github.com/davidsarkisyan280-cyber/vidreadpy.git
```

## Быстрый старт
```python
from vidreadpy import VideoReader

with VideoReader("video.mp4") as vr:
    print(vr.info)  # метаданные
    for frame in vr.frames(start=10, end=15, size=(320, 240)):
        # frame — numpy.ndarray (H, W, 3), RGB
        ...
```

## API

### `VideoReader(path)`
- `.info` — `VideoInfo(width, height, fps, duration, codec, frame_count)`
- `.frames(start=0, end=None, size=None)` — генератор кадров (`np.ndarray` в RGB)

### Утилиты
```python
from vidreadpy import extract_audio, clip, check_ffmpeg

check_ffmpeg()                      # -> bool
extract_audio("video.mp4")          # -> "audio.aac"
clip("video.mp4", 5, 10, "out.mp4") # -> "out.mp4"
```

## Лицензия
MIT
