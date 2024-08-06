#!/bin/bash
/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -noreset &

XVFB_PID=$!
sleep 5
/usr/bin/xrandr --newmode "1920x1080_60.00"  173.00  1920 2048 2248 2576  1080 1083 1088 1120 -hsync +vsync
/usr/bin/xrandr --addmode screen "1920x1080_60.00"
/usr/bin/xrandr --output screen --mode "1920x1080_60.00"
wait $XVFB_PID
