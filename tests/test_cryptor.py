import os
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from utils.cryptor import generate_password, encrypt_data, decrypt_data


def test_generate_password():
    # Cobre a função generate_password()
    password = generate_password()
    password_2 = generate_password()

    assert isinstance(password, str)
    assert len(password) == 50
    # Garante que a aleatoriedade está funcionando (senhas geradas sequencialmente devem ser diferentes)
    assert password != password_2


def test_decrypt_data_invalid_tag():
    # Cobre o "except InvalidTag:"
    key = AESGCM.generate_key(bit_length=256)  # Chave válida de 32 bytes
    associated_data = b"test_context"
    data = {"secret": "my_password"}

    # Criptografamos dados corretamente
    iv, encrypted_data = encrypt_data(key, data, associated_data)

    # 1. Testando com uma chave diferente (simulando chave errada)
    wrong_key = AESGCM.generate_key(bit_length=256)
    with pytest.raises(ValueError, match="Invalid key or Corrupted data."):
        decrypt_data(wrong_key, iv, encrypted_data, associated_data)

    # 2. Testando com os dados corrompidos (simulando alteração indevida no banco)
    corrupted_data = bytearray(encrypted_data)
    corrupted_data[0] ^= 0xFF  # Inverte um bit do dado criptografado
    with pytest.raises(ValueError, match="Invalid key or Corrupted data."):
        decrypt_data(key, iv, bytes(corrupted_data), associated_data)


def test_decrypt_data_invalid_json():
    # Cobre o "except json.JSONDecodeError:"
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    associated_data = b"test_context"

    # Criptografamos manualmente um texto comum (não formatado como dicionário/JSON)
    not_json_bytes = b"just a regular string, not a dictionary"
    encrypted_bad_json = aesgcm.encrypt(iv, not_json_bytes, associated_data)

    # A descriptografia do AESGCM vai funcionar, mas o json.loads() vai falhar
    with pytest.raises(ValueError, match="Decrypted data is not valid JSON."):
        decrypt_data(key, iv, encrypted_bad_json, associated_data)
