import time
import logging
import threading
import sys
from postep256usb import PoStep256USB

def wait_for_position():
    
    while True:
        data = postep.read_stream()
        #print("Received: {}".format(data))
        if data["pos"] == data["final"]:
            print("Reached: {}".format(data["final"]))
            break
        time.sleep(0.1)

# Discover devices if multiple are connected
devices = PoStep256USB.discover_devices()
print(f"Discovered devices: {devices}")
# Here the user should specify which serial number to use
# postep = PoStep256USB(logging.INFO, "1700C01A-AECAA109-56CFA5BE-F5001980")

postep = PoStep256USB(logging.INFO)
# defined to show only errors as log values, set to logging.INFO or logging.DEBUG for more

# Check if driver was detected and configuration could be established
if postep.device is None:
    print("Driver not found, exiting.")
    sys.exit(0)

# postep.get_device_info()
postep.read_configuration()

postep.change_configuration()

postep.read_configuration()
# time.sleep(1)
# print(f"Setting pwm")
# postep.set_pwm(100, 100, 0, 0)
# enable streaming of real-time data
# postep.enable_rt_stream()
# set the motor to run or sleep
# postep.run_sleep(True)

# # Example 1: Run motor with fixed speed
# postep.move_speed(100, "cw")
# time.sleep(20)

# # Example 2: Use motor position control

# # # First reset the position to known value (do not do this if you wish the motor to retain position during program restart). Power cycle resets this also.
# # postep.move_reset_to_zero()
# # #configure speed acceleration and deceleration and endswitch for move commands
# # postep.move_config(10000,1000,1000,None)

# # Assuming there is a finite motion range defined, the end of range must be found first and configured to zero
# # Move slowly for fixed time to reach the end of range.
# postep.move_speed(100, "acw")
# time.sleep(20)

# # # Now define this as zero position
# # postep.move_reset_to_zero()

# # # Move to a fixed position and wait
# # postep.move_to(10)
# # wait_for_position()

# # postep.move_to(100)
# # wait_for_position()

# # postep.move_to(1000)
# # wait_for_position()

# # postep.move_to(0)
# # wait_for_position()
# # #postep.move_speed(100,"acw")


# # while True:
# #     data = postep.read_stream()
# #     if data != None:
# #         print("Received: {}".format(data))
# #     time.sleep(1)