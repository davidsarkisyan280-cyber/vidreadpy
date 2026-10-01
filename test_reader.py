import shutil
import subprocess

import pytest

from vidreadpy import VideoReader, check_ffmpeg


pytestmark = pytest.mark.skipif(
    not check_ffmpeg(), reason="ffmpeg/ffprobe не установлены"
)


@pytest.fixture(scope="module")
def sample_video(tmp_path_factory):
    """Сгенерировать тестовое видео через ffmpeg."""
    path = tmp_path_factory.mktemp("media") / "sample.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=size=160x120:rate=10:duration=2",
            "-pix_fmt", "yuv420p",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return str(path)


def test_probe(sample_video):
    vr = VideoReader(sample_video)
    assert vr.info.width == 160
    assert vr.info.height == 120
    assert vr.info.fps == pytest.approx(10, rel=0.1)
    assert vr.info.frame_count > 0


def test_frames(sample_video):
    vr = VideoReader(sample_video)
    frames = list(vr.frames())
    assert len(frames) >= 10
    assert frames[0].shape == (120, 160, 3)


def test_frames_resize(sample_video):
    vr = VideoReader(sample_video)
    frame = next(vr.frames(size=(80, 60)))
    assert frame.shape == (60, 80, 3)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        VideoReader("no_such_file.mp4")