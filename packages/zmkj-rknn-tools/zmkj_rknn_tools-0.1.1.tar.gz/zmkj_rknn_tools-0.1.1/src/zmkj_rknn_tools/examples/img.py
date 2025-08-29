#!/usr/bin/env python3
import cv2
import time
import os
from datetime import datetime

# ---------- 可自行修改的参数 ----------
CAM_ID   = 25          # /dev/video0
SAVE_DIR = "snap"     # 保存目录
# -------------------------------------

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(CAM_ID, cv2.CAP_V4L2)   # Linux 推荐 V4L2

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

if not cap.isOpened():
    raise RuntimeError("无法打开摄像头")
# 设置分辨率：宽 1920，高 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 1 秒 1 帧 → 间隔 1000 ms
interval = 1.0
next_time = time.time()

print("按 Ctrl+C 停止采集，正在保存到", SAVE_DIR)
try:
    while True:
        now = time.time()
        if now < next_time:
            time.sleep(next_time - now)        # 精确等待
        next_time += interval

        ret, frame = cap.read()
        if not ret:
            print("读取帧失败，跳过")
            continue

        # fname = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        fname =  "123.jpg"
        cv2.imwrite(os.path.join(SAVE_DIR, fname), frame)
        print("保存:", fname)

except KeyboardInterrupt:
    print("\n用户中断")

cap.release()