# Sesi 5: Merancang dan Mengevaluasi Dashboard Visualisasi Data yang Berpusat pada Pengguna

**Nama:** (Rheby Ersa Monica) | **NPM:** (G1A023016) | Prodi Informatika, Universitas Bengkulu

Tugas Informatics Practitioner Lecture Series, *"Human-Computer Interaction & Data Visualization"*
(Arafat Febriandirza, Chief of Research Group for Human-Computer Interaction & Visualization, BRIN; 19 Oktober 2026).

## Latar belakang
Materi menekankan bahwa grafik yang canggih tetap gagal jika tidak dirancang berdasarkan cara manusia berpikir dan bekerja.
Pemateri membahas pendekatan *user-centered design*, psikologi kognitif dan persepsi, proses desain interaksi (analisis, desain, prototipe, evaluasi),
persona dan skenario, pemilihan grafik yang jujur (Tufte), serta dashboard interaktif dengan prinsip *overview first, zoom and filter, details on demand*.
Studi kasus ini menerapkan alur itu pada satu dashboard: **risiko drop out mahasiswa untuk dosen wali dan koordinator prodi**.

> **Pertanyaan:** bagaimana merancang dan mengevaluasi dashboard yang membuat kelompok berisiko terlihat dalam hitungan detik, dengan grafik yang jujur dan dapat diakses?

## Alur
| Modul | Isi | Kaitan dengan materi |
|---|---|---|
| 1. Persona dan kebutuhan | Persona fiktif, skenario (konteks, trigger, action, outcome), kebutuhan fungsional dan non-fungsional | Modul 5: persona, kebutuhan |
| 2. Grafik buruk vs baik | Sumbu terpotong vs mulai dari nol, pie vs bar, warna pelangi vs satu warna sorot | Modul 6: pemilihan grafik, Tufte, pra-atentif |
| 3. Kontras warna | Rasio kontras WCAG untuk palet dashboard dan contoh buruk | Modul 3: Perceivable (WCAG) |
| 4. Usability testing | SUS, tingkat keberhasilan, waktu tugas, uji statistik | Modul 4: usability testing |
| 5. Heuristik Nielsen | Templat 10 heuristik untuk evaluasi pakar | Tanya jawab: indikator keberhasilan UI |
| 6. Dashboard interaktif | HTML interaktif: pilih variabel (filter), hover (detail), sorotan merah di atas rata-rata | Modul 6: mantra Shneiderman |
| 7. Verifikasi kebutuhan | Memeriksa kebutuhan fungsional dan non-fungsional terhadap dashboard | Modul 5 dan 4 |

## Data
UCI *Predict Students' Dropout and Academic Success* (CC BY 4.0), sudah ada di `data/data.csv`. Dipakai mahasiswa berstatus *Dropout* dan *Graduate*
(3.630 mahasiswa; status *Enrolled* dikeluarkan karena hasil akhirnya belum diketahui).

> Realinho, V., Vieira Martins, M., Machado, J., & Baptista, L. (2021). *Predict Students' Dropout and Academic Success* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5MC89

**Data usability (modul 4) adalah SINTETIS** (simulasi) agar prosedur analisisnya dapat didemonstrasikan. Untuk hasil yang bermakna, lakukan uji coba nyata
dengan teman atau dosen: isi `data/usability_template.csv` (satu baris per peserta; `desain` = A atau B; `tugas_berhasil` 0/1; `waktu_detik`; `sus_1` sampai `sus_10` skala 1-5),
simpan sebagai `data/usability.csv`, lalu jalankan ulang. Kode otomatis memakai data nyata jika file itu ada.

## Cara menjalankan
```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python case_study_hci.py
# opsi: --offline (dashboard bisa dibuka tanpa internet, file ±5 MB)
```
Lalu **buka `output/dashboard_dropout.html` di browser**. Secara bawaan file ini memuat pustaka grafik dari internet (CDN), sehingga perlu koneksi saat dibuka.

## Hasil (data UCI)
- Tingkat dropout keseluruhan 39,1%. Kelompok tertinggi yang ditandai dashboard: mahasiswa dengan **biaya kuliah menunggak** (±94%, 486 mahasiswa); debitur ±76%; kelompok umur 23-29 dan ≥30 tahun ±62-64%.
- Palet dashboard lulus WCAG AA (rasio terendah 4,6:1); tiga contoh warna buruk (kuning, abu muda, hijau muda di latar putih) semuanya gagal (1,2:1 sampai 1,9:1).
- Sumbu terpotong membuat batang terendah tampak hanya ±22% dari batang tertinggi, padahal sebenarnya ±74% (lihat `output/01_grafik_buruk_vs_baik.png`).
- Verifikasi: 6 dari 6 kebutuhan terpenuhi (7 pilihan variabel, hover detail, ekspor gambar, dibangun < 2 detik, kontras lulus, ukuran file di bawah batas).
- Simulasi usability (sintetis, n = 15 per desain): SUS desain B ±71 vs A ±54; keberhasilan tugas 87% vs 53% (beda keberhasilan belum signifikan pada n sekecil ini, p ±0,11).
- File lain: `persona_skenario.md`, `dashboard_ringkasan.md` (alternatif teks), `checklist_heuristik_nielsen.csv`, `verifikasi_kebutuhan.csv`, `ringkasan.md`.

## Kaitan dengan materi dan perbedaannya
**Diambil dari materi:** user-centered design, persona dan skenario, kebutuhan fungsional dan non-fungsional, siklus analisis-desain-prototipe-evaluasi, usability testing,
heuristik Nielsen, WCAG, atribut pra-atentif, prinsip Gestalt (kemiripan: warna sama untuk kelompok yang sama), pemilihan jenis grafik, Tufte (chartjunk), mantra Shneiderman, dan etika grafik yang jujur.

**Berbeda dari materi:**
- Persona dan skenario saya buat sebagai contoh fiktif, bukan hasil wawancara atau observasi pengguna nyata.
- Prototipe *low-fidelity* dan *high-fidelity* tidak dikerjakan di perangkat desain; dashboard HTML ini setara prototipe *high-fidelity*.
- Hanya sebagian prinsip Gestalt dan Nielsen yang diterapkan; heuristik Nielsen hanya berupa templat kosong.
- Tema materi lebih luas (misalnya antarmuka suara, AR/VR, dan interaksi sosial) dan tidak diimplementasikan.

## Keterbatasan
- **Data usability sintetis**; angka SUS dan waktunya hanya mendemonstrasikan analisis, bukan temuan tentang pengguna sebenarnya.
- Dashboard diperiksa lewat kode (struktur dan syarat teknis), tetapi **interaksinya perlu Anda coba sendiri di browser**.
- Pemeriksaan kebutuhan hanya proksi teknis. Kenyamanan sebenarnya hanya bisa dipastikan lewat uji coba pengguna.
- Data UCI berasal dari institusi di Portugal, dan sebagian kelompok kecil (misalnya program studi bersampel sedikit) tingkat dropout-nya kurang stabil.
- Kelompok gender hanya diberi kode karena arti kode tidak diverifikasi di kode ini; fitur sensitif sebaiknya tidak dipakai untuk menentukan tindakan terhadap individu.
