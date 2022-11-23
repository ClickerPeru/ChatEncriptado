from django.urls import re_path
from knox import views as knox_views
from api_chat.views import ValidateOTP, Register, LoginAPI, ValidatePhoneSendOTP,CreateChat

urlpatterns = [
    re_path('^validate_send_otp/', ValidatePhoneSendOTP.as_view()),
    re_path('^validate_otp/', ValidateOTP.as_view()),
    re_path('^register/', Register.as_view()),
    re_path("^login/$", LoginAPI.as_view()),
    re_path("^logout/$", knox_views.LogoutView.as_view()),
    re_path("^created_chat/", CreateChat.as_view()),

]