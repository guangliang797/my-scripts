# My Scripts

实用小工具和学习代码集合。

## 📁 目录说明

### camera/ — 摄像头监控脚本
用 mpv 播放器把电脑前置摄像头当监视器用，支持崩溃自动重启、24 小时循环。
- `camera24h.sh` — 24 小时摄像头监控（意外退出自动重开）
- `mpv-camera.sh` — mpv 摄像头守护脚本（带低延迟配置）
- `camera24.sh` — 另一个监控变体

### voice-dictation/ — 语音听写工具
按一下开始录音，再按一下停止并识别语音，结果自动复制到剪贴板。
- `dictate.sh` — 录音控制脚本
- `transcribe.py` — 语音识别脚本

### guitar/ — 吉他谱工具
从音频中提取旋律，自动生成吉他谱。
- `analyze_melody.py` — 音频旋律音高检测（numpy 自相关）
- `make_guitar_tab.py` — 把检测到的音高转换成吉他谱
- `make_simple_tab.py` — 生成简单版吉他谱
- `歌词吉他谱.html` — 吉他谱网页版工具

### mcu/ — 单片机实验代码
AT89C51 单片机学习代码（Keil C51 编译）。
- `流水灯.c` — 花样流水灯（P1 口 8 LED 共阳极）
- `flow_led.c` — 流水灯英文版

## 使用环境
- 摄像头脚本：Linux + mpv
- 语音听写：Linux + Python 3
- 吉他谱工具：Python 3 + numpy
- 单片机代码：Keil C51 + Proteus 仿真
