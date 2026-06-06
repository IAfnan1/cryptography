from flask import Flask, render_template, request
import hashlib
import pyotp
import qrcode
import time

from database import (
    create_database,
    add_user,
    get_user,
    get_secret_key,
    increase_failed_attempts,
    reset_failed_attempts,
    is_account_locked,
    lock_account,
    store_used_otp,
    is_used_otp
)

MAX_FAILED = 5
LOCK_MINUTES = 5

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

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]
    otp = request.form["otp"]

    if is_account_locked(username):
        return "Account Locked. Try again later."

    user = get_user(username)

    if user is None:
        return "User Not Found"

    stored_password_hash = user[1]

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    if password_hash != stored_password_hash:

        increase_failed_attempts(username)

        if user[3] + 1 >= MAX_FAILED:
            lock_account(username, LOCK_MINUTES)

            return (
                f"Account Locked due to failed attempts. "
                f"Try again in {LOCK_MINUTES} minutes."
            )

        return "Invalid Password"

    secret_key = get_secret_key(username)

    if secret_key is None:
        return "Secret Key Not Found"

    totp = pyotp.TOTP(secret_key)

    current_time = int(time.time())

    if is_used_otp(username, otp):
        return "OTP Already Used"

    if totp.verify(otp):

        reset_failed_attempts(username)

        store_used_otp(
            username,
            otp,
            current_time
        )

        return "Access Granted"

    increase_failed_attempts(username)

    return "Invalid OTP"

if __name__ == "__main__":
    app.run(debug=True)