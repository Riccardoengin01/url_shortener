from flask import Flask, render_template, request, redirect, abort, url_for
import string
import random
import os
import qrcode
from urllib.parse import urlparse
from database import create_table, insert_url, get_long_url

app = Flask(__name__)
create_table()

QR_FOLDER = os.path.join(app.root_path, "static", "qrcodes")
os.makedirs(QR_FOLDER, exist_ok=True)

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme in ['http', 'https'], parsed.netloc])

def create_qr(url, filename):
    img = qrcode.make(url)
    path = os.path.join(QR_FOLDER, f"{filename}.png")
    img.save(path)
    return f"qrcodes/{filename}.png"

def generate_unique_code(long_url, max_attempts=5):
    for _ in range(max_attempts):
        code = generate_short_code()
        try:
            insert_url(code, long_url)
            return code
        except Exception:
            continue
    raise Exception("❌ Impossibile generare un codice univoco dopo vari tentativi.")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form.get("long_url", "").strip()
        if not long_url:
            return render_template("index.html", error="Inserisci un URL.")
        if not is_valid_url(long_url):
            return render_template("index.html", error="URL non valido. Inizia con http:// o https://")

        try:
            short_code = generate_unique_code(long_url)
        except Exception as e:
            return render_template("index.html", error=str(e))

        short_url = request.host_url + short_code
        qr_path  = create_qr(short_url, short_code)
        return render_template("index.html",
                               short_url=short_url,
                               qr_src=url_for('static', filename=qr_path))
    return render_template("index.html")

@app.route("/<short_code>")
def redirect_short_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)
