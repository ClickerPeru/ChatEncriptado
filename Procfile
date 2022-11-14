web: gunicorn iot_stracontech.wsgi
worker: celery -A mqtt_handler worker -l debug