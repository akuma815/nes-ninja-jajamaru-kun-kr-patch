# ?? ? 2026-10-10 ? ?? title_kr_ai_002

?? ??? **title_kr_ai_002**. ???? ??? ??? ?? `?`? ? ?? ??? ?? ??? ?? ???? ROM? ????. ?? 001? ??? ????.

?? ?? ????????/?????/???/?? ?? ????? ?????????? ?? ??? [REVISION_title_kr_ai_002_2026-10-10.md](REVISION_title_kr_ai_002_2026-10-10.md)? ????.

- ? ROM: `build/title_kr_ai_002/Ninja_Jajamaru_kun_KR_title_ai_002.nes`
- ?? ?? ??: `build/title_kr_ai_002_runtime_comparison.png`
- ??: `patches/Ninja_Jajamaru_kun_KR_title_ai_002.ips`
- ?? ROM SHA-256: `041d01147696ff064e164bfe8c36f0ab8339d691c12982b1f787808a4c345a46`
- ??: 86/94??, ? ?? 18??/? ?? 38??, ? ??/IPS ?? ??, Mesen ?? ?? 12? ?? ???? ?? ? ?? 0. ?? ??? ???.
- ?? ??? ??: `SESSION_ARTIFACTS_2026-10-10_title_kr_ai_002.json`.

??? ?? ?? ??: ? ?? ?? ???? ?? ?? ?? ??? ???? ???? ??/?? ??? ?? ???? ????.

??? ?? ??? ??? ???? ?? ????? ????? ???? ? ?? ?? ??? ???.

---

# 인계 — 2026-10-10

## 현재 상태

NES 닌자 자자마루군 신규 프로젝트 구성과 첫 타이틀 한글화 작업을 수행했다. 사용자의 후속 지시에 따라 원본 로고를 PNG로 추출하고 내장 **image_gen**으로 원본과 비슷한 자유로운 붓글씨의 `닌자 자자마루군`을 생성한 뒤 ROM에 이식했다.

현재 후보: **title_kr_ai_001**. 정적·빌드·IPS 적용·Mesen 콜드부팅 및 첫 스테이지 스모크·장면 시각 확인 통과. 사용자의 미감 최종 확인은 아직 없다. 전체 한글화 또는 전체 게임 QA 완료가 아니다.

## 폴더와 원본 보존

루트에 있던 `Ninja Jajamaru-kun (Japan).nes`는 수정하지 않았다. `original/rom/`에 동일 해시 보관 사본을 만들었다. 원본, 그래픽 입력, 재생성 산출물, 실행 증거와 문서를 분리했다. `AGENTS.md`에 **모든 작업 세션 뒤 dated handoff 작성 및 HANDOFF.md 연결** 규칙을 고정했다.

## 이번 변경 파일

- 진입·규칙: `AGENTS.md`, `.gitignore`, `README.md`, `requirements.txt`.
- 원본·구조 사양: `config/source.json`, `config/title.json`, `analysis/title_survey.json`.
- 추출 PNG: `analysis/raw/title_original_indexed.png`, `title_original.png`, `title_original_reference_x6.png`, CHR 전체 미리보기 `chr_all.png`.
- 생성형 로고: `assets/title/title_kr_ai_001_generated.png`, `title_kr_ai_001_prompt.txt`, `title_kr_ai_001_nes.png`.
- 재현 코드: `scripts/build.ps1`, `build_title.py`, `convert_generated_title.py`, `extract_title_png.py`, `nes_graphics.py`, `survey_title.py`, `capture_title.lua`, `run_title_qa.py`, `verify_title_qa.py`.
- 최종 산출물: `build/title_kr_ai_001/Ninja_Jajamaru_kun_KR_title_ai_001.nes`, `build_report.json`, `expected_writes.json`, `build/title_kr_ai_001_conversion.json`, `build/title_kr_ai_001_art_preview.png`, `build/title_kr_ai_001_runtime_comparison.png`, `patches/Ninja_Jajamaru_kun_KR_title_ai_001.ips`.
- QA: `qa/original/cold_boot_001/`, `qa/title_kr_ai_001/cold_boot_002/`, `qa/title_kr_ai_001/VISUAL_REVIEW.md`, `qa/static_input_rejection/`.
- 문서: `docs/ARCHITECTURE.md`, 본 인계, `docs/HANDOFF.md`, `docs/SESSION_ARTIFACTS_2026-10-10.json`.
- 미사용 초안: `scripts/make_title_art.py`, `assets/title/title_kr_001.png`, `build/title_kr_001_art_preview.png`. 사용자 스타일 수정 요청 전의 격자형 픽셀 초안이며 현재 빌드에 들어가지 않는다.

