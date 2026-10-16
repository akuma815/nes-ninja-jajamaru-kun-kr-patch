"""Extract ZIP into Korean/space paths and run the shipped Windows CMD helper."""
import argparse,hashlib,json,os,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'qa/release_v1_0_apply');a=ap.parse_args()
    info=json.loads((ROOT/'releases/v1.0_package.json').read_text(encoding='utf-8'));archive=Path(info['archive']);assert sha(archive)==info['archive_sha256']
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);extracted=out/'한글 공백 경로 검증';extracted.mkdir()
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==13
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts and not n.lower().endswith(('.nes','.bin','.exe','.dll')) for n in z.namelist())
        z.extractall(extracted)
    for line in (extracted/'FILES.sha256').read_text(encoding='ascii').splitlines():
        expected,name=line.split('  ',1);assert sha(extracted/name)==expected
    meta=json.loads((extracted/'release_report.json').read_text(encoding='utf-8'));original=ROOT/'original/rom/Ninja Jajamaru-kun (Japan).nes';original_hash=sha(original)
    source=out/'보관 원본 일본판.nes';source.write_bytes(original.read_bytes());target=out/'결과 한글 이름.nes';cmd=extracted/'apply.cmd';env=os.environ.copy();env['NINJA_NO_PAUSE']='1';tests=[]
    def run(id,src,dst=None,success=False):
        # Fixed test paths are quoted as Windows CMD arguments, with the /S outer quote pair.
        values=[cmd,src]+([dst] if dst else [])
        assert all('"' not in str(v) and '\n' not in str(v) for v in values)
        command='"'+' '.join('"'+str(v)+'"' for v in values)+'"'
        commandline='"'+os.environ.get('COMSPEC','cmd.exe')+'" /d /s /c '+command
        r=subprocess.run(commandline,env=env,capture_output=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        (out/(id+'_stdout.txt')).write_bytes(r.stdout);(out/(id+'_stderr.txt')).write_bytes(r.stderr)
        assert (r.returncode==0)==success,(id,r.returncode,r.stderr)
        tests.append({'id':id,'exit_code':r.returncode,'result':'PASS','mode':'real shipped apply.cmd -> Windows PowerShell 5.1, Korean and space-containing paths'})
    run('valid_explicit_output',source,target,True);assert sha(target)==meta['target']['sha256']
    run('existing_output_rejected',source,target);assert sha(target)==meta['target']['sha256']
    run('original_overwrite_rejected',source,source);assert sha(source)==original_hash
    bad=out/'잘못된 원본.nes';data=bytearray(original.read_bytes());data[0x10]^=1;bad.write_bytes(data);badout=out/'실패 결과.nes'
    run('wrong_source_sha_rejected',bad,badout);assert not badout.exists()
    patch=extracted/meta['patch']['filename'];patchbytes=patch.read_bytes();patch.write_bytes(patchbytes[:-1]+bytes([patchbytes[-1]^1]))
    run('wrong_patch_sha_rejected',source,badout);assert not badout.exists();patch.write_bytes(patchbytes)
    run('drag_drop_default_output',source,success=True);assert sha(extracted/meta['output_filename'])==meta['target']['sha256']
    assert sha(original)==sha(source)==original_hash and sha(archive)==info['archive_sha256']
    result={'schema_version':1,'version':'1.0','result':'PASS','archive_sha256':info['archive_sha256'],'archive_size':archive.stat().st_size,'zip_crc_and_13_files':'PASS','embedded_hash_manifest':'PASS','rom_free_archive':'PASS','source_preserved':True,'result_rom_sha256':sha(target),'tests':tests,'unperformed':['Full playthrough','Hardware','Other emulators','Audio listening']}
    (ROOT/'releases/v1.0_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
