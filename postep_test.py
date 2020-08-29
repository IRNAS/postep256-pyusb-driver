import os
#os.environ['PYUSB_DEBUG'] = 'debug' # uncomment for verbose pyusb output
import sys
import platform
import usb.core
import usb.backend.libusb1
import time

VENDOR_ID = 0x1dc3
PRODUCT_ID = 0x0641
OUT_ENPOINT = 0x01
IN_ENPOINT = 0x81

def write_to_postep(dev):

    data_list = [0] * 64
    #for run/sleep send data[1] = 0xA1
    #data_list[0] = 0x01
    data_list[1] = 0x90

    data = bytearray(data_list)
    print("Writing command: {}".format(bytes(data).hex()))

    num_bytes_written = 0
    try:
        num_bytes_written = dev.write(OUT_ENPOINT, data,500)
    except usb.core.USBError as e:
        print (e.args)

    return num_bytes_written

def read_from_postep(dev, timeout):
    try:
        data = dev.read(IN_ENPOINT, 64, timeout)
    except usb.core.USBError as e:
        print ("Error reading response: {}".format(e.args))
        return None
    if len(data) == 0:
        return None

    return data


was_kernel_driver_active = False
device = None

if platform.system() == 'Windows':
    # required for Windows only
    # libusb DLLs from: https://sourcefore.net/projects/libusb/
    arch = platform.architecture()
    if arch[0] == '32bit':
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb/x86/libusb-1.0.dll") # 32-bit DLL, select the appropriate one based on your Python installation
    elif arch[0] == '64bit':
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb/x64/libusb-1.0.dll") # 64-bit DLL

    device = usb.core.find(backend=backend, idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
elif platform.system() == 'Linux':
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

    # if the OS kernel already claimed the device
    if device.is_kernel_driver_active(0) is True:
        # tell the kernel to detach
        device.detach_kernel_driver(0)
        was_kernel_driver_active = True
else:
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if device is None:
    raise ValueError('ADU Device not found. Please ensure it is connected to the tablet.')
    sys.exit(1)

device.reset()

# Set the active configuration. With no arguments, the first configuration will be the active one
device.set_configuration()

# Claim interface 0
usb.util.claim_interface(device, 0)

# Write
bytes_written=write_to_postep(device)
print("bytes_written: {}".format(bytes_written))

# Read
data = read_from_postep(device, 500) # read from device with a 200 millisecond timeout
if data != None:
    print("Received string: {}".format(bytes(data).hex()))

usb.util.release_interface(device, 0)

# This applies to Linux only - reattach the kernel driver if we previously detached it
if was_kernel_driver_active == True:
    device.attach_kernel_driver(0)