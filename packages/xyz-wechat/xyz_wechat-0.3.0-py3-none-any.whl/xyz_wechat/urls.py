from django.urls import path, include
from . import mp
app_name = "wechat"
urlpatterns = [
    path('mp/', include(mp.urls)),
]