## 주요 SHA-256

| 파일 | SHA-256 |
|---|---|
| 루트 원본 및 original/rom 보관 사본 | `c44602e4605d0c60e72a13565cdf12798262bcf22e6a70319375c250fc2ac45b` |
| 생성 원본 title_kr_ai_001_generated.png | `4be05500ada136bfcdd86d3a62470581e830e8353e18545858e3be183ca4c009` |
| NES PNG title_kr_ai_001_nes.png | `0a0b960e6fc487f6e4694d7c0d7cc1b3cfea49a19f66d5e2c90468d7c5a0cbb8` |
| 최종 테스트 ROM | `2146dd2527e0f213595c576b9194c3296d412ffbbe7177dc0c6d199fcc74491c` |
| IPS | `e18e7d1fbb77e068da3db249a6dcebaacd5a19388c1d1e74d18c73881a953be6` |
| Mesen 2.1.1 실행 파일 | `d2eb03c2590c648bf329f127ebcfefd70130e7690a9e2ccdba8616faea1fe96b` |

기타 파일별 해시는 `SESSION_ARTIFACTS_2026-10-10.json` 및 각 QA의 `environment.json` 참조.

## 검증 구분

### 정적 — PASS

- 지원 원본의 크기 32,784바이트·전체 해시·iNES 헤더 검증. 최초 원본과 보관 사본의 동일 해시 재확인.
- 1,024개 CHR 타일 decode→encode 무수정 왕복. 최종 ROM 타일 역디코드 픽셀과 NES 입력 PNG 동일.
- 원본 로고의 파일 `$317F..$31F1` 23×5 행렬, 타일 슬롯 `$34..$91`, 화면 `(32,48,184,40)` 확인. 런타임 주소 매핑과 115회 데이터 읽기로 소비자 연결.
- 생성 이미지의 네이티브 변환은 디더링 없이 4색, 93개 고유 비공백 타일/94개 예산. 처음 중앙 배치는 95개였고, 글자 그림 수정 없이 1픽셀 아래 배치로 93개에 맞췄다.
- Expected Write 94건을 원본에서 먼저 검증한 후 적용. 변경 1,418바이트는 로고 타일맵과 기존 로고 CHR 허용 영역에만 존재. 헤더·팔레트·속성·스프라이트·명령 등 나머지 바이트 보존.
- 원본 한 바이트를 바꾼 음성 입력 검사: 지원 원본 해시 불일치로 실패, 출력 폴더 생성 없음. `qa/static_input_rejection/verification.json`.

### 빌드·적용 — PASS

- `build.ps1` 주 경로로 원본 PNG 추출 → 생성 원본 PNG의 NES 변환 → ROM → IPS까지 재생성.
- 재빌드 ROM/PNG/IPS 해시가 위 최종 해시와 일치.
- 별도 IPS 읽기·적용 구현으로 패치를 원본에 적용한 전체 바이트가 최종 빌드와 동일.
- 이번 산출물은 개발용 ROM과 단일 IPS 차분이다. 배포 ZIP 또는 Windows 사용자용 적용 패키지는 만들지 않았다.

### 런타임 — PASS, 제한된 범위

