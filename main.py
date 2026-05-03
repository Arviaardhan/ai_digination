"""
KudusFlow — Advanced Vehicle Tracker
=====================================
Di atas deteksi YOLO, tambahan:
  • Multi-object tracking (ByteTrack built-in ultralytics)
  • Speed estimation (px/frame → km/h via perspektif kalibrasi)
  • Direction vector (vektor gerak centroid per track)
  • Heading label (Utara/Selatan/Timur/Barat + diagonal)
  • Vehicle class breakdown (motor, mobil, bus, truk)
  • ROI counting line (kendaraan masuk/keluar garis virtual)
  • Per-track trail history untuk visualisasi jejak
  • JSON output per frame untuk integrasi ke ATSC server
"""

import cv2
import json
import time
from collections import deque

from ultralytics import YOLO

from config import settings
from core.logic import angle_to_direction, check_line_crossing
from core.tracking import TrackState
from utils.visualizer import draw_trail, draw_arrow, draw_info_box, draw_hud

def main():
    model = YOLO(settings.MODEL_PATH)
    print("[KudusFlow] Model loaded:", settings.MODEL_PATH)

    cap = cv2.VideoCapture(settings.STREAM_URL, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("[ERROR] Gagal buka stream:", settings.STREAM_URL)
        return

    fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[KudusFlow] Stream: {fw}×{fh}")

    # Counting line horizontal di 60% tinggi frame
    settings.COUNTING_LINE = ((0, int(fh * 0.6)), (fw, int(fh * 0.6)))

    # Track registry
    tracks: dict[int, TrackState] = {}

    # Smoothing buffer jumlah kendaraan
    smooth_buf = deque(maxlen=settings.SMOOTH_WIN)

    # Counters
    total_in   = 0
    total_out  = 0
    frame_count = 0
    fps_timer   = time.time()
    fps_val     = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame drop, reconnecting...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_count += 1

        # FPS calc
        if frame_count % 30 == 0:
            fps_val = 30 / (time.time() - fps_timer)
            fps_timer = time.time()

        if frame_count % settings.FRAME_SKIP != 0:
            continue

        # ── YOLO Tracking ────────────────────────────────────────
        results = model.track(
            frame,
            imgsz=640,
            conf=settings.CONF,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
            classes=list(settings.VEHICLE_CLASSES.keys()),
        )

        annotated = frame.copy()

        # Draw counting line
        cv2.line(annotated, settings.COUNTING_LINE[0], settings.COUNTING_LINE[1], (0, 255, 255), 1)
        cv2.putText(annotated, "Counting Line", (10, settings.COUNTING_LINE[0][1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        counts = {"motor": 0, "mobil": 0, "berat": 0, "orang": 0, "total": 0}
        frame_data = []

        if results[0].boxes.id is not None:
            boxes   = results[0].boxes.xyxy.cpu().numpy()
            ids     = results[0].boxes.id.cpu().numpy().astype(int)
            classes = results[0].boxes.cls.cpu().numpy().astype(int)
            confs   = results[0].boxes.conf.cpu().numpy()

            for box, tid, cls, conf in zip(boxes, ids, classes, confs):
                x1, y1, x2, y2 = box
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                w  = x2 - x1
                h  = y2 - y1
                area = w * h

                if area < 400:
                    continue

                if tid not in tracks:
                    tracks[tid] = TrackState(tid)
                tr = tracks[tid]
                tr.update(cx, cy, cls)

                # ── Velocity & direction ──────────────────────────
                vx, vy, spd_px, angle = tr.velocity
                speed_kmh = tr.smooth_speed
                direction = angle_to_direction(angle) if spd_px > 1.5 else "Diam"

                # ── Counting line crossing ────────────────────────
                cross = check_line_crossing(tr, settings.COUNTING_LINE)
                if cross and not tr.crossed:
                    tr.crossed  = True
                    tr.cross_dir = cross
                    if cross == "masuk":  total_in  += 1
                    else:                 total_out += 1
                if cross is None and tr.crossed:
                    tr.crossed = False

                # ── Class count ───────────────────────────────────
                dom_cls = tr.dominant_class
                if dom_cls in settings.MOTOR_CLASSES:  counts["motor"] += 1
                elif dom_cls in settings.CAR_CLASSES:  counts["mobil"] += 1
                elif dom_cls in settings.HEAVY_CLASSES: counts["berat"] += 1
                elif dom_cls == 0:            counts["orang"] += 1
                counts["total"] += 1

                # ── Draw trail ────────────────────────────────────
                color = settings.CLASS_COLORS.get(dom_cls, (200, 200, 200))
                draw_trail(annotated, tr.history, color)

                # ── Draw bounding box ─────────────────────────────
                cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)),
                              color, 1)

                # ── Draw velocity arrow ───────────────────────────
                if spd_px > 1.5:
                    draw_arrow(annotated, cx, cy, vx, vy, color)

                # ── Info box ──────────────────────────────────────
                cls_name = settings.VEHICLE_CLASSES.get(dom_cls, "?")
                info = [
                    f"#{tid} {cls_name}",
                    f"{speed_kmh:.0f} km/h",
                    direction,
                ]
                draw_info_box(annotated, x1, y1, info, color)

                # ── JSON per vehicle ──────────────────────────────
                frame_data.append({
                    "track_id":  tid,
                    "class":     cls_name,
                    "speed_kmh": round(speed_kmh, 1),
                    "direction": direction,
                    "angle_deg": round(angle, 1),
                    "bbox":      [round(x1), round(y1), round(x2), round(y2)],
                    "centroid":  [round(cx), round(cy)],
                    "conf":      round(float(conf), 2),
                })

        smooth_buf.append(counts["total"])
        counts["total"] = int(sum(smooth_buf) / len(smooth_buf))

        draw_hud(annotated, counts, total_in, total_out, fps_val)

        json_output = {
            "timestamp":   time.time(),
            "frame":       frame_count,
            "counts":      counts,
            "total_in":    total_in,
            "total_out":   total_out,
            "vehicles":    frame_data,
        }

        if frame_count % 300 == 0:
            active_ids = set(ids.tolist()) if (
                results[0].boxes.id is not None) else set()
            stale = [k for k in tracks if k not in active_ids]
            for k in stale:
                del tracks[k]

        cv2.imshow("KudusFlow — Traffic AI", annotated)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[KudusFlow] Selesai. Total masuk: {total_in} | keluar: {total_out}")

if __name__ == "__main__":
    main()