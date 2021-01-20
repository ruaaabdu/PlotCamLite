import sys
from PyQt5 import QtGui, QtWidgets

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # pass accelerometer coordinates
        self.plot(0, 1)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, x, y):
        ''' plot some random stuff '''
        # random data
        data = [random.randrange(-3, 3)]
        img = plt.imread(r"C:\Users\ruaaa\Documents\School\Coop\coop\Work Term 3 - Agri-Foods\Qt for Python\Code\HOLD\Windows-Code\def.JPG")
        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        ax.imshow(img, extent = [-3, 3, -3, 3])
        # plot data
        ax.plot(x, y, 'o')

        # refresh canvas
        self.canvas.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())