- Mesen 2.1.1 `--testrunner`, fresh portable 사본, no savestate. ROM/RAM/PPU 쓰기 없음. 컨트롤러 입력과 리셋만 사용.
- Start 240..247, A 펄스 및 좌우 이동 360..599, reset 720, Select 900..907, Start 960..967, stop 1140.
- 콜드부팅/1인 시작/첫 스테이지/리셋 후 타이틀/2인 선택 및 시작, 종료 코드 0.
- 패치본 타이틀의 CHR 상주 바이트 및 115개 타일맵 데이터 읽기가 최종 ROM과 일치.
- 같은 입력의 원본·패치본 12개 캡처에서 로고 바깥 변경 픽셀 0. 타이틀 6개 표본은 각각 로고 내부 3,378픽셀만 변경. 비타이틀 6개 캡처는 전체 화면 동일.
- 원본 첫 실행은 넓은 읽기 추적, 패치본은 로고 115바이트만 추적했다. 입력·캡처 시점은 같고, 서로 다른 Lua 해시는 각 environment에 보존했다. `verification.json`에 이 차이를 명시했다.

### 장면 시각 — PASS, assistant 확인

실제 `frame_0060.png`, `frame_0960.png`, `frame_0600.png`와 원본/한글 비교 이미지를 직접 확인했다. 한글 로고가 잘리지 않고 원본의 붉은 작은 접두/노란 외곽선/파란 주 제목 느낌을 유지한다. 점수·캐릭터·메뉴를 보존한다. 상세 기록 `qa/title_kr_ai_001/VISUAL_REVIEW.md`.

## 실패·제약·미해결

- emucap은 호환 바이너리 부재로 실행 준비 불가. emucap을 통한 런타임 검증은 수행하지 않았다. 별도 일반 Mesen 2.1.1 테스트러너로 실제 실행했다.
- 한 번의 빌드가 Windows 기본 cp949로 UTF-8 한글 config를 읽다가 실패했다. UTF-8을 명시해 수정했다. 그 직후 존재하지 않는 ROM으로 호출된 `qa/title_kr_ai_001/cold_boot_001/`는 **실패 시도이며 증거로 사용하지 않는다**. FAILED.txt를 남겼고 유효한 최종 증거는 cold_boot_002이다.
- 전체 완주, 실기, 다른 에뮬레이터, 오디오 청취, 전체 게임 공유 타일 전수 조사, 사용자의 최종 미감 확인은 미수행.
- 메뉴·HUD·게임 내 문구는 첫 작업 범위 밖이며 원문 그대로다.
- 생성 원본과 정확한 프롬프트를 고정 입력으로 보존했다. 재빌드는 image_gen을 다시 호출하지 않는다. 생성 서비스 재호출의 픽셀 동일성은 보장하지 않는다.

## 재현 명령

프로젝트 루트 `G:\Downloads\Korean Traslate Project\Games\Ninja Jajamaru-kun`에서 Python 3.12.10 / Pillow 12.3.0 사용.

```powershell
python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1 -TitleConfig config/title_kr_ai_001.json
python scripts/survey_title.py --qa qa/original/cold_boot_001
python scripts/verify_title_qa.py --config config/title_kr_ai_001.json
```

새 실행 증거를 만들 때 이전 폴더를 덮어쓰지 않는다. 이번에 확인한 Mesen 공급원은 `../Tiny Toon Adventures/tools/mesen-2.1.1/Mesen.exe`이며 그 파일을 수정하지 않았다.

```powershell
python scripts/run_title_qa.py --rom build/title_kr_ai_001/Ninja_Jajamaru_kun_KR_title_ai_001.nes --output qa/title_kr_ai_001/new_run --mesen '../Tiny Toon Adventures/tools/mesen-2.1.1/Mesen.exe'
python scripts/verify_title_qa.py --config config/title_kr_ai_001.json --target-qa qa/title_kr_ai_001/new_run
```

## 정확한 다음 행동 하나

`build/title_kr_ai_001_runtime_comparison.png`의 실제 한글 타이틀을 사용자와 확인하고, 그 시안에 대한 유지 또는 수정 지시를 다음 작업 입력으로 기록한다.
