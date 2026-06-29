from django.urls import path
from . import views



urlpatterns = [
    path('messages/', views.message_list, name='message_list'),  
    path('create/', views.create_message, name='create_message'),
    path('test_results/', views.test_results, name='test_results'),

]
