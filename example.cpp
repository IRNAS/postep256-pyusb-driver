// This file contains the 'main' function. Program execution begins and ends there.//

#include <iostream>
#include <libusb.h>


#define VID 0x0641
#define PID 0x1DC3
#define OUT_ENPOINT 0x01
#define IN_ENPOINT 0x81

using namespace std;

int main() {
	libusb_device** devs;				//pointer to pointer of device, used to retrieve a list of devices
	libusb_device_handle* dev_handle;	//a device handle
	libusb_context* ctx = NULL;			//a libusb session
	int r;								//for return values
	ssize_t cnt;						//holding number of devices in list
	r = libusb_init(&ctx);				//initialize the library for the session we just declared
	if (r < 0) {
		cout << "Init Error " << r << endl;			//there was an error
		return 1;
	}
	libusb_set_debug(ctx, 3);			//set verbosity level to 3, as suggested in the documentation

	cnt = libusb_get_device_list(ctx, &devs);		//get the list of devices
	if (cnt < 0) {
		cout << "Get Device Error" << endl;		
		return 1;
	}
	cout << cnt << " Devices in list." << endl;

	dev_handle = libusb_open_device_with_vid_pid(ctx, PID, VID);	// vendorID and productID I found for my usb device
	if (dev_handle == NULL)
		cout << "Cannot open device" << endl;
	else
		cout << "Device Opened" << endl;
	libusb_free_device_list(devs, 1);								// free the list, unref the devices in it

	unsigned char* data = new unsigned char[64];					//data to write
	/*Select command data */

	//data[0] = 0x00; data[1] = 0xA0; data[20] = 0x00; data[63] = 0x00;		// Command Enable RTS
	data[0] = 0x00; data[1] = 0xA1; data[20] = 0x00; data[63] = 0x00;		// Command RUN/SLEEP
	//data[0] = 0x00; data[1] = 0x90; data[20] = 0x10; data[21] = 0x01; data[22] = 0x00; data[23] = 0x00; data[24] = 0x01; data[63] = 0x00;			//  Command STEP/DIR  
	//data[0] = 0x00; data[1] = 0x90; data[20] = 0x10; data[21] = 0x01; data[22] = 0x00; data[23] = 0x00; data[24] = 0x00; data[63] = 0x00;			//  Command STEP/DIR  change direction
	//data[0] = 0x00; data[1] = 0x02; data[20] = 0x01; data[63] = 0x00;		//  Command SYSRST
	
	int actual;								//used to find out how many bytes were written

	if (libusb_kernel_driver_active(dev_handle, 0) == 1) {		//find out if kernel driver is attached
		cout << "Kernel Driver Active" << endl;
		if (libusb_detach_kernel_driver(dev_handle, 0) == 0)	//detach it
			cout << "Kernel Driver Detached!" << endl;
	}
	r = libusb_claim_interface(dev_handle, 0);					//claim interface 0 (the first) of device (mine had jsut 1)
	if (r < 0) {
		cout << "Cannot Claim Interface" << endl;
		return 1;
	}
	cout << "Claimed Interface" << endl;

	
	/* Write to device */
	cout << "Writing Command OUT_DATA[1]: ";
	printf("%X", data[1]);
	cout << endl;

	r = libusb_bulk_transfer(dev_handle, OUT_ENPOINT, data, 65, &actual, 0);  
    
	if (r == 0 && actual == 65)//we wrote the 65 bytes successfully
		cout << "Writing Successful!" << endl;
	else
		cout << "Write Error" << endl;

	
	/* Read from device */
	cout << "Reading Data..." << endl;
	int i = 0;
	r = libusb_interrupt_transfer(dev_handle, IN_ENPOINT, data, 64, &actual, 500);  
	if (r == 0 && actual == 64)						//we read the 64 bytes successfully
	{
		cout << "Reading Successful!" << endl;
		while (i < 64)
		{
			cout <<"IN_DATA[" << i << "]: ";
			printf("%d", data[i]);
			cout<< endl;
			i++;
		}
	}
	else
		cout << "Read Error" << endl;


	r = libusb_release_interface(dev_handle, 0);	//release the claimed interface
	if (r != 0) {
		cout << "Cannot Release Interface" << endl;
		return 1;
	}
	cout << "Released Interface" << endl;

	libusb_close(dev_handle);						//close the device we opened
	libusb_exit(ctx);								//needs to be called to end the

	delete[] data;									//delete the allocated memory for data
	return 0;
}





//https://developer-archive.leapmotion.com/documentation/cpp/devguide/Project_Setup.html  how to set library
//https://www.dreamincode.net/forums/topic/148707-introduction-to-using-libusb-10/        libusb-1.0 example code