from flask import Flask, render_template, request
import hashlib
import pyotp
import qrcode

from database import create_database, add_user

app = Flask(__name__)

create_database()


@app.route("/", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        password_hash = hashlib.sha256(
            password.encode()
        ).hexdigest()

        secret_key = pyotp.random_base32()

        totp_uri = pyotp.TOTP(secret_key).provisioning_uri(
            name=username,
            issuer_name="CryptographyProject"
        )

        qr = qrcode.make(totp_uri)
        qr.save(f"static/{username}_qr.png")

        add_user(
            username,
            password_hash,
            secret_key
        )

        return f"""
        <h2>User Registered Successfully</h2>

        <p>Scan this QR Code using Google Authenticator</p>

        <img src="/static/{username}_qr.png" width="250">
        """

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)