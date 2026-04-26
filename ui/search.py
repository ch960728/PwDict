import customtkinter as ctk
from core.session import Session

class SearchWindow(ctk.CTkToplevel):
    def __init__(self, session: Session, on_add, on_edit):
        super().__init__()
        self._session = session
        self._on_add = on_add           # "+ 추가" 버튼 콜백
        self._on_edit = on_edit         # 항목 "수정" 버튼 콜백
        self._pw_visible: dict[str, bool] = {}  # 항목별 비밀번호 표시 상태

        self.title("PwDict")
        self.geometry("420x480")
        self.resizable(False, True)
        self._center()
        self.protocol("WM_DELETE_WINDOW", self.withdraw)    # X 버튼 시 숨기기 (종료 아님)

        # 검색창
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=12, pady=(12, 4))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh())  # 입력값 변경 시 자동 필터링
        search_entry = ctk.CTkEntry(search_frame, textvariable=self._search_var, placeholder_text="검색...", width=380)
        search_entry.pack()
        search_entry.focus()

        # 항목 목록 (스크롤 가능)
        self._list_frame = ctk.CTkScrollableFrame(self)
        self._list_frame.pack(fill="both", expand=True, padx=12, pady=4)

        # 하단 "+ 추가" 버튼
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(4, 12))
        ctk.CTkButton(bottom, text="+ 추가", width=80, command=self._on_add).pack(side="right")

        self._refresh()

    def _center(self):
        self.update_idletasks()
        w, h = 420, 480
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _refresh(self):
        # 기존 목록 전부 제거 후 재생성
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        self._pw_visible.clear()

        query = self._search_var.get()
        entries = self._session.vault.search(query)
        self._session.record_activity()     # 검색 시 자동잠금 타이머 갱신

        for entry in entries:
            self._render_row(entry)

    def _render_row(self, entry: dict):
        eid = entry["id"]
        self._pw_visible[eid] = False       # 초기 상태: 비밀번호 숨김

        row = ctk.CTkFrame(self._list_frame)
        row.pack(fill="x", pady=2)

        # 왼쪽: 서비스명 + 아이디 + 비밀번호
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        ctk.CTkLabel(info, text=entry["service"], font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=entry["username"], text_color="gray", anchor="w").pack(fill="x")
        pw_label = ctk.CTkLabel(info, text="••••••••", anchor="w")
        pw_label.pack(fill="x")

        # 오른쪽: 복사 / 토글 / 수정 버튼
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=8)

        def copy_pw(e=entry):
            self.clipboard_clear()
            self.clipboard_append(e["password"])
            self._session.record_activity()

        def toggle_pw(e=entry, lbl=pw_label, eid=eid):
            self._pw_visible[eid] = not self._pw_visible[eid]
            lbl.configure(text=e["password"] if self._pw_visible[eid] else "••••••••")
            self._session.record_activity()

        def edit(e=entry):
            self._on_edit(e)
            self._session.record_activity()

        ctk.CTkButton(btn_frame, text="복사", width=44, command=copy_pw).pack(pady=2)
        ctk.CTkButton(btn_frame, text="👁", width=44, command=toggle_pw).pack(pady=2)
        ctk.CTkButton(btn_frame, text="수정", width=44, command=edit).pack(pady=2)

    def show(self):
        self.deiconify()    # withdraw로 숨긴 창 다시 표시
        self._refresh()
        self.lift()         # 다른 창 위로 올리기
        self.focus()
