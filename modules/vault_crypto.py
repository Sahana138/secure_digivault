# file: modules/vault_crypto.py

import os
from cryptography.fernet import Fernet

# CONFIGURATION

KEY_FILE = "vault.key"

# KEY MANAGEMENT

def load_key():
    """
    Load encryption key or generate one if missing.
    """

    if not os.path.exists(KEY_FILE):

        # Create new key for first-time vault setup
        key = Fernet.generate_key()

        with open(KEY_FILE,"wb") as f:
            f.write(key)

    else:

        # Load existing vault encryption key
        with open(KEY_FILE,"rb") as f:
            key = f.read()

    return key

# Fernet instance initialized once for reuse
fernet = Fernet(load_key())

# FILE ENCRYPTION

def encrypt_file(filepath):
    """
    Encrypt file contents in-place.
    """

    try:

        with open(filepath,"rb") as f:
            data = f.read()

        encrypted_data = fernet.encrypt(data)

        with open(filepath,"wb") as f:
            f.write(encrypted_data)

    except Exception as e:
        print("Encryption failed:",e)

# FILE DECRYPTION

def decrypt_file(filepath):
    """
    Decrypt file contents in-place.
    """

    try:

        with open(filepath,"rb") as f:
            data = f.read()

        decrypted_data = fernet.decrypt(data)

        with open(filepath,"wb") as f:
            f.write(decrypted_data)

    except Exception as e:
        print("Decryption failed:",e)