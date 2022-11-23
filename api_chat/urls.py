from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from knox import views as knox_views
from .views import *
app_name = 'api_chat'

urlpatterns = [

    re_path(r'^validate_phone/', ValidatePhoneSendOTP.as_view()),
    #re_path('^validate_otp/', ValidateOTP.as_view()),
    #re_path('^register/', Register.as_view()),
    #re_path("^login/$",LoginAPI.as_view()),
    #re_path("^logout/$",knox_views.LogoutView.as_view()),

    re_path(r'^admin/', admin.site.urls),

    ##por si arroja error
    #re_path(r'^api/', include('api_chat.urls', namespace='api_chat')),
    re_path(r'^api/', include(("api_chat.urls", 'api_chat'), namespace="api_chat")),

    #re_path(r'^assess/', include('check.urls', namespace='check')),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset', ),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done', ),
    path('accounts/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm', ),
    path('accounts/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete', ),


]

if settings.DEBUG:
    urlpatterns = urlpatterns + \
                  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + \
                  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)