import time 
import threading
import paho.mqtt.client as mqtt 
import json 

domoticzIn  = "domoticz/in"
domoticzOut = "domoticz/out"

mode_topic  = "/e-monitor/mode/" ; 




prise_on  = {"command": "switchlight", "idx": 35, "switchcmd": "On" }
prise_off = {"command": "switchlight", "idx": 35, "switchcmd": "Off" }



jsPrise_1_on  = json.dumps(prise_on)
jsPrise_1_off = json.dumps(prise_off)

class mqtt_domoticz(object):
	_mqttc = None ; 
	_tThread = None;

	def publishToDomotiz(self,topic,data):
		client.publish(topic,data)

	def on_message(self,client, userdata, msg):
		try :
			print("Message recieved "); 
			print("New message on " + msg.topic + " : " + str(msg.payload) + "\n");
			payload = json.loads(msg.payload.decode('utf-8'))
		except Exception as ex: 
			print ("Error");
		else : 
			if(payload['idx']== 34) : 
				jsframe = dict() ; 
				if(payload['nvalue']== 1):
					jsframe['mode'] = "auto" ; 
					self._mqttc.publish(mode_topic,json.dumps(jsframe,ensure_ascii=False)); 
					self._mqttc.publish(domoticzIn,jsPrise_1_on);
					print ("On cmd") ; 
				else : 
					jsframe['mode'] = "manual" ; 
					self._mqttc.publish(mode_topic,json.dumps(jsframe,ensure_ascii=False)); 
					self._mqttc.publish(domoticzIn,jsPrise_1_off);
					print ("Off cmd") ; 


	def __init__(self):
	
		self._mqttc= mqtt.Client() ; 
		self._mqttc.on_message = self.on_message ; 
		self._mqttc.connect("localhost",1883,60); 
		self._mqttc.subscribe(domoticzOut) ; 
		

	def runMqqt_domoritcz(self):
		self._tThread = threading.Thread(target = self.transfering) ; 
		self._tThread.daemon= True ; 
		self._tThread.start() ; 
		self._mqttc.loop_start() ; 

	def transfering(self): 
		print("message Transfering....") ; 
		
		


def main(): 

	mqtt_transfert = mqtt_domoticz() ; 
	mqtt_transfert.runMqqt_domoritcz() ; 

	while True : 
		pass ;
     

if __name__ == '__main__':
    main(); 
 


