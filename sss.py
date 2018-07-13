import threading 
import json 
import time 
import paho.mqtt.client as mqtt 
from mqtt_client import MQTTclient


host = "localhost"
port =  1883 

weather_topic = "/e-monitor/ext/today" 

left_margin = time.asctime( time.localtime(time.time()) )+" : "
right_margin = "\n--------------------------"

class MQTT_Client(object) :
    _mqttClient = None;
    _unitID = None;
    _topic = [];


    #
    # ---Callbacks--- #    
    
    # callback lors de la reussite de connexion au broker
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(left_margin+"Connected To MQTT Broker"+right_margin);

           

    #
    # callback lors de la deconnexion
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            # Deconnexion inatendue
            print(left_margin+"Unexpected disconnection from broker"+right_margin);
            client.reconnect();            
        else:        
            print("Deconnection from broker\n");5

    #
    # callback lorsqu un nouveau message survient sur un des topics subscribe
    def on_message(self, client, userdata, msg):
        print("New message on " + msg.topic + " : " + str(msg.payload) + "\n");
    
    #
    # ---Fonctions--- #
    #

    #
    # fonction d init de la classe

    def onMsg_weather(self, client, userdata, msg):

        try: 
            payload =json.loads(msg.payload.decode('utf-8'))
        except Exception as ex : 
            print(left_margin+"exception decoding json payload : "+ str(ex)+right_margin)
        else: 
            print (left_margin+"On Message weather")
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
            #print self._tomorrowTmp ; 
            print (left_margin+"In On Weather function"+right_margin) ;



    #
    # fonction de subscribe
    def subscribe(self, lTopic):
        self._mqttClient.subscribe(lTopic);

    """def message_callback_add(self,sub, callback) :
        self._mqttClient.message_callback_add(sub,callback) ;"""

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
        self._mqttClient.subscribe = self.subscribe ; 
        #self._mqttClient.message_callback_add = self.message_callback_add ;  

        # connexion
        self._mqttClient.message_callback_add(weather_topic, self.onMsg_weather);
        self._mqttClient.connect("localhost",1883,60);
        self._mqttClient.loop_start() ;
        
        #self._mqttClient.subscribe(weather_topic)

 

class monitoring(MQTT_Client):
    """docstring for monitoring"""
    _auto_mode = False
    _manu_mode = False
    _tThread  = None
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
    """
    def onMsg_weather(self, client, userdata, msg):

        try: 
            payload =json.loads(msg.payload.decode('utf-8'))
        except Exception as ex : 
            print(left_margin+"exception decoding json payload : "+ str(ex)+right_margin)
        else: 
            print (left_margin+"On Message weather")
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
            #print self._tomorrowTmp ; 
            print (left_margin+"In On Weather function"+right_margin) ;
    """

    def OnMsg_counter(self, client, userdata, msg):
        print ("On countter Msg")


    def __init__(self, host, port):
        super(monitoring, self).__init__(host, port)
        self._manu_mode = False ;
        print (left_margin+"Before Calling "+right_margin)
        #self._mqttClient.message_callback_add("/e-monitor/ext/today/", self.onMsg_weather);
        #self._mqttClient.message_callback_add("/e-monitor/ext/today/", self.OnMsg_counter);
        #self._mqttClient.subscribe(weather_topic) ;
        
        print (left_margin+"After Calling "+right_margin)

    def runMonitoring(self):
        print(left_margin+"Energy Monitor starting"+right_margin) ; 
        self._tThread = threading.Thread(target = self.global_monitoring) ; 
        self._tThread.daemon = True ; 
        self._tThread.start() ; 
        self._mqttClient.loop_forever(); 

    def global_monitoring(self):
        print(left_margin+"Monitoring..."+right_margin)
        print(left_margin+"In Global monitoring"+right_margin);
        i = 0 ; 
        while i < 180: 
            print self._current_tmp ;
            #self._mqttClient.subscribe(weather_topic) ;
            #print i ; 
            i = i+ 1 ; 
        
def main(): 
    moni = monitoring(host,port); 
    moni.runMonitoring() ;
    #moni.onMsg_weather(); 

    while True : 
        pass ;
     #   sys.exit(0); 

if __name__ == '__main__':
    print(left_margin+"In main"+right_margin);
    main()
    #sys.exit(0) ;



 
        