
----
>**📦 QRIS Dinamis Generator (Web Version)
Alat berbasis web untuk mengubah QRIS statis (gambar atau teks) menjadi QRIS dinamis dengan nominal dan biaya layanan yang dapat disesuaikan.**


## Fitur
- Upload gambar QRIS statis 
- Input nominal pembayaran
- Tambahan biaya layanan dalam persen atau rupiah
- Menampilkan QR code hasil beserta teks 
- Mendukung berbagai format gambar: .png, .jpg, .jpeg

## Teknologi yang Digunakan
- Python 
- Flask
- OpenCV
- qrcode
- pyzbar
- pillow
- HTML + CSS (template sederhana)

## Instalasi & Menjalankan
1. Clone Repo
```
  git clone https://github.com/topibajaa/qrisweb.git
  cd qrisweb
```
3. Install dependensi
```
  pip install flask qrcode opencv-python pyzbar pillow
```
4. Jalankan Aplikasi
```
  python app.py
```

