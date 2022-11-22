from django.db import models

class User(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=20)
    numero_telefono = models.CharField(max_length=20, blank=False, null=None, unique=True)
    nombre = models.CharField(max_length=250, blank=True, null=True)
    apellido = models.CharField(max_length=250, blank=False, null=True)
    correo = models.EmailField(blank=True, null=True)
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True)
    sms_validacion_creacion = models.BooleanField(blank=False, null=False, default=False)
    sms_validacion_lastlogin = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self) -> str:
        return str(self.numero_telefono)

class Chat(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=20)
    user_desde = models.ForeignKey(to=User, null=True, blank=False, on_delete=models.SET_NULL, related_name="user_desde")
    user_hasta = models.ForeignKey(to=User, null=True, blank=False, on_delete=models.SET_NULL, related_name="user_hasta")
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True)
    aceptado = models.CharField(max_length=250, blank=False, null=True)

    class Meta:
        verbose_name = 'chat'
        verbose_name_plural = 'chats'

    def __str__(self) -> str:
        return str(self.id)
