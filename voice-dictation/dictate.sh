#!/bin/bash
# 语音听写：按一下开始录音，再按一下停止并识别，文字复制到剪贴板
set -u

DIR="$HOME/voice-dictation"
STATE="$DIR/.state"
mkdir -p "$STATE"

# 记录每次调用，方便排查问题
echo "=== $(date '+%F %T') 被调用  PATH=$PATH  桌面=${WAYLAND_DISPLAY:-无}  通知总线=${DBUS_SESSION_BUS_ADDRESS:+有} ===" >> "$STATE/invocations.log"
exec 2>> "$STATE/invocations.log"

# 防止识别还没跑完时重复触发
exec 9>"$STATE/.lock"
flock -n 9 || { echo "  （因锁被占用而静默退出）" >> "$STATE/invocations.log"; notify-send "语音听写" "⏳ 识别中，请稍候…"; exit 0; }

PIDFILE="$STATE/recorder.pid"
WAV="$STATE/recording.wav"
LOG="$STATE/ffmpeg.log"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    # 第二次按：停止录音并识别
    kill -INT "$(cat "$PIDFILE")" 2>/dev/null
    rm -f "$PIDFILE"
    notify-send "语音听写" "⏳ 正在识别，请稍候…"
    TEXT="$("$DIR/venv/bin/python" "$DIR/transcribe.py" "$WAV" 2>"$STATE/err.log")"
    # 去掉识别结果里偶尔混入的非法字符，避免通知发不出去
    TEXT="$(printf '%s' "$TEXT" | iconv -f UTF-8 -t UTF-8 -c 2>/dev/null)"
    if [ -n "$TEXT" ]; then
        printf '%s' "$TEXT" | head -c 4000 | wl-copy 9>&-
        SHORT="$(printf '%s' "$TEXT" | head -c 60)"
        notify-send "语音听写" "✅ 已复制到剪贴板，按 Ctrl+V 粘贴：$SHORT"
    else
        notify-send "语音听写" "⚠️ 没有识别到文字（详见 $STATE/err.log）"
    fi
else
    # 第一次按：开始录音
    rm -f "$WAV"
    ffmpeg -hide_banner -loglevel error -y -f pulse -i default -ar 16000 -ac 1 "$WAV" >>"$LOG" 2>&1 9>&- &
    echo $! > "$PIDFILE"
    notify-send -u critical "语音听写" "🎙️ 正在录音，说完再按一次 F9"
fi
