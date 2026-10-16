# 타이틀 경로와 작업 범위

## 확정된 원본

`config/source.json`이 지원 원본의 크기·SHA-256·헤더를 소유한다. 32,784바이트, iNES mapper 87, PRG 16KB, CHR 16KB. 루트의 최초 ROM과 `original/rom/`의 보관 사본을 모두 보존한다.

## 저장 → 소비 → 표시

- 타이틀은 CHR 8KB bank 1. 배경 PPU `$1000`은 CHR 상대 `$3000` / 파일 `$7010`에 대응한다. Mesen의 실제 주소 변환과 PPU 덤프로 확인했다.
- 로고 네임테이블은 파일 `$317F..$31F1`, CPU `$B16F..$B1E1`, 23×5=115바이트. CPU `$AAC6`에서 순서대로 115회 읽혀 PPU `$20C4`부터 32바이트 행 간격으로 표시된다. 압축되지 않은 고정 행렬이다.
- 화면 범위 `(32,48,184,40)`. 원본 로고 타일은 배경 패턴 `$34..$91` 94개, 빈 타일은 `$30`. 타이틀 화면에서 로고 바깥의 배경 셀은 이 타일들을 참조하지 않는다.
- 로고는 팔레트 3의 검정·노랑·빨강·파랑 인덱스 0..3을 쓴다. 헤더·팔레트·속성표·스프라이트·프로그램 명령은 변경하지 않는다.
- 정적 근거: `analysis/title_survey.json`. 실행 근거: 원본 `qa/original/cold_boot_001/`, 패치본 `qa/title_kr_ai_002/cold_boot_001/`.
- mapper 확인에 참고한 1차 구현: [Mesen 2.1.1 JalecoJfxx](https://github.com/SourMesen/Mesen2/blob/2.1.1/Core/NES/Mappers/Jaleco/JalecoJfxx.h). [Lua API 문서](https://github.com/SourMesen/Mesen2/blob/2.1.1/UI/Debugger/Documentation/LuaDocumentation.json).

## 생성형 이미지 경로

1. `extract_title_png.py`: 원본에서 로고를 PNG로 추출하고 무수정 타일 왕복을 검증.
2. 내장 image_gen에 `analysis/raw/title_original_reference_x6.png`를 참조로 넣고 생성. 정확한 프롬프트는 `assets/title/title_kr_ai_002_prompt.txt`.
3. `assets/title/title_kr_ai_002_generated.png`: 보존된 생성 원본. 재빌드는 생성 서비스를 다시 호출하지 않고 이 고정 PNG를 입력으로 사용한다.
4. `convert_generated_title.py`: 전경 추출, 167×38로 축소, 원본 4색 인덱스로 디더링 없이 변환. 기존 타일 예산에 들어가는 중앙 배치 `(8,1)` 선택. 글자 그림을 수작업으로 고치지 않았다.
5. 네이티브 PNG `title_kr_ai_002_nes.png`: 184×40, 86개 비공백 고유 타일. 94개 예산 이내. 끝의 군은 노란색이며 높이 18픽셀로 주 제목 38픽셀의 약 절반이다.
6. `build_title.py`: 모든 쓰기를 원본 조건과 허용 범위로 사전 검증한 뒤 적용. 최종 diff·역디코드 픽셀·IPS 적용 동일성 검증.
7. `run_title_qa.py` / `verify_title_qa.py`: 격리 Mesen 콜드부팅·컨트롤러 입력·리셋 캡처 및 비교.

초기 격자형 픽셀 초안 `assets/title/title_kr_001.png`와 `make_title_art.py`는 사용자 스타일 수정 요청 전의 미사용 초안이다. 현재 빌드 입력은 `config/title.json`만 따른다.

## 범위와 열린 사항

현재 003 범위는 게임 이름 로고와 1인용/2인용 메뉴다. HUD·스테이지 안내·기타 문구는 아직 번역하지 않았다. 첫 스테이지·타이틀 재진입 표본의 비교는 통과했으나 전체 게임의 공유 타일 사용을 전수 조사했다고 주장하지 않는다. 전체 완주, 실기, 다른 에뮬레이터, 오디오 청취와 사용자 미감 최종 확인은 남아 있다.

## 003 메뉴 경로

- 원본 공유 테이블 파일 `$2C2A..$2C30` / CPU `$AC1A..$AC20`: 공백+PLAYER 7바이트. CPU `$AC0E`의 LDA absolute,X로 읽히고 `$AC11`의 STA `$2007`로 표시된다. 원본 추적은 두 번×7=14개 읽기를 확인했다.
- 숫자는 즉시 쓰기, 마지막 S는 별도의 즉시 쓰기다. 숫자와 선택 상태는 그대로 두고 행 시작 주소를 `$226F/$22AF`로 중앙 배치했다. 읽기 수를 5로 줄여 오른쪽 메뉴 테두리를 침범하지 않고 남는 셀을 공백으로 쓴다. S는 공백으로 대체했다.
- 8px 완성형 인·용은 기존 로고 타일 예산에서 남은 `$8A/$8B` 슬롯에 공급한다. 원래 영문 폰트는 수정하지 않았다. 002의 로고는 `$34..$89`까지 쓰므로 두 메뉴 슬롯과 겹치지 않는다. 대표 타이틀-bank 상태의 visible references가 없음을 검사했다.
- 공급 폰트는 프로젝트 제공 Galmuri7 2.403의 고정 해시 TTF. 원점 (0,0), 8×8 셀, 8px 직접 래스터, 임계값 128, 흰색 인덱스 3. `assets/menu/menu_kr.json`이 원문·역문·레이아웃·폰트·구조·쓰기 사양을 소유한다.
- 독립 종성 27종 감사는 동일한 대체 글리프가 나와 실패했다. 이 공급자는 조합형/독립 종성 용도로 채택하지 않았고, cmap·자형·게임 표시를 검증한 완성형 두 글자에만 사용한다.
- 새 소비 검증은 두 번×5=10개 테이블 읽기, 실제 PPU 메뉴 셀, OAM 동일성, 1/2인 선택과 시작을 포함한다. 원본과 로고·메뉴 행 밖 차이 0, 이전 002와 메뉴 행 밖 차이 0.
- 코드 개입은 확정된 LDA/CPX 즉시값 4바이트 교체뿐이다. opcode·명령 경계·분기·호출은 보존했다. `analysis/menu_disassembly.json`에 py65 1.2.0 NMOS 6502 디코드 증거가 있다. 기계어 생성/재배치 및 전체 호출 그래프 주장은 없다.
- 현재 ROM: `build/title_kr_menu_003/Ninja_Jajamaru_kun_KR_title_menu_003.nes`. 실행 증거: `qa/title_kr_menu_003/cold_boot_001/`. 이전 001/002 자산·ROM·IPS·증거와 프로파일은 보존한다.

emucap bootstrap/launch_plan은 호환 바이너리 부재로 실행 준비 불가였다. 이를 런타임 통과로 표기하지 않는다. 별도의 Mesen 2.1.1 테스트러너 실행으로 실제 캡처를 확보했고, 실행 파일·ROM·Lua·설정·각 증거 파일의 해시는 `environment.json`에 남겼다. 외부 게임 프로젝트의 Mesen 원본을 수정하지 않고 QA별 portable 사본을 사용했다.
