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
        try:
            data = json.loads(request.body)
            pesan_user = data.get('pesan')
            session_id = data.get('session_id')
            
            # --- BARU: TANGKAP PANJANG JAWABAN ---
            # Default ke 'sedang' kalau misal dari frontend kosong
            panjang_jawaban = data.get('panjang_jawaban', 'sedang') 
            
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
            # Sekarang variabel panjang_jawaban udah terdefinisi
            jawaban_ai, skor_ai, sumber_file, halaman = tanya_bot_k3(pesan_user, panjang_jawaban)

            # --- 3. SELESAI HITUNG WAKTU ---
            end_time = time.time()
            durasi = round(end_time - start_time, 2) # Hasil dalam detik (misal: 1.45)

            # 4. Simpan jawaban AI ke database 
            # (PENTING: Pastikan kolom 'waktu_proses' sudah ada di models.py)
            ChatMessage.objects.create(
                session=sesi, 
                role='ai', 
                content=jawaban_ai, 
                waktu_proses=durasi, 
                skor_akurasi=skor_ai
            )

            # --- 5. KIRIM BALIKAN KE FRONTEND ---
            return JsonResponse({
                'jawaban': jawaban_ai, 
                'skor': skor_ai,
                'session_id': str(sesi.id),
                'judul': sesi.judul,
                'waktu': durasi, 
                'sumber_file': sumber_file, # <--- BARU: Kirim nama file PDF
                'halaman': halaman          # <--- BARU: Kirim nomor halaman
            })
            
        except Exception as e:
            # Biar gampang debug kalau ada error lain
            print("Error di api_chat:", e)
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid Request'}, status=400)
        
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