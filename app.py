from flask import Flask, render_template, request

import hashlib
import sqlite3
import pyotp

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

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password_hash,secret_key) VALUES(?,?,?)",
            (username, password_hash, secret_key)
        )

        conn.commit()
        conn.close()

        return f"""
        User Registered Successfully <br><br>

        Username: {username} <br>
        Secret Key: {secret_key}
        """

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)