"""ChatEncriptado URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

admin.site.site_header = "Encripted Chat Stracontech"
admin.site.site_title = "Encripted Chat Stracontech"
admin.site.index_title = "Bienvenido a la Plataforma de administración del Chat Encriptado de Stracontech"

urlpatterns = [

    re_path(r'^api/', include('api_chat.urls')),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset', ),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done', ),
    path('accounts/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm', ),
    path('accounts/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete', ),

    path('', admin.site.urls)
]

if settings.DEBUG:
    urlpatterns = urlpatterns + \
                  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + \
                  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
