"""Isolated Mesen test runner; read-only capture plus documented input/reset."""
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--mesen',type=Path,required=True)
    a=ap.parse_args();assert a.rom.is_file(), 'ROM does not exist';assert a.mesen.is_file(), 'Mesen does not exist';out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    portable=out/'emulator';portable.mkdir();exe=portable/'Mesen.exe';shutil.copy2(a.mesen,exe)
    cfg={'Debug':{'ScriptWindow':{'AllowIoOsAccess':True,'ScriptTimeout':10}},'Nes':{'Port1':{'Type':'NesController'},'Port2':{'Type':'NesController'},'AutoConfigureInput':False}}
    settings=portable/'settings.json';settings.write_text(json.dumps(cfg),encoding='utf-8')
    lua=ROOT/'scripts/capture_title.lua';env=os.environ.copy();env['JAJA_QA_OUT']=str(out)
    command=[str(exe),'--testrunner',str(lua),str(a.rom.resolve()),'--timeout=60','--enableStdout']
    r=subprocess.run(command,env=env,capture_output=True,timeout=75,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (out/'stdout.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr)
    report={'emulator':'Mesen 2.1.1','exe_source':str(a.mesen.resolve()),'exe_sha256':sha(exe),'rom_path':str(a.rom.resolve()),'rom_sha256':sha(a.rom),'lua_sha256':sha(lua),'settings_sha256':sha(settings),'command':command,'exit_code':r.returncode,'mode':'cold boot, fresh isolated portable directory, no savestate','input_sequence':'Start 240..247; A pulses and left/right 360..599; reset 720; Select 900..907; Start 960..967; stop 1140','rom_ram_ppu_writes':False,'scope':'runtime capture; visual review and regression comparison are separate','files':{p.name:sha(p) for p in out.iterdir() if p.is_file()}}
    (out/'environment.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert r.returncode==0, f'Mesen failed {r.returncode}; inspect stdout/stderr'
    assert (out/'frame_1140.png').is_file(), 'Missing final capture'
    print(json.dumps({k:v for k,v in report.items() if k not in ('files','command')},indent=2))
if __name__=='__main__': main()
