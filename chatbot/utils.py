import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama

# Simpan riwayat chat di memori
riwayat_chat = []

# --- 1. FUNGSI BUAT BACA PDF (DENGAN AUTO-CLEAN) ---
def ingest_pdf_ke_vektor():
    path_pdf = "data_pdf/"
    path_db = "db_vektor/"

    if os.path.exists(path_db):
        shutil.rmtree(path_db)
        print("Database lama dibersihkan! ✨")

    loader = PyPDFDirectoryLoader(path_pdf)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)

    Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="nomic-embed-text"),
        persist_directory=path_db
    )
    print("SELESAI! Database bener-bener fresh sekarang.")

# --- 2. FUNGSI UTAMA TANYA JAWAB (YG DIPANGGIL VIEWS) ---
def tanya_bot_k3(pertanyaan, panjang_jawaban="sedang"):
    global riwayat_chat
    path_db = "db_vektor/"
    
    vektor_db = Chroma(
        persist_directory=path_db, 
        embedding_function=OllamaEmbeddings(model="nomic-embed-text")
    )
    
    llm = ChatOllama(model="llama3", temperature=0)
    
    # PERBAIKAN 1: Turunin k jadi 5 (biar AI fokus) & pakai with_score buat ngecek relevansi
    dokumen_dengan_skor = vektor_db.similarity_search_with_score(pertanyaan, k=5)
    
    # PERBAIKAN 2: Filter dokumen. (Catatan: Chroma pake L2 distance, makin KECIL skornya = makin mirip).
    # Threshold 1.5 ini angka aman buat nomic-embed-text, bisa lu naik-turunin (1.0 - 1.8) sesuai hasil tes.
    dokumen_valid = []
    skor_terbaik = 0
    
    for doc, score in dokumen_dengan_skor:
        if score < 1.5:  # Kalau jaraknya di bawah 1.5, berarti nyambung
            dokumen_valid.append(doc)
            # Konversi L2 distance ke persentase akurasi (kasarannya aja buat di UI)
            skor_sementara = max(0.0, 1.0 - (score / 2.0))
            if skor_sementara > skor_terbaik:
                skor_terbaik = skor_sementara

    # Kalau nggak ada dokumen yang lolos filter kemiripan, langsung tolak di backend!
    if not dokumen_valid:
        jawaban_kosong = "Maaf, informasi mengenai pertanyaan tersebut tidak ditemukan di dalam dokumen K3 kami."
        riwayat_chat.append({"user": pertanyaan, "ai": jawaban_kosong})
        return jawaban_kosong, 0.0, "", 0

    # Kalau ada, gabungin teksnya
    teks_konteks = "\n\n".join([doc.page_content for doc in dokumen_valid])
    
    # Ambil metadata dari dokumen yang paling relevan (ranking 1)
    sumber_file = os.path.basename(dokumen_valid[0].metadata.get('source', ''))
    halaman = dokumen_valid[0].metadata.get('page', 0) + 1 

    teks_history = ""
    for obrolan in riwayat_chat:
        teks_history += f"USER: {obrolan['user']}\nAI: {obrolan['ai']}\n\n"

    # --- LOGIKA INSTRUKSI PANJANG JAWABAN ---
    if panjang_jawaban == "pendek":
        instruksi_panjang = "Jawablah dengan SANGAT SINGKAT (maksimal 2 kalimat)."
    elif panjang_jawaban == "panjang":
        instruksi_panjang = "Jawablah dengan SANGAT DETAIL dan sebutkan poin-poinnya secara mendalam."
    else:
        instruksi_panjang = "Jawablah dengan panjang SEDANG."

    # PERBAIKAN 3: Prompt diganti Full Bahasa Indonesia biar AI nggak bingung konteks
    prompt_ke_ai = f"""
Kamu adalah asisten ahli K3 (Keselamatan dan Kesehatan Kerja) yang SANGAT KAKU dan HANYA MENGANDALKAN DOKUMEN.

ATURAN WAJIB (JIKA DILANGGAR SISTEM AKAN RUSAK):
1. JAWAB HANYA BERDASARKAN DOKUMEN KONTEKS DI BAWAH INI. Jangan pernah menggunakan pengetahuan di luar dokumen.
2. Jika dokumen konteks tidak membahas sama sekali tentang pertanyaan, jawab PERSIS seperti ini: "Maaf, informasi tidak ditemukan di dalam dokumen."
3. JANGAN PERNAH mengarang singkatan, teori, atau menebak-nebak jawaban.
4. Gunakan bahasa Indonesia baku dan formal.
5. {instruksi_panjang}

--- RIWAYAT OBROLAN ---
{teks_history}

--- DOKUMEN KONTEKS ---
{teks_konteks}

--- PERTANYAAN USER ---
{pertanyaan}

Jawaban Asisten K3:"""
    
    jawaban_ai = llm.invoke(prompt_ke_ai).content
    riwayat_chat.append({"user": pertanyaan, "ai": jawaban_ai})
    
    if len(riwayat_chat) > 3: 
        riwayat_chat.pop(0)

    # Return pake skor kemiripan asli, bukan 0.99 hardcode lagi
    return jawaban_ai, skor_terbaik, sumber_file, halaman