import logging
import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel,
                             QMessageBox, QPushButton, QVBoxLayout)

from util import PCL_EXP_PATH, PLOT_NUM_DEFAULT_TEXT, DEFAULT_FONT
from .virtual_keyboard import ClickableLineEdit, VirtualKeyboard

log = logging.getLogger("new_experiment_dialog")

class NewExperimentPage(QDialog):
    """Pop up dialog to setup a new experiment

    Args:
        QDialog (QDialog): Base class of dialog windows.
    """

    expirementCreated = pyqtSignal(str)
    changePlotNumber = pyqtSignal(int)

    def __init__(self):
        """Initalize required layout variables and add widgets."""
        super(NewExperimentPage, self).__init__()
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
        self.plotNumberLineEdit.setPlaceholderText("Enter Start Plot Number Here")

        self.keyboard = VirtualKeyboard()

        self.newFileLineEdit.clicked.connect(self.keyboard.setLineEdit)
        self.newFileLineEdit.setToolTip(
            "Setting a file name with an existing folder with the same filename will cause an error"
        )

        self.plotNumberLineEdit.clicked.connect(self.keyboard.setLineEdit)
        self.plotNumberLineEdit.setToolTip(
            "Leaving this blank will set the plot number to 1"
        )

        newFileLineEdit_label = QLabel("Experiment Name")
        plotNumberLineEdit_label = QLabel("Plot Number")
        newFileLineEdit_label.setFont(DEFAULT_FONT)
        plotNumberLineEdit_label.setFont(DEFAULT_FONT)

        self.lineedit_layout.addWidget(self.newFileLineEdit, 0, 0)
        self.lineedit_layout.addWidget(self.plotNumberLineEdit, 0, 1)
        self.lineedit_layout.addWidget(newFileLineEdit_label, 1, 0)
        self.lineedit_layout.addWidget(plotNumberLineEdit_label, 1, 1)

        self.keyboard_layout.addWidget(self.keyboard, 0, 0)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.create_experiment)
        self.saveButton.setFont(DEFAULT_FONT)
        
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        self.cancelButton.setFont(DEFAULT_FONT)
        
        self.keyboard_layout.addWidget(self.saveButton, 1, 0)
        self.keyboard_layout.addWidget(self.cancelButton, 1, 1)

        self.lineedit_group_box.setLayout(self.lineedit_layout)
        self.keyboard_group_box.setLayout(self.keyboard_layout)

    def create_experiment(self):
        """
        Sets up a new experiment based off the user's input.
        Creates all of the RGB, Depth, and Metadata directories using filename and sets the plot number.
        """
        # validate experiment name ?
        experiment_name = self.newFileLineEdit.text()

        # validate plot number
        plot_number = 1 # default
        plot_number_str = self.plotNumberLineEdit.text()
        if plot_number_str.isnumeric():
            plot_number = int(plot_number_str)
        elif plot_number_str not in ["", PLOT_NUM_DEFAULT_TEXT]:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setStandardButtons(QMessageBox.Ok)
            error_msg.setText(
                "Uh oh, there are no numbers in the plot number field. Please enter a number or leave it blank to set to default"
            )
            error_msg.exec()
            return

        # try to make the new path
        new_exp_path = os.path.join(PCL_EXP_PATH, experiment_name)
        try:
            os.mkdir(new_exp_path)
        except OSError:
            log.info("Creation of the directory %s failed" % new_exp_path)
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            error_msg.setText(
                "Uh oh, an error occured. \n Double check that there is not an existing experiment under this name"
            )
            error_msg.exec()

        else:
            # create the child directories
            os.mkdir(os.path.join(new_exp_path, "RGB"))
            os.mkdir(os.path.join(new_exp_path, "Depth"))
            os.mkdir(os.path.join(new_exp_path, "Metadata"))

            # success message
            success_msg = QMessageBox()
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setStandardButtons(QMessageBox.Ok)
            success_msg.setText("Creation of directory successful")
            success_msg.setDetailedText(
                "Directory can be found at this file path: \n" + new_exp_path
            )
            response = success_msg.exec()
            log.info("Created experiment directory %s" % new_exp_path)

            if response == QMessageBox.Ok:
                # let the main gui know of the update
                self.changePlotNumber.emit(plot_number)
                self.expirementCreated.emit(experiment_name)

                self.close()
