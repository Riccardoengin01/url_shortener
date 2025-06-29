import os
import string
import random
import sqlite3
import qrcode
from flask import Flask, render_template, request, redirect, abort, url_for

app = Flask(__name__)
DATABASE = "url_shortener.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT
        )""")
        conn.commit()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def save_url(short_code, long_url):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
        conn.commit()

def get_long_url(short_code):
    with sqlite3.connect(DATABASE) as conn:
        result = conn.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,)).fetchone()
        return result[0] if result else None

def generate_qr_code(data, filename):
    img = qrcode.make(data)
    path = os.path.join("static", filename)
    img.save(path)
    return path

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    qr_src = None
    error = None

    if request.method == "POST":
        long_url = request.form.get("long_url")
        if long_url:
            short_code = generate_short_code()
            save_url(short_code, long_url)
            short_url = request.url_root + short_code
            qr_path = generate_qr_code(short_url, f"{short_code}.png")
            qr_src = url_for("static", filename=f"{short_code}.png")
        else:
            error = "URL non valido."

    return render_template("index.html", short_url=short_url, qr_src=qr_src, error=error)

@app.route("/<short_code>")
def redirect_short_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    else:
        return abort(404)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
