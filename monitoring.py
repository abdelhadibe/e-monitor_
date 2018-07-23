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
    _waching_machin = None ; 
    _home_heating = None; 
    _pool_heating = None ; 
    _water_heating = None; 
    _waching_machine_planning = False , 
    _home_heating_planning = False ; 
    _water_heating_plannig = False ; 
    _pool_heating_planning = False ; 




    def homeDevice_update(self, device_type, in_planning, start_time, stop_time, priority, power_consumption, achieved):
    	my_device = dict();
    	my_device['type'] = device_type ; 
    	my_device['in_planning'] = in_planning;
    	my_device['start_time'] = start_time; 
    	my_device['stop_time'] = stop_time; 
    	my_device['priority'] = priority ; 
    	my_device['power_consumption'] = power_consumption ; 
    	my_device['achieved'] = achieved ; 

    	return my_device ; 

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
			self._mqttClient.publish(domoticzIn_topic, json_data);
			print(log+data['switchcmd']+"-cmd sended to switch idx:"+str(idx)); 

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
            log = log_time()+" : "
            payload = json.loads(msg.payload.decode('utf-8')) ;
        except Exception as ex : 
            print("error loading json frame"); 
        else:
            log = time.asctime( time.localtime(time.time()) )+" : "
            self._general_consum = payload['gle_consum'] ; 
            self._photoVol_prodution = payload['pv_produc'] ; 

            print ("On countter Msg"); 
    

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
        log = log_time();
        #
        # Mqtt Client
        #
        self._mqttClient = mqtt.Client()
        self._mqttClient.on_connect = self.on_connect ; 
        self._mqttClient.message_callback_add(weather_topic, self.onMsg_weather);
        self._mqttClient.message_callback_add(mode_topic,self.OnMsg_mode) ; 
        self._mqttClient.message_callback_add(swimPool_topic,self.OnMsg_swimPool) ; 
        self._mqttClient.message_callback_add(autoConsommation_scenari_topic,self.OnMsg_autoconsommation) ;
        self._mqttClient.message_callback_add(planning_topic,self.OnMsg_devicePlanning) ;  



        self._mqttClient.connect("localhost", 1883, 60)
        self._mqttClient.subscribe("/e-monitor/#");

        # Home device initialisation 
        self._waching_machin = self.homeDevice_update(12,12,12,12,12,12,12) ;
        self._home_heating = self.homeDevice_update(12,12,12,12,12,12,12);
        self._water_heating = self.homeDevice_update(12,12,12,12,12,12,12) ;
        self._pool_heating = self.homeDevice_update(12,12,12,12,12,12,12);

        #Domoticz Initilisation 
        self.sendSwitch_cmd(auto_mode_idx,"Off");
        self.sendSwitch_cmd(waching_machin_idx,"Off"); 
        self.sendSwitch_cmd(water_heating_idx,"Off");
        self.sendSwitch_cmd(home_heating_idx,"Off");
        self.sendSwitch_cmd(pool_heating_idx,"Off");



    

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
	        	#self.sendSwitch_cmd(waching_machin_idx,"On");
	        	print("On \n");
	        	time.sleep(20);
	        	#self.sendSwitch_cmd(waching_machin_idx,"Off");
	        	print("Off \n");
	        	time.sleep(20);



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



 
        