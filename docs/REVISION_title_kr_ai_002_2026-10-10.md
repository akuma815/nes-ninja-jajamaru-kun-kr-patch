# 타이틀 수정 인계 — title_kr_ai_002 — 2026-10-10

## 요청과 현재 결과

사용자 지시: 원본의 마지막 `군`은 작고 노란색이므로 이전 시안의 같은 크기 파란 `군`을 다시 작업한다.

내장 image_gen으로 이전 생성 PNG를 편집하고 원본 게임 화면을 참조했다. 현재는 작은 붉은 `닌자`, 큰 파란 `자자마루`, 마지막은 **작고 노란 군/얇은 파란 테두리**, 루 오른쪽 아래 배치다. 현재 주 빌드는 **title_kr_ai_002**. 원본과 이전 001의 PNG·ROM·IPS·QA는 보존했다.

## 변경 파일

- 신규 이미지 입력·프롬프트·변환 PNG: `assets/title/title_kr_ai_002_generated.png`, `title_kr_ai_002_prompt.txt`, `title_kr_ai_002_nes.png`.
- 현재 사양: `config/title.json`. 이전 001을 재현할 프로파일 `config/title_kr_ai_001.json` 신규 보존.
- 버전별 입출력·보고서를 지원하도록 갱신: `scripts/build.ps1`, `build_title.py`, `convert_generated_title.py`, `verify_title_qa.py`.
- 생성 산출물: `build/title_kr_ai_002_conversion.json`, `title_kr_ai_002_art_preview.png`, `title_kr_ai_002_runtime_comparison.png`, `build/title_kr_ai_002/` ROM·build_report·expected_writes.
- 차분: `patches/Ninja_Jajamaru_kun_KR_title_ai_002.ips`.
- 실행 증거: `qa/title_kr_ai_002/cold_boot_001/` 12개 PNG 및 PPU/OAM/RAM/주소 매핑/상태, 읽기 추적, 환경·verification 보고서. 시각 판정 `qa/title_kr_ai_002/VISUAL_REVIEW.md`.
- 진입·인계 갱신: `README.md`, `docs/ARCHITECTURE.md`, `HANDOFF.md`, `HANDOFF_2026-10-10.md`, 본 수정 인계, `SESSION_ARTIFACTS_2026-10-10_title_kr_ai_002.json`.

## 주요 해시

| 대상 | SHA-256 |
|---|---|
| 불변 원본 | `c44602e4605d0c60e72a13565cdf12798262bcf22e6a70319375c250fc2ac45b` |
| 생성 원본 PNG | `1d0ce224ab72bcd954997387b5ad053dbe8f7273280a0eb51a53e2faec2cdb9b` |
| NES PNG | `b91ffe31a5bc8589f826937c07f1cacc6827f77aa45c1a85d1e6f2788de13e2e` |
| 새 ROM | `041d01147696ff064e164bfe8c36f0ab8339d691c12982b1f787808a4c345a46` |
| 새 IPS | `e84cdbc7c06eea4cc4c3ccaaddcc85d355af853db06a2c992c23ef4d524bfe5e` |

## 검증 구분

**정적 — PASS:** 184×40의 4색 이미지. 고유 비공백 타일 86/94개. 군의 로고 상대 영역 `(160,20,15,18)`, 주 제목 높이 38픽셀 대비 47.4%. 군 비공백 색상은 노랑 145개/파란 테두리 51개(노랑 74.0%). `suffix_constraints`에서 노랑 최소 70%·빨강 없음·주 제목 높이의 최대 55%를 검사해 같은 문제의 재발을 막는다. CHR 1,024타일 무수정 왕복, 최종 ROM 역디코드와 입력 픽셀 동일, 원본 크기·헤더·해시와 보호 바이트 검사 통과. Expected Write 87건, 원본 대비 변경 1,295바이트는 로고 타일맵/허용 CHR 범위 안에만 존재한다.

**빌드·적용 — PASS:** 주 build.ps1으로 추출·변환·빌드·IPS 생성 통과. 별도 IPS 적용 결과와 빌드 전체 바이트 동일. 스타일 검사 추가 후 재빌드도 위 ROM/PNG/IPS 해시와 같아 이미 확보한 실행 증거가 같은 최종 이미지에 귀속된다. ROM 전체 배포 ZIP은 만들지 않았다.

**런타임 — PASS, 제한된 범위:** Mesen 2.1.1, 콜드부팅·격리 portable/no savestate. 이전과 같은 1,140프레임 입력/리셋 시퀀스로 새 ROM을 실행, 종료 코드 0. 콜드부팅·1인 시작·첫 스테이지 스모크·리셋 후 타이틀·Select/2인 시작 확인. 타이틀 CHR 및 115회 데이터 읽기가 새 ROM과 일치. 원본과 12개 캡처 비교에서 로고 밖 차이 0, 비타이틀 6개는 전체 픽셀 동일. 타이틀 6개는 로고 내부 3,662픽셀만 변경됐다.

**장면 시각 — PASS, assistant:** 실제 `frame_0060.png`·`frame_0960.png`·`frame_0600.png`를 직접 확인했다. 마지막 군은 작고 노란색이며 잘림이 없다. HUD·캐릭터·메뉴 보존. `VISUAL_REVIEW.md`에 판정했다.

## 미해결과 제한

사용자의 최종 미감 확인, 전체 완주, 실기, 다른 에뮬레이터, 오디오 청취 및 전체 게임 공유 타일 전수 조사는 미수행. 게임 이름 외 메뉴/HUD는 원문 유지. 이전 001은 군 색상·크기 기준이 틀린 이전 시안으로 남기며 현재 후보로 사용하지 않는다.

## 재현

프로젝트 루트에서 Python 3.12.10/Pillow 12.3.0.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1
python scripts/verify_title_qa.py
# 새 증거 폴더에서 다시 실행하려면:
python scripts/run_title_qa.py --rom build/title_kr_ai_002/Ninja_Jajamaru_kun_KR_title_ai_002.nes --output qa/title_kr_ai_002/new_run --mesen '../Tiny Toon Adventures/tools/mesen-2.1.1/Mesen.exe'
python scripts/verify_title_qa.py --target-qa qa/title_kr_ai_002/new_run
```

이전 001 재현을 명시적으로 요청한 경우:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -TitleConfig config/title_kr_ai_001.json
python scripts/verify_title_qa.py --config config/title_kr_ai_001.json
```

## 정확한 다음 행동 하나

`build/title_kr_ai_002_runtime_comparison.png`에서 작고 노란 군이 포함된 수정 시안을 사용자와 확인하고 그 유지/수정 지시를 다음 작업 입력으로 기록한다.
