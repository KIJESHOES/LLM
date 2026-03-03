from django.db import models

from django.db import models

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