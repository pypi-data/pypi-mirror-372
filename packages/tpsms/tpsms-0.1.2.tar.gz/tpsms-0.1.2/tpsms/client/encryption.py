from base64 import b64encode, b64decode
from .cipher.hash import hash_md5
from .cipher.cipher import create_cipher
from urllib.parse import urlencode

def create_encryption(modulus, exponent, username="admin", password=None):
    cipher = create_cipher(modulus=modulus, exponent=exponent)
    hash_value = hash_md5(f"{username}{password}").hex()

    def encrypt(data, sequence, signature=None):
        if signature is None:
            signature = {}
        encrypted_data = cipher["aes_encrypt"](data)
        data_base64 = b64encode(encrypted_data).decode("ascii")  # Proper base64 encoding
        signed = {k: v for k, v in signature.items()}
        signed["h"] = hash_value
        signed["s"] = str(sequence + len(data_base64))
        sign_string = urlencode(signed)

        sign_bytes = sign_string.encode("utf-8")
        encrypted_signature = cipher["rsa_encrypt"](sign_bytes)

        return {
            "data": data_base64,
            "sign": encrypted_signature.hex(),
        }

    def decrypt(data):
        return cipher["aes_decrypt"](b64decode(data)).decode("utf-8")

    return {
        "key": cipher["key"],
        "iv": cipher["iv"],
        "encrypt": encrypt,
        "decrypt": decrypt,
    }