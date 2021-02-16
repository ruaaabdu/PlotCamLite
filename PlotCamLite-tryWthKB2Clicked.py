import sys
import cv2
import numpy as np
import pyrealsense2 as rs
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QIcon, QImage, QPixmap, QTransform
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

rs.__path__
['/usr/lib/python3/dist-packages/pyrealsense2']


  
#import readchar


#Keyboard Section
class InputState:
    LOWER = 0
    CAPITAL = 1


class KeyButton(QPushButton):
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self, key):
        super(KeyButton, self).__init__()

        self._key = key
        self._activeSize = QSize(50,50)
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

class VirtualKeyboard(QWidget):
    sigInputString = pyqtSignal()
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self):
        super(VirtualKeyboard, self).__init__()

        self.globalLayout = QVBoxLayout(self)
        self.keysLayout = QGridLayout()
        self.buttonLayout = QHBoxLayout()

        self.keyListByLines = [
                    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm'],
                    ['z', 'x', 'c', 'v', 'b', 'n', '_', '.', '/', ' '],
                ]
        self.inputString = ""
        self.state = InputState.LOWER

        self.stateButton = QPushButton()
        self.stateButton.setText('Caps')
        self.backButton = QPushButton()
        self.backButton.setText('Delete')

        self.inputLine = QLineEdit()


        for lineIndex, line in enumerate(self.keyListByLines):
            for keyIndex, key in enumerate(line):
                buttonName = "keyButton" + key.capitalize()
                self.__setattr__(buttonName, KeyButton(key))
                self.keysLayout.addWidget(self.getButtonByKey(key), self.keyListByLines.index(line), line.index(key))
                self.getButtonByKey(key).setText(key)
                self.getButtonByKey(key).sigKeyButtonClicked.connect(lambda v=key: self.addInputByKey(v))
                self.keysLayout.setColumnMinimumWidth(keyIndex, 50)
            self.keysLayout.setRowMinimumHeight(lineIndex, 50)

        self.stateButton.clicked.connect(self.switchState)
        self.backButton.clicked.connect(self.backspace)


        self.buttonLayout.addWidget(self.backButton)
        self.buttonLayout.addWidget(self.stateButton)

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

    def sizeHint(self):
        return QSize(480,272)
    
    def changeTextBox(self, textBox):
        self.inputString = ""
        self.inputLine = textBox


"""class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal() # signal when the text entry is left clicked

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicked.emit()
        else: super().mousePressEvent(event)"""

class CameraThread(QThread):
    changePixmap = pyqtSignal(QImage)
    #flags

    

    def run(self):
        rotateImage = True
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
        
        while True: # while loop gets image
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())

            if rotateImage:
                color_image = np.rot90(color_image, 1).copy()

            height, width, channel = color_image.shape
            bytesPerLine = channel * width

            qImg = QImage(color_image.data, width, height, bytesPerLine, QImage.Format_BGR888)

            self.changePixmap.emit(qImg) # triggers the signal, which updates the image


class Window(QWidget):

    def __init__(self):
        super().__init__()#runs everytime tou make a window object ( like GUI = window()), core application stuff,  main window goes here, like a template
        
        self.title = "PlotCam Lite Using PyQt5"
        self.width = 1000 #width of window
        self.height = 1000 #height of window
        self.left = 100 #distance from left
        self.top = 100 #distance from top

       
        
        self.initUI()#run the method which sets up the UI
        
    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('cameraleaf')) #sets icon in top left of screen
        
        #set up grid layout        
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

         #set up camera feed
        camThread = CameraThread(self)
        camThread.changePixmap.connect(self.setImage)
        camThread.start()
        
        self.show()
    
    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setColumnStretch(0, 4)        
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        
        newFileBTN = QPushButton("New File", self)
        newFileBTN.clicked.connect(self.executeNewFileDialog)
        #quitBTN = QPushButton("Quit", self)
        #quitBTN.clicked.connect(self.close) #exits current application        
        self.image_label = QLabel(self)
        #self.kb = VirtualKeyboard()
        layout.addWidget(newFileBTN,0,0)
        layout.addWidget(self.image_label,2, 2)
        #layout.addWidget(self.kb, 2,0)
        #layout.addWidget(quitBTN,2,2)
        
        self.horizontalGroupBox.setLayout(layout)        
    
    @pyqtSlot(QImage)
    def setImage(self, image):
        
        pix = QPixmap.fromImage(image)
        #transform = QTransform()
        #transform.rotate(90)
        #self.image_label.setPixmap(pix.transformed(transform))
        self.image_label.setPixmap(pix)

    def executeNewFileDialog(self):
        newFile_page = NewFilePage()
        newFile_page.exec_()

    """def exitDialog(self):
        exitMsg = QMessageBox()
        exitMsg.setIcon(QMessageBox.Critical)
        exitMsg.setText("Are you sure you want to exit?")
        exitMsg.setInformativeText("Ensure All Data is Saved")
        exitMsg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        exitMsg.buttonClicked.connect(self.close)"""
    
class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal(QLineEdit)

    def mousePressEvent(self, event):
        self.clicked.emit(self)

        """else:
            super().mousePressEvent(event)
            print("HELLLOOOOOOO I AM CLICK")"""
    
class NewFilePage(QDialog):
    def __init__(self):
        super(NewFilePage, self).__init__()
        loadUi('NewFileDialog.ui', self)
        self.setUpLayout()
        self.show()
    def setUpLayout(self):
        self.keyboard = VirtualKeyboard()
        self.keyboardLayout.addWidget(self.keyboard)

        self.fileNameTextBox = ClickableLineEdit("Enter File Name Here")
        self.fileNameTextBox.clicked.connect(self.changeKeyboardTextBox)

        self.textBoxLayout.addWidget(self.fileNameTextBox)
        
        self.plotNumberTextBox = ClickableLineEdit("Enter Plot Number Here")
        self.plotNumberTextBox.clicked.connect(self.changeKeyboardTextBox)

        self.textBoxLayout.addWidget(self.plotNumberTextBox)

        self.saveFileNameBtn.clicked.connect(self.printTextBox)

    def changeKeyboardTextBox(self, textBox):
        self.keyboard.changeTextBox(textBox)
    
    def printTextBox(self):
        print(self.fileNameTextBox.text() + self.plotNumberTextBox.text())
    

        

        

def printCameraSerial():
    ctx = rs.context()
    if len(ctx.devices) > 0: 
        for d in ctx.devices:
            print ('Found device: ', d.get_info(rs.camera_info.name), ' ', d.get_info(rs.camera_info.serial_number))
    else:
        print("No Intel Device connected")


def main():
    printCameraSerial()
    app = QApplication(sys.argv)
    ex = Window()
    #ex.displayCameraFeed()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



