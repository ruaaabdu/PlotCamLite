import sys
import cv2
import numpy as np
import pyrealsense2 as rs
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QIcon, QImage, QPixmap, QTransform
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)
from PyQt5.uic import loadUi


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
        layout.addWidget(newFileBTN,0,0)
        layout.addWidget(self.image_label,2, 2)
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
    
    
class NewFilePage(QDialog):
    def __init__(self):
        super(NewFilePage, self).__init__()
        loadUi('NewFileDialog.ui', self)

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
