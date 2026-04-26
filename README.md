# PwDict

로컬 파일 기반 비밀번호 관리자. 시스템 트레이에 상주하며 AES-256-GCM으로 암호화하여 저장합니다.

## 기능

- 시스템 트레이 상주 — 트레이 아이콘 클릭으로 빠르게 열기
- AES-256-GCM 암호화 + PBKDF2 키 도출 (마스터 패스워드 방식)
- 서비스명 실시간 검색
- 비밀번호 클립보드 복사 / 마스킹 토글
- 항목 추가 / 수정 / 삭제
- 일정 시간 미사용 시 자동 잠금 (기본 5분)
- vault 파일 내보내기 / 가져오기 (다른 PC 간 이전)


## 설치 및 실행

### 실행 파일 (Windows)

[Releases](https://github.com/ch960728/PwDict/releases) 에서 `PwDict.exe` 다운로드 후 실행.

### 소스에서 실행

**요구사항:** Python 3.12+

```bash
git clone https://github.com/ch960728/PwDict.git
cd PwDict
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 빌드

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name PwDict main.py
```

`dist/PwDict.exe` 생성됨.

## 사용법

1. 첫 실행 시 마스터 패스워드 설정 (분실 시 복구 불가)
2. 시스템 트레이 아이콘 우클릭으로 메뉴 접근
3. 검색창에서 서비스명 입력 → 실시간 필터링
4. `+ 추가` 버튼으로 새 항목 등록

### 내보내기 / 가져오기

- **내보내기**: 트레이 → 내보내기 → 저장 위치 선택
- **가져오기**: 트레이 → 가져오기 → 파일 선택 → 원본 마스터 패스워드 입력 → 현재 vault에 병합

## 기술 스택

| 항목 | 내용 |
|---|---|
| Language | Python 3.12 |
| UI | customtkinter |
| Tray | pystray |
| 암호화 | cryptography (AES-256-GCM, PBKDF2-HMAC-SHA256) |
| 이미지 | Pillow |

## 보안

- 마스터 패스워드 분실 시 데이터 복구 불가
- 복호화된 데이터는 메모리에만 존재, 평문 파일 저장 없음
- `data/vault.dat` 는 `.gitignore` 에 포함 (커밋되지 않음)
