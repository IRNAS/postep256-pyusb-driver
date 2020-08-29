import os
#os.environ['PYUSB_DEBUG'] = 'debug' # uncomment for verbose pyusb output
import sys
import platform
import usb.core
import usb.backend.libusb1
import time
import struct

VENDOR_ID = 0x1dc3
PRODUCT_ID = 0x0641
OUT_ENPOINT = 0x01
IN_ENPOINT = 0x81

def postep_enable_rt_stream(dev):

    data_list = [0] * 64
    # request data streaming
    data_list[1] = 0xA0
    # write to driver
    write_to_postep(dev,data_list)
    # request data
    received = read_from_postep(dev, 500)
    # check if response is valid
    if(received[0]!=0x02):
        return False
    return True

def postep_read_stream(dev):
    received = read_from_postep(dev, 500)
    #parse data
    #postep_stream["endswitch"]=received[6]
    print(struct.unpack('>III', received[20:32]))

def postep_run_sleep(dev,run):

    data_list = [0] * 64
    # request data streaming
    data_list[1] = 0xA1
    if run:
        data_list[20] = 0x01
    # write to driver
    write_to_postep(dev,data_list)
    # request data
    received = read_from_postep(dev, 500)
    # check if response is valid
    if(received[0]!=0x02):
        return False
    return True

def postep_move_speed(dev,speed,direction="cw"):

    data_list = [0] * 64
    # request data streaming
    data_list[1] = 0x90
    #480000 kHz/step_value = speed
    if speed is not 0:
        step_values=480000/speed
    else:
        step_values=480000
    data_list[20:24]=struct.pack('<I', int(step_values))
    if direction == "acw":
        data_list[24]=0x01
    # write to driver
    write_to_postep(dev,data_list)
    # request data
    received = read_from_postep(dev, 500)
    # check if response is valid
    if(received[15]!=0x90):
        return False
    return True

def postep_move_trajectory(dev,final_position,max_speed,max_accel,max_decel,direction,endsw=None):

    data_list = [0] * 64
    data_list[1] = 0xb1
    #enable autorun
    data_list[2]= 0x01<<1
    # Set trajectory final position
    data_list[20:23]=struct.pack('<I', final_position)
    # Set trajectory max speed
    data_list[24:27]=struct.pack('<I', max_speed)
    # Set traject. max acceleration
    data_list[28:31]=struct.pack('<I', max_accel)
    # Set traject. max deceleration
    data_list[32:35]=struct.pack('<I', max_decel)
    # Set InvDir<<2|NCSw<<1| SwEn
    if direction == "acw":
        data_list[36]=0b00000100
    if endsw is not None:
        data_list[36]=data_list[36]|0b00000001
        if endsw == "nc":
            data_list[36]=data_list[36]|0b00000010
    # write to driver
    write_to_postep(dev,data_list)
    # request data
    received = read_from_postep(dev, 500)
    # check if response is valid
    if(received[15]!=0xb1):
        return False
    return True

def postep_stop_trajectory(dev):

    data_list = [0] * 64
    data_list[1] = 0xb2
    
    # write to driver
    write_to_postep(dev,data_list)
    # request data
    received = read_from_postep(dev, 500)
    # check if response is valid
    if(received[0]!=0x02):
        return False
    return True

def postep_zero_trajectory(dev):

    data_list = [0] * 64
    data_list[1] = 0xb3
    
    # write to driver
    write_to_postep(dev,data_list)
    # request data
    received = read_from_postep(dev, 500)
    # check if response is valid
    if(received[0]!=0x02):
        return False
    return True

def postep_system_reset(dev):

    data_list = [0] * 64
    data_list[1] = 0x02
    
    # write to driver
    write_to_postep(dev,data_list)

def write_to_postep(dev,data_list):

    #data_list = [0] * 64
    #for run/sleep send data[1] = 0xA1
    #data_list[0] = 0x01
    #data_list[1] = 0x90

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
    print("Receive command: {}".format(bytes(data).hex()))
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
#bytes_written=write_to_postep(device)
#print("bytes_written: {}".format(bytes_written))

##postep_system_reset(device)
postep_enable_rt_stream(device)
postep_run_sleep(device,True)
#postep_move_speed(device,100,"cw")
#postep_stop_trajectory(device)
#time.sleep(1)
#postep_move_speed(device,0,"acw")
postep_move_trajectory(device,10000,10000,10000,10000,"cw")
while True:
    postep_read_stream(device)
    time.sleep(1)


# Read
data = read_from_postep(device, 500) # read from device with a 200 millisecond timeout
if data != None:
    print("Received string: {}".format(bytes(data).hex()))

usb.util.release_interface(device, 0)

# This applies to Linux only - reattach the kernel driver if we previously detached it
if was_kernel_driver_active == True:
    device.attach_kernel_driver(0)