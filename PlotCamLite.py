import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QMessageBox, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import pyrealsense2 as rs
import numpy as np
import cv2

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
        
        self.show()
    
    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setColumnStretch(0, 4)        
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        
        newFileBTN = QPushButton("New File", self);
        quitBTN = QPushButton("Quit", self);
        quitBTN.clicked.connect(self.close) #exits current application
        
        
        layout.addWidget(newFileBTN,0,0)

        layout.addWidget(quitBTN,2,2)
        
        self.horizontalGroupBox.setLayout(layout)
    """def exitDialog(self):
        exitMsg = QMessageBox()
        exitMsg.setIcon(QMessageBox.Critical)
        exitMsg.setText("Are you sure you want to exit?")
        exitMsg.setInformativeText("Ensure All Data is Saved")
        exitMsg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        exitMsg.buttonClicked.connect(self.close)"""
    
    

def main():
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())    


if __name__ == '__main__':
    main()