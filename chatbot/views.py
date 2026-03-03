from django.shortcuts import render
from django.http import JsonResponse
import json
from .utils import tanya_bot_k3

# Fungsi 1: Nampilin halaman web UI-nya
def halaman_chat(request):
    return render(request, 'chat.html')

# Fungsi 2: Nerima pesan dari pengunjung dan ngirim ke AI
def api_chat(request):
    if request.method == "POST":
        try:
            # Ambil pesan dari web
            data = json.loads(request.body)
            pesan_user = data.get('pesan', '')

            # Panggil bot sakti kita!
            jawaban_ai = tanya_bot_k3(pesan_user)

            # Kirim balik ke web
            return JsonResponse({'jawaban': jawaban_ai})
        except Exception as e:
            return JsonResponse({'jawaban': f"Waduh error cuy: {str(e)}"})
    
    return JsonResponse({'jawaban': "Hanya menerima metode POST."})