from flask import Flask, render_template, request

import hashlib
import sqlite3
import pyotp
import qrcode

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        password_hash = hashlib.sha256(
            password.encode()
        ).hexdigest()

        secret_key = pyotp.random_base32()

        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=username,
            issuer_name="CryptographyProject"
        )

        qr = qrcode.make(totp_uri)
        qr.save(f"static/{username}_qr.png")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password_hash,secret_key) VALUES(?,?,?)",
            (username, password_hash, secret_key)
        )

        conn.commit()
        conn.close()

        return f"""
         <h2>User Registered Successfully</h2>

         <p>Scan this QR Code using Google Authenticator</p>

         <img src="/static/{username}_qr.png" width="250">
         """

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)