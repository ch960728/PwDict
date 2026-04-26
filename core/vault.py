import os
import shutil
import json
import uuid
from datetime import datetime
from core.crypto import derive_key, encrypt, decrypt
from cryptography.exceptions import InvalidTag


SALT_SIZE = 16

class Vault:
    def __init__(self, path: str):
        self.path = path                        # vault.dat 파일 경로 — exists(), unlock(), save()에서 사용
        self._key: bytes | None = None          # 복호화 키 — encrypt/decrypt에 사용, lock() 시 None으로 초기화
        self._salt: bytes | None = None         # 파일 앞 16바이트 — save() 시 파일 맨 앞에 기록, unlock() 시 파일에서 읽어옴
        self._entries: list[dict] = []          # 복호화된 항목 목록 — search/add/update/delete 대상, lock() 시 [] 초기화

    @property
    def is_unlocked(self) -> bool:
        return self._key is not None

    def exists(self) -> bool:
        # os.path.exists로 파일 존재 여부 반환
        if os.path.exists(self.path):
            return True

    def create(self, master_password: str) -> None:
        # derive_key로 key, salt 생성
        # _entries = [] 초기화
        # save() 호출
        key, salt = derive_key(master_password)
        self._key = key
        self._salt = salt
        self._entries = []
        self.save()

    def unlock(self, master_password: str) -> bool:
        # 파일 읽기 → salt 분리 → derive_key → decrypt → json.loads
        # 성공 시 _key, _salt, _entries 세팅, True 반환
        # InvalidTag 등 예외 시 False 반환
        if not self.exists():
            return False
        with open(self.path, "rb") as f:
            data = f.read()
        salt = data[:SALT_SIZE]
        key, _ = derive_key(master_password, salt)
        try:
            decrypted = decrypt(key, data[SALT_SIZE:]) 
        except InvalidTag:
            return False
        data = json.loads(decrypted.decode())
        self._key = key
        self._salt = salt
        self._entries = data["entries"]
        return True

    def lock(self) -> None:
        # _key, _salt, _entries 초기화
        self._key = None
        self._salt = None
        self._entries = []

    def save(self) -> None:
        # json.dumps(_entries) → encode → encrypt → salt + 암호문 파일에 저장
        plaintext = json.dumps({"entries": self._entries}).encode()  # dict → JSON 문자열 → bytes
        encrypted = encrypt(self._key, plaintext)                    # AES-256-GCM 암호화
        with open(self.path, "wb") as f:
            f.write(self._salt + encrypted)                          # [salt 16B][nonce+암호문] 순서로 저장


    def search(self, query: str) -> list[dict]:
        # query.lower()가 entry["service"].lower()에 포함되면 반환
        if query.lower() == "":
            return self._entries
        results = []
        for entry in self._entries:
            if query.lower() in entry["service"].lower():
                results.append(entry)
        return results
        

    def add_entry(self, service, username, password, url, memo) -> dict:
        now = datetime.now().isoformat()
        entry = {
            "id": str(uuid.uuid4()),    # 항목 고유 식별자 — update/delete 시 찾는 기준
            "service": service,
            "username": username,
            "password": password,
            "url": url,
            "memo": memo,
            "created_at": now,
            "updated_at": now,
        }
        self._entries.append(entry)
        self.save()
        return entry

    def update_entry(self, entry_id: str, **kwargs) -> None:
        for entry in self._entries:
            if entry["id"] == entry_id:
                for k, v in kwargs.items():
                    if k in entry:          # 존재하는 필드만 업데이트 (id, created_at 등 덮어쓰기 방지)
                        entry[k] = v
                entry["updated_at"] = datetime.now().isoformat()
                break
        self.save()

    def delete_entry(self, entry_id: str) -> None:
        self._entries = [e for e in self._entries if e["id"] != entry_id]  # id 불일치 항목만 남기기
        self.save()

    def export(self, dest_path: str) -> None:
        shutil.copy2(self.path, dest_path)  # vault.dat를 선택한 경로에 그대로 복사

    def import_from(self, src_path: str, src_password: str) -> bool:
        # 외부 vault 파일을 src_password로 복호화 → 항목 전부 현재 vault에 append
        try:
            with open(src_path, "rb") as f:
                raw = f.read()
            salt = raw[:SALT_SIZE]
            key, _ = derive_key(src_password, salt)
            plaintext = decrypt(key, raw[SALT_SIZE:])
            data = json.loads(plaintext.decode())
            for entry in data["entries"]:
                entry["id"] = str(uuid.uuid4())     # uuid 충돌 방지를 위해 새 id 발급
                self._entries.append(entry)
            self.save()
            return True
        except (InvalidTag, FileNotFoundError, json.JSONDecodeError):
            return False