from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages # <-- TAMBAHAN: Untuk nampilin notifikasi error
import json
import time 
from .models import ChatSession, ChatMessage
from .utils import tanya_bot_k3 

# ==========================================
# 1. FUNGSI AUTENTIKASI (LOGIN & REGISTER)
# ==========================================
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('halaman_utama')
    else:
        form = UserCreationForm()
    # Ini render login/register biarin ke filenya masing-masing
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('halaman_utama')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('halaman_utama')

# ==========================================
# 2. FUNGSI UTAMA, CHAT & DASHBOARD
# ==========================================
def halaman_utama(request):
    # 1. Kalau BELUM LOGIN, lempar ke index.html biar index.html yang nampilin landing page
    if not request.user.is_authenticated:
        return render(request, 'index.html')

    # 2. Kalau SUDAH LOGIN, tarik riwayat sesinya
    semua_sesi = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    
    # 3. Cek apakah dia Admin atau User biasa, biar index.html lu bisa ngatur nampilin dashboard atau chat
    context = {
        'riwayat_sesi': semua_sesi,
        'is_admin': request.user.is_staff or request.user.is_superuser 
    }
    
    # 👇 BALIKIN KE SINI. Wajib pake index.html biar CSS Tailwind lu nyala lagi!
    return render(request, 'index.html', context)


# 👇 TAMBAHAN BARU: FUNGSI KHUSUS ANALISIS AKURASI DENGAN PROTEKSI ADMIN
@login_required(login_url='/login/')
def analisis_akurasi_view(request):
    # PROTEKSI: Cek apakah yang akses adalah admin/superuser
    if not (request.user.is_staff or request.user.is_superuser):
        # Kalau bukan admin, kasih pesan error dan tendang ke halaman utama
        messages.error(request, "Akses ditolak! Halaman Analisis Akurasi khusus untuk Admin.")
        return redirect('halaman_utama')
    
    # Kalau lolos (dia admin), siapkan data dashboard
    semua_sesi = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    context = {
        'riwayat_sesi': semua_sesi,
        'is_admin': True,
        'tampilkan_dashboard': True # Variabel bantuan buat di index.html
    }
    
    # Tetap render index.html sebagai kerangka utamanya
    return render(request, 'index.html', context)


@csrf_exempt
@login_required(login_url='/login/')
def api_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pesan_user = data.get('pesan')
            session_id = data.get('session_id')
            
            panjang_jawaban = data.get('panjang_jawaban', 'sedang') 
            start_time = time.time()

            if not session_id:
                judul_baru = pesan_user[:30] + "..." if len(pesan_user) > 30 else pesan_user
                sesi = ChatSession.objects.create(judul=judul_baru, user=request.user)
            else:
                sesi = ChatSession.objects.get(id=session_id, user=request.user)
                sesi.save()

            ChatMessage.objects.create(session=sesi, role='user', content=pesan_user)

            jawaban_ai, skor_ai, sumber_file, halaman = tanya_bot_k3(pesan_user, panjang_jawaban)

            end_time = time.time()
            durasi = round(end_time - start_time, 2)

            ChatMessage.objects.create(
                session=sesi, 
                role='ai', 
                content=jawaban_ai, 
                waktu_proses=durasi, 
                skor_akurasi=skor_ai
            )

            return JsonResponse({
                'jawaban': jawaban_ai, 
                'skor': skor_ai,
                'session_id': str(sesi.id),
                'judul': sesi.judul,
                'waktu': durasi, 
                'sumber_file': sumber_file,
                'halaman': halaman 
            })
            
        except Exception as e:
            print("Error di api_chat:", e)
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid Request'}, status=400)
        
# ==========================================
# 3. FUNGSI RIWAYAT CHAT
# ==========================================
@login_required(login_url='/login/')
def hapus_sesi(request, session_id):
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            sesi = ChatSession.objects.get(id=session_id, user=request.user)
            sesi.delete()
            return JsonResponse({'status': 'success'})
        except ChatSession.DoesNotExist:
            return JsonResponse({'status': 'error', 'pesan': 'Sesi tidak ditemukan'}, status=404)

@login_required(login_url='/login/')
def get_history(request, session_id):
    try:
        sesi = ChatSession.objects.get(id=session_id, user=request.user)
        pesan_pesan = sesi.messages.all().order_by('created_at')
        
        data_pesan = []
        for p in pesan_pesan:
            data_pesan.append({
                'role': p.role,
                'content': p.content,
                # Pake getattr biar aman jaya kalau kolomnya emang ga ada di database
                'sumber_file': getattr(p, 'sumber_file', ""), 
                'halaman': getattr(p, 'halaman', 1), # <--- INI PENYELAMATNYA BOS
                'skor': getattr(p, 'skor', 0),
                'waktu': getattr(p, 'waktu', 0)
            })
            
        return JsonResponse({'status': 'ok', 'messages': data_pesan})
    except ChatSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sesi tidak ditemukan'})