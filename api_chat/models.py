from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_staff=False, is_active=True, is_admin=False):
        if not phone:
            raise ValueError('users must have a phone number')
        if not password:
            raise ValueError('user must have a password')

        user_obj = self.model(
            phone=phone
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,

        )
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,
            is_admin=True,

        )
        return user


class User(AbstractBaseUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    id = models.AutoField(primary_key=True)
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    standard = models.CharField(max_length=3, blank=True, null=True)
    score = models.IntegerField(default=16)
    first_login = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self):
        return self.phone

    def get_short_name(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self) -> str:
        return str(self.phone)


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    user_desde = models.ForeignKey(to=User, null=True, blank=False, on_delete=models.SET_NULL,
                                   related_name="user_desde")
    user_hasta = models.ForeignKey(to=User, null=True, blank=False, on_delete=models.SET_NULL,
                                   related_name="user_hasta")
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True)
    aceptado = models.BooleanField(max_length=250, blank=False, null=True, default=False)

    class Meta:
        verbose_name = 'chat'
        verbose_name_plural = 'chats'

    def __str__(self) -> str:
        return str(self.id)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    address = models.CharField(max_length=900, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    first_count = models.IntegerField(default=0,
                                      help_text='It is 0, if the user is totally new and 1 if the user has saved his standard once')

    def __str__(self):
        return str(self.user)


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


post_save.connect(user_created_receiver, sender=User)


class PhoneOTP(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    otp = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Number of otp sent')
    logged = models.BooleanField(default=False, help_text='If otp verification got successful')
    forgot = models.BooleanField(default=False, help_text='only true for forgot password')
    forgot_logged = models.BooleanField(default=False, help_text='Only true if validdate otp forgot get successful')

    def __str__(self):
        return str(self.phone) + ' is sent ' + str(self.otp)
