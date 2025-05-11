# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chat'),
    path('novo/', views.limpar_chat_view, name='novo_chat'), 
]