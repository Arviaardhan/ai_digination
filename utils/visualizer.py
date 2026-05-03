import cv2

def draw_trail(frame, history, color):
    pts = list(history)
    for i in range(1, len(pts)):
        alpha = i / len(pts)
        c = tuple(int(v * alpha) for v in color)
        thickness = max(1, int(alpha * 2))
        cv2.line(frame, (int(pts[i-1][0]), int(pts[i-1][1])),
                        (int(pts[i][0]),   int(pts[i][1])), c, thickness)

def draw_arrow(frame, cx, cy, vx, vy, color):
    scale = 3.0
    ex, ey = int(cx + vx * scale), int(cy + vy * scale)
    cv2.arrowedLine(frame, (int(cx), int(cy)), (ex, ey), color, 2, tipLength=0.3)

def draw_info_box(frame, x1, y1, lines, color):
    line_h = 16
    pad    = 5
    box_h  = len(lines) * line_h + pad * 2
    box_w  = max(len(l) for l in lines) * 7 + pad * 2
    bx1, by1 = int(x1), max(0, int(y1) - box_h - 2)
    bx2, by2 = bx1 + box_w, by1 + box_h
    overlay = frame.copy()
    cv2.rectangle(overlay, (bx1, by1), (bx2, by2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    for i, line in enumerate(lines):
        ty = by1 + pad + (i + 1) * line_h - 3
        cv2.putText(frame, line, (bx1 + pad, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)

def draw_hud(frame, counts, total_in, total_out, fps):
    h, w = frame.shape[:2]
    lines = [
        f"FPS     : {fps:.1f}",
        f"Motor   : {counts.get('motor', 0)}",
        f"Mobil   : {counts.get('mobil', 0)}",
        f"Bus/Truk: {counts.get('berat', 0)}",
        f"Total   : {counts.get('total', 0)}",
        f"Masuk   : {total_in}",
        f"Keluar  : {total_out}",
    ]
    pad, line_h = 8, 18
    box_w = 170
    box_h = len(lines) * line_h + pad * 2
    ox = w - box_w - 10
    oy = 10
    overlay = frame.copy()
    cv2.rectangle(overlay, (ox, oy), (ox + box_w, oy + box_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)
    for i, l in enumerate(lines):
        cv2.putText(frame, l, (ox + pad, oy + pad + (i + 1) * line_h - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.46, (200, 230, 255), 1, cv2.LINE_AA)
