"""
import pyudev
context = pyudev.Context()
#monitor = Monitor.from_netlink()
monitor = pyudev.Monitor.from_netlink(context)
# For USB devices
monitor.filter_by(subsystem='usb')
# OR specifically for most USB serial devices
monitor.filter_by(subsystem='tty')
for action, device in monitor:
    vendor_id = device.get('ID_VENDOR_ID')
    # I know the devices I am looking for have a vendor ID of '22fa'
    print 'Detected {} for device with vendor ID {}'.format(action, vendor_id)
"""

#!/usr/bin/python
import sys

import usb.core
# find USB devices
def detect():
	dev = usb.core.find(find_all=True)
	# loop through devices, printing vendor and product ids in decimal and hex
	for cfg in dev:
	  #sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
	  #sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')
	  if cfg.idVendor == 6790 :
	  	print cfg.idVendor ; 
	  	return True ; 
	return False ; 
a = detect();
print a ; 