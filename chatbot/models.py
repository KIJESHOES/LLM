from django.db import models

class K3Chat(models.Model):
    pertanyaan = models.TextField()
    jawaban = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)