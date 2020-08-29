import usb1

# /lib/udev/rules.d/50-udev-default.rules
# udev rules SUBSYSTEM=="usb", ATTRS{idVendor}=="1DC3", ATTRS{idProduct}=="0641", MODE="0666"

VENDOR_ID = 0x1dc3
PRODUCT_ID = 0x0641
OUT_ENPOINT = "0x01"
IN_ENPOINT = "0x81"

with usb1.USBContext() as context:
    handle = context.openByVendorIDAndProductID(
        VENDOR_ID,
        PRODUCT_ID,
        skip_on_error=True,
    )
    if handle is None:
        # Device not present, or user is not allowed to access device.
        print("Device not present")
        pass
    else:
        if (handle.kernelDriverActive(0)==1):
            print("Kernel driver attached")
            if(handle.detachKernelDriver(0)==0):
                print("Kernel driver detached")
        with handle.claimInterface(0):
            pass
