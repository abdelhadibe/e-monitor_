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

domoticzIn_topic = "domoticz/in"
weather_topic = "/e-monitor/ext/today/" ; 
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



left_margin = time.asctime( time.localtime(time.time()) )+" : "
right_margin = "\n--------------------------"

def log_time(): 
    dt = datetime.datetime.now() ; 
    log = dt.strftime("%H:%M:%S : ")
    return log ; 


class monitoring(object):
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

    	
    def sendSwitch_cmd(self, idx, cmd):
		try: 
			left_margin = log_time();
			data = dict();
			data['command'] = "switchlight"; 
			data['idx'] = idx ; 
			data['switchcmd'] = cmd; 
			json_data = json.dumps(data);
			#print json_data ;
		except Exception as ex : 
			print("error to switch cmd "); 
		else :
			self._mqttClient.publish(domoticzIn_topic, json_data);
			print(left_margin+data['switchcmd']+"-cmd sended to switch idx:"+str(idx)); 

    def OnMsg_mode(self, client, userdata, msg):
        try:
            left_margin = log_time()
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception as ex:
            print(left_margin+"exception decoding json payload : "+ str(ex)+right_margin)
        else:
            if (payload['mode'] == "auto"): 
                self._auto_mode = True ;
                self._manu_mode = False ;    
                print(left_margin+"On message - mode : Automatic mode activated = " + str(self._auto_mode)+right_margin) ; 
            elif (payload['mode'] == "manual"):
                self._manu_mode = True ;
                self._auto_mode = False ;
                print(left_margin+"On message - mode : Manual mode activated = "+ str(self._manu_mode)+right_margin) ; 

    def OnMsg_scheduling(self, client, userdata, msg):
    	try : 
    		left_margin = log_time() ; 
    	except Exception as ex : 
    		print(left_margin+"Error loading json payload : "+ str(ex)+right_margin ); 
    	else: 
    		pass ; 


    def on_message(self, client, userdata, msg):
        print("New message on " + msg.topic + " : " + str(msg.payload) + "\n");

    def on_connect(self, client,userdata ,flags, rc):
		if rc==0: 
			left_margin = time.asctime( time.localtime(time.time()) )+" : "
			print(left_margin+"Connected to broker"+right_margin);


    def OnMsg_consumption(self, client, userdata, msg):
        try:
            left_margin = time.asctime( time.localtime(time.time()) )+" : "
            payload = json.loads(msg.payload.decode('utf-8')) ;
        except Exception as ex : 
            print("error loading json frame"); 
        else:
            left_margin = time.asctime( time.localtime(time.time()) )+" : "
            self._general_consum = payload['gle_consum'] ; 
            self._photoVol_prodution = payload['pv_produc'] ; 

            print ("On countter Msg"); 
    

    def OnMsg_swimPool(self, client, userdata, msg):
        try : 
            left_margin = log_time();
            payload =json.loads(msg.payload.decode('utf-8'))

        except Exception as ex : 
            print(left_margin+"error loading json frame On swimPool msg"); 
        else :
            self._swimPool_tmp = payload['tmp'];
            print(left_margin+"On message - swimPool : Temperature = "+str(self._swimPool_tmp)+right_margin) ; 

        


    def onMsg_weather(self, client, userdata, msg):
        left_margin = log_time();
        try: 
            
            payload =json.loads(msg.payload.decode('utf-8'))
        except Exception as ex : 
            print(left_margin+"exception decoding json payload : "+ str(ex)+right_margin)
        else: 
            print (left_margin+"On Message weather .....")
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
            #print (left_margin+"In On Weather function"+right_margin) ;




    def __init__(self):

        super(monitoring, self).__init__()
        self._manu_mode = False ;
        self._auto_mode = False
        left_margin = time.asctime( time.localtime(time.time()) )+" : "
        # Mqtt Client
        #
        self._mqttClient = mqtt.Client()
        self._mqttClient.on_connect = self.on_connect ; 
        self._mqttClient.message_callback_add(weather_topic, self.onMsg_weather);
        self._mqttClient.message_callback_add(mode_topic,self.OnMsg_mode) ; 
        self._mqttClient.message_callback_add(swimPool_topic,self.OnMsg_swimPool) ; 

        self._mqttClient.connect("localhost", 1883, 60)
        self._mqttClient.subscribe("/e-monitor/#");

    def runMonitoring(self):
        print(left_margin+"Energy Monitor starting"+right_margin) ; 
        self._tThread = threading.Thread(target = self.global_monitoring) ; 
        self._tThread.daemon = True ; 
        self._tThread.start() ; 
        self._mqttClient.loop_start();

    def stopMonitoring(self):
    	self._shutdown = True ; 

    def global_monitoring(self):
        print(left_margin+"Monitoring..."+right_margin)
        
        
        while True : 
     
	        # test mode 
	        if (self._auto_mode == True ) : 
	        	self.sendSwitch_cmd(1,"On");
	        	time.sleep(20);
	        	self.sendSwitch_cmd(1,"Off");
	        	time.sleep(20);

def main(): 
	global shutdown;
	global energy_monitoring ; 

	energy_monitoring = monitoring();
	energy_monitoring.runMonitoring();
	
	while True: 
		pass ;
     #   sys.exit(0); 

if __name__ == '__main__':
    print(left_margin+"In main"+right_margin);
    main()
    #sys.exit(0) ;



 
        