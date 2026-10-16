"""Create the ROM-free v1.0 release ZIP from verified build and QA records."""
import hashlib,json,shutil,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
VERSION='1.0';BUILD='title_kr_release_100';PATCH='Ninja_Jajamaru_kun_KR_v1.0.ips'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((ROOT/'build'/BUILD/'build_report.json').read_text(encoding='utf-8'));qa=ROOT/'qa'/BUILD
    natural=json.loads((qa/'cold_boot_001/verification.json').read_text(encoding='utf-8'));roots=json.loads((qa/'roots_verification.json').read_text(encoding='utf-8'))
    assert natural['target_sha256']==roots['target_sha256']==build['target_sha256']
    assert all(r['outside_bounds']==0 for r in roots['roots']) and len(roots['roots'])==7
    stage=ROOT/'releases/v1.0';stage.mkdir(parents=True,exist_ok=True);archive=ROOT/'releases/Ninja_Jajamaru_kun_KR_v1.0.zip';assert not archive.exists(),'Release archive already exists; preserve it'
    shutil.copy2(build['patch_path'],stage/PATCH)
    for name in ('apply.cmd','apply.ps1'):
        s=(ROOT/'scripts/release'/name).read_text(encoding='utf-8');(stage/name).write_bytes(s.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
    licenses=stage/'licenses';licenses.mkdir(exist_ok=True)
    for source,target in (('Galmuri_OFL.md','Galmuri_OFL.md'),('JejuHallasan_OFL.txt','JejuHallasan_OFL.txt')):shutil.copy2(ROOT/'assets/fonts'/source,licenses/target)
    shutil.copy2(qa/'cold_boot_001/frame_0060.png',stage/'title.png');shutil.copy2(qa/'cold_boot_001/frame_0480.png',stage/'appearance.png')
    im=Image.open(ROOT/f'build/{BUILD}_runtime_names.png');im.crop((0,260,im.width,im.height)).save(stage/'enemy_names.png')
    report={'schema_version':1,'version':VERSION,'game':'Ninja Jajamaru-kun (Japan), NES','build_id':BUILD,'source':{'sha256':build['source_sha256'],'size':build['size'],'header_hex':'4e45531a010271500000000000000000'},'target':{'sha256':build['target_sha256'],'size':build['size']},'patch':{'filename':PATCH,'sha256':build['patch_sha256']},'output_filename':'Ninja_Jajamaru_kun_KR_v1.0.nes','scope':['Korean title logo and player-count menu','All seven known Japanese enemy-name introductions and shared appearance label in Jeju Hallasan','Non-title English retained'],'validation':{'static_and_build':build['checks'],'native_smoke':natural['runtime_result'],'all_name_renderer_roots':roots['result'],'probe_method':roots['mode'],'windows_apply':'Source, patch and output hashes are enforced by apply.ps1; extracted archive application evidence is recorded separately.'},'limitations':['Natural first enemy encounter verified; remaining six checked by native-renderer CPU-A probes','Full playthrough, hardware, other emulators and audio listening not performed','Known introduction-label scope; no claim of exhaustive hidden-message discovery'],'fonts':[{'name':'Galmuri7','license':'licenses/Galmuri_OFL.md','purpose':'Title player-count menu'},{'name':'Jeju Hallasan','license':'licenses/JejuHallasan_OFL.txt','purpose':'Seven names and appearance; 17px, origin (0,-1), 16x16 cells'}]}
    (stage/'release_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    readme=f'''닌자 자자마루군 (패미컴/NES) 한글 패치 v1.0

한글화: 타이틀 로고, 1인용/2인용 메뉴, 적 이름 7종과 공통 등장 안내.
등장 글꼴: 제주한라산체. HUD·SCENE/PLAYER/START·PAUSE·GAME OVER·보너스 영문은 유지합니다.
적 이름: 오유키 / 쿠로베에 / 카라캇사 / 헤도본 / 핀보 / 카쿠탄 / 나마즈다유.

적용 방법 (Windows)
1. 이 ZIP을 모두 압축 해제합니다.
2. 지원 일본판 원본 .nes를 apply.cmd 위에 끌어 놓습니다.
3. 같은 폴더에 Ninja_Jajamaru_kun_KR_v1.0.nes가 생성됩니다.
4. 원본·기존 결과 파일은 덮어쓰지 않습니다. 같은 결과가 이미 있으면 먼저 다른 이름으로 보관하세요.
별도 출력 경로: apply.cmd "원본 경로.nes" "새 결과 경로.nes"
Windows PowerShell과 .NET을 사용하며 별도 패처 설치는 필요 없습니다.
다른 운영체제에서는 IPS 패처로 {PATCH}를 지원 원본에 적용할 수 있습니다. 결과 해시를 대조하세요.

지원 원본: Ninja Jajamaru-kun (Japan), iNES 헤더 포함 32,784바이트
원본 SHA-256: {build['source_sha256']}
결과 SHA-256: {build['target_sha256']}
IPS SHA-256: {build['patch_sha256']}

검증: 원본 식별·글리프·타일맵·IPS 왕복, Mesen2.1.1 자연 첫 적 등장/시작/리셋/인원 선택,
7종 이름의 네이티브 출력 분기·이탈, 배포 적용 도구를 검증합니다.
enemy_names.png는 A 선택값을 지정한 7개 출력 실험의 실제 캡처입니다.
전체 완주·실기·다른 에뮬레이터·오디오 청취 및 나머지 적 6종의 자연 조우는 미수행입니다.
숨은 모든 문구까지 찾았다는 의미의 완전 한글판은 아닙니다.

원본 ROM·BIOS·완성 ROM은 포함하지 않습니다. 본인이 보유한 지원 원본에 적용하세요.
폰트 원문 라이선스와 출처를 함께 보존하세요.
프로젝트: https://github.com/akuma815/nes-ninja-jajamaru-kun-kr-patch
릴리즈: https://github.com/akuma815/nes-ninja-jajamaru-kun-kr-patch/releases/tag/v1.0
'''
    (stage/'README_KO.txt').write_text(readme,encoding='utf-8-sig')
    (stage/'CHANGELOG.txt').write_text('v1.0 (2026-10-16)\n- Existing title/menu003 retained.\n- All seven enemy names and appearance translated with Jeju Hallasan brush-style glyphs.\n- Windows IPS apply helper with input/patch/output SHA-256 guards.\n- Non-title English retained.\n',encoding='utf-8')
    (stage/'THIRD_PARTY_NOTICES.txt').write_text('Jeju Hallasan: https://github.com/google/fonts/tree/main/ofl/jejuhallasan\nGalmuri: https://github.com/quiple/galmuri\nFull font notices and SIL OFL texts are in licenses/.\nWindows PowerShell/.NET are provided by Windows and are not bundled.\nThe emulator is used for verification and is not bundled.\n',encoding='utf-8')
    files=sorted(p for p in stage.rglob('*') if p.is_file() and p.name!='FILES.sha256')
    assert not any(p.suffix.lower() in ('.nes','.bin','.exe','.dll') for p in files)
    (stage/'FILES.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(stage).as_posix()+'\n' for p in files),encoding='ascii')
    files.append(stage/'FILES.sha256')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            info=zipfile.ZipInfo(p.relative_to(stage).as_posix(),date_time=(2026,10,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
    result={'archive':str(archive),'archive_sha256':sha(archive),'size':archive.stat().st_size,'file_count':len(files),'target_sha256':build['target_sha256'],'patch_sha256':build['patch_sha256']}
    (ROOT/'releases/v1.0_package.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
