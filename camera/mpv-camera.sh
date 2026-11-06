#!/bin/bash
# mpv 摄像头守护脚本 - 崩溃后自动重启

while true; do
    mpv av://v4l2:/dev/video0 --profile=low-latency --title=摄像头(24小时) --ontop --autofit=40% --msg-level=all=warn
    # 如果 mpv 意外退出，等 2 秒后重新启动
    sleep 2
done
