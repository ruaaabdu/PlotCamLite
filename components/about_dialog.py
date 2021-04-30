"""
This code handles the about dialog
@author Ruaa Abdulmajeed
@date April 30th, 2021
"""
import logging
import os

from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel,
                             QMessageBox, QPushButton, QVBoxLayout)

from util import ABOUT_DIALOG_PATH
log = logging.getLogger("new_experiment_dialog")

class AboutPage(QDialog):
    """Pop up dialog to setup a new experiment

    Args:
        QDialog (QDialog): Base class of dialog windows.
    """

    def __init__(self):
        """Initalize required layout variables and add widgets."""
        super(AboutPage, self).__init__()
        loadUi(ABOUT_DIALOG_PATH, self)