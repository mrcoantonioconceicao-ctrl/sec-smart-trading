import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SENHA_MESTRA_PADRAO = "NOLAN_SEC_MASTER_KEY_2026"
SALT_FIXO = b"sec_smart_trading_salt_v1"

def derivar_chave(senha: str = SENHA_MESTRA_PADRAO, salt: bytes = SALT_FIXO) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(senha.encode())

def cifrar_dados(dados_dict: dict) -> bytes:
    chave = derivar_chave()
    aesgcm = AESGCM(chave)
    nonce = os.urandom(12)
    plaintext = json.dumps(dados_dict).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # Retorna o nonce concatenado com o ciphertext
    return nonce + ciphertext

def decifrar_dados(payload_binario: bytes) -> dict:
    chave = derivar_chave()
    aesgcm = AESGCM(chave)
    nonce = payload_binario[:12]
    ciphertext = payload_binario[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode('utf-8'))
