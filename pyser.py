import serial.tools.list_ports;
def find_usb_port():
	try :
		rs =  serial.tools.list_ports.comports()
		for dev in rs:
			if ( dev.vid == 6790 and dev.pid == 29987):
				return dev.device; 
		return "none" ; 
	except Exception as ex :
		print("error to open usb device : "+str(ex));

print find_usb_port();