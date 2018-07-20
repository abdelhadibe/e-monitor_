
import minimalmodbus
import threading 
import json  
import paho.mqtt.client as mqtt
import time 
import datetime  
from config import * 

usb_port = '/dev/ttyUSB0' ; 
host = "localhost" ;
port = 1883 ;

energy_meters_topic = "/e-monitor/energy/";

consumption_meter_id = 1 ; 
production_meter_id = 2; 

def log_time(): 
    dt = datetime.datetime.now() ; 
    log = dt.strftime("%H:%M:%S : ")
    return log ; 


class EnergyMeter(object):
	_mqttc = None ; 
	_tThread = None;
	_consumption_counter = None ; 
	_pv_procduction_counter = None; 
	_voltage_consumption = 0 ; 
	_voltage_production = 0 ; 
	_current_consumption = 0 ; 
	_current_production = 0 ; 
	_active_power_consumption = 0; 
	_active_power_production = 0 ; 
	_total_active_energy_consumption = 0;
	_total_active_energy_production = 0;

 
	def counter_initilisation(self, port, counter_id):
		log = log_time(); 
		counter = minimalmodbus.Instrument(port,counter_id);
		counter.serial.baudrate = 2400
		counter.serial.bytesize = 8
		counter.serial.parity = minimalmodbus.serial.PARITY_NONE
		counter.serial.stopbits = 1
		counter.serial.timeout = 1
		counter.debug = False
		counter.mode = minimalmodbus.MODE_RTU
		print("Waiting for initialisation...\n");
		time.sleep(3);
		print(log+"Counter id = {} initialised \n".format(counter_id));
		return counter ; 

	def publishToDomoticz(self, metering_type, voltage_idx, current_idx, power_idx, energy_idx):

		if(metering_type == "consumption"):
			data_1= json.dumps({ "idx" : voltage_idx, "nvalue" : 0, "svalue" :str(self._voltage_consumption) })
			data_2= json.dumps({ "idx" : current_idx, "nvalue" : 0, "svalue" :str(self._current_consumption )})
			data_3= json.dumps({ "idx" : energy_idx, "nvalue" : 0, "svalue" :str(self._total_active_energy_consumption)})
		
		elif(metering_type == "production"):
			data_1= json.dumps({ "idx" : voltage_idx, "nvalue" : 0, "svalue" :str(self._voltage_production) })
			data_2= json.dumps({ "idx" : current_idx, "nvalue" : 0, "svalue" :str(self._current_production )})
			data_3= json.dumps({ "idx" : energy_idx, "nvalue" : 0, "svalue" :str(self._total_active_energy_production)})
			
		self._mqttc.publish("domoticz/in",data_1)
		self._mqttc.publish("domoticz/in",data_2)
		self._mqttc.publish("domoticz/in",data_3)

	def __init__(self):
		super(EnergyMeter, self).__init__();

		self._consumption_counter = self.counter_initilisation(usb_port, consumption_meter_id);
		self._pv_procduction_counter = self.counter_initilisation(usb_port, production_meter_id);


		self._mqttc = mqtt.Client();
		self._mqttc.connect(host, port, 60);
		self._mqttc.subscribe(energy_meters_topic);

	def readEnergy_values(self):
		#Values adress from datasheet
		# Consumption Values
		self._voltage_consumption = self._consumption_counter.read_float(0, functioncode =4, numberOfRegisters=2);
		self._current_consumption = self._consumption_counter.read_float(6, functioncode =4, numberOfRegisters=2);
		self._active_power_consumption = self._consumption_counter.read_float(12, functioncode =4, numberOfRegisters=2);
		self._total_active_energy_consumption = self._consumption_counter.read_float(344, functioncode =4, numberOfRegisters=2);
		#PV Productionn values
		"""
		self._voltage_production = self._pv_procduction_counter.read_float(0, functioncode =4, numberOfRegisters=2);
		self._consumption_counter = self._pv_procduction_counter.read_float(6, functioncode =4, numberOfRegisters=2);
		self._active_power_production = self._pv_procduction_counter.read_float(12, functioncode =4, numberOfRegisters=2);
		self._total_active_energy_production = self._pv_procduction_counter.read_float(344, functioncode =4, numberOfRegisters=2);
		"""
		
	def runEnergy_meter(self):
		log = log_time();
		print(log+"Energy meter is running\n");
		self._tThread = threading.Thread(target = self.metering_system); 
		self._tThread.daemon = True ; 
		self._tThread.start() ; 
		self._mqttc.loop_start();
	
	def metering_system(self):
		while True :
			self.readEnergy_values();
			self.publishToDomoticz("consumption",30,35,31,32);
			#self.readEnergy_values(self._pv_procduction_counter,self._voltage_production, self._current_production, self._active_power_production, self._total_active_energy_production);
			print self._voltage_consumption ;
			print self._current_consumption ;
			print self._total_active_energy_consumption ; 
			time.sleep(4);

def main():
	met = EnergyMeter();
	met.runEnergy_meter();
	while True: 
		pass ;

if __name__ == '__main__':
	main();


