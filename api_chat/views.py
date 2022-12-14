from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth import login
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from api_chat.utils import otp_generator
from .serializers import (CreateUserSerializer, ChangePasswordSerializer,
                          UserSerializer, LoginUserSerializer, ForgetPasswordSerializer,
                          CreateChatSerializer, ValidateChatSerializer, AuthorizedChatSerializer)
from api_chat.models import User, PhoneOTP, Chat
from django.shortcuts import get_object_or_404
from django.db.models import Q
from twilio.rest import Client
from django.conf import settings
from api_chat.get_token import get_user_from_token
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from knox.settings import knox_settings
from django.utils import timezone
from knox.models import AuthToken
from django.contrib.auth.signals import user_logged_in
from rest_framework.serializers import DateTimeField

class LoginView(APIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated,)

    def get_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_token_ttl(self):
        return knox_settings.TOKEN_TTL

    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def get_user_serializer_class(self):
        return knox_settings.USER_SERIALIZER

    def get_expiry_datetime_format(self):
        return knox_settings.EXPIRY_DATETIME_FORMAT

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def get_post_response_data(self, request, token, instance):
        UserSerializer = self.get_user_serializer_class()
        if UserSerializer is not None:
            data = {
                'expiry': self.format_expiry_datetime(instance.expiry),
                'token': token,
                'user_name': request.user.name
            }
        else:
            data = {
                'expiry': self.format_expiry_datetime(instance.expiry),
                'token': token
            }
        if UserSerializer is not None:
            data["user"] = UserSerializer(
                request.user,
                context=self.get_context()
            ).data
        return data

    def post(self, request, format=None):
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = request.user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(request.user, token_ttl)
        user_logged_in.send(sender=request.user.__class__,
                            request=request, user=request.user)
        data = self.get_post_response_data(request, token, instance)
        return Response(data)

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPI(LoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.last_login is None:
            user.first_login = True
            user.save()

        elif user.first_login:
            user.first_login = False
            user.save()

        login(request, user)
        print(request.user.name)
        return super().post(request, format=None)

@method_decorator(csrf_exempt, name='dispatch')
class UserAPI(generics.RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordAPI(generics.UpdateAPIView):
    """
    Change password endpoint view
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self, queryset=None):
        """
        Returns current logged in user instance
        """
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('password_1')):
                return Response({
                    'status': False,
                    'current_password': 'Does not match with our data',
                }, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get('password_2'))
            self.object.password_changed = True
            self.object.save()
            return Response({
                "status": True,
                "detail": "Password has been successfully changed.",
            })

        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


def send_otp(phone):
    """
    This is an helper function to send otp to session stored phones or
    passed phone number as argument.
    """

    if phone:

        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)

        client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        message = client.messages.create(
            body=f'Buenos dias, tu c??digo de verificaci??n es: ' + str(otp_key) + '.',
            from_='+14254753844',
            to=phone
        )
        print(message)
        return otp_key
    else:
        return False


def send_otp_forgot(phone):
    if phone:
        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)
        user = get_object_or_404(User, phone__iexact=phone)
        if user.name:
            name = user.name
        else:
            name = phone
        client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        message = client.messages.create(
            body=f'Buenos dias: ' + str(name) + ' tu c??digo de verificaci??n es: ' + str(otp_key) + '.',
            from_='+14254753844',
            to=phone
        )

        print(message)

        return otp_key
    else:
        return False


############################################################################################################################################################################################
################################################################################################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class ValidatePhoneSendOTP(APIView):
    '''
    This class view takes phone number and if it doesn't exists already then it sends otp for
    first coming phone numbers'''

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already exists'})
                # logic to send the otp and store the phone number and that otp in table.
            else:
                otp = send_otp(phone)
                print(phone, otp)
                if otp:
                    otp = str(otp)
                    count = 0
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        count = old.first().count
                        old.first().count = count + 1
                        old.first().save()

                    else:
                        count = count + 1

                        PhoneOTP.objects.create(
                            phone=phone,
                            otp=otp,
                            count=count

                        )
                    if count > 7:
                        return Response({
                            'status': False,
                            'detail': 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                        })


                else:
                    return Response({
                        'status': 'False', 'detail': "OTP sending error. Please try after some time."
                    })

                return Response({
                    'status': True, 'detail': 'Otp has been sent successfully.'
                })
        else:
            return Response({
                'status': 'False', 'detail': "I haven't received any phone number. Please do a POST request."
            })

@method_decorator(csrf_exempt, name='dispatch')
class ValidateOTP(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to set the password

    '''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.logged = True
                    old.save()

                    return Response({
                        'status': True,
                        'detail': 'OTP matched, kindly proceed to save password'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP incorrect, please try again'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'Phone not recognised. Kindly request a new otp with this number'
                })


        else:
            return Response({
                'status': 'False',
                'detail': 'Either phone or otp was not recieved in Post request'
            })

@method_decorator(csrf_exempt, name='dispatch')
class Register(APIView):
    '''Takes phone and a password and creates a new user only if otp was verified and phone is new'''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)
        name = request.data.get('name', False)

        if phone and password:
            phone = str(phone)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({'status': False,
                                 'detail': 'Phone Number already have account associated. Kindly try forgot password'})
            else:
                old = PhoneOTP.objects.filter(phone__iexact=phone)
                if old.exists():
                    old = old.first()
                    if old.logged:
                        Temp_data = {'phone': phone, 'password': password}

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        if name and len(name) > 0:
                            user.name = name
                        user = serializer.save()

                        user.name = name
                        user.save()

                        old.delete()
                        return Response({
                            'status': True,
                            'detail': 'Congrats, user has been created successfully.'
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': 'Your otp was not verified earlier. Please go back and verify otp'

                        })
                else:
                    return Response({
                        'status': False,
                        'detail': 'Phone number not recognised. Kindly request a new otp with this number'
                    })





        else:
            return Response({
                'status': 'False',
                'detail': 'Either phone or password was not recieved in Post request'
            })

@method_decorator(csrf_exempt, name='dispatch')
class ValidatePhoneForgot(APIView):
    '''
    Validate if account is there for a given phone number and then send otp for forgot password reset'''

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                otp = send_otp_forgot(phone)
                print(phone, otp)
                if otp:
                    otp = str(otp)
                    count = 0
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old = old.first()
                        k = old.count
                        if k > 10:
                            return Response({
                                'status': False,
                                'detail': 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                            })
                        old.count = k + 1
                        old.save()

                        return Response(
                            {'status': True, 'detail': 'OTP has been sent for password reset. Limits about to reach.'})

                    else:
                        count = count + 1

                        PhoneOTP.objects.create(
                            phone=phone,
                            otp=otp,
                            count=count,
                            forgot=True,

                        )
                        return Response({'status': True, 'detail': 'OTP has been sent for password reset'})

                else:
                    return Response({
                        'status': 'False', 'detail': "OTP sending error. Please try after some time."
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'Phone number not recognised. Kindly try a new account for this number'
                })

@method_decorator(csrf_exempt, name='dispatch')
class ForgotValidateOTP(APIView):
    '''
    If you have received an otp, post a request with phone and that otp and you will be redirected to reset  the forgotted password

    '''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                if old.forgot == False:
                    return Response({
                        'status': False,
                        'detail': 'This phone havenot send valid otp for forgot password. Request a new otp or contact help centre.'
                    })

                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.forgot_logged = True
                    old.save()

                    return Response({
                        'status': True,
                        'detail': 'OTP matched, kindly proceed to create new password'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP incorrect, please try again'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'Phone not recognised. Kindly request a new otp with this number'
                })


        else:
            return Response({
                'status': 'False',
                'detail': 'Either phone or otp was not recieved in Post request'
            })

@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordChange(APIView):
    '''
    if forgot_logged is valid and account exists then only pass otp, phone and password to reset the password. All three should match.APIView
    '''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp = request.data.get("otp", False)
        password = request.data.get('password', False)

        if phone and otp and password:
            old = PhoneOTP.objects.filter(Q(phone__iexact=phone) & Q(otp__iexact=otp))
            if old.exists():
                old = old.first()
                if old.forgot_logged:
                    post_data = {
                        'phone': phone,
                        'password': password
                    }
                    user_obj = get_object_or_404(User, phone__iexact=phone)
                    serializer = ForgetPasswordSerializer(data=post_data)
                    serializer.is_valid(raise_exception=True)
                    if user_obj:
                        user_obj.set_password(serializer.data.get('password'))
                        user_obj.active = True
                        user_obj.save()
                        old.delete()
                        return Response({
                            'status': True,
                            'detail': 'Password changed successfully. Please Login'
                        })

                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP Verification failed. Please try again in previous step'
                    })

            else:
                return Response({
                    'status': False,
                    'detail': 'Phone and otp are not matching or a new phone has entered. Request a new otp in forgot password'
                })




        else:
            return Response({
                'status': False,
                'detail': 'Post request have parameters mising.'
            })

@method_decorator(csrf_exempt, name='dispatch')
class CreateChat(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):

        serializer = CreateChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telefono_hasta = serializer.validated_data['phone_hasta']
        consulta_usuario = User.objects.filter(phone__exact=telefono_hasta)
        peticion = request.headers['Authorization']
        last = peticion.rsplit(' ', 1)[-1]

        user_desde = get_user_from_token(last)
        # print(user_desde)

        if len(consulta_usuario) >= 1:
            user_hasta = consulta_usuario[0]

        else:

            return Response({
                'status': False,
                'detail': '??El numero de telefono del destinatario no existe!'
            })

        new_chat = Chat(user_desde=user_desde, user_hasta=user_hasta)

        new_chat.save()

        return Response({
            'status': True,
            'detail': 'El Chat ha sido creado satisfactoriamente.',
            'id_conversacion': str(new_chat.pk),
            'id_destinatario': str(new_chat.user_hasta.pk),
            'nombre_destinatario': str(new_chat.user_hasta.name)
        })

@method_decorator(csrf_exempt, name='dispatch')
class ValidateChat(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):

        serializer = ValidateChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # valida la estructura
        id_chat = serializer.validated_data['id_chat']
        consulta_chat = Chat.objects.filter(id__exact=id_chat)
        peticion = request.headers['Authorization']
        last = peticion.rsplit(' ', 1)[-1]

        user_hasta = get_user_from_token(last)

        if len(consulta_chat) >= 1:
            chat = consulta_chat[0]


        else:

            return Response({
                'status': False,
                'detail': '??La conversaci??n no existe!'
            })

        if user_hasta == chat.user_hasta:
            return Response({
                'status': True,
                'detail': 'La conversaci??n ha sido verificada con ??xito.'
            })
        else:
            return Response({
                'status': False,
                'detail': 'La conversaci??n no ha sido verificada correctamente.'
            })

@method_decorator(csrf_exempt, name='dispatch')
class AuthorizedChat(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):

        serializer = AuthorizedChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # valida la estructura
        id_chat = serializer.validated_data['id_chat']
        consulta_chat = Chat.objects.filter(id__exact=id_chat)
        peticion = request.headers['Authorization']
        last = peticion.rsplit(' ', 1)[-1]

        user_hasta = get_user_from_token(last)

        if len(consulta_chat) >= 1:
            chat = consulta_chat[0]

        else:

            return Response({
                'status': False,
                'detail': '??La conversaci??n no existe!'
            })

        if user_hasta == chat.user_hasta:
            chat.aceptado = True
            chat.save()
            return Response({
                'status': True,

                'detail': 'La conversaci??n ha sido aceptada.'
            })
        else:

            return Response({
                'status': False,
                'detail': 'La conversaci??n no ha sido aceptada.'
            })

@method_decorator(csrf_exempt, name='dispatch')
class ValidateChatAproved(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):

        serializer = ValidateChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # valida la estructura
        id_chat = serializer.validated_data['id_chat']
        consulta_chat = Chat.objects.filter(id__exact=id_chat)
        peticion = request.headers['Authorization']
        last = peticion.rsplit(' ', 1)[-1]

        user_desde = get_user_from_token(last)

        if len(consulta_chat) >= 1:
            chat = consulta_chat[0]

        else:

            return Response({
                'status': False,
                'detail': '??La conversaci??n no existe!'
            })

        if user_desde == chat.user_desde:

            if chat.aceptado == True:
                return Response({
                    'status': True,
                    'detail': 'La conversaci??n ha sido aceptada por el receptor.'
                })

            else:
                return Response({
                    'status': False,
                    'detail': 'La conversaci??n no ha sido aceptada por el receptor.'
                })

        else:
            return Response({
                'status': False,
                'detail': 'La conversaci??n consultada no le corresponde.'
            })
