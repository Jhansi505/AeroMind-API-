import cv2
import numpy as np


def detect_obstacles_opencv() -> dict:
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {"obstacle_detected": False, "reason": "Camera unavailable"}

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"obstacle_detected": False, "reason": "Frame capture failed"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    edge_pixels = int(np.sum(edges > 0))
    obstacle = edge_pixels > 5000

    return {
        "obstacle_detected": obstacle,
        "edge_pixel_count": edge_pixels
    }
