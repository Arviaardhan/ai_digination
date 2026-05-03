from ultralytics import YOLO
import cv2
from collections import deque

STREAM_URL = "https://stream.kuduskab.go.id/memfs/8d4f74b4-28e2-409c-9593-525c3d594bc4.m3u8"

model = YOLO("yolov8s.pt")  # lebih kuat dari n

CONF_THRESHOLD = 0.25
FRAME_SKIP = 4
SMOOTH_WINDOW = 5

cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)

buffer = deque(maxlen=SMOOTH_WINDOW)
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    # JANGAN resize dulu (biar akurat)
    results = model(frame, imgsz=640, conf=CONF_THRESHOLD, verbose=False)

    vehicle_count = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if conf < CONF_THRESHOLD:
                continue

            x1, y1, x2, y2 = box.xyxy[0]

            width = x2 - x1
            height = y2 - y1
            area = width * height
            aspect_ratio = height / (width + 1)

            # =========================
            # IGNORE NOISE
            # =========================
            if area < 500:
                continue

            # =========================
            # PERSON → MOTOR DETECTION
            # =========================
            if cls == 0:
                if area > 2500 and aspect_ratio < 2.5:
                    vehicle_count += 1
                continue

            # =========================
            # VEHICLE NORMAL
            # =========================
            if cls in [2, 3, 5, 7]:

                # HANDLE MOTOR BERDEKATAN
                if area > 12000:
                    vehicle_count += 2
                elif area > 6000:
                    vehicle_count += 1
                else:
                    vehicle_count += 1
    
    # smoothing
    buffer.append(vehicle_count)
    avg_count = int(sum(buffer) / len(buffer))

    annotated = results[0].plot()

    cv2.putText(annotated, f"Vehicles: {avg_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.putText(annotated, "Press Q / ESC to Stop", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    cv2.imshow("KudusFlow - Traffic AI", annotated)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()