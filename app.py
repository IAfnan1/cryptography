from flask import Flask, render_template, request
import hashlib
import pyotp
import qrcode

from database import (

    create_database,

    add_user,

    get_secret_key

)

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

          <img src="/static/{username}_qr.png" width="250" alt="QR code for two-factor authentication setup with {username} account on CryptographyProject. Scan this code using Google Authenticator or similar authenticator app to enable TOTP-based login security.">

          <br><br>

          <a href="/totp/{username}">
           View Generated TOTP
          </a>
          """
    return render_template("register.html")

@app.route("/totp/<username>")
def show_totp(username):

    secret_key = get_secret_key(username)

    if secret_key is None:
        return "<h2>User Not Found</h2>"

    totp = pyotp.TOTP(secret_key)

    current_code = totp.now()

    return f"""
    <h2>Generated TOTP Code</h2>

    <p>Username: {username}</p>

    <h3>Current OTP: {current_code}</h3>
    """


if __name__ == "__main__":
    app.run(debug=True)