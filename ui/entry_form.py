import customtkinter as ctk
from core.vault import Vault

class EntryFormWindow(ctk.CTkToplevel):
    def __init__(self, vault: Vault, on_save, parent=None, entry: dict = None):
        super().__init__(parent)    # 부모 창 위에 뜨도록 명시
        self._vault = vault
        self._on_save = on_save     # 저장/삭제 후 검색창 _refresh() 호출용
        self._entry = entry         # None이면 추가 모드, dict이면 수정 모드
        self._pw_visible = False

        title = "항목 수정" if entry else "항목 추가"
        self.title(f"PwDict — {title}")
        self.geometry("360x400")
        self.resizable(False, False)
        self._center()
        self.after(50, self._bring_to_front)

        fields = ctk.CTkFrame(self, fg_color="transparent")
        fields.pack(fill="both", expand=True, padx=20, pady=16)

        # 입력 필드 5개
        self._service  = self._add_field(fields, "서비스명 *", entry.get("service", "")  if entry else "")
        self._username = self._add_field(fields, "아이디",    entry.get("username", "") if entry else "")
        self._url      = self._add_field(fields, "URL",       entry.get("url", "")      if entry else "")
        self._memo     = self._add_field(fields, "메모",      entry.get("memo", "")     if entry else "")

        # 비밀번호 행 (입력란 + 토글 버튼)
        pw_row = ctk.CTkFrame(fields, fg_color="transparent")
        pw_row.pack(fill="x", pady=4)
        ctk.CTkLabel(pw_row, text="비밀번호 *", width=80, anchor="w").pack(side="left")
        self._pw_entry = ctk.CTkEntry(pw_row, show="*", width=180)
        self._pw_entry.pack(side="left", padx=(0, 4))
        if entry:
            self._pw_entry.insert(0, entry.get("password", ""))
        ctk.CTkButton(pw_row, text="👁", width=36, command=self._toggle_pw).pack(side="left")

        # 오류 메시지
        self._error_label = ctk.CTkLabel(self, text="", text_color="red")
        self._error_label.pack()

        # 하단 버튼
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(btn_frame, text="저장", command=self._save).pack(side="left", expand=True, padx=4)
        ctk.CTkButton(btn_frame, text="취소", command=self.destroy, fg_color="gray").pack(side="left", expand=True, padx=4)
        if entry:   # 수정 모드일 때만 삭제 버튼 표시
            ctk.CTkButton(btn_frame, text="삭제", command=self._delete, fg_color="#c0392b").pack(side="left", expand=True, padx=4)

    def _add_field(self, parent, label: str, value: str) -> ctk.CTkEntry:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label, width=80, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(row, width=220)
        entry.insert(0, value)      # 수정 모드 시 기존 값 채워넣기
        entry.pack(side="left")
        return entry

    def _bring_to_front(self):
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()
        self.grab_set()     # 이 창이 닫힐 때까지 다른 창 입력 차단 + 포커스 강제 유지

    def _toggle_pw(self):
        self._pw_visible = not self._pw_visible
        self._pw_entry.configure(show="" if self._pw_visible else "*")

    def _center(self):
        self.update_idletasks()
        w, h = 360, 400
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _save(self):
        service = self._service.get().strip()
        password = self._pw_entry.get()
        if not service or not password:
            self._error_label.configure(text="서비스명과 비밀번호는 필수입니다.")
            return
        if self._entry:
            self._vault.update_entry(
                self._entry["id"],
                service=service,
                username=self._username.get().strip(),
                password=password,
                url=self._url.get().strip(),
                memo=self._memo.get().strip(),
            )
        else:
            self._vault.add_entry(
                service,
                self._username.get().strip(),
                password,
                self._url.get().strip(),
                self._memo.get().strip(),
            )
        self._on_save()     # 검색창 목록 갱신
        self.destroy()

    def _delete(self):
        self._vault.delete_entry(self._entry["id"])
        self._on_save()     # 검색창 목록 갱신
        self.destroy()
