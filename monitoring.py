import threading 
import json 
import time 
import signal 
import sys 
import datetime 
import paho.mqtt.client as mqtt 
from mqtt_client import MQTTclient
from config import * 


host = "localhost"
port =  1883 

domoticzIn_topic = "domoticz/in";
weather_topic = "/e-monitor/ext/today/" ;
forecast_scenari_topic = "/e-monitor/scenario/forecast/" ;
autoConsommation_scenari_topic = "/e-monitor/scenario/autoconsommation/";
planning_topic = "/e-monitor/planning/";
mode_topic  = "/e-monitor/mode/" ;
consumption_topic = "/e-monitor/consumption/"; 
swimPool_topic= "/e-monitor/swimpool/tmp/"

prise_on  = {"command": "switchlight", "idx": 45, "switchcmd": "On" }
prise_off = {"command": "switchlight", "idx": 45, "switchcmd": "Off" }

jsPrise_1_on  = json.dumps(prise_on)
jsPrise_1_off = json.dumps(prise_off)

cmd_on  = json.dumps({"cmd":"on"});
cmd_off = json.dumps({"cmd":"off"});

#Switch Idx 
autoMode_idx = 34 ;
plug_1 = 41;  



#log = time.asctime( time.localtime(time.time()) )+" : "
right_margin = "\n--------------------------"

def log_time(): 
    dt = datetime.datetime.now() ; 
    log = dt.strftime("%H:%M:%S : ")
    return log ; 


