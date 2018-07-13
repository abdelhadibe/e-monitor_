import paho.mqtt as mqtt 
import json 

class MQTTclient(object):
	_mqttClient = None
	_unitId = None
	_topic =[]

	def onConnect(self, client,userdata ,rc):
		if rc==0: 
			print("Connected as"+self._unitId+"\n");
			for pTopic in self._topic:
				client.subscribe(pTopic);
	
	def onDisconnect(self,client, userdata, rc):
		if rc!=0 : 
			print("Unexpected disconnection from broker \n"); 
			client.reconnect();
		else: 
			print("Deconnnection from broker\n");

	
	def onMessage(self, unitid,client, userdata, msg):
		print("Message :"+msg.topic+ " : "+str(msg.payload)+ "\n");

	def __init__(self, client, mqtt_conf, topic):
		#ID
		self._unitId = unitid ;
		
		#subscribing To topics 
		for pTopic in topic:
			self._topic.append(pTopic);

		# init mqtt client 
		self._mqttClient = mqtt.Client(self._unitId);

		# Callback Init 
		self._mqttClient.on_message = self.onMessage ; 
		self._mqttClient.on_disconnect = self.onDisconnect ; 
		self._mqttClient.on_message = self.onMessage ; 

		# Connexion
		self._mqttClient.Connect(mqtt_conf['host'],mqtt_conf['port'],mqtt_conf['keepalive']);

	def subscribe(self,topic):
		for p in topic : 
			self._mqttClient.subscribe(p);


	def unsubscribe(self,topic):
		for p in topic : 
			self._mqttClient.unsubscribe(p);
	
	def disconnect(self):
		self._mqttClient.disconnect()

	def publish(self, topic, data):
		self._mqttClient.publish(topic,data)

	def loop(self, time):
		self._mqttClient.loop(time) ;

	def loopStart(self):
		self._mqttClient.loop_start();

	def loopStop(self):
		self._mqttClient.loop_stop();

	def loopForever(self):
		self._mqttClient.loop_forever();


	
