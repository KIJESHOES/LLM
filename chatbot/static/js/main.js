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
    if (themeIcon) themeIcon.innerText = '☀️'; 
} else {
    htmlRoot.classList.remove('dark');
    if (themeIcon) themeIcon.innerText = '🌙';
}

function toggleDarkMode() {
    if (htmlRoot.classList.contains('dark')) {
        htmlRoot.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        if (themeIcon) themeIcon.innerText = '🌙';
    } else {
        htmlRoot.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        if (themeIcon) themeIcon.innerText = '☀️';
    }
}

// VARIABEL PENTING BUAT DATABASE
let currentSessionId = null;

// Navigasi UI
function bukaSistem() {
    if (landingPage) landingPage.classList.add('opacity-0', 'pointer-events-none');
    setTimeout(() => {
        if (landingPage) landingPage.style.display = 'none';
        if (sidebar) {
            sidebar.classList.remove('hidden');
            sidebar.classList.add('flex');
        }
        if (chatSec) {
            chatSec.classList.remove('hidden');
            chatSec.classList.add('flex');
        }
    }, 500);
}

function switchTab(tab) {
    const mChat = document.getElementById('menu-chat');
    const mDash = document.getElementById('menu-dashboard');
    
    if(tab === 'chat') {
        if (chatSec) { chatSec.classList.remove('hidden'); chatSec.classList.add('flex'); }
        if (dashSec) dashSec.classList.add('hidden');
        if (mChat) mChat.classList.add('bg-blue-50', 'border-blue-200', 'dark:bg-blue-900/30', 'dark:border-blue-800'); 
        if (mDash) mDash.classList.remove('active-menu');
    } else {
        if (dashSec) { dashSec.classList.remove('hidden'); dashSec.classList.add('block'); } // atau flex tergantung desain lu
        if (chatSec) chatSec.classList.add('hidden');
        if (mDash) mDash.classList.add('active-menu'); 
        if (mChat) mChat.classList.remove('bg-blue-50', 'border-blue-200', 'dark:bg-blue-900/30', 'dark:border-blue-800');
        initChart(); // Render grafik saat tab dashboard dibuka
    }
}

function chatBaru() {
    switchTab('chat');
    currentSessionId = null; // Reset ID Sesi untuk obrolan baru
    if (chatBox) chatBox.innerHTML = ''; // Kosongkan layar chat
}

