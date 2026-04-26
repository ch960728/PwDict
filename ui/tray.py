import threading
import pystray
from PIL import Image, ImageDraw

class TrayApp:
    def __init__(self, on_open, on_lock, on_export, on_import, on_quit):
        self._on_open = on_open     # 트레이 "열기" 클릭 시
        self._on_lock = on_lock     # 트레이 "잠금" 클릭 시
        self._on_export = on_export # 트레이 "내보내기" 클릭 시
        self._on_import = on_import # 트레이 "가져오기" 클릭 시
        self._on_quit = on_quit     # 트레이 "종료" 클릭 시
        self._icon = None

    def _create_image(self) -> Image.Image:
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))    # 투명 배경 64x64
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, 60, 60], fill=(70, 130, 180))  # 파란 원
        draw.text((22, 18), "P", fill=(255, 255, 255))      # 흰색 "P" 텍스트
        return img

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("열기", lambda _, _item: self._on_open()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("내보내기", lambda _, _item: self._on_export()),
            pystray.MenuItem("가져오기", lambda _, _item: self._on_import()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("잠금", lambda _, _item: self._on_lock()),
            pystray.MenuItem("종료", lambda _, _item: self._quit()),
        )

    def _quit(self):
        self._on_quit()
        if self._icon:
            self._icon.stop()   # 트레이 아이콘 제거 및 run() 블로킹 해제

    def run(self):
        self._icon = pystray.Icon(
            "PwDict",
            self._create_image(),
            "PwDict",           # 마우스 오버 시 표시되는 툴팁
            menu=self._build_menu(),
        )
        self._icon.run()        # 블로킹 — 트레이가 종료될 때까지 여기서 멈춤

    def run_in_thread(self):
        t = threading.Thread(target=self.run, daemon=True)  # daemon=True: 메인 스레드 종료 시 같이 종료
        t.start()
