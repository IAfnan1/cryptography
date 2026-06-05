import sqlite3
import time

from security import encrypt_secret, decrypt_secret


def create_database():

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        encrypted_secret BLOB NOT NULL,
        failed_attempts INTEGER DEFAULT 0,
        lock_until INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS used_otps (
        username TEXT NOT NULL,
        otp TEXT NOT NULL,
        timestamp INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

    print("Database Created Successfully")


def add_user(username, password_hash, secret_key):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    encrypted_secret = encrypt_secret(secret_key)

    cursor.execute(
        """
        INSERT INTO users
        (username, password_hash, encrypted_secret)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, encrypted_secret)
    )

    conn.commit()
    conn.close()

    print("User Added Successfully")


def get_user(username):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def get_secret_key(username):

    user = get_user(username)

    if user is None:
        return None

    encrypted_secret = user[2]

    return decrypt_secret(encrypted_secret)


def increase_failed_attempts(username):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET failed_attempts = failed_attempts + 1
        WHERE username = ?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


def reset_failed_attempts(username):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET failed_attempts = 0
        WHERE username = ?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


def get_failed_attempts(username):

    user = get_user(username)

    if user is None:
        return None

    return user[3]


def lock_account(username, minutes=5):

    lock_until = int(time.time()) + (minutes * 60)

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET lock_until = ?
        WHERE username = ?
        """,
        (lock_until, username)
    )

    conn.commit()
    conn.close()


def get_lock_until(username):

    user = get_user(username)

    if user is None:
        return None

    return user[4]


def is_account_locked(username):

    lock_until = get_lock_until(username)

    if lock_until is None:
        return False

    current_time = int(time.time())

    return current_time < lock_until


def store_used_otp(username, otp, timestamp):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO used_otps
        (username, otp, timestamp)
        VALUES (?, ?, ?)
        """,
        (username, otp, timestamp)
    )

    conn.commit()
    conn.close()


def is_used_otp(username, otp):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM used_otps
        WHERE username = ?
        AND otp = ?
        """,
        (username, otp)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


if __name__ == "__main__":
    create_database()