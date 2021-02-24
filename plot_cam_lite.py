####################################################
# plot_cam_lite.py v0.2
####################################################
"""
This code runs the Plot Cam Lite Module
@author Ruaa Abdulmajeed
@date February 8th, 2021
"""
# Sys module provides functions to manipulate Python runtime environment
import sys

# OS module provides functions related to the OS
import os

# PyQt Widgets for the applicaton and layout
from PyQt5.QtWidgets import QApplication, QWidget, \
    QGroupBox, QVBoxLayout, QPushButton, QGridLayout, QLabel,\
    QDialog, QMainWindow, QErrorMessage, QHBoxLayout, QLineEdit, QSizePolicy, QMessageBox

# PyQt GUI for GUI components
from PyQt5.QtGui import QIcon, QImage, QPixmap, QClipboard, QPainter, QPen

# PyQt UIC for UI methods
from PyQt5.uic import loadUi

# PyQt Core for slots, signals, and threads
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QSize, Qt, QPoint, QPointF

# Figure Canvas for adding Figure as a widget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# The following files store the rest of the code of the program
from virtual_keyboard import VirtualKeyboard, ClickableLineEdit
from accelerometer import Position, AccelerometerThread
from camera_feed import CameraThread
from target import Target
from metadata import Metadata, sampleMetaData
import extra_functions


# ---------------------------------- Global Variables -------------------------------------#

# path where the three folders will be set up in, can possible change this to a browser search in a later update.
main_path = r"C:\Users\ruaaa\Desktop\CameraData"

# False for Windows and True for RPI
RPI = False

file_name = ""


