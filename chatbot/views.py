from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatSession, ChatMessage
from .utils import tanya_bot_k3 # Pastikan import fungsi AI lu bener

def halaman_utama(request):
    # Ambil semua riwayat sesi dari database untuk ditampilin di sidebar
    semua_sesi = ChatSession.objects.all().order_by('-updated_at')
    context = {
        'riwayat_sesi': semua_sesi
    }
    return render(request, 'chat.html', context)

@csrf_exempt
def api_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pesan_user = data.get('pesan')
        session_id = data.get('session_id') # Bakal dapet ID dari frontend
        
        # 1. Cek apakah ini chat di sesi baru atau sesi lama
        if not session_id:
            # Bikin sesi baru
            # Bikin judul otomatis dari 30 huruf pertama pesan user
            judul_baru = pesan_user[:30] + "..." if len(pesan_user) > 30 else pesan_user
            sesi = ChatSession.objects.create(judul=judul_baru)
        else:
            # Lanjutin sesi yang udah ada
            sesi = ChatSession.objects.get(id=session_id)
            sesi.save() # Biar updated_at nya ke-refresh

        # 2. Simpan pertanyaan User ke database
        ChatMessage.objects.create(session=sesi, role='user', content=pesan_user)

        # 3. Panggil fungsi AI Langchain lu
        jawaban_ai, skor_ai = tanya_bot_k3(pesan_user)

        # 4. Simpan jawaban AI ke database
        ChatMessage.objects.create(
            session=sesi, 
            role='ai', 
            content=jawaban_ai, 
            skor_akurasi=skor_ai
        )

        return JsonResponse({
            'jawaban': jawaban_ai, 
            'skor': skor_ai,
            'session_id': str(sesi.id), # Balikin ID sesi biar frontend tau
            'judul': sesi.judul
        })

# API khusus buat ngambil riwayat pas tombol history diklik
def get_history(request, session_id):
    try:
        sesi = ChatSession.objects.get(id=session_id)
        pesan_pesan = sesi.messages.all().order_by('created_at')
        
        data_pesan = []
        for p in pesan_pesan:
            data_pesan.append({
                'role': p.role,
                'content': p.content,
                'skor': p.skor_akurasi
            })
            
        return JsonResponse({'status': 'ok', 'messages': data_pesan})
    except ChatSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sesi tidak ditemukan'})