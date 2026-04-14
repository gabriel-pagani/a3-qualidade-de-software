import os, secrets, json
from argon2 import PasswordHasher, low_level
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


ARGON2_CONFIG = {
    "time_cost": 12,
    "memory_cost": 262144,
    "parallelism": 12,
    "hash_len": 32,
    "salt_len": 32
}

password_hasher = PasswordHasher(**ARGON2_CONFIG)


def generate_hash(master_password: str) -> str:
    return password_hasher.hash(master_password)


def verify_hash(master_password_hash: str, master_password: str) -> bool:
    try:
        return password_hasher.verify(master_password_hash, master_password)
    except Exception:
        return False


def derive_master_password(master_password: str, salt: bytes) -> bytes:
    return low_level.hash_secret_raw(
        secret=(master_password).encode(),
        salt=salt,
        time_cost=ARGON2_CONFIG["time_cost"],
        memory_cost=ARGON2_CONFIG["memory_cost"],
        parallelism=ARGON2_CONFIG["parallelism"],
        hash_len=ARGON2_CONFIG["hash_len"],
        type=low_level.Type.ID
    )


def generate_password() -> str:
    characters = r"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&-_=~^,.<>;:()[]{}"
    password = ''.join(secrets.choice(characters) for _ in range(50))
    return password


def encrypt_data(derived_master_password: bytes, data: dict, associated_data: bytes) -> tuple[bytes, bytes]:
    aesgcm = AESGCM(derived_master_password)
    iv = os.urandom(12)
    serialized_data = json.dumps(data).encode('utf-8')
    encrypted_data = aesgcm.encrypt(iv, serialized_data, associated_data)
    return (iv, encrypted_data)


def decrypt_data(derived_master_password: bytes, iv: bytes, encrypted_data: bytes, associated_data: bytes) -> dict:
    try:
        aesgcm = AESGCM(derived_master_password)
        decrypted_bytes = aesgcm.decrypt(iv, encrypted_data, associated_data)
        decrypted_data = json.loads(decrypted_bytes.decode('utf-8'))
        return decrypted_data
        
    except InvalidTag:
        raise ValueError("Invalid key or Corrupted data.")
    except json.JSONDecodeError:
        raise ValueError("Decrypted data is not valid JSON.")
