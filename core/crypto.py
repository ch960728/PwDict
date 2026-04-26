from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
ITERATIONS = 100_000

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    # 1. salt가 None이면 os.urandom으로 새로 생성
    # 2. PBKDF2HMAC 객체 생성 (algorithm, length, salt, iterations 인자 필요)
    # 3. kdf.derive(password.encode()) 로 키 생성
    # 4. (key, salt) 반환
    if not salt:
        salt = os.urandom(SALT_SIZE)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS
    )
    key = kdf.derive(password.encode())
    return key, salt

def encrypt(key: bytes, plaintext: bytes) -> bytes:
    nonce = os.urandom(NONCE_SIZE)          # 매번 랜덤 12바이트 — 같은 데이터도 매번 다른 암호문 생성
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)  # AES-256-GCM 암호화, None = 추가 인증 데이터 없음
    return nonce + ciphertext               # nonce를 앞에 붙여 반환 — 복호화 때 분리해서 사용

def decrypt(key: bytes, data: bytes) -> bytes:
    nonce = data[:NONCE_SIZE]               # 앞 12바이트가 nonce
    ciphertext = data[NONCE_SIZE:]          # 나머지가 실제 암호문 + GCM 인증 태그
    return AESGCM(key).decrypt(nonce, ciphertext, None)  # 키 불일치 시 InvalidTag 예외 발생
