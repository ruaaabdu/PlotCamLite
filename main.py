"""
Plot Cam Lite main.
"""

from PyQt5.QtWidgets import QApplication
from pcl_mainwindow import PlotCamLiteWindow
import sys


def main():
    global app
    app = QApplication(sys.argv)
    ex = PlotCamLiteWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
