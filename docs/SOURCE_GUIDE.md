# 공개 소스 빌드 안내 — v1.0

지원 일본판 원본은 별도로 준비합니다. 원본 ROM·원본 추출 그래픽/폰트·QA 메모리 덤프는 저장소에 넣지 않습니다.
직접 만든 한글 타이틀 아트, 한글 사양, 라이선스가 허용하는 TTF/OFL과 빌드 코드를 포함합니다.

```powershell
python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -SourceRom '지원 원본 ROM의 절대 경로' -TitleConfig config/release_v1_0.json
```

Python3.12.10 / Pillow12.3.0 / fonttools4.63.0에서 원본 식별·빌드·IPS 왕복과 최종 해시를 검증합니다.
목표 ROM SHA-256은 `b7e79f8de2bc76e0e09db0b2e8041b349eb051e04b73067ea231cd0117c243f9`입니다.
생성한 원본 추출 PNG·ROM·QA는 .gitignore 대상입니다. 커밋하지 않습니다.

실행 검증은 외부 Mesen2.1.1과 별도 원본/목표 QA 기록이 필요합니다.
로컬 메모리 덤프는 공개하지 않았으므로 저장소만으로 과거 실행 증거 전체를 재검사할 수 있는 것은 아닙니다.
`docs/releases/v1.0/`의 보고서는 실제 수행 범위와 한계를 요약합니다. 과거003 문서는 역사 기록으로 남아 있습니다.

`package_release.py`는 게임 빌드와 로컬 QA 보고서에서 ROM 없는 배포물을 만듭니다.
배포 ZIP은 릴리즈에서 내려받을 수 있으며 실제 Windows apply.cmd 검증 결과를 함께 기록했습니다.

The v1.0 public source checkout was rebuilt with an externally supplied supported ROM; the output hash matched the released target.
