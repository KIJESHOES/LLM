// Tangkap elemen-elemen DOM
const landingPage = document.getElementById('landing-page');
const sidebar = document.getElementById('sidebar');
const chatSec = document.getElementById('section-chat');
const dashSec = document.getElementById('section-dashboard');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const htmlRoot = document.getElementById('html-root');
const themeIcon = document.getElementById('theme-icon');

// Cek memori lokal pas web dibuka, kemaren milih gelap apa terang?
if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    htmlRoot.classList.add('dark');
    themeIcon.innerText = '☀️'; // ganti icon matahari
} else {
    htmlRoot.classList.remove('dark');
    themeIcon.innerText = '🌙';
}

function toggleDarkMode() {
    if (htmlRoot.classList.contains('dark')) {
        htmlRoot.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        themeIcon.innerText = '🌙';
    } else {
        htmlRoot.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        themeIcon.innerText = '☀️';
    }
}
// VARIABEL PENTING BUAT DATABASE
let currentSessionId = null;

// Navigasi UI
function bukaSistem() {
    landingPage.classList.add('opacity-0', 'pointer-events-none');
    setTimeout(() => {
        landingPage.style.display = 'none';
        sidebar.classList.remove('hidden');
        sidebar.classList.add('flex');
        chatSec.classList.remove('hidden');
        chatSec.classList.add('flex');
    }, 500);
}

function switchTab(tab) {
    const mChat = document.getElementById('menu-chat');
    const mDash = document.getElementById('menu-dashboard');
    
    if(tab === 'chat') {
        chatSec.classList.remove('hidden'); chatSec.classList.add('flex');
        dashSec.classList.add('hidden');
        mChat.classList.add('bg-blue-50', 'border-blue-200', 'dark:bg-blue-900/30', 'dark:border-blue-800'); 
        mDash.classList.remove('active-menu');
    } else {
        dashSec.classList.remove('hidden');
        chatSec.classList.add('hidden');
        mDash.classList.add('active-menu'); 
        mChat.classList.remove('bg-blue-50', 'border-blue-200', 'dark:bg-blue-900/30', 'dark:border-blue-800');
        initChart(); // Render grafik saat tab dashboard dibuka
    }
}

function chatBaru() {
    switchTab('chat');
    currentSessionId = null; // Reset ID Sesi untuk obrolan baru
    
    // 4. Tampilkan jawaban AI
        chatBox.innerHTML += `
            <div class="flex items-start gap-4 fade-in max-w-4xl mb-6">
                <div class="bg-blue-600 text-white w-9 h-9 rounded-lg flex items-center justify-center shrink-0 shadow-sm text-xs font-bold">AI</div>
                <div class="flex flex-col gap-2 max-w-[85%]">
                    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 p-6 rounded-3xl rounded-tl-none shadow-sm text-[15px] leading-relaxed">
                        ${data.jawaban.replace(/\n/g, '<br>')}
                    </div>
                    
                    <div class="flex items-center gap-2 px-2 mt-1">
                        <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Waktu Proses:</span>
                        <div class="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-md">
                            <span class="text-[11px] font-bold text-slate-500 dark:text-slate-300">⏱️ ${data.waktu} Detik</span>
                        </div>
                    </div>
                    
                </div>
            </div>`;
}

