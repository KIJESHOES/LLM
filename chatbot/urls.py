from django.urls import path
from . import views
from .views import analisis_akurasi_view

urlpatterns = [
    # Ganti views.chat_view jadi views.halaman_utama
    path('', views.halaman_utama, name='halaman_utama'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # API buat ngirim pesan
    path('api/chat/', views.api_chat, name='api_chat'),
    
    # API buat narik riwayat chat
    path('api/history/<str:session_id>/', views.get_history, name='get_history'),
    
    # Tambahin baris ini di dalem list urlpatterns lu ya:
    path('api/hapus/<str:session_id>/', views.hapus_sesi, name='hapus_sesi'),
    path('analisis/', analisis_akurasi_view, name='analisis_akurasi'),
]