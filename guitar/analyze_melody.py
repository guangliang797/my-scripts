"""
从音频中提取旋律音高，并生成吉他谱
使用 numpy 做自相关音高检测
"""
import numpy as np

# 读取原始音频 (f32le, 22050 Hz, mono)
SAMPLE_RATE = 22050
with open("/home/guangliang/下载/temp_audio.raw", "rb") as f:
    audio = np.frombuffer(f.read(), dtype=np.float32)

print(f"音频长度: {len(audio)/SAMPLE_RATE:.2f} 秒")

# 音高检测参数
WIN_SIZE = 2048       # 分析窗口
HOP_SIZE = 512        # 窗口步进
MIN_FREQ = 70         # 最低频率 (E2 约 82Hz)
MAX_FREQ = 600        # 最高频率
ENERGY_THRESHOLD = 0.01  # 能量阈值，低于此视为静音

def detect_pitch(frame):
    """用自相关法检测单帧的基频"""
    # 去直流
    frame = frame - np.mean(frame)
    energy = np.sqrt(np.mean(frame ** 2))
    if energy < ENERGY_THRESHOLD:
        return 0.0, energy

    # 自相关
    autocorr = np.correlate(frame, frame, mode='full')
    autocorr = autocorr[len(autocorr)//2:]

    # 找自相关峰值
    min_lag = int(SAMPLE_RATE / MAX_FREQ)
    max_lag = int(SAMPLE_RATE / MIN_FREQ)
    if max_lag >= len(autocorr):
        max_lag = len(autocorr) - 1

    segment = autocorr[min_lag:max_lag]
    if len(segment) == 0:
        return 0.0, energy

    peak_idx = np.argmax(segment) + min_lag
    peak_val = autocorr[peak_idx]
    if peak_val < 0.3 * autocorr[0]:
        return 0.0, energy

    freq = SAMPLE_RATE / peak_idx

    # 抛物线插值提高精度
    if 1 <= peak_idx < len(autocorr) - 1:
        y0, y1, y2 = autocorr[peak_idx-1], autocorr[peak_idx], autocorr[peak_idx+1]
        denom = y0 - 2*y1 + y2
        if denom != 0:
            delta = 0.5 * (y0 - y2) / denom
            freq = SAMPLE_RATE / (peak_idx + delta)

    return freq, energy

# 滑动窗口分析
freqs = []
times = []
for i in range(0, len(audio) - WIN_SIZE, HOP_SIZE):
    frame = audio[i:i+WIN_SIZE]
    t = i / SAMPLE_RATE
    freq, energy = detect_pitch(frame)
    freqs.append(freq)
    times.append(t)

freqs = np.array(freqs)
times = np.array(times)

# 打印检测到的有效音符
valid = freqs > 0
print(f"总帧数: {len(freqs)}, 有效音高帧: {np.sum(valid)}")

# 打印前30个有效音符看看
count = 0
for t, f in zip(times, freqs):
    if f > 0:
        print(f"  t={t:.2f}s  freq={f:.1f}Hz")
        count += 1
        if count >= 30:
            break

# 保存供下一步使用
np.save("/home/guangliang/下载/freqs.npy", freqs)
np.save("/home/guangliang/下载/times.npy", times)
print("已保存 freqs.npy / times.npy")