class Monitoring(object):
    """docstring for monitoring"""
    _shutdown = None ; 
    _mqttClient = None ; 
    _auto_mode = False ;  
    _manu_mode = False ;
    _tThread  = None ; 
    _scheduler = None ; 
    _current_tmp = 0 ; 
    _todayTmp_max = 0;
    _todayTmp_min =0 ; 
    _current_hum = 0 ; 
    _current_cloud = 0; 
    _current_weather = "" ; 
    _tomorrowTmp = 50 ; 
    _tomorrowTmp_max = 0 ; 
    _tomorrowTmp_min = 0 ; 
    _tomorrow_hum = 0 ; 
    _tomorrow_weather = "" ; 
    _tomorrow_cloud = 0 ; 
    _swimPool_tmp = 0 ; 
    _general_consum = 0 ; 
    _photoVol_prodution = 0; 
    _stopCond = None  ;
    ## Scenarios 
    _autoConsommation_scenari = False ; 
    _weatherForcast_scenari = False ;
    _waching_machin = 0 ; 
    _home_heating = 0; 
    _pool_heating = 0 ; 
    _water_heating = 0; 
    _waching_machine_planning = False , 
    _home_heating_planning = False ; 
    _water_heating_plannig = False ; 
    _pool_heating_planning = False ; 
    _devices_planner = 0; 
    _consumed_power = 0 ;
    _remaining_power = 0 ; 
    _device_state = ""; 

 

    def update_remaining_time(self, planner):
        for k,d in planner.items(): 
            if(d['in_planning'] == "True"):
                if(d['is_running'] == "True"):
                    d['stop_time'] = datetime.datetime.now() ; 
                    d['elapsed_time'] = self.get_elapsed_time(d['start_time'], d['stop_time']) ; 

    def device_control(self, planner):
    	device = dict() ;
        for k,d in  planner.items():
            if (d['elapsed_time'] >= d['time_to_run'] ):
                device_name = d['name'] ; 
                if(d['is_running'] == "True"):
	                d['is_running'] = "False"
	                d['stop_time'] = datetime.datetime.now() ; 
	                self.sendSwitch_cmd(switch_device_idx[device_name], "Off") ;
	                self._consumed_power = self._consumed_power - d['power_demande'] ; 


    def homeDevice_update(self, device_name, in_planning, start_time, time_to_run, priority, power_demande):
    	my_device = dict();
    	my_device['name'] = device_name ; 
    	my_device['in_planning'] = in_planning;
    	my_device['is_running'] = "False"
    	my_device['start_time'] = start_time; 
    	my_device['stop_time'] = ""; 
    	my_device['elapsed_time'] = "" ; 
    	my_device['time_to_run'] = time_to_run ;
    	my_device['priority'] = priority ; 
    	my_device['power_consumption'] = "" ; 
    	my_device['energy_consumption'] = 0; 
    	my_device['energy_consumption_threshold'] = 15 ; 
    	my_device['power_demande'] = power_demande  ;
    	my_device['achieved'] = ""; 

    	return my_device ; 

    def device_search(self, planner) : 
    	d = dict () ; 
    	for k,device in planner.items() : 
    		if(device['in_planning'] == "True") :
    			if(device['is_running'] == "False") :
	    			if( device['power_demande'] < self._remaining_power) : 
	    				device['start_time'] = datetime.datetime.now() ;
	    				d = device ; 
	    				return d; 
    		else:
    			d = {}  ;
    			return 0 ;   

    def get_elapsed_time(self,start, stop):

    	start_in_minute =  (start.hour)*60 + (start.minute) + (start.second)/60 ;
    	stop_in_minute =  (stop.hour)*60 + (stop.minute) + (stop.second)/60 ;
    	elapsed = stop_in_minute - start_in_minute ; 

    	return elapsed ; 

    def OnMsg_devicePlanning(self, client, userdata, msg):
    	try: 
    		log = log_time(); 
    		payload = json.loads(msg.payload.decode('utf-8'));
    	except Exception as ex:
    		print(log+"Error decoding json payload on OnMsg_devicePlanning: "+ str(ex)+right_margin);
    	else: 
    		self._waching_machine_planning = payload['waching_machin'] ;
    		self._home_heating_planning = payload['home_heating']; 
    		self._water_heating_plannig = payload['water_heating']; 
    		self._pool_heating_planning = payload['pool_heating']; 


    		self._waching_machin['in_planning'] = self._waching_machine_planning ; 
    		self._home_heating['in_planning'] = self._home_heating_planning ; 
    		self._water_heating['in_planning'] = self._water_heating_plannig ; 
    		self._pool_heating['in_planning'] = self._pool_heating_planning ; 

    		print "Waching_machin : {} \n".format(self._waching_machin['in_planning']) 
    		print "Home_heating : {} \n".format(self._home_heating['in_planning'])
    		print "Water_heating : {} \n".format(self._water_heating['in_planning'])
    		print "Pool_heating : {} \n".format(self._pool_heating['in_planning'])

    		self._devices_planner['waching_machin'] = self._waching_machin ; 
    		self._devices_planner['home_heating'] = self._home_heating ; 
    		self._devices_planner['water_heating'] = self._water_heating ; 
    		self._devices_planner['pool_heating'] = self._pool_heating ; 


    		print("-----------------------\n")


    def OnMsg_autoconsommation(self, client, userdata, msg):
    	try: 
    		log = log_time(); 
    		payload = json.loads(msg.payload.decode('utf-8'));
    	except Exception as ex:
    		print(log+"Error decoding json payload on OnMsg_autoconsommation: "+ str(ex)+right_margin);
    	else: 
    		if(payload['autoconsommation'] == "On"):
    			self._autoConsommation_scenari = True;
    			print(log+"OnMsg autoconsommation : autoconsommation scenari enabled \n");
    		elif(payload['autoconsommation'] == "Off"):
    			self._autoConsommation_scenari = False ;
    			print(log+"OnMsg autoconsommation : autoconsommation scenari disabled \n");

    def OnMsg_weatherforecast(self, client, userdata, msg):
    	try: 
    		log = log_time(); 
    		payload = json.loads(msg.payload.decode('utf-8'));
    	except Exception as ex:
    		print(log+"exception decoding json payload on OnMsg_autoconsommation: "+ str(ex)+right_margin);
    	else: 
    		if(payload['autoconsommation'] == "On"):
    			self._autoConsommation_scenari = True;
    			print(log+"OnMsg autoconsommation : autoconsommation scenari enabled \n");
    		elif(payload['autoconsommation'] == "Off"):
    			self._autoConsommation_scenari = False ;
    			print(log+"OnMsg autoconsommation : autoconsommation scenari disabled \n");

    def sendSwitch_cmd(self, idx, cmd):
		try:
			log = log_time();
			data = dict();
			data['command'] = "switchlight";
			data['idx'] = idx;
			data['switchcmd'] = cmd;
			json_data = json.dumps(data);
		except Exception as ex : 
			print("error to switch cmd "); 
		else :
			device_name = "" ;
			for k,v in switch_device_idx.items():
				if v == idx :
					device_name = k ; 

			self._mqttClient.publish(domoticzIn_topic, json_data);
			print(log+data['switchcmd']+"-cmd sended to switch: "+device_name+str(idx)); 

    def OnMsg_mode(self, client, userdata, msg):
        try:
            log = log_time() ;
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception as ex:
            print(log+"exception decoding json payload : "+ str(ex)+right_margin)
        else:
            if (payload['mode'] == "auto"): 
                self._auto_mode = True ;
                self._manu_mode = False ;    
                print(log+"On message - mode : Automatic mode activated = " + str(self._auto_mode)+right_margin) ; 
            elif (payload['mode'] == "manual"):
                self._manu_mode = True ;
                self._auto_mode = False ;
                print(log+"On message - mode : Manual mode activated = "+ str(self._manu_mode)+right_margin) ; 


    def OnMsg_scheduling(self, client, userdata, msg):
    	try : 
    		log = log_time() ; 
    	except Exception as ex : 
    		print(log+"Error loading json payload : "+ str(ex)+right_margin ); 
    	else: 
    		pass ; 


    def on_message(self, client, userdata, msg):
        print("New message on " + msg.topic + " : " + str(msg.payload) + "\n");

    def on_connect(self, client,userdata ,flags, rc):
		if rc==0: 
			log = log_time();
			print(log+"Connected to broker"+right_margin);


    def OnMsg_consumption(self, client, userdata, msg):
        try:
            log = log_time()
            payload = json.loads(msg.payload.decode('utf-8')) ;
        except Exception as ex : 
            print(log+"error loading json frame in OnMsg_comsumption\n"); 
        else:
            self._general_consum = payload['gle_consum'] ; 
            self._photoVol_prodution = payload['pv_produc'] ; 

            print (log+"OnMsg consumption\n"); 
    

    def OnMsg_swimPool(self, client, userdata, msg):
        try : 
            log = log_time();
            payload =json.loads(msg.payload.decode('utf-8'))

        except Exception as ex : 
            print(log+"error loading json frame On swimPool msg"); 
        else :
            self._swimPool_tmp = payload['tmp'];
            print(log+"On message - swimPool : Temperature = "+str(self._swimPool_tmp)+right_margin) ; 

        


    def onMsg_weather(self, client, userdata, msg):
        log = log_time();
        try: 
            
            payload =json.loads(msg.payload.decode('utf-8'))
        except Exception as ex : 
            print(log+"exception decoding json payload : "+ str(ex)+right_margin)
        else: 
            print (log+"On Message weather .....")
            self._current_tmp    = payload['today']['tmp'];
            self._todayTmp_max   = payload['today']['tmp_max']
            self._todayTmp_min   = payload['today']['tmp_min']
            self._current_cloud  = payload['today']['cloud'];
            self._current_weather= payload['today']['weather']
            self._tomorrowTmp    = payload['tomorr']['tmp'];
            self._tomorrTmp_max  = payload['tomorr']['tmp_max']
            self._tomorrTmp_min  = payload['tomorr']['tmp_min']
            self._tomorr_hum     = payload['tomorr']['hum'];
            self._tomorr_cloud   = payload['tomorr']['cloud'];
            self._current_weather= payload['tomorr']['weather'];
            #print self._tomorrowTmp ; 
            #print (log+"In On Weather function"+right_margin) ;

	def onMsg_auto(self, client, userdata, msg):
	        log = log_time();
	        try: 
	            
	            payload =json.loads(msg.payload.decode('utf-8'))
	        except Exception as ex : 
	            print(log+"exception decoding json payload : "+ str(ex)+right_margin)
	        else: 
	            print (log+"On Message weather .....")
	            self._current_tmp    = payload['today']['tmp'];
	            self._todayTmp_max   = payload['today']['tmp_max']
	            self._todayTmp_min   = payload['today']['tmp_min']
	            self._current_cloud  = payload['today']['cloud'];
	            self._current_weather= payload['today']['weather']
	            self._tomorrowTmp    = payload['tomorr']['tmp'];
	            self._tomorrTmp_max  = payload['tomorr']['tmp_max']
	            self._tomorrTmp_min  = payload['tomorr']['tmp_min']
	            self._tomorr_hum     = payload['tomorr']['hum'];
	            self._tomorr_cloud   = payload['tomorr']['cloud'];
	            self._current_weather= payload['tomorr']['weather'];

    def __init__(self):

        super(Monitoring, self).__init__()
        self._shutdown = False ; 
        self._manu_mode = False ;
        self._auto_mode = False ; 
        self._devices_planner = dict() ;
        self._device_state = dict() ;  
        self._consumed_power = 0 ; 
        log = log_time();
        
        # Mqtt Client
        
        self._mqttClient = mqtt.Client()
        self._mqttClient.on_connect = self.on_connect ; 
        self._mqttClient.message_callback_add(weather_topic, self.onMsg_weather);
        self._mqttClient.message_callback_add(mode_topic, self.OnMsg_mode) ; 
        self._mqttClient.message_callback_add(swimPool_topic,self.OnMsg_swimPool) ; 
        self._mqttClient.message_callback_add(consumption_topic, self.OnMsg_consumption);
        self._mqttClient.message_callback_add(autoConsommation_scenari_topic,self.OnMsg_autoconsommation) ;
        self._mqttClient.message_callback_add(planning_topic,self.OnMsg_devicePlanning) ;  



        self._mqttClient.connect("localhost", 1883, 60)
        self._mqttClient.subscribe("/e-monitor/#");

        # Home device initialisation 
        self._waching_machin = self.homeDevice_update("waching_machin","False","",2,1,2000);
        self._home_heating = self.homeDevice_update("home_heating","False","",1,1,200);
        self._water_heating = self.homeDevice_update("water_heating","False","",3,1,1500);
        self._pool_heating = self.homeDevice_update("pool_heating","False","",5,1,1000);

        # Planner Initialisation ; 
        self._devices_planner['waching_machin'] = self._waching_machin ; 
        self._devices_planner['home_heating'] = self._home_heating ; 
        self._devices_planner['water_heating'] = self._water_heating; 
        self._devices_planner['pool_heating'] = self._pool_heating ; 

        #Domoticz Initilisation 
        self.sendSwitch_cmd(auto_mode_idx,"Off");
        self.sendSwitch_cmd(waching_machin_idx,"Off"); 
        self.sendSwitch_cmd(water_heating_idx,"Off");
        self.sendSwitch_cmd(home_heating_idx,"Off");
        self.sendSwitch_cmd(pool_heating_idx,"Off");

        #Device State ; 
        self._device_state['waching_machin'] = "Off"; 
        self._device_state['water_heating'] = "Off"; 
        self._device_state['home_heating'] = "Off"; 
        self._device_state['pool_heating'] = "Off";



    

    def runMonitoring(self):
    	log = log_time() ; 
        print(log+"Energy Monitor starting"+right_margin) ; 
        self._tThread = threading.Thread(target = self.global_monitoring) ; 
        self._tThread.daemon = True ; 
        self._tThread.start() ; 
        self._mqttClient.loop_start();

    def stopMonitoring(self):
    	self._shutdown = True ; 

    def disconnect_Monitoring(self):
    	log = log_time();
    	self._mqttClient.loop_stop();
    	self._mqttClient.disconnect();
    	print(log+"Disconnection from MQTT \n"); 


    def global_monitoring(self):
    	log = log_time();
    	print(log+"Monitoring..."+right_margin);

    	while not self._shutdown:
	        # test mode 
	        if (self._auto_mode == True ) : 
	        	if(self._photoVol_prodution > pv_production_threshold_1 ):
					
					self._remaining_power = self._photoVol_prodution - self._consumed_power ; 
					if(self._remaining_power > 0 ):
						device = self.device_search(self._devices_planner);
						if(device != 0 ):
							device['start_time'] = datetime.datetime.now() ;
							device['is_running'] = "True" ; 
							device_name = device['name']; 
							self._consumed_power = self._consumed_power + device['power_demande'];
							self.sendSwitch_cmd(switch_device_idx[device_name], "On") ; 

					self.update_remaining_time(self._devices_planner);
					self.device_control(self._devices_planner) ; 
	        		


def cntrl_handler(signum, frame):
	global shutdown ;
	global energy_monitoring ;
	log = log_time() ; 

	print(log+"<CTRL+C> cmd detected \n");
	print(log+"energy monitoring [Shutdown]\n");
	energy_monitoring.stopMonitoring();
	energy_monitoring.disconnect_Monitoring();
	
	shutdown = True ; 

def main(): 
	global shutdown;
	global energy_monitoring ;

	log = log_time() ; 
	print(log+"In main"+right_margin);
	
	shutdown = False ;
	signal.signal(signal.SIGINT, cntrl_handler);
	energy_monitoring = Monitoring();
	energy_monitoring.runMonitoring();

	while not shutdown: 
		pass ;
	sys.exit(0); 

if __name__ == '__main__':
    main() ;
    sys.exit(0) ;



 
        