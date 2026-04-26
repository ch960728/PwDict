import customtkinter as ctk
from core.vault import Vault
from core.session import Session
from ui.tray import TrayApp
from ui.unlock import UnlockWindow
from ui.search import SearchWindow
from ui.entry_form import EntryFormWindow

VAULT_PATH = "data/vault.dat"
AUTO_LOCK_MINUTES = 5

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PwDictApp:
    def __init__(self):
        self._vault = Vault(VAULT_PATH)
        self._session = Session(self._vault, timeout_minutes=AUTO_LOCK_MINUTES)
        self._session.on_lock = self._on_auto_lock  # 자동잠금 발생 시 UI 갱신 연결

        self._root = ctk.CTk()
        self._root.geometry("1x1+-10000+-10000")    # 화면 밖으로 이동 (withdraw 시 CTkToplevel도 숨어버리는 문제 방지)
        self._root.overrideredirect(True)           # 타이틀바 제거

        self._search_win: SearchWindow | None = None
        self._unlock_win: UnlockWindow | None = None

        self._tray = TrayApp(
            on_open=self._open,
            on_lock=self._lock,
            on_quit=self._quit,
        )

    def run(self):
        self._tray.run_in_thread()  # 트레이를 백그라운드 스레드로 실행
        self._show_unlock()         # 시작 시 마스터 패스워드 창 표시
        self._root.mainloop()       # 메인 스레드에서 tkinter 이벤트 루프 실행

    # ── 창 표시 ───────────────────────────────────────────────────────────────

    def _show_unlock(self):
        if self._unlock_win and self._unlock_win.winfo_exists():
            return  # 이미 열려있으면 중복 생성 방지
        is_new = not self._vault.exists()
        self._unlock_win = UnlockWindow(
            is_new_vault=is_new,
            on_submit=self._handle_unlock,
        )

    def _show_search(self):
        if self._search_win and self._search_win.winfo_exists():
            self._search_win.show()     # 이미 있으면 숨김 해제
            return
        self._search_win = SearchWindow(
            session=self._session,
            on_add=self._open_add_form,
            on_edit=self._open_edit_form,
        )

    # ── 패스워드 검증 ─────────────────────────────────────────────────────────

    def _handle_unlock(self, password: str):
        if not self._vault.exists():
            # 최초 실행: 새 vault 생성
            self._vault.create(password)
            self._session.unlock(password)
            self._unlock_win.destroy()
            self._show_search()
        else:
            # 기존 vault: 패스워드 검증
            if self._session.unlock(password):
                self._unlock_win.destroy()
                self._show_search()
            else:
                self._unlock_win.show_error("패스워드가 올바르지 않습니다.")

    # ── 항목 폼 ───────────────────────────────────────────────────────────────

    def _open_add_form(self):
        EntryFormWindow(vault=self._vault, on_save=self._refresh_search, parent=self._search_win)

    def _open_edit_form(self, entry: dict):
        EntryFormWindow(vault=self._vault, on_save=self._refresh_search, parent=self._search_win, entry=entry)

    def _refresh_search(self):
        if self._search_win and self._search_win.winfo_exists():
            self._search_win._refresh()

    # ── 트레이 콜백 ───────────────────────────────────────────────────────────
    # pystray는 별도 스레드 → tkinter 조작은 root.after()로 메인 스레드에 위임

    def _open(self):
        self._root.after(0, self._open_from_tray)

    def _open_from_tray(self):
        if self._session.is_locked:
            self._show_unlock()
        else:
            self._show_search()

    def _lock(self):
        self._root.after(0, self._do_lock)

    def _do_lock(self):
        self._session.lock()
        if self._search_win and self._search_win.winfo_exists():
            self._search_win.withdraw()
        self._show_unlock()

    def _on_auto_lock(self):
        self._root.after(0, self._do_lock)  # session 타이머 스레드 → 메인 스레드 위임

    def _quit(self):
        self._root.after(0, self._root.destroy)


def main():
    app = PwDictApp()
    app.run()


if __name__ == "__main__":
    main()
