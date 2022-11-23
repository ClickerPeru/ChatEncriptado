from django.urls import re_path
from knox import views as knox_views
from api_chat.views import ValidateOTP, Register, LoginAPI, CreateChat, ValidateChat, \
    ForgotValidateOTP, ValidatePhoneForgot, ChangePasswordAPI, ForgetPasswordChange, ValidatePhoneSendOTP, \
    AuthorizedChat

urlpatterns = [
    re_path('^validate_send_otp/', ValidatePhoneSendOTP.as_view()),
    re_path('^validate_otp/', ValidateOTP.as_view()),
    re_path('^register/', Register.as_view()),
    re_path("^login/$", LoginAPI.as_view()),
    re_path("^logout/$", knox_views.LogoutView.as_view()),
    re_path("^created_chat/", CreateChat.as_view()),
    re_path("^validated_chat/", ValidateChat.as_view()),
    re_path("^validate_phone_forgot/", ValidatePhoneForgot.as_view()),
    re_path("^change_psw_api/", ChangePasswordAPI.as_view()),
    re_path("^forget_psw_change/", ForgetPasswordChange.as_view()),
    re_path("^forgot_validate_otp/", ForgotValidateOTP.as_view()),
    re_path("^validate_phone_send_otp/", ValidatePhoneSendOTP.as_view()),
    re_path("^authorized_chat/", AuthorizedChat.as_view()),

]
