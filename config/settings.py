STREAM_URL  = "https://stream.kuduskab.go.id/memfs/8d4f74b4-28e2-409c-9593-525c3d594bc4.m3u8"
MODEL_PATH  = "yolov8s.pt"
CONF        = 0.25
FRAME_SKIP  = 2
SMOOTH_WIN  = 5
TRAIL_LEN   = 30

PIXEL_TO_METER = 0.06
FPS_REAL       = 25.0

COUNTING_LINE = None  # Akan di-set dari main.py

VEHICLE_CLASSES = {
    0:  "Orang",
    1:  "Sepeda",
    2:  "Mobil",
    3:  "Motor",
    5:  "Bus",
    7:  "Truk",
}
MOTOR_CLASSES   = {1, 3}
CAR_CLASSES     = {2}
HEAVY_CLASSES   = {5, 7}

CLASS_COLORS = {
    0:  (200, 200, 200),
    1:  (150, 255, 150),
    2:  (0,   200, 255),
    3:  (100, 200, 255),
    5:  (255, 150,  50),
    7:  (255,  80,  80),
}

DIRECTION_LABELS = [
    "Timur", "Timur Laut", "Utara", "Barat Laut",
    "Barat", "Barat Daya", "Selatan", "Tenggara"
]
