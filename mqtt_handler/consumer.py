from mqttasgi.consumers import MqttConsumer
from mqtt_handler.tasks import processmqttmessage
import json

class MyMqttConsumer(MqttConsumer):

    async def connect(self):
        await self.subscribe('application/+/device/+/event/up', 2)
        await self.channel_layer.group_add("stracontech", self.channel_name)

    async def receive(self, mqtt_message):
        print('Received a message at topic:', mqtt_message['topic'])
        print('With payload', mqtt_message['payload'])
        print('And QOS:', mqtt_message['qos'])
        dictresult = json.loads(mqtt_message['payload'])
        jsonresult = json.dumps(dictresult)
        processmqttmessage.delay(jsonresult, mqtt_message['topic'])
        pass

    async def publish_results(self, event):
        data = event['result']
        await self.publish("stracontech/procesed/"+event['result']['device_id']+"/result", json.dumps(data).encode('utf-8'), qos=2, retain=False)

    async def disconnect(self):
        await self.unsubscribe('application/+/device/+/event/up')
