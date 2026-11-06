"""
生成超简单版吉他谱 — 只写「按哪根弦第几格」
"""
import numpy as np

freqs = np.load("/home/guangliang/下载/freqs.npy")
times = np.load("/home/guangliang/下载/times.npy")

# ===== 基础转换 =====
def freq_to_midi(f):
    return 69 + 12 * np.log2(f / 440.0)

STRING_MIDI = [40, 45, 50, 55, 59, 64]

def midi_to_tab(midi):
    midi = int(round(midi))
    best = None
    for i, open_midi in enumerate(STRING_MIDI):
        fret = midi - open_midi
        if 0 <= fret <= 15:
            string_num = 6 - i
            score = abs(fret) * 10 + i
            if best is None or score < best[0]:
                best = (score, string_num, fret)
    if best:
        return best[1], best[2]
    return None

# ===== 提取音符 =====
midi_seq = []
for f in freqs:
    if f > 0:
        midi_seq.append(round(freq_to_midi(f)))
    else:
        midi_seq.append(None)

notes = []
current_midi = None
current_start = 0.0
for i, m in enumerate(midi_seq):
    t = times[i]
    if m is not None and current_midi is None:
        current_midi = m
        current_start = t
    elif m is not None and current_midi is not None:
        if m != current_midi:
            notes.append({"midi": current_midi, "start": current_start, "end": t})
            current_midi = m
            current_start = t
    elif m is None and current_midi is not None:
        notes.append({"midi": current_midi, "start": current_start, "end": t})
        current_midi = None
if current_midi is not None:
    notes.append({"midi": current_midi, "start": current_start, "end": times[-1]})

filtered = [n for n in notes if (n["end"] - n["start"]) >= 0.08]

# ===== 歌词分段 =====
lyric_groups = [
    ("Always uphold teacher 笑来", 0.0, 4.5),
    ("always uphold community", 4.5, 8.5),
    ("always uphold 墙大", 8.5, 11.0),
    ("always uphold teacher Wei", 11.0, 14.0),
    ("always uphold family", 14.0, 16.0),
    ("always uphold parents", 16.0, 18.0),
]

# ===== 生成超简单版 =====
L = []
L.append("╔══════════════════════════════════════════════╗")
L.append("║                                              ║")
L.append("║     超简单吉他谱（新手专用）                   ║")
L.append("║     I Love My Teachers and Community         ║")
L.append("║                                              ║")
L.append("╚══════════════════════════════════════════════╝")
L.append("")
L.append("【怎么弹？记住一句话】")
L.append("   看到「X弦Y品」就用手指按住那根弦的第Y格，然后拨一下。")
L.append("   看到「X弦空弦」就直接拨那根弦，不用按。")
L.append("")
L.append("【吉他弦怎么认？】")
L.append("   抱起吉他，从上往下（细到粗）依次是：")
L.append("")
L.append("      最细 → 第1弦")
L.append("             第2弦")
L.append("             第3弦")
L.append("             第4弦")
L.append("             第5弦")
L.append("      最粗 → 第6弦")
L.append("")

# 和弦建议
L.append("【伴奏和弦（可选）】")
L.append("   如果会按和弦，整首歌可以这样配：")
L.append("")
L.append("      Am  →  F  →  C  →  G")
L.append("      (每一句歌词换一个和弦)")
L.append("")

L.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
L.append("")
L.append("   下面按歌词分段，一段一段弹：")
L.append("")

for text, t_start, t_end in lyric_groups:
    group_notes = [n for n in filtered if t_start <= n["start"] < t_end]
    L.append("┌─────────────────────────────────────────┐")
    L.append(f"│  歌词：{text}")
    L.append("└─────────────────────────────────────────┘")
    if not group_notes:
        L.append("   （这一段没有明显旋律音，可以用和弦伴奏）")
        L.append("")
        continue
    L.append("")
    for j, n in enumerate(group_notes, 1):
        tab = midi_to_tab(n["midi"])
        if tab:
            s, f = tab
            if f == 0:
                how = f"第{s}弦  空弦（不用按）"
            else:
                how = f"第{s}弦  第{f}格"
            L.append(f"   {j}. {how}")
        else:
            L.append(f"   {j}. （超出常见范围，可跳过）")
    L.append("")

L.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
L.append("")
L.append("【小提示】")
L.append("   1. 不用急，慢慢弹，弹错了没事。")
L.append("   2. 如果觉得某个音听起来不对，可以对照原录音微调。")
L.append("   3. 这首歌很短，只有不到 19 秒，多弹几遍就熟了。")
L.append("")
L.append("   祝弹得开心！🎸")
L.append("")

output_path = "/home/guangliang/下载/I_Love_My_Teachers_吉他谱_简单版.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(L))

print(f"已保存到: {output_path}")
print()
print("\n".join(L))
