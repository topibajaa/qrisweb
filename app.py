from flask import Flask, render_template, request
import os
import cv2
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def crc16_ccitt(data: str):
    crc = 0xFFFF
    for c in bytearray(data.encode()):
        crc ^= c << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, '04X')

# Fungsi untuk decode QR dari gambar
def decode_qr_image(image_path):
    img = cv2.imread(image_path)
    decoded_objects = decode(img)
    for obj in decoded_objects:
        return obj.data.decode("utf-8")
    return None

# Fungsi membuat QR dinamis dari QRIS statis
def generate_qris_dinamis(base_qris, nominal, biaya, jenis_biaya):
    try:
        nominal = int(nominal)
        biaya = float(biaya)
    except ValueError:
        return None, None, "Nominal atau biaya tidak valid."

    # Hitung total nominal
    if jenis_biaya == "persen":
        biaya_rp = round(nominal * (biaya / 100))
    else:
        biaya_rp = int(biaya)

    total = nominal + biaya_rp
    total_str = f"{total:06d}"
    nominal_tag = f"5406{total_str}"

    # Sisipkan tag 54 sebelum tag 58
    pos_58 = base_qris.find("5802")
    if pos_58 == -1:
        return None, None, "Tag 5802 tidak ditemukan dalam QRIS statis."

    raw_data = base_qris[:pos_58] + nominal_tag + base_qris[pos_58:]

    # Tambahkan tag 63 (CRC) kosong dulu
    raw_data_no_crc = raw_data + "6304"
    crc = crc16_ccitt(raw_data_no_crc)
    final_qris = raw_data_no_crc + crc

    # Buat gambar QR
    qr_img_path = os.path.join("static", "qr_generated.png")
    img = qrcode.make(final_qris)
    img.save(qr_img_path)

    return final_qris, qr_img_path, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['qris_image']
        nominal = request.form['amount']
        fee = request.form['fee']
        fee_type = request.form['fee_type']

        if uploaded_file.filename != '':
            path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(path)

            base_qris = decode_qr_image(path)
            if not base_qris:
                return "QR Code tidak bisa dibaca."

            final_qris, qr_img_path, error = generate_qris_dinamis(base_qris, nominal, fee, fee_type)
            if error:
                return error

            return render_template('index.html', base_qr=base_qris, dynamic_qr=final_qris, qr_img=qr_img_path)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
