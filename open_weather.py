
import json 
import urllib
import paho.mqtt.client as mqtt 
import time 
import threading
#myAPPID = da4129fd505da7e78ad1da77ef375160

#url = 'api.openweathermap.org/data/2.5/forecast?id=524901&APPID=da4129fd505da7e78ad1da77ef375160'
url = 'http://api.openweathermap.org/data/2.5/forecast?q=toulouse,fr&APPID=da4129fd505da7e78ad1da77ef375160&units=metric&lang=fr'
#url = 'api.penweathermap.org/data/2.5/forecast?zip=31400,fr'

Wheath_ext_today = "/e-monitor/ext/today/" # max min actual , dt , 
Wheath_ext_tomor = "/e-monitor/ext/tomor/" 

#create Mqtt client 

client = mqtt.Client()
client.connect("localhost",1883,60)
 

def getForcast(url):
	
	while True : 
		# request server 
		responce = urllib.urlopen(url)
		data = json.loads(responce.read())	

		#Date recupration
	    #actul weather 
		city = data['city']['name']
		tmp = data['list'][0]['main']['temp'] 
		tmp_max = data['list'][0]['main']['temp_max'] 
		tmp_min = data['list'][0]['main']['temp_min'] 
		humidity = data['list'][0]['main']['humidity'] 
		weather = data['list'][0]['weather'][0]['description']
		clouds = data['list'][0]['clouds']['all']
		date = data['list'][0]['dt_txt']
		dt = data['list'][0]['dt']
		dt= time.ctime(dt)

		## Day +1 forecast	
	 
		tmp_1 = data['list'][1]['main']['temp'] 
		tmp_max_1 = data['list'][1]['main']['temp_max'] 
		tmp_min_1 = data['list'][1]['main']['temp_min'] 
		humidity_1 = data['list'][1]['main']['humidity'] 
		weather_1 = data['list'][1]['weather'][0]['description']
		clouds_1 = data['list'][1]['clouds']['all']
		date_1 = data['list'][1]['dt_txt']
		dt_1 = data['list'][1]['dt']
		dt_1= time.ctime(dt_1)

		#publish Data To Broker 

		todaysForcast = {"today":{"date":dt, "tmp":tmp, "hum":humidity, "tmp_max": tmp_max, "tmp_min":tmp_min,"weather":weather ,"cloud":clouds},
		"tomorr":{"date":dt_1, "tmp":tmp_1, "hum":humidity_1, "tmp_max": tmp_max_1, "tmp_min":tmp_min_1,"weather":weather_1 ,"cloud":clouds_1}}

		jsToday =json.dumps(todaysForcast);
		#jsTomor =json.dumps(tomorrForcast);

		client.publish(Wheath_ext_today,jsToday);
		#client.publish(Wheath_ext_tomor,jsTomor);



		print ("Ville :"+city)
		print("Tmp actuele : {} degre".format(tmp))
		print("Tmp Max : {} degre".format(tmp_max))
		print("Tmp Min : {} degre".format(tmp_min))
		print("humidite: {} %".format(humidity))
		print("Heure de previstion : {} ".format(date))
		print("Type de journee : "+weather)
		print("Clouds : {} %".format(clouds))
		print("Heure fin de previstion : {} ".format(dt))

		print "\n ----- day +1 ------- \n"

		 
		print("Tmp : {} degre".format(tmp_1))
		print("Tmp Max : {} degre".format(tmp_max_1))
		print("Tmp Min : {} degre".format(tmp_min_1))
		print("humidite: {} %".format(humidity_1))
		print("Heure de previstion : {} ".format(date_1))
		print("Type de journee : "+weather_1)
		print("Clouds : {} %".format(clouds_1))
		print("Heure fin de previstion : {} \n".format(dt_1))
		time.sleep(2) ; 


def startForcast(url): 
	th= threading.Thread(target=getForcast(url))
	th.daemon=True;
	th.start() ; 
	client.loop_start() ;

def main():
	
	startForcast(url);
	while True:
		pass;
if __name__ == '__main__':
	main()
	exit(0);





"""
domoticz_topic = "domoticz/in"

def humidityStatus(value):
	if value <= 25 :
		return "0"
	elif value > 25 and value <=50 : 
		return "1"
	elif value > 50 and value <= 75:
		return "2"
	else: 
		return "3"

def publishToDomotiz(topic,data):
	client = mqtt.Client()
	client.connect("localhost",1883,60)
	client.publish(topic,data)
	client.disconnect()

tmp_today        	= { "idx" : 25, "nvalue" : 0, "svalue" :str(tmp) }
tmp_max_today    	= { "idx" : 12, "nvalue" : 0, "svalue" :str(tmp_max)}
tmp_min_today    	= { "idx" : 13, "nvalue" : 0, "svalue" :str(tmp_min) }
tmp_max_tomorrow    = { "idx" : 14, "nvalue" : 0, "svalue" :str(tmp_max_1) }
tmp_min_tomorrow    = { "idx" : 15, "nvalue" : 0, "svalue" :str(tmp_min_1) }
humidity_today      = { "idx" : 23, "nvalue" : humidity,   "svalue" : humidityStatus(humidity) }
humidity_tomorrow   = { "idx" : 24, "nvalue" : humidity_1, "svalue" : humidityStatus(humidity_1) }
DHT				 	= { "idx" : 16, "nvalue" : 100, "svalue" : "3"}
tmp_hum_today       = { "idx" : 26, "nvalue" : 0, "svalue" :str(tmp)+";"+str(humidity)+";"+humidityStatus(humidity)}
cloudsDz			= { "idx" : 33, "nvalue" : 0, "svalue" :weather + " : " +str(clouds)+"%" }

data_out_0 = json.dumps(tmp_today)
data_out_1 = json.dumps(tmp_max_today)
data_out_2 = json.dumps(tmp_min_today)
data_out_3 = json.dumps(tmp_max_tomorrow)
data_out_4 = json.dumps(tmp_min_tomorrow)
data_out_5 = json.dumps(humidity_today)
data_out_6 = json.dumps(humidity_tomorrow)
data_out_7 = json.dumps(DHT)
data_out_8 = json.dumps(tmp_hum_today)
data_out_9 = json.dumps(cloudsDz)


publishToDomotiz(domoticz_topic,data_out_0)
publishToDomotiz(domoticz_topic,data_out_1)
publishToDomotiz(domoticz_topic,data_out_2)
publishToDomotiz(domoticz_topic,data_out_3)
publishToDomotiz(domoticz_topic,data_out_4)
publishToDomotiz(domoticz_topic,data_out_5)
publishToDomotiz(domoticz_topic,data_out_6)
publishToDomotiz(domoticz_topic,data_out_7)
publishToDomotiz(domoticz_topic,data_out_8)
publishToDomotiz(domoticz_topic,data_out_9)
"""