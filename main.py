import threading 
import json 
import time 
import paho.mqtt.client as mqtt 
from mqtt_client import MQTTclient


host = 'localhost'
port =  1883 

Wheath_ext_today = "/e-monitor/ext/today/" # max min actual , dt , 
Wheath_ext_tomor = "/e-monitor/ext/tomor/"

class MQTT_Client(object) :
    _mqttClient = None;
    _unitID = None;
    _topic = [];


    #
    # ---Callbacks--- #    
    #

    #
    # callback lors de la reussite de connexion au broker
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected ");

           

    #
    # callback lors de la deconnexion
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            # Deconnexion inatendue
            print("Unexpected disconnection from broker\n");
            client.reconnect();            
        else:        
            print("Deconnection from broker\n");

    #
    # callback lorsqu un nouveau message survient sur un des topics subscribe
    def on_message(self, client, userdata, msg):
        print("New message on " + msg.topic + " : " + str(msg.payload) + "\n");



    #
    # ---Fonctions--- #
    #

    #
    # fonction d init de la classe
    def __init__(self,host,port):
        # ID
        self._unitID = None;

        # Topic
         
                
        # init mqtt client
        self._mqttClient = mqtt.Client();

        # callback init

        self._mqttClient.on_connect = self.on_connect;
        self._mqttClient.on_disconnect = self.on_disconnect;
        self._mqttClient.on_message = self.on_message;

        # connexion
        self._mqttClient.connect(host,port);

    #
    # fonction de subscribe
    def subscribe(self, lTopic):
        for topic in lTopic:
            self._mqttClient.subscribe(topic);

    #
    # fonction d unsubscribe
    def unsubscribe(self, lTopic):
        for topic in lTopic:
            self._mqttClient.unsubscribe(topic);

    #
    # fonction de deconnexion
    def disconnect(self):
        self._mqttClient.disconnect();

    #
    # fonction d envoie
    def publishData(self, topic, data):
        self._mqttClient.publish(topic, data);

    #
    # fonction loop
    def loop(self, time):
        self._mqttClient.loop(time);

    #
    # fonction loop start
    def loopStart(self):
        self._mqttClient.loop_start();

    #
    # fonction loop stop
    def loopStop(self):
        self._mqttClient.loop_stop();

    #
    # fonction loop forever
    def loopForever(self):
        self._mqttClient.loop_forever();

class monitoring(MQTT_Client):
	_auto_mode = False
	_manu_mode = False
	_tThread  = None
	_current_tmp = 0 ; 
	_todayTmp_max = 0;
	_todayTmp_min =0 ; 
	_current_hum = 0 ; 
	_current_cloud = 0; 
	_current_weather = "" ; 
	_tomorrowTmp = 0 ; 
	_tomorrowTmp_max = 0 ; 
	_tomorrowTmp_min = 0 ; 
	_tomorrow_hum = 0 ; 
	_tomorrow_weather = "" ; 
	_tomorrow_cloud = 0 ; 
	_swimPool_tmp = 0 ; 
	_general_consum = 0 ; 
	_photoVol_prodution = 0; 
	_stopCond = None  ;

    def __init__(self,host,port):

        self._manu_mode = False ;
        self._stopCond = threading.Condition() ; 


    def onMsg_weather(self,client,msg):
		try: 
			payload =json.loads(msg.payload.decode('utf-8'))
		except Exception as ex : 
			print("exception decoding json payload : "+ str(ex))
		else: 
			self._current_tmp    = payload['today']['tmp'];
			self._todayTmp_max   = payload['today']['tmp_max']
			self._todayTmp_min   = payload['today']['tmp_min']
			self._current_cloud  = payload['today']['cloud'];
			self._current_weather= payload['today']['weather']
			self._tomorrowTmp    = payload['tomorrow']['tmp'];
			self._tomorrowTmp_max= payload['tomorrow']['tmp_max']
			self._tomorrowTmp_min= payload['tomorrow']['tmp_min']
			self._tomorrow_hum   = payload['tomorrow']['hum'];
			self._tomorrow_cloud = payload['tomorrow']['cloud'];
			self._current_weather= payload['tomorrow']['weather'];
    def imer():




	def runMonitoring(self):
		print("Energy Monitor starting \n") ; 
        self._tThread = threading.Thread(target = self.onMsg_weather(self)) ; 
        self._tThread.daemon = True ; 
        self._tThread.start() ; 
        self.loopForever(); 
    _photoVol_prodution1 = 0;

def main(): 

    moni = monitoring(host,port); 
    moni.runMonitoring() ;
    #moni.onMsg_weather(); 

    while True : 
        pass ;
     #   sys.exit(0); 

if __name__ == '__main__':
    print("SSSS")
    main()
    #sys.exit(0) ;
    


