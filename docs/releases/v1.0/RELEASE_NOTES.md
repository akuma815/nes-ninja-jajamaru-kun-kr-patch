# 닌자 자자마루군 한글 패치 v1.0

제주한라산체를 적 등장 문구 전체에 적용한 v1.0이다. 한글 타이틀 로고·1인용/2인용 메뉴와 적 이름 7종·공통 등장 안내를 포함한다. HUD·스테이지 시작·일시정지·게임 종료·보너스 영문은 유지한다.

적 이름은 오유키, 쿠로베에, 카라캇사, 헤도본, 핀보, 카쿠탄, 나마즈다유다. 제주한라산 17px를 16×16 셀에 직접 래스터하고 공통 원점 (0,-1), 임계값128을 사용한다. 전체 글자 집합을 셀 안에 넣기 위해 PoC006의 원점에서 x만 1픽셀 옮겼다. 글자별 중앙 정렬·축소·팽창은 없다.

## 다운로드와 적용

- [v1.0 릴리즈](https://github.com/akuma815/nes-ninja-jajamaru-kun-kr-patch/releases/tag/v1.0)
- ZIP: `Ninja_Jajamaru_kun_KR_v1.0.zip`, 19,939바이트, ROM 없음.
- ZIP을 모두 풀고 지원 원본 `.nes`를 `apply.cmd` 위에 끌어 놓는다. 결과는 `Ninja_Jajamaru_kun_KR_v1.0.nes`다.
- 원본·기존 결과 파일을 덮어쓰지 않는다. 적용 도구는 입력·패치·출력 SHA-256을 검사한다.
- 다른 운영체제에서는 ZIP의 IPS를 IPS 패처로 적용하고 결과 해시를 확인할 수 있다.

| 대상 | SHA-256 |
| --- | --- |
| 일본판 원본, iNES 헤더 포함 32,784바이트 | `c44602e4605d0c60e72a13565cdf12798262bcf22e6a70319375c250fc2ac45b` |
| v1.0 결과 | `b7e79f8de2bc76e0e09db0b2e8041b349eb051e04b73067ea231cd0117c243f9` |
| IPS | `571a29e72c3700584b2243f73f9d962483880c303a568078d42a7a443014f362` |
| 배포 ZIP | `efb84dc43454abf66753d5726d694519eaaac284be34e315119579f88d7bfacb` |

## 검증 범위

- 정적/빌드: 지원 원본·23음절 실제 cmap·92타일·8개 문자열 경계와 종료자·보호 영역·최종 픽셀·IPS 적용 일치. 194건 Expected Write, 원본 대비 변경2,560바이트, 원본 크기/헤더 유지.
- 자연 스모크: Mesen2.1.1 콜드부트, 첫 적 등장, 1인용 시작·초기 입력, reset 타이틀 복귀, 2인용 선택/시작. 003 대비12캡처 중11개 완전 동일, 480프레임은 이름·등장464픽셀만 변경. OAM12개 동일.
- 7종 출력: 원래 표시 루틴의 선택 A=0..6을 지정한 별도 제어 실험에서 전체 이름·등장·이탈을 확인. 실제 CHR/타일맵/스크린샷 픽셀이 빌드와 일치하고 영역 밖 변경0, 이탈 후 화면·PPU·OAM이 원본과 동일.
- Windows ZIP 적용: 한글·공백 경로에서 실제 `apply.cmd`/PowerShell5.1 실행. 명시 출력/기본 출력 성공, 잘못된 원본·손상 패치·기존 출력·원본 덮어쓰기 거부, 원본 보존과 결과 해시 확인. ZIP CRC·13개 파일·내장 파일 해시 PASS.
- assistant가 실제7종 출력과 첫 등장/타이틀/게임 화면을 시각 확인했다. 사용자 요청으로 선택한 글꼴을 전체에 적용했다.

전체 완주·실기·다른 에뮬레이터·오디오 청취 및 나머지6종의 자연 조우는 미수행이다. 모든 숨은 문구의 모집단을 확정한 완전 한글판이라는 의미는 아니다. 이번 v1.0 범위는 알려진 등장 문구 전체와 기존 타이틀·메뉴다.

독립 종성27종 감사는 동일 대체 마스크로 실패했다. 실제 cmap·서로 다른 픽셀을 확인한 완성형23음절만 사용하고 조합형/독립 종성 공급으로 채택하지 않았다.

## 빌드·검증 재현

```powershell
python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -TitleConfig config/release_v1_0.json
python -X utf8 scripts/verify_title_qa.py --config config/release_v1_0.json
python -X utf8 scripts/verify_enemy_roots.py --config config/release_v1_0.json
```

게임 원본은 별도 준비한다. 실행 검증은 보존한 정확한 환경 기록을 검사하며, 새 실행은 고유 출력 경로로 수행한다. 공개 저장소에 로컬 QA 메모리 덤프는 포함하지 않는다.

로컬 산출물: `releases/Ninja_Jajamaru_kun_KR_v1.0.zip`, `releases/v1.0_package.json`, `releases/v1.0_validation.json`. 게임 빌드/실행은 `build/title_kr_release_100/`, `qa/title_kr_release_100/`. 별도 배포 검증의 첫 실행은 테스트 하네스의 CMD 따옴표 문제로 실행 전에 실패했으며, 하네스를 바로잡은 `qa/release_v1_0_apply_002/`의 실제 6개 검사가 모두 통과했다. 배포 helper 자체의 바이트는 변경하지 않았다.

폰트 출처·OFL은 배포 ZIP과 소스의 notices/licenses에 있다. 원본·기존003/004·PoC005/006을 보존하고 v1.0을 별도로 생성했다.
