
import sys

import os

# PyQt Widgets for the applicaton and layout
from PyQt5.QtWidgets import QApplication, QWidget, \
    QGroupBox, QVBoxLayout, QPushButton, QGridLayout, QLabel,\
    QDialog, QMainWindow, QErrorMessage, QHBoxLayout, QLineEdit, QSizePolicy, QMessageBox
# PyQt GUI for GUI components
from PyQt5.QtGui import QIcon, QImage, QPixmap
# PyQt UIC for UI methods
from PyQt5.uic import loadUi

from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QSize

# Figure Canvas for adding Figure as a widget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# Global Variables

# path where the three folders will be set up in
main_path = r"C:\Users\ruaaa\Documents\School\Coop\coop\Work Term 3 - Agri-Foods\Working Directory\CameraData"

file_name = ""
class Window(QMainWindow):

    def __init__(self):  # runs everytime a window object is created
        """ Initalizes the window class by introducing the variables needed """
        super().__init__()
        self.init_ui()


    def init_ui(self):
        """ Initalizes the UI and camera feed processing thread """
        loadUi('MainWindowUI.ui', self)
        self.setWindowIcon(QIcon('cameraleaf.png'))


        self.exit_button.clicked.connect(self.teardown)
        self.new_file_button.clicked.connect(self.new_file_dialog)
        self.file_name_label.setText(file_name)

        self.show()
    
    @pyqtSlot(str)
    def update(self, new_file_name):
        self.file_name_label.setText(new_file_name)
        print("made it here")


    def new_file_dialog(self):
        new_file_page = NewFilePage()
        new_file_page.changeFileName.connect(self.update)
        new_file_page.exec_()
        
    
    def teardown(self):
        sys.exit()

class NewFilePage(QDialog):
    """ Pop up dialog to select files to write data to.

    Args:
        QDialog (QDialog): Base class of dialog windows.
    """
    changeFileName = pyqtSignal(str)

    def __init__(self):
        super(NewFilePage, self).__init__()
        #loadUi('NewFileDialog.ui', self)
        self.lineedit_group_box = QGroupBox()
        self.keyboard_group_box = QGroupBox()
        self.setUpLayout()
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.lineedit_group_box)
        window_layout.addWidget(self.keyboard_group_box)
        self.setLayout(window_layout)
        self.show()

    def setUpLayout(self):

        self.lineedit_layout = QGridLayout()
        self.lineedit_layout.setColumnStretch(0, 4)
        self.lineedit_layout.setColumnStretch(1, 4)

        self.keyboard_layout = QGridLayout()

        self.newFileLineEdit = ClickableLineEdit("Enter File Name Here")
        self.plotNumberLineEdit = ClickableLineEdit("Enter Plot Number here")
        
        self.newFileLineEdit.clicked.connect(lambda: self.initKBforLineEdit(self.newFileLineEdit))
        self.newFileLineEdit.setToolTip("Setting a file name with an existing folder with the same filename will cause an error")

        self.plotNumberLineEdit.clicked.connect(lambda: self.initKBforLineEdit(self.plotNumberLineEdit))
        self.plotNumberLineEdit.setToolTip("Leaving this blank will set the plot number to 1")

        self.keyboard = VirtualKeyboard(self.newFileLineEdit)


        newFileLineEdit_label = QLabel("File Name")
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


        print("UI: Grid Layout created and widgets are added")

    def create_directories(self):
        file_name = self.newFileLineEdit.text()
        print("The new filename is: " + file_name)

        new_path = main_path + "\\" + file_name


        try:
            plotnumber = self.set_plot_number()
            if not plotnumber.isnumeric():
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                error_msg.setText("Uh oh, there are no numbers in the plot number field. Please enter a number or leave it blank to set to default")
                error_msg.exec()
                return
            os.mkdir(new_path)

        except OSError:
            print ("Creation of the directory %s failed" % main_path)
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            error_msg.setText("Uh oh, an error occured. \n Double check that there is not an existing experiment under this name")
            error_msg.exec()
        else:
            success_msg = QMessageBox()
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            success_msg.setText("Creation of the directory %s successful" % main_path)
            success_msg.exec()
            os.mkdir(new_path + "\\" + "RGB")
            os.mkdir(new_path + "\\" + "Depth")
            os.mkdir(new_path + "\\" + "Metadata")
            self.changeFileName.emit(file_name)
    
    def set_plot_number(self):
        plot_number_input = self.plotNumberLineEdit.text()
        if plot_number_input == "" or plot_number_input == "Enter Plot Number here":
            plot_number_input = "0"

        return plot_number_input
    
    def initKBforLineEdit(self, lineToEdit):
        self.keyboard.terminate()
        self.newKeyboard = VirtualKeyboard(lineToEdit)
        self.keyboard_layout.addWidget(self.newKeyboard, 0, 0)
        print("here")

    def terminate(self):

        self.close()

