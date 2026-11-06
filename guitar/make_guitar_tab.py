"""
把检测到的音高转换成吉他谱
"""
import numpy as np

freqs = np.load("/home/guangliang/下载/freqs.npy")
times = np.load("/home/guangliang/下载/times.npy")
SAMPLE_RATE = 22050
HOP_SIZE = 512

# ============ 基础乐理 ============
def freq_to_midi(f):
    """频率 → MIDI 音符编号"""
    return 69 + 12 * np.log2(f / 440.0)

def midi_to_name(m):
    """MIDI 编号 → 音名，如 C4, D#3"""
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    m = int(round(m))
    octave = (m // 12) - 1
    name = names[m % 12]
    return f"{name}{octave}"

# 标准调弦 (从粗弦到细弦): E2 A2 D3 G3 B3 E4
STRING_MIDI = [40, 45, 50, 55, 59, 64]  # 空弦 MIDI
STRING_NAME = ["E2", "A2", "D3", "G3", "B3", "E4"]

def midi_to_tab(midi):
    """
    把 MIDI 音符映射到吉他指法
    返回: (弦号1-6, 品格) 或 None (超出范围)
    弦号: 6=最粗的E弦, 1=最细的E弦
    """
    midi = int(round(midi))
    best = None
    for i, open_midi in enumerate(STRING_MIDI):
        fret = midi - open_midi
        if 0 <= fret <= 15:  # 常用范围 0-15 品
            string_num = 6 - i  # 6弦是粗E
            # 优先选择低把位、细弦（同一音高可能多种按法）
            score = abs(fret) * 10 + i
            if best is None or score < best[0]:
                best = (score, string_num, fret)
    if best:
        return best[1], best[2]
    return None

# ============ 把连续帧合并成「音符」 ============
# 1. 把每帧频率量化到最近的半音
midi_seq = []
for f in freqs:
    if f > 0:
        midi_seq.append(round(freq_to_midi(f)))
    else:
        midi_seq.append(None)

# 2. 合并连续相同音高的帧为一个音符
notes = []  # 每个元素: {"midi": int, "start": float, "end": float}
current_midi = None
current_start = 0.0

for i, m in enumerate(midi_seq):
    t = times[i]
    if m is not None and current_midi is None:
        # 音符开始
        current_midi = m
        current_start = t
    elif m is not None and current_midi is not None:
        if m != current_midi:
            # 换音了，结束上一个
            notes.append({
                "midi": current_midi,
                "start": current_start,
                "end": t
            })
            current_midi = m
            current_start = t
    elif m is None and current_midi is not None:
        # 静音了，结束当前音
        notes.append({
            "midi": current_midi,
            "start": current_start,
            "end": t
        })
        current_midi = None

# 处理最后一个
if current_midi is not None:
    notes.append({
        "midi": current_midi,
        "start": current_start,
        "end": times[-1]
    })

# 3. 过滤太短的音（噪音）和太长的（拖尾）
filtered = []
for n in notes:
    duration = n["end"] - n["start"]
    if duration >= 0.08:  # 至少 80ms
        filtered.append(n)

print(f"检测到 {len(filtered)} 个音符:")
for n in filtered:
    name = midi_to_name(n["midi"])
    tab = midi_to_tab(n["midi"])
    tab_str = f"{tab[0]}弦{tab[1]}品" if tab else "超出吉他范围"
    print(f"  [{n['start']:.2f}s - {n['end']:.2f}s]  {name}  → {tab_str}")

# ============ 歌词对齐 ============
lyrics_lines = [
    ("Always uphold teacher 笑来", 0.0),
    ("always uphold community", 4.5),
    ("always uphold 墙大", 8.5),
    ("always uphold teacher Wei", 11.0),
    ("always uphold family", 14.0),
    ("always uphold parents", 16.0),
    ("always focus on self growth", 18.0),
]

# ============ 生成吉他谱 ============
def format_time(t):
    return f"{int(t//60)}:{t%60:05.2f}"

tab_lines = []
tab_lines.append("=" * 60)
tab_lines.append("  吉他谱 — I Love My Teachers and Community")
tab_lines.append("  (自动生成版 · 仅供参考 · 建议弹奏时微调)")
tab_lines.append("=" * 60)
tab_lines.append("")
tab_lines.append("【调弦】标准调弦 (E A D G B E)")
tab_lines.append("【拍号】4/4")
tab_lines.append("【速度】约 80 BPM (中速)")
tab_lines.append("")
tab_lines.append("【和弦建议】(按句搭配)")
tab_lines.append("  Am   F    C    G")
tab_lines.append("  (下行抒情走向，适合本曲)")
tab_lines.append("")

# 六线谱视图
tab_lines.append("-" * 60)
tab_lines.append("【六线谱】(数字=品格, 0=空弦)")
tab_lines.append("")

# 先按时间把音符画到六线谱上
string_names = ["e", "B", "G", "D", "A", "E"]  # 1弦到6弦显示顺序
# 构建6行谱
rows = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
row_labels = {1: "e|", 2: "B|", 3: "G|", 4: "D|", 5: "A|", 6: "E|"}

# 时间轴：每 0.25 秒一格
duration_total = filtered[-1]["end"] if filtered else 18.88
cell = 0.22  # 每格时长（秒）
n_cells = int(duration_total / cell) + 2

# 先填满空格
for s in range(1, 7):
    rows[s] = ["-"] * n_cells

for n in filtered:
    tab = midi_to_tab(n["midi"])
    if tab is None:
        continue
    string_num, fret = tab
    col = int(n["start"] / cell)
    if col >= n_cells:
        col = n_cells - 1
    fret_str = str(fret)
    # 放置品格数字（最多3位占位）
    for j, ch in enumerate(fret_str):
        if col + j < n_cells:
            rows[string_num][col + j] = ch

for s in range(1, 7):
    tab_lines.append(f"  {row_labels[s]}{''.join(rows[s])}|")
tab_lines.append("")

# 音符 + 歌词对照表
tab_lines.append("-" * 60)
tab_lines.append("【音符 & 歌词对照】")
tab_lines.append("")
tab_lines.append(f"  {'时间':<12} {'音名':<8} {'吉他指法':<14} 歌词")
tab_lines.append(f"  {'-'*12} {'-'*8} {'-'*14} {'-'*20}")

# 为每个音符分配歌词（按时间最近原则）
lyric_idx = 0
for n in filtered:
    name = midi_to_name(n["midi"])
    tab = midi_to_tab(n["midi"])
    tab_str = f"{tab[0]}弦{tab[1]}品" if tab else "—"
    # 找当前时间对应的歌词
    current_lyric = ""
    for text, start_t in lyrics_lines:
        if n["start"] >= start_t:
            current_lyric = text
    tab_lines.append(
        f"  {format_time(n['start']):<12} {name:<8} {tab_str:<14} {current_lyric}"
    )

tab_lines.append("")
tab_lines.append("-" * 60)
tab_lines.append("【歌词】")
tab_lines.append("")
for text, t in lyrics_lines:
    tab_lines.append(f"  [{format_time(t)}] {text}")

tab_lines.append("")
tab_lines.append("=" * 60)
tab_lines.append("  提示: 这是由软件自动识别生成的参考谱。")
tab_lines.append("  如果弹起来感觉不准，可对照录音微调品格。")
tab_lines.append("=" * 60)

# 写入文件
output_path = "/home/guangliang/下载/I_Love_My_Teachers_吉他谱.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(tab_lines))

print(f"\n吉他谱已保存到: {output_path}")
print("\n" + "\n".join(tab_lines))
