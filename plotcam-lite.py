import sys
from PyQt5.QtWidgets import QApplication
from components.main_window import PlotCamLiteWindow
from util import configure_plotcamlite


def main():
    """
    Plot Cam Lite main.
    Starts the PlotCamLite.
    Configures the PCL through command line arguments.
    """

    configure_plotcamlite()
    app = QApplication(sys.argv)
    ex = PlotCamLiteWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
