from django.urls import path, include
from .views import *

urlpatterns = [
    path('sendEmail', fnSendEmail, name="automail"),
    path('', fnIndex, name="index")

]
