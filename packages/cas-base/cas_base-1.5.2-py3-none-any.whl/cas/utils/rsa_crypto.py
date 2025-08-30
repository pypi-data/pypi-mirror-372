import os
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

"""
# 示例使用
rsa_crypto = RSACrypto()

# 生成并保存密钥对
rsa_crypto.generate_keys()

# 加载密钥对
rsa_crypto.load_keys()

# 加密数据
data = "重要的数据"
encrypted_data = rsa_crypto.encrypt_data(data)
print("加密数据:", encrypted_data)

# 解密数据
decrypted_data = rsa_crypto.decrypt_data(encrypted_data)
print("解密数据:", decrypted_data)

# 签名数据
signature = rsa_crypto.sign_data(data)
print("签名:", signature)

# 验证签名
is_valid = rsa_crypto.verify_signature(data, signature)
print("签名验证结果:", is_valid)
"""


class RSACrypto:
    def __init__(self, private_key_file="config/cer/rsa_private_key.pem", public_key_file="config/cer/rsa_public_key.pem"):
        self.private_key_file = private_key_file
        self.public_key_file = public_key_file
        self.private_key = None
        self.public_key = None

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.private_key_file), exist_ok=True)

    def generate_keys(self):
        # Generate a new private key and corresponding public key
        key = RSA.generate(2048)
        self.private_key = key
        self.public_key = key.publickey()

        # Save the private key to a file
        with open(self.private_key_file, "wb") as f:
            f.write(self.private_key.export_key("PEM"))

        # Save the public key to a file
        with open(self.public_key_file, "wb") as f:
            f.write(self.public_key.export_key("PEM"))

    def load_keys(self):
        if os.path.exists(self.private_key_file):
            # Load the private key from a file
            with open(self.private_key_file, "rb") as f:
                self.private_key = RSA.import_key(f.read())

        if os.path.exists(self.public_key_file):
            # Load the public key from a file
            with open(self.public_key_file, "rb") as f:
                self.public_key = RSA.import_key(f.read())
                
    def load_private_key(self, private_str: str):
        self.private_key = RSA.import_key(private_str)

    def load_public_key(self, public_str: str):
        self.public_key = RSA.import_key(public_str)

    def encrypt_data(self, data):
        if not self.public_key:
            raise ValueError("Public key is not loaded.")

        if isinstance(data, str):
            data = data.encode("utf-8")  # Ensure data is bytes

        cipher = PKCS1_OAEP.new(self.public_key)
        encrypted_data = cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt_data(self, encrypted_data):
        if not self.private_key:
            raise ValueError("Private key is not loaded.")

        encrypted_data = base64.b64decode(encrypted_data)

        cipher = PKCS1_OAEP.new(self.private_key)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode("utf-8")

    def _normalize_data(self, data):
        if isinstance(data, str):
            # 去除 BOM，统一换行符
            data = data.replace('\ufeff', '').replace('\r\n', '\n').replace('\r', '\n')
            return data.encode('utf-8')
        return data

    def sign_data(self, data):
        if not self.private_key:
            raise ValueError("Private key is not loaded.")
        data = self._normalize_data(data)
        h = SHA256.new(data)
        signature = pkcs1_15.new(self.private_key).sign(h)
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        return signature_b64

    def verify_signature(self, data, signature):
        if not self.public_key:
            raise ValueError("Public key is not loaded.")
        data = self._normalize_data(data)
        try:
            signature_bytes = base64.b64decode(signature)
        except Exception as e:
            return False
            
        h = SHA256.new(data)
        try:
            pkcs1_15.new(self.public_key).verify(h, signature_bytes)
            return True
        except (ValueError, TypeError) as e:
            return False
