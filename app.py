from flask import Flask, render_template, request, redirect, abort
import string
import random
from database import create_table, insert_url, get_long_url

app = Flask(__name__)
create_table()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form.get("long_url")
        if not long_url:
            return render_template("index.html", error="Inserisci un URL valido.")
        short_code = generate_short_code()
        try:
            insert_url(short_code, long_url)
        except Exception:
            short_code = generate_short_code()
            insert_url(short_code, long_url)
        short_url = request.host_url + short_code
        return render_template("index.html", short_url=short_url)
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
