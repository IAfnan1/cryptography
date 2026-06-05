
from cryptography.fernet import Fernet
from cryptography.fernet import Fernet

AES_KEY = b'KcAkTsFwO30wIRl56xkhuxxe1rO_yWYPepymEMAPCcE='

cipher = Fernet(AES_KEY)

def encrypt_secret(secret_key):

    encrypted_secret = cipher.encrypt(
        secret_key.encode()
    )

    return encrypted_secret

def decrypt_secret(encrypted_secret):

    decrypted_secret = cipher.decrypt(
        encrypted_secret
    )

    return decrypted_secret.decode()