// FUNGSI BUAT NARIK HISTORY DARI DATABASE
async function bukaHistory(sessionId) {
    switchTab('chat');
    currentSessionId = sessionId; // Set ID sesi yang dipilih
    
    chatBox.innerHTML = `<div class="text-center text-slate-400 dark:text-slate-500 mt-10 animate-pulse">Memuat riwayat obrolan...</div>`;

    try {
        const response = await fetch(`/api/history/${sessionId}/`);
        const data = await response.json();

        if (data.status === 'ok') {
            chatBox.innerHTML = ''; // Kosongkan chatbox
            
            // Render ulang pesan-pesan lama dari database
            data.messages.forEach(msg => {
                if (msg.role === 'user') {
                    chatBox.innerHTML += `
                        <div class="flex justify-end fade-in w-full mb-6">
                            <div class="bg-slate-800 dark:bg-blue-600 text-white p-5 rounded-3xl rounded-tr-none shadow-md max-w-[75%] text-[15px]">
                                ${msg.content}
                            </div>
                        </div>`;
                } else {
                    chatBox.innerHTML += `
                        <div class="flex items-start gap-4 fade-in max-w-4xl mb-6">
                            <div class="bg-blue-600 text-white w-9 h-9 rounded-lg flex items-center justify-center shrink-0 shadow-sm text-xs font-bold">AI</div>
                            <div class="flex flex-col gap-2 max-w-[85%]">
                                <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 p-6 rounded-3xl rounded-tl-none shadow-sm text-[15px] leading-relaxed">
                                    ${msg.content.replace(/\n/g, '<br>')}
                                </div>
                                <div class="flex items-center gap-2 px-2">
                                    <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Akurasi Konteks:</span>
                                    <div class="w-32 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                                        <div class="h-full bg-blue-500" style="width: ${msg.skor * 100}%"></div>
                                    </div>
                                    <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500">${(msg.skor * 100).toFixed(0)}%</span>
                                </div>
                            </div>
                        </div>`;
                }
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    } catch (e) {
        chatBox.innerHTML = `<div class="text-center text-red-400 mt-10">Gagal memuat riwayat obrolan.</div>`;
    }
}

function handleEnter(e) { if (e.key === 'Enter') kirimPesan(); }

// FUNGSI CHAT UTAMA
async function kirimPesan() {
    const pesan = userInput.value.trim();
    if (!pesan) return;

    // 1. Tampilkan pesan user di layar
    chatBox.innerHTML += `
        <div class="flex justify-end fade-in w-full mb-6">
            <div class="bg-slate-800 dark:bg-blue-600 text-white p-5 rounded-3xl rounded-tr-none shadow-md max-w-[75%] text-[15px]">
                ${pesan}
            </div>
        </div>`;
    
    userInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2. Tampilkan indikator loading AI
    const loadingId = 'load-' + Date.now();
    chatBox.innerHTML += `
        <div id="${loadingId}" class="flex items-center gap-3 text-slate-400 dark:text-slate-500 animate-pulse italic text-sm mb-6">
            <div class="w-2 h-2 bg-blue-400 rounded-full"></div> AI sedang menganalisis dokumen...
        </div>`;

    // 3. Kirim ke Backend Django
    try {
        const tokenCSRF = document.getElementById('csrf_token') ? document.getElementById('csrf_token').value : '';
        
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'X-CSRFToken': tokenCSRF 
            },
            // Kirim pesan DAN session_id ke backend
            body: JSON.stringify({ pesan: pesan, session_id: currentSessionId }) 
        });
        const data = await response.json();
        
        // Hapus loading
        if (document.getElementById(loadingId)) {
            document.getElementById(loadingId).remove();
        }

        // Simpan ID Sesi dari backend (penting biar obrolan nyambung)
        if (data.session_id) {
            currentSessionId = data.session_id;
        }

        // 4. Tampilkan jawaban AI
        chatBox.innerHTML += `
            <div class="flex items-start gap-4 fade-in max-w-4xl mb-6">
                <div class="bg-blue-600 text-white w-9 h-9 rounded-lg flex items-center justify-center shrink-0 shadow-sm text-xs font-bold">AI</div>
                <div class="flex flex-col gap-2 max-w-[85%]">
                    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 p-6 rounded-3xl rounded-tl-none shadow-sm text-[15px] leading-relaxed">
                        ${data.jawaban.replace(/\n/g, '<br>')}
                    </div>
                    <div class="flex items-center gap-2 px-2">
                        <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Akurasi Konteks:</span>
                        <div class="w-32 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500" style="width: ${data.skor * 100}%"></div>
                        </div>
                        <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500">${(data.skor * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>`;
        
        // Refresh halaman otomatis kalau ini chat pertama, biar judul riwayat muncul di sidebar
        if (chatBox.querySelectorAll('.flex.justify-end').length === 1) {
            setTimeout(() => location.reload(), 2000); 
        }

    } catch (e) {
        if (document.getElementById(loadingId)) {
            document.getElementById(loadingId).innerText = "Error koneksi server. Pastikan Django sedang berjalan.";
        }
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Setup Chart.js
function initChart() {
    const ctx = document.getElementById('accuracyChart').getContext('2d');
    if (window.myChart) window.myChart.destroy();
    
    // Ambil data dari variabel global (jembatan dari HTML)
    const labelGrafik = window.DJANGO_DATA ? window.DJANGO_DATA.labelGrafik : ['Sesi 1', 'Sesi 2', 'Sesi 3'];
    const dataGrafik = window.DJANGO_DATA ? window.DJANGO_DATA.dataGrafik : [0.85, 0.92, 0.88];

    // Deteksi tema buat warna teks di chart
    const isDark = document.getElementById('html-root').classList.contains('dark');
    const textColor = isDark ? '#94a3b8' : '#64748b'; // slate-400 / slate-500

    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labelGrafik,
            datasets: [{
                label: 'Skor Akurasi',
                data: dataGrafik,
                borderColor: '#3b82f6', // blue-500
                backgroundColor: isDark ? 'rgba(59, 130, 246, 0.2)' : 'rgba(37, 99, 235, 0.1)',
                borderWidth: 4,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: isDark ? '#1e293b' : '#fff',
                pointBorderColor: '#3b82f6',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    beginAtZero: true, 
                    max: 1, 
                    grid: { display: false },
                    ticks: { color: textColor }
                },
                x: { 
                    grid: { display: false },
                    ticks: { color: textColor }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// FUNGSI HAPUS HISTORY
async function hapusHistory(sessionId, event) {
    // Mencegah chat terbuka saat tombol hapus diklik
    event.stopPropagation();

    if (confirm("Yakin mau hapus riwayat chat ini?")) {
        try {
            const tokenCSRF = document.getElementById('csrf_token') ? document.getElementById('csrf_token').value : '';
            
            const response = await fetch(`/api/hapus/${sessionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': tokenCSRF 
                }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                location.reload(); // Refresh layar biar chatnya hilang
            } else {
                alert("Gagal menghapus riwayat!");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Terjadi kesalahan sistem saat menghapus.");
        }
    }
}