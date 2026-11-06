#!/bin/bash
# 用 mpv 全天显示摄像头画面：意外退出自动重开，24 小时后自动停止
end=$((SECONDS + 86400))
while [ $SECONDS -lt $end ]; do
    remaining=$((end - SECONDS))
    timeout "$remaining" mpv --profile=low-latency --fullscreen av://v4l2:/dev/video0
    sleep 2
done
