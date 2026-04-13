# BAB 4
# EKSPERIMEN DAN ANALISIS

Uraian pada bab ini meliputi parameter eksperimen, karakteristik data, skenario ujicoba, tempat, waktu, spesifikasi peralatan, hasil eksperimen, hingga analisis mendalam terhadap performa sistem RAG yang telah dibangun.

---

## 4.1 PARAMETER EKSPERIMEN DAN KARAKTERISTIK DATA

### 4.1.1 Parameter Eksperimen
Eksperimen ini menggunakan parameter kunci untuk mengoptimalkan kinerja Retrieval-Augmented Generation (RAG). Parameter utama yang ditetapkan adalah:
1.  **Top-K Retrieval**: Nilai $K=5$ dipilih untuk menyeimbangkan antara kelengkapan informasi dan efisiensi konsumsi token.
2.  **Model Generasi**: Google Gemini 1.5 Flash digunakan karena memiliki latensi yang rendah namun tetap mampu menangani konteks yang panjang.
3.  **Embedding Model**: `text-embedding-004` dengan dimensi 768 digunakan untuk representasi vektor data personal.
4.  **Temporal Grounding**: Parameter `client_local_time` dikirim secara eksplisit untuk menjamin akurasi jawaban yang sensitif terhadap waktu.

### 4.1.2 Karakteristik Data
Data yang digunakan dalam eksperimen ini memiliki karakteristik sebagai berikut:
1.  **Data Akademik**: Berupa kurikulum program studi (CSV/Excel) yang berisi nama mata kuliah, SKS, dan deskripsi kompetensi.
2.  **Data Personal User**: Berupa entitas jadwal kuliah, daftar tugas (*todo*), profil bio, dan riwayat aktivitas UKM.
3.  **Data Transaksional**: Chat history yang tersimpan secara relasional dan vektor untuk memberikan memori jangka pendek pada asisten AI.
Alasan penggunaan data ini adalah untuk menyimulasikan ekosistem data mahasiswa yang dinamis, sehingga kemampuan AI dalam memilah informasi yang relevan dapat diuji secara nyata.

---

## 4.2 TEMPAT UJICOBA
Ujicoba dilaksanakan di Laboratorium Pengembangan Perangkat Lunak menggunakan infrastruktur lokal yang terhubung dengan layanan cloud Google AI Studio. Lingkungan ini dipilih untuk meminimalkan gangguan jaringan eksternal dan memastikan konsistensi pengukuran latensi.

---

## 4.3 WAKTU UJICOBA
Ujicoba teknis secara komprehensif dilakukan pada periode April 2026. Waktu ini mencakup fase *stress test* konkurensi, pengukuran tokenisasi, dan validasi fungsionalitas RAG dari ujung ke ujung.

---

## 4.4 SPESIFIKASI PERALATAN UJICOBA

### 4.4.1 Perangkat Keras (Hardware)
- **Prosesor**: Intel Core i7 / AMD Ryzen 7 (setara).
- **Memori**: 16 GB RAM.
- **Penyimpanan**: SSD NVMe (untuk akses database PostgreSQL yang cepat).
- **Koneksi**: Internet stabil minimal 10 Mbps (untuk komunikasi API Gemini).

### 4.4.2 Perangkat Lunak (Software)
- **Sistem Operasi**: Linux / Windows 11.
- **Bahasa Pemrograman**: Python 3.10+ (Backend) dan JavaScript (Frontend).
- **Database**: PostgreSQL 17 dengan ekstensi `pgvector`.
- **Backend Framework**: FastAPI.
- **AI Engine**: Google Gemini API via REST.

---

## 4.5 HASIL EKSPERIMEN

### 4.5.1 Latensi dan Akurasi Retrieval
Berdasarkan pengujian sistematis, didapatkan performa dasar sebagai berikut:

| Parameter | Metrik / Deskripsi | Target / Hasil Ujicoba |
| :--- | :--- | :--- |
| **Response Latency** | Waktu dari input hingga jawaban AI. | < 2.5 Detik (Hasil: 1,93s) |
| **Retrieval Top-K** | Jumlah dokumen relevan yang ditarik. | 5 Dokumen per Kueri |
| **Context Relevancy** | Tingkat kesesuaian dokumen. | > 80% Relevansi |
| **Temporal Accuracy** | Ketepatan identifikasi waktu. | 100% |

### 4.5.2 Perbandingan Beban Kerja Fitur
Pengujian membandingkan fitur konsultasi biasa dengan pembuatan roadmap karier:

| Fitur | Avg. Latency | Estimasi Token | Intensitas Komputasi |
| :--- | :--- | :--- | :--- |
| **Konsultasi Biasa** | 0,68 Detik | ~60 Tokens | Rendah |
| **Generasi Roadmap** | 5,08 Detik | ~1.322 Tokens | Sangat Tinggi |

### 4.5.3 Hasil Uji Stres (Stress Test)
Sistem diuji dengan beban permintaan beruntun untuk menemukan batas kuota harian dan stabilitas API:

| Jumlah User | Status | Rata-rata Latency | Keterangan |
| :--- | :--- | :--- | :--- |
| **5 User** | Success | 2,38 Detik | Performa stabil. |
| **10 User** | Failed | N/A | *500 Internal Error* |
| **20 User** | Failed | N/A | *429 Too Many Requests* |

---

## 4.6 ANALISIS HASIL EKSPERIMEN
Hasil eksperimen menunjukkan bahwa sistem RAG yang dibangun sangat efektif untuk query personal satu arah (latensi 1,93s). Namun, pada fitur **Adaptive Roadmap**, terjadi kenaikan latensi yang signifikan (5,08s) dikarenakan volume token yang dikirimkan mencapai ~1.322 per request.

Analisis terhadap kegagalan pada 10-20 pengguna menunjukkan bahwa batasan utama sistem bukan terletak pada database PostgreSQL+pgvector, melainkan pada **API Rate Limit** layanan Gemini Free Tier. Hal ini membuktikan bahwa arsitektur RAG memerlukan mekanisme *caching* atau *queuing* untuk menjaga ketersediaan layanan pada beban tinggi.

---

## 4.7 KESIMPULAN
Kesimpulan dari penelitian dan eksperimen ini adalah:
1.  **Problem & Urgensi**: Mahasiswa membutuhkan asisten personal yang memahami context akademik secara detail, sebuah masalah yang berhasil dijawab dengan integrasi data personal ke dalam RAG.
2.  **Solusi**: Platform berbasis FastAPI dengan pgvector terintegrasi mampu menyatukan data relasional dan data vektor secara atomik.
3.  **Kinerja**: Sistem mampu memberikan jawaban dengan akurasi temporal 100% dan latensi rata-rata di bawah 2 detik untuk penggunaan normal.

---

## 4.8 SARAN
Untuk pengembangan lebih lanjut, disarankan:
1.  **Optimasi Biaya/Quota**: Menggunakan model yang lebih kecil atau melakukan *prompt compression* pada fitur Roadmap.
2.  **Peningkatan Skalabilitas**: Mengimplementasikan *Redis Caching* untuk menyimpan context RAG yang sering ditanyakan.
3.  **Infrastruktur**: Menggunakan Gemini Paid Tier atau model *self-hosted* untuk menghindari batasan *Rate Limit* pada saat ujicoba dengan jumlah pengguna besar.
