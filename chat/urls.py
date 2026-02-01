# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('conversation/<int:conversation_id>/', views.get_messages, name='get_messages'),
    path('send/', views.send_message, name='send_message'),
    path('open/<int:booking_id>/', views.open_chat_for_booking, name='open_chat_for_booking'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('conversations/', views.get_conversations, name='conversations'),
]
