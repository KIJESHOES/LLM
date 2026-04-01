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
def tanya_bot_k3(pertanyaan):
    global riwayat_chat
    path_db = "db_vektor/"
    
    vektor_db = Chroma(
        persist_directory=path_db, 
        embedding_function=OllamaEmbeddings(model="nomic-embed-text")
    )
    
    llm = ChatOllama(model="llama3", temperature=0)
    
    # Ambil 20 potongan teks biar lebih akurat
    dokumen_ketemu = vektor_db.similarity_search(pertanyaan, k=20)
    teks_konteks = "\n\n".join([doc.page_content for doc in dokumen_ketemu])
    
    teks_history = ""
    for obrolan in riwayat_chat:
        teks_history += f"USER: {obrolan['user']}\nAI: {obrolan['ai']}\n\n"

    prompt_ke_ai = f"""
    Kamu adalah asisten sistem K3 yang JUJUR dan KAKU. 
    Tugasmu HANYA menjawab berdasarkan DOKUMEN K3 di bawah.
    
    ATURAN:
    1. Jika jawaban TIDAK ADA di teks, jawab: "Maaf, informasi tidak ditemukan." atau dapat dikembangkan lagi dengan kalimat serupa yang menyatakan ketidaktahuan. JANGAN buat jawaban sendiri.
    2. Atau jika jawaban tidak ditemuka berikan referensi dokumen yang paling relevan dengan pertanyaan
    2. JANGAN pakai pengetahuan luar.
    3. Pakai bahasa Indonesia yang formal.
    4. Jika pertanyaan ada pada jawaban sertakan sumber nama file dokumennya juga
    
    
    --- RIWAYAT ---
    {teks_history}

    --- DOKUMEN ---
    {teks_konteks}
    
    --- PERTANYAAN ---
    {pertanyaan}
    
    Jawaban:"""
    
    jawaban_ai = llm.invoke(prompt_ke_ai).content
    riwayat_chat.append({"user": pertanyaan, "ai": jawaban_ai})
    if len(riwayat_chat) > 3: riwayat_chat.pop(0)

    # Menambahkan skor default agar unpacking tidak error.
    # Ingat untuk mengganti ini dengan perhitungan skor sebenarnya nanti.
    skor_ai = 0.99
        
    return jawaban_ai, skor_ai