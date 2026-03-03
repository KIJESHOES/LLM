from django.shortcuts import render
from django.http import JsonResponse
from .models import LogAkurasi
from .utils import tanya_bot_k3
import json

# Fungsi nampilin halaman HTML sama Data Grafik
def chat_view(request):
    try:
        logs = LogAkurasi.objects.all().order_by('-waktu_simpan')[:10]
        data_grafik = [log.skor_akurasi for log in logs][::-1]
        label_grafik = [f"Uji {i+1}" for i in range(len(logs))]
        total = LogAkurasi.objects.count()
    except Exception:
        # Jaga-jaga error kalo belum migrasi DB
        data_grafik = []
        label_grafik = []
        total = 0

    context = {
        'data_grafik': json.dumps(data_grafik),
        'label_grafik': json.dumps(label_grafik),
        'total_uji': total
    }
    return render(request, 'chat.html', context)


# Fungsi terima pesan dan kirim ke AI
def api_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pesan_user = data.get('pesan', '')

            # Pastikan fungsi tanya_bot_k3 melempar (return) dua nilai ya!
            jawaban_ai, skor_ai = tanya_bot_k3(pesan_user)

            return JsonResponse({
                'jawaban': jawaban_ai,
                'skor': skor_ai
            })
        except Exception as e:
            return JsonResponse({
                'jawaban': f"Waduh error cuy: {str(e)}", 
                'skor': 0
            })
            
    return JsonResponse({'jawaban': "Hanya menerima metode POST.", 'skor': 0})