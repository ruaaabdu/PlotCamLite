# import sys
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *

# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setGeometry(30, 30, 500, 300)

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         pixmap = QPixmap(r"C:\Users\ruaaa\Documents\School\Coop\coop\Work Term 3 - Agri-Foods\Working Directory\Examples\Accelerometer\target.JPG")
#         painter.drawPixmap(self.rect(), pixmap)
#         x, y = input("Input the x and y coordinates for the point").split()
#         print("The given point is: " + x + y)
#         self.drawGivenPoint(painter, int(x), int(y))

#     def drawGivenPoint(self, painter, x, y):
#         pen = QPen(Qt.red, 3)
#         painter.setPen(pen)
#         painter.drawPoint(x, y)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     ex.show()
#     sys.exit(app.exec_())

# from PyQt5.QtWidgets import QWidget, QApplication
# from PyQt5.QtGui import QPainter, QPen
# from PyQt5.QtCore import Qt
# import sys, random


# class Example(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.initUI()

#     def initUI(self):
#         self.setGeometry(300, 300, 300, 190)
#         self.setWindowTitle('Points')
#         self.show()

#     def paintEvent(self, e):
#         qp = QPainter(self)
#         qp.begin(self)
#         self.drawPoints(qp)
#         qp.end()

#     def drawPoints(self, qp):
#         p = QPen()
#         p.setWidth(10)
#         qp.setPen(p)
#         qp.drawPoint(150, 50)


# def main():
#     app = QApplication(sys.argv)
#     ex = Example()
#     sys.exit(app.exec_())


# if __name__ == '__main__':
#     main()

# import sys
# from PyQt5.QtCore import Qt, QPoint
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
# from PyQt5.QtGui import QPixmap, QPainter, QPen


# class Target(QWidget):

#     def __init__(self):
#         super().__init__()
#         self.drawing = False
#         self.lastPoint = QPoint()
#         self.image = QPixmap(r"Pictures\target.JPG")
#         self.setGeometry(100, 100, 500, 300)
#         self.resize(self.image.width(), self.image.height())
#         self.show()

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.drawPixmap(self.rect(), self.image)

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.drawing = True
#             self.lastPoint = event.pos()

#     def mouseMoveEvent(self, event):
#         if event.buttons() and Qt.LeftButton and self.drawing:
#             painter = QPainter(self.image)
#             painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
#             painter.drawLine(self.lastPoint, event.pos())
#             self.lastPoint = event.pos()
#             self.update()

#     def mouseReleaseEvent(self, event):
#         if event.button == Qt.LeftButton:
#             self.drawing = False


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainMenu = Target()
#     sys.exit(app.exec_())

import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush

from PyQt5.QtSvg import QSvgRenderer


# class Target(QWidget):
# # coordinate doenst move
#     def __init__(self):
#         super().__init__()
#         self.drawing = False
#         self.image = QPixmap(r"Pictures\target.JPG")
#         self.setGeometry(100, 100, 500, 500)
#         self.resize(self.image.width(), self.image.height())
#         self.show()

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.drawPixmap(self.rect(), self.image)
#         self.paintCoordinate()
    
#     def paintCoordinate(self):
#         painter = QPainter(self.image)
#         pen = QPen(Qt.red, 10, Qt.DashDotLine)
#         color = QColor(0, 0, 0)
#         #painter.setPen(pen)
#         brush = QBrush(Qt.SolidPattern)
#         brush.setStyle(Qt.Dense1Pattern)
#         painter.setBrush(brush)
#         #painter.fillRect(50, 50, 30, 30, color)
#         painter.drawPoint (50, 50)

class Target(QWidget):
# coordinate doenst move
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.drawing = False
        self.image = QPixmap(r"Pictures\target_png_300.png")
        self.setGeometry(0, 0, 300, 300)
        self.resize(self.image.width(), self.image.height())
        #self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)
        #self.paintCoordinate(50,50)
    
    def paintCoordinate(self, x, y):
        painter = QPainter(self.image)
        color = QColor(0, 0, 0)
        pen = QPen(color, 10, Qt.DashDotLine)
        painter.setPen(pen)
        painter.drawPoint (x, y)



# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainMenu = Target()
#     sys.exit(app.exec_())


# import sys, random
# from PyQt5.QtCore import Qt, QPoint
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
# from PyQt5.QtGui import QPixmap, QPainter, QPen

# class Target(QWidget):
    
#     def __init__(self):
#         super(Target, self).__init__()
#         self.x = 100
#         self.y = 200
#         self.initUI()
        
#     def initUI(self):      

#         self.setGeometry(300, 300, 280, 170)
#         self.setWindowTitle('Points')
#         self.show()

#     def paintEvent(self, e):

#         qp = QPainter()
#         painter = QPainter(self)
#         pixmap = QPixmap(r"Pictures\target.JPG")
#         painter.drawPixmap(self.rect(), pixmap)
#         pen = QPen(Qt.red, 20)
#         painter.setPen(pen)
#         painter.drawPoint(self.x, self.y)
        
# def main():
    
#     app = QApplication(sys.argv)
#     ex = Target()
#     sys.exit(app.exec_())


# if __name__ == '__main__':
#     main()