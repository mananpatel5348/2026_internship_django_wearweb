from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/',views.usersignupview,name='signup'),
    path('login/',views.userloginview,name='login')  
]