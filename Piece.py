
import math
from PyQt6.QtCore import QPointF, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

class Piece(QGraphicsPixmapItem):
    def __init__(self, img: QPixmap, piece_type: str, color: str):
        super().__init__(img)

        self.type = piece_type
        self.color = color
        
        self.target = QPointF()
        self.timer = QTimer();
        self.timer.timeout.connect(self._tick)
        self.speed = 10

    def move(self, y, x, w, h):
        self.target = QPointF(w * x, h * y)

        self.timer.start(16);

    def _tick(self):
        pos = self.pos()
        
        dx, dy = self.target.x() - pos.x(), self.target.y() - pos.y()
        dist = math.hypot(dx, dy)

        if dist < 1:
            self.setPos(self.target)
            self.timer.stop()

        else:
            step = min(dist, self.speed)
            self.setPos(pos.x() + dx / dist * step, pos.y() + dy / dist * step)

    def string(self):
        return f"{self.type}{self.color}"

    def upgrade(self, piece_type, new_pixmap):
        self.setPixmap(new_pixmap)
        self.type = piece_type

    def __eq__(self, value):
        if isinstance(value, str):
            return self.string() == value
        
        return false

    def __ne__(self, value):
        if isinstance(value, str):
            return self.string() != value

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return self.string()[idx.start:idx.stop:idx.step]

        return self.string()[idx]

    def __len__(self):
        return len(self.string())
