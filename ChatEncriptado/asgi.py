"""
ASGI config for ChatEncriptado project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter
from mqtt_handler.consumer import MyMqttConsumer
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'integrator_mqtt.settings')

django.setup()

application = ProtocolTypeRouter({
        'http': get_asgi_application(),
        'mqtt': MyMqttConsumer.as_asgi(),
    })
