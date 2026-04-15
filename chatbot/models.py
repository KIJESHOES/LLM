from django.db import models
from django.contrib.auth.models import User
class LogAkurasi(models.Model):
    pertanyaan = models.TextField()
    jawaban_ai = models.TextField()
    skor_akurasi = models.FloatField() # Nilai 0.0 - 1.0
    waktu_simpan = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pertanyaan[:30]} - {self.skor_akurasi}"

class K3Chat(models.Model):
    pertanyaan = models.TextField()
    jawaban = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    from django.db import models
import uuid

# Tabel untuk nyimpen "Room" atau Sesi Chat (yang muncul di Sidebar)
class ChatSession(models.Model):
    # --- TAMBAHKAN BARIS INI ---
    # null=True biar data history lama (yang belum ada user-nya) nggak bikin error database
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    
    judul = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.judul

# Tabel untuk nyimpen riwayat chat (User nanya apa, AI jawab apa)
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=10) # isinya nanti 'user' atau 'ai'
    content = models.TextField() # Isi teks chat-nya
    waktu_proses = models.FloatField(default=0.0)
    skor_akurasi = models.FloatField(null=True, blank=True) # Cuma diisi kalau role == 'ai'
    created_at = models.DateTimeField(auto_now_add=True)
    sumber_file = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"[{self.role}] {self.content[:50]}..."