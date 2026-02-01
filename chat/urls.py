# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('conversation/<int:conversation_id>/', views.get_messages, name='get_messages'),
    path('send/', views.send_message, name='send_message'),
]
