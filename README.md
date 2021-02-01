# PlotCamLite
- Set up Debian OS (formerly known as Raspbian OS)
  1. Install Raspberry Pi Imager on whatever PC you are working on
  2. Connect micro-SD card of at least 8GB to the computer which you’re working on. 
  3. Open up the imager and choose the “Raspberry Pi OS” for OS, the micro SD card for the SD card and press Write
  4. Move card from PC to RPI
  5. Connect RPI to monitor, mouse, keyboard, and power
  6. Follow the set up instructions and set a user name, password, etc.




- Install VSCode
  1. Go to https://code.visualstudio.com/Download 
  2. choose the “ARM” option from the .deb installation menu


- Install PIP
  1. sudo apt update, sudo apt install python3-pip
- Install PyQt5
  1. sudo apt-get && install python3-pyqt5 && sudo apt-get install pyqt5-dev-tools && sudo apt-get install qttools5-dev-tools
- Install Pyrealsense
  1. Follow the instructions mentioned here :: https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md
    - Note: in Add Swap: change sudo vim to sudo nano, rest of command stays the same.
    - For the “protobuf” subsection, the installation instructions didn’t work too well so I referred to the instructions in the ReadMe: https://github.com/protocolbuffers/protobuf/blob/master/src/README.md . The make commands will take a long amount of time.

  
  
- Install OpenCV
  1. sudo apt update && sudo apt upgrade && sudo apt install python3-opencv
  
- Install Phidget Library
  1. pip install phidget22
  
- Install Pillow
  1. pip install pillow

- Install Git
  1. sudo apt-get install Git

- Clone Project

