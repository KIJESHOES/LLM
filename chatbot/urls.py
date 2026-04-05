from django.urls import path
from . import views

urlpatterns = [
    # Ganti views.chat_view jadi views.halaman_utama
    path('', views.halaman_utama, name='halaman_utama'),
    
    # API buat ngirim pesan
    path('api/chat/', views.api_chat, name='api_chat'),
    
    # API buat narik riwayat chat
    path('api/history/<str:session_id>/', views.get_history, name='get_history'),
    
    # Tambahin baris ini di dalem list urlpatterns lu ya:
    path('api/hapus/<str:session_id>/', views.hapus_sesi, name='hapus_sesi'),
]