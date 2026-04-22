# Monopoly Superapps - Django Edition

Game Monopoli berbasis web yang dibangun dengan Django dan Javascript, menampilkan papan 3D interaktif dan sistem manajemen admin yang lengkap.

## 🚀 Fitur Utama
- **Papan 3D Interaktif**: Tampilan isometrik dengan kontrol orbit (Yaw, Pitch, Roll).
- **Setup Game Fleksibel**: Pilih 2-4 pemain, mendukung kombinasi Human dan Bot.
- **Manajemen Karakter**: Kustomisasi warna, ikon 2D, dan model 3D untuk setiap token.
- **Admin Dashboard**: Kelola pengguna, karakter, papan, dan kartu kemampuan.
- **Multiplayer Lokal**: Sistem giliran pemain dengan animasi gerakan token.
- **Login Admin via Email**: Autentikasi modern menggunakan email sebagai identitas utama.

## 📋 Prasyarat (Requirements)
Sebelum menginstal, pastikan Anda telah menginstal:
- Python 3.9+
- MySQL Server / MariaDB
- Git

## 🛠️ Instalasi

1. **Clone Repositori**
   ```bash
   git clone <repository-url>
   cd djanggo-monopoli
   ```

2. **Buat Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instal Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Database**
   - Buat database di MySQL dengan nama `monopoly-superapps`.
   - Sesuaikan konfigurasi database di `monopoli_game/settings.py` jika diperlukan (user, password, host).

5. **Migrasi Database**
   ```bash
   python manage.py migrate
   ```

6. **Buat Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```
   *Catatan: Sistem menggunakan Email sebagai identitas login utama.*

7. **Jalankan Server**
   ```bash
   python manage.py runserver
   ```

## 🎮 Cara Penggunaan

### Memulai Permainan
1. Buka browser dan akses `http://localhost:8000/`.
2. Anda akan disambut dengan **Setup Game Overlay**.
3. Pilih jumlah pemain (2-4).
4. Tentukan tipe pemain (**Human** atau **Bot**) untuk setiap slot.
5. Pilih karakter untuk setiap pemain Human (Bot akan mendapatkan karakter acak).
6. Klik **MULAI PERMAINAN**.

### Kontrol Permainan
- **ROLL**: Klik tombol ROLL untuk melempar dadu dan bergerak.
- **Klik Petak**: Klik pada petak di papan untuk melihat detail sewa dan deskripsi.
- **Kontrol 3D**: Gunakan tombol bulat di pojok kanan bawah untuk membuka panel kontrol kamera (Yaw, Pitch, Roll, Perspektif).

### Manajemen Admin
1. Akses `http://localhost:8000/admin/`.
2. Login menggunakan email dan password superuser yang telah dibuat.
3. Di sini Anda dapat:
   - Menambah/mengedit karakter permainan.
   - Mengunggah model 3D (`.glb`) untuk token.
   - Mengatur role dan izin pengguna.
   - Mengelola aset papan.

## 📂 Struktur Folder
- `board/`: Logika utama permainan, views, dan models.
- `static/`: File aset (CSS, JS, Gambar, Model 3D).
- `templates/`: File HTML (Papan permainan dan Dashboard Admin).
- `media/`: Lokasi penyimpanan file yang diunggah (Foto karakter, Model 3D).
- `monopoli_game/`: Pengaturan inti proyek Django.

## 📄 Lisensi
Copyright © 2026 Monopoly Superapps Team.