class KeyButton(QPushButton):
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self, key):
        super(KeyButton, self).__init__()

        self._key = key
        self._activeSize = QSize(50, 50)
        self.clicked.connect(self.emitKey)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def emitKey(self):
        self.sigKeyButtonClicked.emit()

    def enterEvent(self, event):
        self.setFixedSize(self._activeSize)

    def leaveEvent(self, event):
        self.setFixedSize(self.sizeHint())

    def sizeHint(self):
        return QSize(40, 40)

class InputState:
    LOWER = 0
    CAPITAL = 1

class VirtualKeyboard(QWidget):
    sigInputString = pyqtSignal()
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self, lineToEdit):
        super(VirtualKeyboard, self).__init__()

        self.globalLayout = QVBoxLayout(self)
        self.keysLayout = QGridLayout()
        self.buttonLayout = QHBoxLayout()

        self.keyListByLines = [
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "m"],
            ["z", "x", "c", "v", "b", "n", "_", ".", "/", " "],
        ]
        self.inputString = "" ## resetting input
        self.state = InputState.LOWER

        self.stateButton = QPushButton()
        self.stateButton.setText("Caps")
        self.backButton = QPushButton()
        self.backButton.setText("Delete")
        self.okButton = QPushButton()
        self.okButton.setText("Enter")
        self.cancelButton = QPushButton()
        self.cancelButton.setText("Cancel")

        self.inputLine = lineToEdit

        for lineIndex, line in enumerate(self.keyListByLines):
            for keyIndex, key in enumerate(line):
                buttonName = "keyButton" + key.capitalize()
                self.__setattr__(buttonName, KeyButton(key))
                self.keysLayout.addWidget(
                    self.getButtonByKey(key),
                    self.keyListByLines.index(line),
                    line.index(key),
                )
                self.getButtonByKey(key).setText(key)
                self.getButtonByKey(key).sigKeyButtonClicked.connect(
                    lambda v=key: self.addInputByKey(v)
                )
                self.keysLayout.setColumnMinimumWidth(keyIndex, 50)
            self.keysLayout.setRowMinimumHeight(lineIndex, 50)
        
        self.stateButton.setCheckable(True) 
        self.stateButton.clicked.connect(self.switchState)
        self.backButton.clicked.connect(self.backspace)
        self.okButton.clicked.connect(self.emitInputString)
        self.cancelButton.clicked.connect(self.emitCancel)

        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.backButton)
        self.buttonLayout.addWidget(self.stateButton)
        self.buttonLayout.addWidget(self.okButton)

        #self.globalLayout.addWidget(self.inputLine)
        self.globalLayout.addLayout(self.keysLayout)

        self.globalLayout.addLayout(self.buttonLayout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def getButtonByKey(self, key):
        return getattr(self, "keyButton" + key.capitalize())

    def getLineForButtonByKey(self, key):
        return [key in keyList for keyList in self.keyListByLines].index(True)

    def switchState(self):
        self.state = not self.state

    def addInputByKey(self, key):
        self.inputString += (key.lower(), key.capitalize())[self.state]
        self.inputLine.setText(self.inputString)

    def backspace(self):
        self.inputLine.backspace()
        self.inputString = self.inputString[:-1]

    def emitInputString(self):
        self.sigInputString.emit(self.inputString)

    def emitCancel(self):
        self.sigInputString.emit()

    def sizeHint(self):
        return QSize(480, 272)
    
    def terminate(self):
        self.close


class ClickableLineEdit(QLineEdit):  # need this to know which line edit were on
    clicked = pyqtSignal()  # signal when the text entry is left clicked
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, event)


def main():
    """ Creates an instance of the PlotCamLite program """
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
