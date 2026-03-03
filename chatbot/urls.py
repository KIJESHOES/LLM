from django.urls import path
from . import views

urlpatterns = [
    # Manggil fungsi chat_view dari views.py buat nampilin web
    path('', views.chat_view, name='chat_view'), 
    
    # Endpoint API buat chat RAG-nya
    path('api/chat/', views.api_chat, name='api_chat'),
]