"""
This code handles the target functions
@author Ruaa Abdulmajeed
@date February 23rd, 2021
"""

import sys
from PyQt5.QtCore import Qt, QRect, QPointF
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen

class Target(QWidget):
    def __init__(self):
        super().__init__()
        self._pixmap = QPixmap()
        self._coordinate = QPointF()

    @property
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, pixmap):
        self._pixmap = pixmap.copy()
        self.update()
        size = self.pixmap.size()
        if size.isValid():
            self.resize(size)
        else:
            self.resize(300, 300)

    @property
    def coordinate(self):
        return self._coordinate

    @coordinate.setter
    def coordinate(self, point):
        self._coordinate = point
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)
        r = QRect(-1, -1, 2, 2)
        painter.setWindow(r)
        pen = QPen(Qt.red, 0.5, Qt.DotLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawPoint(self.coordinate)
        #print("curent coordinate = " + str(self.coordinate))


# TODO delete main, add comments
if __name__ == "__main__":
    """For testing purposes"""
    app = QApplication(sys.argv)
    ex = Target()
    ex.pixmap = QPixmap(r"C:\Users\yozoh\Documents\random code\plotcam-lite\resources\icons\target_png_300.png")
    ex.coordinate = QPointF(0, 0)
    ex.coordinate = QPointF(0.5, 0.5)
    ex.coordinate = QPointF(0.75, 0.75)
    ex.coordinate = QPointF(1, 1)
    ex.show()
    sys.exit(app.exec_())