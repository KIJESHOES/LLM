from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time # Pastikan ini ada
from .models import ChatSession, ChatMessage
from .utils import tanya_bot_k3 

def halaman_utama(request):
    semua_sesi = ChatSession.objects.all().order_by('-updated_at')
    context = {
        'riwayat_sesi': semua_sesi
    }
    return render(request, 'index.html', context)

@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pesan_user = data.get('pesan')
        session_id = data.get('session_id')
        
        # --- 1. MULAI HITUNG WAKTU DI SINI ---
        start_time = time.time()

        # Logika Sesi
        if not session_id:
            judul_baru = pesan_user[:30] + "..." if len(pesan_user) > 30 else pesan_user
            sesi = ChatSession.objects.create(judul=judul_baru)
        else:
            sesi = ChatSession.objects.get(id=session_id)
            sesi.save()

        # Simpan pertanyaan User
        ChatMessage.objects.create(session=sesi, role='user', content=pesan_user)

        # --- 2. PROSES AI ---
        # Fungsi ini yang biasanya lama, makanya kita hitung di sekelilingnya
        jawaban_ai, skor_ai = tanya_bot_k3(pesan_user)

        # --- 3. SELESAI HITUNG WAKTU ---
        end_time = time.time()
        durasi = round(end_time - start_time, 2) # Hasil dalam detik (misal: 1.45)

        # 4. Simpan jawaban AI ke database (PENTING: Pastikan kolom 'waktu_proses' sudah ada di models.py)
        ChatMessage.objects.create(
            session=sesi, 
            role='ai', 
            content=jawaban_ai, 
            waktu_proses=durasi, # Pakai variabel durasi yang baru dihitung
            skor_akurasi=skor_ai
        )

        return JsonResponse({
            'jawaban': jawaban_ai, 
            'skor': skor_ai,
            'session_id': str(sesi.id),
            'judul': sesi.judul,
            'waktu': durasi, # Kirim ke frontend
        })
        
def hapus_sesi(request, session_id):
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            sesi = ChatSession.objects.get(id=session_id)
            sesi.delete()
            return JsonResponse({'status': 'success'})
        except ChatSession.DoesNotExist:
            return JsonResponse({'status': 'error', 'pesan': 'Sesi tidak ditemukan'}, status=404)

def get_history(request, session_id):
    try:
        sesi = ChatSession.objects.get(id=session_id)
        pesan_pesan = sesi.messages.all().order_by('created_at')
        
        data_pesan = []
        for p in pesan_pesan:
            data_pesan.append({
                'role': p.role,
                'content': p.content,
                'skor': p.skor_akurasi,
                'waktu': p.waktu_proses # Sertakan waktu agar muncul saat history diklik
            })
            
        return JsonResponse({'status': 'ok', 'messages': data_pesan})
    except ChatSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sesi tidak ditemukan'})