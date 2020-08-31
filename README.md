# postep256-pyusb-driver
Driver for PoLabs PoStep256 written in Python and using PyUSB package. See the `postep_test.py` file for usage example of the library.

This library is under development and implementas basic functions. It assumes the driver is priperly configured though PoStep256 configuration application prior to use.

Features available currently allow for the position control of the attached motor and to set it to operate at constant speed.

## Windows Usage

### Installation
* See [this repo](https://github.com/pyusb/pyusb#installing) for installation of `pyusb`

* download `libusb DLL version 1.0` from the link in the code comment (line 28). You can use [this link](https://www.dll4free.com/libusb-1.0.dll.html) if you happen to run into trouble with the original one.

### Test run
* If the first test run fails in backend recognition, you can replace line 37 in `postep256usb.py` with full path to your DLL 1.0 library.
* Occasionally, `NotImplementedError` is raised. In this case, download and install [Zadig](https://zadig.akeo.ie/) and follow these steps:
  1. Click `Device` > `Create New Device`
  2. select `Options` > `List All Aevices`
  3. select `PoStep60-256` from the list
  5. you will see the existing driver on the left hand side. On the right hand side select `WinUSB` and click `Replace Driver`
 
 The correct `libusb` is now installed to run PoStep60-256.
 
 Re-try running the Python `postep_test.py`.

## Installation Linux
See https://github.com/pyusb/pyusb#installing


