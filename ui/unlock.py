import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UnlockWindow(ctk.CTk):
    def __init__(self, is_new_vault: bool, on_submit):
        super().__init__()
        self._on_submit = on_submit
        self._is_new = is_new_vault

        self.title("PwDict — 잠금 해제")
        self.geometry("320x220")
        self.resizable(False, False)
        self._center()

        # 타이틀 라벨
        label_text = "새 Vault 생성" if is_new_vault else "마스터 패스워드 입력"
        ctk.CTkLabel(self, text=label_text, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 8))

        # 패스워드 입력란
        self._pw_entry = ctk.CTkEntry(self, show="*", width=240, placeholder_text="마스터 패스워드")
        self._pw_entry.pack(pady=4)
        self._pw_entry.bind("<Return>", lambda _e: self._handle_submit())  # 엔터키로 제출
        self._pw_entry.focus()

        # 신규 vault일 때만 확인 입력란 추가
        self._pw2_entry = None
        if is_new_vault:
            self._pw2_entry = ctk.CTkEntry(self, show="*", width=240, placeholder_text="패스워드 확인")
            self._pw2_entry.pack(pady=4)
            self._pw2_entry.bind("<Return>", lambda _e: self._handle_submit())

        # 오류 메시지 라벨 (평소엔 빈 텍스트)
        self._error_label = ctk.CTkLabel(self, text="", text_color="red")
        self._error_label.pack(pady=2)

        # 확인 버튼
        ctk.CTkButton(self, text="확인", command=self._handle_submit, width=240).pack(pady=8)

    def _center(self):
        self.update_idletasks()
        w, h = 320, 220
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _handle_submit(self):
        pw = self._pw_entry.get()
        if not pw:
            self.show_error("패스워드를 입력하세요.")
            return
        if self._is_new:
            pw2 = self._pw2_entry.get()
            if pw != pw2:
                self.show_error("패스워드가 일치하지 않습니다.")
                return
        self._on_submit(pw)     # 검증 통과 시 패스워드를 콜백으로 전달

    def show_error(self, msg: str):
        self._error_label.configure(text=msg)
