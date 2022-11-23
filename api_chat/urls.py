from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from knox import views as knox_views
from api_chat.views import ValidateOTP, Register, LoginAPI

urlpatterns = [

    re_path('^validate_otp/', ValidateOTP.as_view()),
    re_path('^register/', Register.as_view()),
    re_path("^login/$",LoginAPI.as_view()),
    re_path("^logout/$",knox_views.LogoutView.as_view()),


]