class Window(QMainWindow):
    """Window class is used to generate UI of the main program.
    Window is the top class, it encompasses the rest of the classes and UI

    Args:
        QWidget (QWidget): Base class of all UI objects
    """

    takePicture = pyqtSignal(str)  # Signal "Take Picture" button

    def __init__(self):  # runs everytime a window object is created
        """ Initalizes the window class by introducing the variables needed """

        super().__init__()

        # Set title depending on OS
        if RPI:
            self.title = "PlotCam Lite - RPI and PyQt5"
        else:
            self.title = "PlotCam Lite - Windows and PyQt5"

        # Set file path variables
        self.current_experiment_name = ""
        self.current_file_path = ""
        self.current_picture_path = ""
        self.current_plot_number = 0

        self.width = 2000  # width of window
        self.height = 2000  # height of window
        self.left = 100  # distance from left
        self.top = 100  # distance from top

        self.setGeometry(self.left, self.top, self.width, self.height)

        self.init_ui()

    def init_ui(self):
        """ Initalizes the UI by assigning methods to the buttons as well as starting the threads """

        loadUi('PlotCamLiteUI.ui', self)
        self.setWindowIcon(QIcon('cameraleaf.png'))

        # Set size of camera label and start camera thread
        camera_size_policy = QSizePolicy(480, 640)
        self.camera_label.setSizePolicy(camera_size_policy)
        self.start_camera_thread()

        self.start_accelerometer_thread()

        # Connect New Experiment Button
        self.new_file_button.clicked.connect(self.new_file_dialog)
        self.file_name_label.setText(file_name)

        self.set_target()

        # Connect Take Picture Button
        self.take_picture_button.clicked.connect(self.take_picture)

        # Connect Exit Button
        self.exit_button.clicked.connect(self.close)

    def start_camera_thread(self):
        """ Starts the camera thread and connects the method which updates the image in the main window and the method which takes the picture """
        self.camera_thread1 = CameraThread(self)
        self.camera_thread1.changePixmap.connect(self.set_image)
        self.camera_thread1.start()
        self.takePicture.connect(lambda: self.camera_thread1.take_picture(
            self.current_file_path, self.current_experiment_name + str(self.current_plot_number).zfill(3)))

    def start_accelerometer_thread(self):
        self.accelerometer_thread = AccelerometerThread(self)
        self.accelerometer_thread.changeTarget.connect(self.draw_coordinate)
        self.accelerometer_thread.start()

    # def setup_metadata(self, metadata_filepath):
    #     self.metadata = Metadata(metadata_filepath)

    @pyqtSlot(QImage)
    def set_image(self, image):
        """ Sets the image set with the next frame from CameraThread to start.

        Args:
            image QImage: Image to be displayed
        """
        pix = QPixmap.fromImage(image)
        self.camera_label.setPixmap(pix)

    @pyqtSlot(Position)
    def draw_coordinate(self, new_position):
        """ 
        """
        self.x = new_position.x
        self.y = new_position.y
        self.target.coordinate = QPointF(self.x, self.y)
        if self.x >= -0.2 and self.x <= 0.2 and self.y >= -0.2 and self.y <= 0.2:
            self.camera_level_label.setText("Camera is Level")
            self.camera_level_label.setStyleSheet("color: green;")
        else:
            self.camera_level_label.setText("Camera is not Level")
            self.camera_level_label.setStyleSheet("color: red;")

    def take_picture(self):
        """ Emits a signal to the Camera Thread to save the current frame.
        """
        self.takePicture.emit(self.current_experiment_name)
        self.save_metadata()
        self.current_plot_number = self.current_plot_number + 1
        self.update_plot_number_label(str(self.current_plot_number))

    def save_metadata(self):
        if self.metadata == None:
            return
        num = str(self.current_plot_number).zfill(3)
        xpos = self.x
        ypos = self.y
        time = sampleMetaData["time"]
        air = sampleMetaData["air"]
        light = sampleMetaData["light"]
        lat = sampleMetaData["lattitude"]
        lon = sampleMetaData["longitude"]
        batt = sampleMetaData["battery"]
        zero = sampleMetaData["zeroingvalue"]
        plantheight = sampleMetaData["plantheight"]
        self.metadata.add_entry(num, time, self.x, self.y, air, light,
                                lat, lon, batt, zero, plantheight)

    @pyqtSlot(str)
    def update_file_name_label(self, new_file_name):
        """ Updates file name label when the experiment name is chosen as well as the variables needed to save the file

        Args:
            new_file_name (str): The new experiment name
        """
        self.file_name_label.setText(new_file_name)
        self.current_file_path = main_path + "\\" + new_file_name
        self.current_experiment_name = new_file_name
        self.metadata = Metadata(
            self.current_file_path + "\\Metadata\\" + self.current_experiment_name)

    @pyqtSlot(str)
    def update_plot_number_label(self, new_plot_number):
        """ Updates plot number label with the current number as well as the variables needed to save the file

        Args:
            new_plot_number (str): The new plot number
        """
        self.plot_number_label.setText("Plot #: " + new_plot_number.zfill(3))
        self.current_plot_number = int(new_plot_number)
        #self.current_picture_path = self.current_file_path + "\RGB\\"+ self.current_experiment_name + new_plot_number

    def new_file_dialog(self):
        """ Open the "New File" Dialog and connect methods to update file name and plot number labels."""
        new_file_page = NewFilePage()
        new_file_page.changeFileName.connect(self.update_file_name_label)
        new_file_page.changePlotNumber.connect(self.update_plot_number_label)
        new_file_page.exec_()
        new_file_page.show()

    def set_target(self):
        self.wrapper = QWidget()
        self.target_layout = QGridLayout()
        self.target_layout.addWidget(self.wrapper)
        self.target_widget.setLayout(self.target_layout)
        self.target = Target()
        self.target.pixmap = QPixmap(r"Pictures\target_png_300.png")
        self.target.setGeometry(0, 0, 300, 300)
        self.target.setParent(self.wrapper)
        self.target.show()

    def closeEvent(self, event):
        """ Overwrites systems "self.close" method so that the program can terminate properly

        Args:
            event (Event): The event to close
        """
        self.camera_thread1.stop()
        self.accelerometer_thread.stop()
        sys.exit()


