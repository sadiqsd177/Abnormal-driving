import cv2
import numpy as np

# Simple test without MediaPipe
cap = cv2.VideoCapture('uploads/223.mp4')
total_frames = 0
frame_skip = max(5, 30 // 6)
print('Frame skip:', frame_skip)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    total_frames += 1
    if total_frames % frame_skip != 0:
        continue
    print(f'Frame {total_frames}: shape {frame.shape}')
    if total_frames > 10:
        break

cap.release()
print('Total frames processed:', total_frames)
