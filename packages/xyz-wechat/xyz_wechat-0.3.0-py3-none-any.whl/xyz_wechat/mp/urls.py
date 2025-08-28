from django.urls import re_path
from . import views
from .decorators import weixin_login_required

app_name = "mp"
urlpatterns = [
    re_path(r'^ports/', views.ports),
    re_path(r'^login/$', weixin_login_required(views.LoginView.as_view()), name="login"),
    re_path(r'^jsapi/config/$', weixin_login_required(views.jsapi_config), name="jsapi_config"),
    re_path(r'^qr_login/(?P<task_id>[\w-]+)/$', weixin_login_required(views.QRLoginView.as_view()), name="qr-login"),
    re_path(r'^login_qrcode/', views.LoginQRCodeView.as_view(), name='login-qrcode')
]
