from celery import shared_task
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import datetime

@shared_task
def processmqttmessage(message, topic):
    #from mqtt_handler.models import Personal, DataGeolocalization, Zona, OutputMqtt, Gateway, Dispositivo
    dictionnary = json.loads(message)
    EUI = topic.split("/")[3]
    #asigned_user = Personal.objects.filter(dispositivo__numero_serie=EUI).first()
