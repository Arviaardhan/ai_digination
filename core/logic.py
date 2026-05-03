import math
import numpy as np
from config.settings import DIRECTION_LABELS, FPS_REAL, FRAME_SKIP, PIXEL_TO_METER

def angle_to_direction(angle_deg):
    idx = round(angle_deg / 45) % 8
    return DIRECTION_LABELS[idx]

def compute_velocity(history):
    if len(history) < 3:
        return 0.0, 0.0, 0.0, 0.0
    pts = np.array(history, dtype=float)
    t = np.arange(len(pts))
    vx = float(np.polyfit(t, pts[:, 0], 1)[0])
    vy = float(np.polyfit(t, pts[:, 1], 1)[0])
    speed_px = math.hypot(vx, vy)
    angle    = math.degrees(math.atan2(-vy, vx))
    if angle < 0:
        angle += 360
    return vx, vy, speed_px, angle

def px_speed_to_kmh(speed_px_per_frame: float) -> float:
    effective_fps = FPS_REAL / max(1, FRAME_SKIP)
    speed_mps = speed_px_per_frame * effective_fps * PIXEL_TO_METER
    return speed_mps * 3.6

def check_line_crossing(track, line):
    if line is None or len(track.history) < 2:
        return None
    (lx1, ly1), (lx2, ly2) = line
    p1 = track.history[-2]
    p2 = track.history[-1]
    
    def cross2d(ax, ay, bx, by): return ax * by - ay * bx
    dx, dy   = lx2 - lx1, ly2 - ly1
    dpx, dpy = p2[0] - p1[0], p2[1] - p1[1]
    denom = cross2d(dx, dy, dpx, dpy)
    if abs(denom) < 1e-9:
        return None
    t = cross2d(p1[0]-lx1, p1[1]-ly1, dpx, dpy) / denom
    u = cross2d(p1[0]-lx1, p1[1]-ly1, dx,  dy ) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return "masuk" if dpy > 0 else "keluar"
    return None
