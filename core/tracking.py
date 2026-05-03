import time
from collections import deque
from core.logic import compute_velocity, px_speed_to_kmh
from config.settings import TRAIL_LEN

class TrackState:
    def __init__(self, track_id: int):
        self.id      = track_id
        self.history = deque(maxlen=TRAIL_LEN)
        self.classes = deque(maxlen=10)
        self.speeds  = deque(maxlen=10)
        self.frames  = 0
        self.first_seen = time.time()
        self.crossed  = False
        self.cross_dir = None

    def update(self, cx: float, cy: float, cls: int):
        self.history.append((cx, cy))
        self.classes.append(cls)
        self.frames += 1

    @property
    def dominant_class(self) -> int:
        if not self.classes:
            return -1
        return max(set(self.classes), key=list(self.classes).count)

    @property
    def velocity(self):
        return compute_velocity(self.history)

    @property
    def smooth_speed(self) -> float:
        vx, vy, spd_px, angle = self.velocity
        kmh = px_speed_to_kmh(spd_px)
        self.speeds.append(kmh)
        if not self.speeds:
            return 0.0
        return sum(self.speeds) / len(self.speeds)
