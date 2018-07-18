import json
import time 
import paho.mqtt.client as mqtt 


domoticzIn  = "domoticz/in"
domoticzOut = "domoticz/out"



def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def publishToDomotiz(topic,data):
	client.publish(topic,data)

	
client = mqtt.Client()
client.connect("localhost",1883,60)
client.on_message = on_message 
client.loop() 

prise_on  = {"command": "switchlight", "idx": 45, "switchcmd": "On" }
prise_off = {"command": "switchlight", "idx": 45, "switchcmd": "Off" }






"""
temp_max_today    = { "idx" : 12, "nvalue" : 0, "svalue" :"1"} 
temp_min_today    = { "idx" : 13, "nvalue" : 0, "svalue" :"1"}
temp_max_tomorrow = { "idx" : 14, "nvalue" : 0, "svalue" :"1"}
temp_min_tomorrow = { "idx" : 15, "nvalue" : 0, "svalue" :"1"} """
jsPrise_1_on  = json.dumps(prise_on)
jsPrise_1_off = json.dumps(prise_off)

while True : 
	publishToDomotiz(domoticzIn,jsPrise_1_on) ; 
	print("On");
	time.sleep(2.0) ; 
	publishToDomotiz(domoticzIn,jsPrise_1_off) ; 
	time.sleep(2.0) ;
	print("Off");
