from flask import Flask, render_template, request, send_file
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import io
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def generate_qris(base_qris, nominal, biaya=0):
    total_nominal = nominal + biaya
    nominal_str = f"{total_nominal:06d}"
    nominal_tag = f"5406{nominal_str}"
    pos_58 = base_qris.find("5802")
    if pos_58 == -1:
        return None
    raw_data = base_qris[:pos_58] + nominal_tag + base_qris[pos_58:]
    raw_data_no_crc = raw_data + "6304"
    crc = crc16_ccitt(raw_data_no_crc)
    return raw_data_no_crc + crc

def decode_qr_image(image_path):
    image = Image.open(image_path)
    decoded = decode(image)
    if decoded:
        return decoded[0].data.decode()
    return ""

@app.route("/", methods=["GET", "POST"])
def index():
    result_text = None
    filename = None

    if request.method == "POST":
        qris_statis = request.form.get("qris_string", "").strip()
        nominal = int(request.form.get("nominal", "0"))
        biaya = int(request.form.get("biaya", "0"))

        if 'qris_image' in request.files:
            file = request.files['qris_image']
            if file.filename:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(image_path)
                decoded = decode_qr_image(image_path)
                if decoded:
                    qris_statis = decoded

        if not qris_statis:
            return render_template("index.html", error="QRIS statis tidak ditemukan.")

        final_qris = generate_qris(qris_statis, nominal, biaya)
        if not final_qris:
            return render_template("index.html", error="Format QRIS statis tidak valid.")

        # Buat QR code
        qr = qrcode.make(final_qris)
        filename = os.path.join(UPLOAD_FOLDER, "qris.png")
        qr.save(filename)

        result_text = final_qris

    return render_template("index.html", result=result_text, filename=filename)

@app.route("/download")
def download():
    path = os.path.join(app.config['UPLOAD_FOLDER'], "qris.png")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
