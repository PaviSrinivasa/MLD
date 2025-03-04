from django.conf.urls import include
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('whisper/', views.whisper, name='whisper'),
]