// FUNGSI BUAT NARIK HISTORY DARI DATABASE
async function bukaHistory(sessionId) {
    switchTab('chat');
    currentSessionId = sessionId; // Set ID sesi yang dipilih
    
    if (!chatBox) return; // Jaga-jaga kalau chatBox ga ketemu
    
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
                    // TAMPILAN AI (ADA AKURASI & WAKTU)
                    chatBox.innerHTML += `
                        <div class="flex items-start gap-4 fade-in max-w-4xl mb-6">
                            <div class="bg-blue-600 text-white w-9 h-9 rounded-lg flex items-center justify-center shrink-0 shadow-sm text-xs font-bold">AI</div>
                            <div class="flex flex-col gap-2 max-w-[85%] w-full">
                                <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 p-6 rounded-3xl rounded-tl-none shadow-sm text-[15px] leading-relaxed w-full">
                                    ${msg.content.replace(/\n/g, '<br>')}
                                </div>
                                
                                <div class="flex flex-wrap items-center gap-4 px-2 mt-1">
                                    <div class="flex items-center gap-2">
                                        <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Akurasi:</span>
                                        <div class="w-24 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                                            <div class="h-full bg-blue-500" style="width: ${(msg.skor || 0) * 100}%"></div>
                                        </div>
                                        <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500">${((msg.skor || 0) * 100).toFixed(0)}%</span>
                                    </div>
                                    <div class="flex items-center gap-2 border-l border-slate-300 dark:border-slate-600 pl-4">
                                        <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Waktu:</span>
                                        <div class="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-md">
                                            <span class="text-[11px] font-bold text-slate-500 dark:text-slate-300">⏱️ ${msg.waktu || 0} Detik</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                }
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        } else {
            chatBox.innerHTML = `<div class="text-center text-red-400 mt-10">Data riwayat kosong atau tidak ditemukan.</div>`;
        }
    } catch (e) {
        console.error("Gagal load history:", e);
        chatBox.innerHTML = `<div class="text-center text-red-400 mt-10">Gagal memuat riwayat obrolan. Cek koneksi server.</div>`;
    }
}

function handleEnter(e) { if (e.key === 'Enter') kirimPesan(); }

// FUNGSI CHAT UTAMA
async function kirimPesan() {
    if (!userInput) return;
    const pesan = userInput.value.trim();
    if (!pesan) return;

    // UDAH DIPERBAIKI: Nyari ID 'panjang-jawaban' sesuai HTML baru lu
    const panjangJawaban = document.getElementById('panjang-jawaban') ? document.getElementById('panjang-jawaban').value : 'sedang';

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
            body: JSON.stringify({ 
                pesan: pesan, 
                session_id: currentSessionId,
                panjang_jawaban: panjangJawaban
            }) 
        });
        const data = await response.json();
        
        // Hapus loading
        if (document.getElementById(loadingId)) {
            document.getElementById(loadingId).remove();
        }

        if (data.session_id) {
            currentSessionId = data.session_id;
        }

        // --- PREVIEW PDF ---
        let pdfPreviewHtml = "";
        if (data.sumber_file && data.sumber_file !== "") {
            let pdfUrl = `/static/data_pdf/${data.sumber_file}#page=${data.halaman}`;
            
            pdfPreviewHtml = `
                <div class="mt-5 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden bg-slate-50 dark:bg-slate-800/50">
                    <div class="px-4 py-3 bg-slate-100 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
                        <div class="flex items-center gap-2">
                            <span class="text-xl">📄</span>
                            <span class="text-[13px] font-bold text-slate-700 dark:text-slate-200">
                                Referensi: ${data.sumber_file} <span class="text-blue-500">(Hal. ${data.halaman})</span>
                            </span>
                        </div>
                        <a href="${pdfUrl}" target="_blank" class="text-[12px] text-blue-600 hover:text-blue-800 dark:text-blue-400 font-bold transition-colors bg-white dark:bg-slate-800 px-3 py-1 rounded-full shadow-sm border border-slate-200 dark:border-slate-600">Buka Penuh ↗</a>
                    </div>
                    <iframe src="${pdfUrl}" class="w-full h-[400px] border-none" title="Preview PDF"></iframe>
                </div>
            `;
        }

        // 4. TAMPILAN AI 
        chatBox.innerHTML += `
            <div class="flex items-start gap-4 fade-in max-w-4xl mb-6 w-full">
                <div class="bg-blue-600 text-white w-9 h-9 rounded-lg flex items-center justify-center shrink-0 shadow-sm text-xs font-bold">AI</div>
                <div class="flex flex-col gap-2 max-w-[85%] w-full">
                    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 p-6 rounded-3xl rounded-tl-none shadow-sm text-[15px] leading-relaxed w-full">
                        
                        <div class="prose dark:prose-invert max-w-none text-slate-700 dark:text-slate-200">
                            ${data.jawaban.replace(/\n/g, '<br>')}
                        </div>
                        
                        ${pdfPreviewHtml}

                    </div>
                    
                    <div class="flex flex-wrap items-center gap-4 px-2 mt-1">
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Akurasi:</span>
                            <div class="w-24 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                                <div class="h-full bg-blue-500" style="width: ${(data.skor || 0) * 100}%"></div>
                            </div>
                            <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500">${((data.skor || 0) * 100).toFixed(0)}%</span>
                        </div>
                        <div class="flex items-center gap-2 border-l border-slate-300 dark:border-slate-600 pl-4">
                            <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Waktu:</span>
                            <div class="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-md">
                                <span class="text-[11px] font-bold text-slate-500 dark:text-slate-300">⏱️ ${data.waktu || 0} Detik</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        
        // Refresh halaman otomatis kalau ini chat pertama (Biar masuk ke list history)
        if (chatBox.querySelectorAll('.flex.justify-end').length === 1) {
            setTimeout(() => location.reload(), 2000); 
        }

    } catch (e) {
        console.error("Gagal kirim pesan:", e);
        if (document.getElementById(loadingId)) {
            document.getElementById(loadingId).innerText = "Error koneksi server. Pastikan Django sedang berjalan.";
        }
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Setup Chart.js
function initChart() {
    const canvasElement = document.getElementById('accuracyChart');
    if (!canvasElement) return; // Jangan paksa render kalau ga ada canvas-nya

    const ctx = canvasElement.getContext('2d');
    if (window.myChart) window.myChart.destroy();
    
    const labelGrafik = window.DJANGO_DATA ? window.DJANGO_DATA.labelGrafik : ['Sesi 1', 'Sesi 2', 'Sesi 3'];
    const dataGrafik = window.DJANGO_DATA ? window.DJANGO_DATA.dataGrafik : [0.85, 0.92, 0.88];
    const isDark = document.getElementById('html-root') && document.getElementById('html-root').classList.contains('dark');
    const textColor = isDark ? '#94a3b8' : '#64748b'; 

    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labelGrafik,
            datasets: [{
                label: 'Skor Akurasi',
                data: dataGrafik,
                borderColor: '#3b82f6', 
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
    event.stopPropagation();
    if (confirm("Yakin mau hapus riwayat chat ini?")) {
        try {
            const tokenCSRF = document.getElementById('csrf_token') ? document.getElementById('csrf_token').value : '';
            const response = await fetch(`/api/hapus/${sessionId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': tokenCSRF }
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                location.reload(); 
            } else {
                alert("Gagal menghapus riwayat!");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Terjadi kesalahan sistem saat menghapus.");
        }
    }
}