class NewFilePage(QDialog):
    """ Pop up dialog to select files to write data to.

    Args:
        QDialog (QDialog): Base class of dialog windows.
    """
    changeFileName = pyqtSignal(str)
    changePlotNumber = pyqtSignal(str)

    def __init__(self):
        """Initalize required layout variables and add widgets."""
        super(NewFilePage, self).__init__()
        self.lineedit_group_box = QGroupBox()
        self.keyboard_group_box = QGroupBox()
        self.setUpLayout()

        window_layout = QVBoxLayout()
        window_layout.addWidget(self.lineedit_group_box)
        window_layout.addWidget(self.keyboard_group_box)
        self.setLayout(window_layout)

    def setUpLayout(self):
        """ Set Up Layout components and adds them to boxes initalized in constructor"""

        self.lineedit_layout = QGridLayout()
        self.lineedit_layout.setColumnStretch(0, 4)
        self.lineedit_layout.setColumnStretch(1, 4)

        self.keyboard_layout = QGridLayout()

        self.newFileLineEdit = ClickableLineEdit("")
        self.plotNumberLineEdit = ClickableLineEdit("")
        self.newFileLineEdit.setPlaceholderText("Enter File Name Here")
        self.plotNumberLineEdit.setPlaceholderText(
            "Enter Start Plot Number Here")

        self.keyboard = VirtualKeyboard()

        self.newFileLineEdit.clicked.connect(self.keyboard.setLineEdit)
        self.newFileLineEdit.setToolTip(
            "Setting a file name with an existing folder with the same filename will cause an error")

        self.plotNumberLineEdit.clicked.connect(self.keyboard.setLineEdit)
        self.plotNumberLineEdit.setToolTip(
            "Leaving this blank will set the plot number to 1")

        newFileLineEdit_label = QLabel("Experiment Name")
        plotNumberLineEdit_label = QLabel("Plot Number")
        self.lineedit_layout.addWidget(self.newFileLineEdit, 0, 0)
        self.lineedit_layout.addWidget(self.plotNumberLineEdit, 0, 1)
        self.lineedit_layout.addWidget(newFileLineEdit_label, 1, 0)
        self.lineedit_layout.addWidget(plotNumberLineEdit_label, 1, 1)

        self.keyboard_layout.addWidget(self.keyboard, 0, 0)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.create_directories)
        self.saveButton.clicked.connect(self.set_plot_number)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.terminate)

        self.keyboard_layout.addWidget(self.saveButton, 1, 0)
        self.keyboard_layout.addWidget(self.cancelButton, 1, 1)

        self.lineedit_group_box.setLayout(self.lineedit_layout)
        self.keyboard_group_box.setLayout(self.keyboard_layout)

    def create_directories(self):
        """ Creates new RGB, Depth, and Metadata directories using filename and sets new plot number"""
        file_name = self.newFileLineEdit.text()
        new_path = main_path + "\\" + file_name

        try:
            plotnumber = self.set_plot_number()
            if not plotnumber.isnumeric():
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setStandardButtons(QMessageBox.Ok)
                error_msg.setText(
                    "Uh oh, there are no numbers in the plot number field. Please enter a number or leave it blank to set to default")
                error_msg.exec()
                return
            os.mkdir(new_path)

        except OSError:
            print("Creation of the directory %s failed" % main_path)
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            error_msg.setText(
                "Uh oh, an error occured. \n Double check that there is not an existing experiment under this name")
            error_msg.exec()

        else:
            success_msg = QMessageBox()
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setStandardButtons(QMessageBox.Ok)
            success_msg.setText("Creation of directory successful")
            success_msg.setDetailedText(
                "Directory can be found at this file path: \n" + new_path)
            response = success_msg.exec()

            os.mkdir(new_path + "\\" + "RGB")
            os.mkdir(new_path + "\\" + "Depth")
            os.mkdir(new_path + "\\" + "Metadata")

            self.changeFileName.emit(file_name)

            if response == QMessageBox.Ok:
                self.close()

    def set_plot_number(self):
        """ Sets new plot number to input value, or to 001 if there was no input.

        Returns:
            str: String storing the current plot number
        """
        plot_number_input = self.plotNumberLineEdit.text()
        if plot_number_input == "" or plot_number_input == "Enter Plot Number here":
            plot_number_input = "1"
        self.changePlotNumber.emit(plot_number_input)

        return plot_number_input.zfill(3)

    def terminate(self):
        """ Terminate the dialog """
        self.close()


def main():
    """ Creates an instance of the PlotCamLite program """
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
