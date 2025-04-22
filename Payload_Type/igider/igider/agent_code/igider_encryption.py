import base64
import os
import logging
from typing import Tuple, Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hmac
import time
import uuid

#logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class EncryptionModule:
    def __init__(self, key_lifetime=3600):
        self.session_key = os.urandom(32)  # AES-256 key
        self.aes_iv_size = 16  # AES block size for IV
        self.key_lifetime = key_lifetime  # Max time before session key rotation
        self.last_key_change = time.time()  # Track when the session key was generated
        self.session_id = uuid.uuid4().hex  # Unique session ID for each agent run

    def check_and_rotate_key(self):
        """Rotate the session key after a defined period."""
        if time.time() - self.last_key_change > self.key_lifetime:
            self.session_key = os.urandom(32)  # New AES key
            self.last_key_change = time.time()  # Reset the key timer
            logging.debug(f"Session key rotated. New session key generated.")

    def generate_keys(self) -> Tuple[bytes, bytes]:
        """Generate RSA key pair for secure key exchange"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        logging.debug("Generated new RSA key pair.")
        return private_key, public_key

    def encrypt(self, data: str) -> str:
        """Encrypt data using AES-256-CBC with the session key"""
        self.check_and_rotate_key()  # Rotate the key periodically
        iv = os.urandom(self.aes_iv_size)  # Random IV for each encryption

        # Pad the data to the AES block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        # Create AES cipher
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV and encrypted data, encode to base64 for easy transmission
        result = base64.b64encode(iv + encrypted_data).decode()
        logging.debug(f"Data encrypted with AES-256-CBC.")
        return result

    def decrypt(self, data: str) -> str:
        """Decrypt data using AES-256-CBC with the session key"""
        self.check_and_rotate_key()  # Rotate the key periodically
        raw_data = base64.b64decode(data.encode())  # Decode base64

        iv = raw_data[:self.aes_iv_size]  # Extract IV
        encrypted_data = raw_data[self.aes_iv_size:]  # Extract encrypted data

        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Unpad the data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        logging.debug(f"Data decrypted with AES-256-CBC.")
        return data.decode()

    def encrypt_with_public_key(self, data: str, public_key_pem: bytes) -> str:
        """Encrypt data using an RSA public key for secure communication"""
        public_key = load_pem_public_key(public_key_pem, backend=default_backend())

        encrypted_data = public_key.encrypt(
            data.encode(),
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_data_b64 = base64.b64encode(encrypted_data).decode()
        logging.debug(f"Data encrypted with RSA public key.")
        return encrypted_data_b64

    def decrypt_with_private_key(self, data: str, private_key_pem: bytes, password: bytes = None) -> str:
        """Decrypt data using an RSA private key"""
        try:
            encrypted_data = base64.b64decode(data.encode())
            private_key = load_pem_private_key(private_key_pem, password=password, backend=default_backend())

            decrypted_data = private_key.decrypt(
                encrypted_data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            logging.debug(f"Data decrypted with RSA private key.")
            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Error decrypting with RSA: {e}")
            return None

    def derive_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """Derive a symmetric key from a password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = kdf.derive(password.encode())
        logging.debug(f"Password-derived symmetric key generated.")
        return key, salt

    def compute_hmac(self, data: str, key: bytes = None) -> str:
        """Compute HMAC for data integrity verification"""
        if key is None:
            key = self.session_key

        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data.encode())
        signature = h.finalize()

        logging.debug(f"HMAC computed for integrity check.")
        return base64.b64encode(signature).decode()

    def verify_hmac(self, data: str, signature: str, key: bytes = None) -> bool:
        """Verify HMAC signature"""
        if key is None:
            key = self.session_key

        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data.encode())

        try:
            h.verify(base64.b64decode(signature.encode()))
            logging.debug(f"HMAC signature verified successfully.")
            return True
        except Exception as e:
            logging.error(f"HMAC verification failed: {e}")
            return False

    def generate_session_nonce(self) -> str:
        """Generate a unique nonce for session security"""
        return uuid.uuid4().hex