import os
import sys

# 模型已下载到本机，强制离线模式，避免每次识别都去联网检查更新导致卡住
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_XET"] = "1"

import av

# PyAV 19 移除了 metadata_errors 参数，而 faster-whisper 1.2.1 仍在传它
# 包一层自动丢弃该参数，让两个版本能配合工作
_orig_av_open = av.open


def _av_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _orig_av_open(*args, **kwargs)


av.open = _av_open

from faster_whisper import WhisperModel

wav_path = sys.argv[1]
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe(
    wav_path,
    language="zh",
    vad_filter=True,
    initial_prompt="以下是普通话的句子。",
    condition_on_previous_text=False,
)
print("".join(seg.text for seg in segments).strip())
