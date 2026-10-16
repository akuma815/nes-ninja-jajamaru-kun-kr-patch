# 닌자 자자마루군 (NES) 한글화

첫 작업: 타이틀 로고 `닌자 자자마루군`.

## 폴더 역할

- `original/rom/`: 해시를 확인한 원본 보관 사본. 루트의 최초 원본도 보존.
- `config/`: 지원 원본과 확정된 자산 위치.
- `analysis/`: 역공학 결과. `raw/`는 원본에서 추출한 로컬 자료.
- `assets/title/`: 한글 로고 소스 및 조판 입력.
- `scripts/`: 조사·빌드·검증의 재현 진입점.
- `build/`: 재생성 가능한 로컬 ROM·프리뷰·보고서.
- `patches/`: ROM을 포함하지 않는 차분 패치.
- `qa/`: 정확한 빌드에 귀속된 실행·시각 증거.
- `docs/`: 현재 결론과 세션 인계.

재개 진입점: [docs/HANDOFF.md](docs/HANDOFF.md).

## 현재 결과

원본 로고 PNG 추출 → 내장 image_gen으로 한글 로고 생성 → 4색 NES 변환 → ROM 이식 후, 현재 `title_kr_menu_003`에서 `1인용 / 2인용` 메뉴까지 한글화했다. 끝의 작고 노란 군이 있는 로고는 002와 동일하다.

- 생성 원본: `assets/title/title_kr_ai_002_generated.png`
- ROM에 들어가는 184×40 PNG: `assets/title/title_kr_ai_002_nes.png`
- 메뉴 글리프/번역 사양: `assets/menu/menu_kr.json`, `menu_glyphs.png`
- 실제 게임 화면 비교: `build/title_kr_menu_003_runtime_comparison.png`
- 로컬 테스트 ROM: `build/title_kr_menu_003/Ninja_Jajamaru_kun_KR_title_menu_003.nes`
- ROM 없는 차분: `patches/Ninja_Jajamaru_kun_KR_title_menu_003.ips`
- 구조·범위: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 재현

Python 3.12.10 / Pillow 12.3.0에서 확인했다. 의존성 설치는 `python -m pip install -r requirements.txt`. 프로젝트 루트에서 아래 명령으로 원본을 검증하고 PNG 변환·ROM·IPS를 재생성한다. 생성 이미지와 정확한 프롬프트를 프로젝트 안에 보존했으므로 재빌드에 이미지 생성 서비스가 필요하지 않다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1
# 다른 위치의 지원 원본을 지정할 수 있다.
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SourceRom '원본 ROM의 절대 경로'
```

실행 검증은 호환 Mesen 2.1.1 실행 파일을 `--mesen`에 지정한다. QA 폴더는 새 이름을 사용해 이전 증거를 덮어쓰지 않는다.

```powershell
python scripts/run_title_qa.py --rom build/title_kr_menu_003/Ninja_Jajamaru_kun_KR_title_menu_003.nes --output qa/title_kr_menu_003/new_run --mesen 'Mesen.exe의 절대 경로'
python scripts/verify_title_qa.py --target-qa qa/title_kr_menu_003/new_run
```

현재 검증은 정적/빌드·IPS 적용/콜드부팅·짧은 게임 스모크/장면 시각 확인이다. 전체 게임 완주·실기 검증은 수행하지 않았다. HUD·스테이지 안내·기타 게임 문구는 아직 원문이다.

메뉴는 제공된 Galmuri7 2.403의 완성형 인·용 두 글자만 사용한다. 폰트와 OFL은 `assets/fonts/`에 보존했다. 독립 종성 27종 감사는 실패 상태로 기록하며 해당 용도로 사용하지 않는다. 조사용 py65는 필요할 때 `python -m pip install --target tools/python py65==1.2.0`으로 설치하고 `python scripts/survey_menu.py`를 실행한다. 주 빌드는 Pillow만 필요하다.

이전 002를 명시적으로 재현하려면 `scripts/build.ps1 -TitleConfig config/title_kr_ai_002.json`과 `verify_title_qa.py --config config/title_kr_ai_002.json`을 사용한다.
