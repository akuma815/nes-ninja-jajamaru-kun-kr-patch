"""Isolated seven-root renderer coverage with an explicitly logged CPU-A probe."""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--mesen',type=Path,required=True);a=ap.parse_args()
 assert a.rom.is_file() and a.mesen.is_file();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);portable=out/'emulator';portable.mkdir();exe=portable/'Mesen.exe';shutil.copy2(a.mesen,exe)
 settings=portable/'settings.json';settings.write_text(json.dumps({'Debug':{'ScriptWindow':{'AllowIoOsAccess':True,'ScriptTimeout':10}},'Nes':{'Port1':{'Type':'NesController'},'Port2':{'Type':'NesController'},'AutoConfigureInput':False}}),encoding='utf-8')
 lua=out/'capture.lua';shutil.copy2(ROOT/'scripts/capture_enemy_roots.lua',lua);env=os.environ.copy();env['JAJA_ENEMY_OUT']=str(out)
 command=[str(exe),'--testrunner',str(lua),str(a.rom.resolve()),'--timeout=90','--enableStdout'];r=subprocess.run(command,env=env,capture_output=True,timeout=105,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (out/'stdout.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr)
 report={'rom_path':str(a.rom.resolve()),'rom_sha256':sha(a.rom),'exe_source':str(a.mesen.resolve()),'exe_sha256':sha(exe),'settings_sha256':sha(settings),'lua_sha256':sha(lua),'command':command,'exit_code':r.returncode,'mode':'cold boot/reset each root in fresh portable directory; controlled CPU A=0..6 at $8751 native PHA','input_sequence':'Each reset: Start 240..247; capture 30/120 frames after native label draw completes; reset at +150','rom_ram_ppu_writes':False,'cpu_register_writes':'Seven logged A injections; original A recorded. ROM is not patched by Lua.','scope':'All seven name renderer branches and transition; not natural progression to all enemy encounters','files':{p.name:sha(p) for p in out.iterdir() if p.is_file()}}
 (out/'environment.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');assert r.returncode==0 and all((out/f'root_{i}_{s}.png').is_file() for i in range(7) for s in ('label','after'))
 print(json.dumps({k:v for k,v in report.items() if k not in ('files','command')},indent=2))
if __name__=='__main__':main()
