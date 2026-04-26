import time
import threading
from core.vault import Vault

class Session:
    def __init__(self, vault: Vault, timeout_minutes: int = 5):
        self.vault = vault
        self.timeout_seconds = timeout_minutes * 60
        self.on_lock = None             # 잠금 시 호출할 콜백 — UI에서 나중에 연결
        self._locked = True
        self._last_activity = 0.0
        self._timer: threading.Timer | None = None

    @property
    def is_locked(self) -> bool:
        # _locked 반환
        return self._locked

    def unlock(self, master_password: str) -> bool:
        # vault.unlock() 호출
        # 성공 시: _locked=False, record_activity(), _schedule_check() 호출, True 반환
        # 실패 시: False 반환
        if self.vault.unlock(master_password):  # vault.unlock()은 성공 True, 실패 False 반환
            self._locked = False
            self.record_activity()
            self._schedule_check()
            return True
        return False

    def lock(self) -> None:
        # _locked=True, vault.lock(), 타이머 취소
        # on_lock 콜백이 있으면 호출
        self._locked = True
        self.vault.lock()
        if self._timer:
            self._timer.cancel()
            self._timer = None
        if self.on_lock:                        # UI에서 on_lock = 콜백함수 로 연결하면 자동잠금 시 호출됨
            self.on_lock()

    def record_activity(self) -> None:
        self. _last_activity = time.time()

    def _check_timeout(self) -> None:
        # 이미 잠겼으면 return
        # time.time() - _last_activity >= timeout_seconds 이면 lock()
        # 아니면 _schedule_check() 재호출
        if self._locked:
            return
        if time.time() - self._last_activity >= self.timeout_seconds:
            self.lock()
        else: 
            self._schedule_check()

    def _schedule_check(self) -> None:
        # 기존 타이머 cancel()
        # 새 Timer(30, _check_timeout) 생성, daemon=True, start()
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(30, self._check_timeout)
        self._timer.daemon = True
        self._timer.start()
        
