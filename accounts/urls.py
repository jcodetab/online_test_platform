from django.urls import path
from . import views
from .views import register_view 
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'), 
    path('home/', views.home, name='home'),
    path("profile/", views.profile_view, name="profile"), 
   
]









