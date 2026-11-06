#!/bin/bash
# 24小时摄像头监控：循环打开 mpv，意外退出后自动重启
while true; do
  mpv av://v4l2:/dev/video0 \
    --profile=low-latency \
    --title="摄像头(24小时)" \
    --ontop \
    --autofit=40% \
    --msg-level=all=warn
  sleep 2
done
