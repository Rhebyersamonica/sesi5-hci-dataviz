# Persona, Skenario, dan Kebutuhan

## Persona: Bu Rina (45 tahun)
- **Peran:** Dosen wali dan anggota gugus mutu prodi
- **Kemampuan teknologi:** Menengah (terbiasa Excel dan e-learning)

### Goal
- Mengetahui kelompok mahasiswa yang paling berisiko drop out dalam 5 detik sebelum rapat prodi
- Menunjukkan temuan kepada koordinator prodi tanpa menjelaskan angka satu per satu

### Pain point
- Laporan Excel panjang dan penuh angka tanpa penekanan warna
- Sulit membandingkan kelompok (beasiswa, biaya kuliah, umur) secara cepat
- Grafik lama sulit dibaca di layar proyektor

### Perilaku
- Membuka laporan di laptop dan tablet
- Lebih suka grafik batang sederhana daripada tabel
- Jarang memakai pintasan keyboard

## Skenario penggunaan (konteks, trigger, action, outcome)
- **Konteks:** Rapat prodi pagi hari, layar proyektor dengan pencahayaan ruangan terang
- **Trigger:** Koordinator prodi bertanya: kelompok mahasiswa mana yang perlu didampingi lebih dulu?
- **Action:** Bu Rina membuka dashboard, memilih variabel 'Status pembayaran biaya kuliah', lalu mengarahkan kursor ke batang tertinggi
- **Outcome:** Kelompok berisiko terlihat jelas (batang merah di atas garis rata-rata) dan diputuskan untuk diberi konseling dalam kurang dari 1 menit

## Kebutuhan fungsional
- F1: Pengguna dapat memilih variabel pengelompokan (filter) minimal 5 pilihan
- F2: Detail angka muncul saat kursor diarahkan ke batang (details on demand)
- F3: Grafik dapat diekspor sebagai gambar

## Kebutuhan non-fungsional
- N1: Dashboard selesai dibangun dalam kurang dari 2 detik
- N2: Semua warna teks dan grafik memenuhi rasio kontras WCAG AA
- N3: Ukuran file dashboard di bawah batas yang ditetapkan (1 MB mode CDN, 10 MB mode offline)

> Persona ini fiktif dan berdasarkan asumsi. Pada penerapan nyata, persona harus disintesis dari wawancara, observasi, dan survei pengguna.
