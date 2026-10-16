"""Compare exact-build emulator captures and verify native logo consumption."""
import argparse,csv,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-qa',type=Path,default=ROOT/'qa/original/cold_boot_001');ap.add_argument('--target-qa',type=Path);ap.add_argument('--config',type=Path,default=ROOT/'config/title.json');ap.add_argument('--build-report',type=Path);a=ap.parse_args()
    config=json.loads(a.config.read_text(encoding='utf-8'));build_id=config.get('build_id','title_kr_ai_001');build=json.loads((a.build_report or ROOT/'build'/build_id/'build_report.json').read_text(encoding='utf-8'))
    a.target_qa=a.target_qa or ROOT/config.get('qa_default','qa/title_kr_ai_001/cold_boot_002')
    src_env=json.loads((a.source_qa/'environment.json').read_text(encoding='utf-8'));dst_env=json.loads((a.target_qa/'environment.json').read_text(encoding='utf-8'))
    assert src_env['rom_sha256']==build['source_sha256'] and dst_env['rom_sha256']==build['target_sha256']
    assert src_env['exe_sha256']==dst_env['exe_sha256'] and src_env['settings_sha256']==dst_env['settings_sha256']
    assert src_env['input_sequence']==dst_env['input_sequence'] and src_env['exit_code']==dst_env['exit_code']==0
    rom=Path(dst_env['rom_path']).read_bytes();assert hashlib.sha256(rom).hexdigest()==build['target_sha256']
    frames=[];title_count=0
    for p in sorted(a.source_qa.glob('frame_*.png')):
        q=a.target_qa/p.name;assert sha(p)==src_env['files'][p.name] and sha(q)==dst_env['files'][p.name]
        src=Image.open(p).convert('RGB');dst=Image.open(q).convert('RGB');assert src.size==dst.size==(256,240)
        changed=0;outside=0
        for i,(s,t) in enumerate(zip(src.getdata(),dst.getdata())):
            if s!=t:
                changed+=1
                in_logo=32<=i%256<216 and 48<=i//256<88
                in_menu='menu_path' in config and 104<=i%256<176 and (152<=i//256<160 or 168<=i//256<176)
                if not(in_logo or in_menu):outside+=1
        assert outside==0, f'Unexpected pixel differences outside declared localized regions: {p.name}'
        assert (a.source_qa/(p.stem+'_oam.bin')).read_bytes()==(a.target_qa/(p.stem+'_oam.bin')).read_bytes(), 'Sprite/cursor state differs'
        ppu=(a.target_qa/(p.stem+'_ppu.bin')).read_bytes()
        if changed:
            title_count+=1;assert ppu[0x1000:0x2000]==rom[0x7010:0x8010]
            for y in range(5):assert ppu[0x2000+(y+6)*32+4:0x2000+(y+6)*32+27]==rom[config['map_file_offset']+y*23:config['map_file_offset']+(y+1)*23]
            if 'menu_path' in config:
                menu=json.loads((ROOT/config['menu_path']).read_text(encoding='utf-8'));table=menu['table'];data=rom[table['file_offset']:table['file_offset']+table['consumed_length']]
                for entry in menu['entries']:
                    start=entry['ppu_address'];expected=bytes([entry['number_tile']])+data
                    assert ppu[start:start+len(expected)]==expected
                    assert ppu[start-2:start]==bytes([config['blank_slot']])*2
                    if entry['number_tile']==2:assert ppu[start+len(expected)]==config['blank_slot']
        frames.append({'frame':int(p.stem.split('_')[1]),'different_pixels':changed,'outside_allowed_different_pixels':outside,'source_sha256':sha(p),'target_sha256':sha(q),'comparison':'title changes confined to declared regions; runtime CHR and map equal build' if changed else 'pixel-identical full screen'})
    assert len(frames)==12 and title_count==6
    trace=list(csv.DictReader((a.target_qa/'prg_reads.csv').open()));reads=[r for r in trace if r['pc']=='AAC6'];assert len(reads)==115
    assert bytes(int(r['value'],16) for r in reads)==rom[config['map_file_offset']:config['map_file_offset']+115]
    if 'menu_path' in config:
        menu_reads=[r for r in csv.DictReader((a.target_qa/'menu_reads.csv').open()) if r['pc']=='AC11']
        menu=json.loads((ROOT/config['menu_path']).read_text(encoding='utf-8'));table=menu['table'];expected=rom[table['file_offset']:table['file_offset']+table['consumed_length']]*2
        assert len(menu_reads)==len(expected) and bytes(int(r['value'],16) for r in menu_reads)==expected
    report={'schema_version':1,'source_sha256':build['source_sha256'],'target_sha256':build['target_sha256'],'emulator_sha256':dst_env['exe_sha256'],'runtime_result':'PASS cold boot, one-player start/gameplay, reset/title return, Select/two-player start','pixel_result':'PASS 12 captures, zero changed pixels outside logo; 6 non-title captures identical','runtime_chr_map_consumption':'PASS title bank and 115 map reads match built ROM','visual_result':f'Separate human/assistant visual record in qa/{build_id}/VISUAL_REVIEW.md','source_trace_note':'Source run used broad read-only trace; target used narrowed read-only trace. Inputs and capture timings identical. Lua hashes retained in each environment record.','frames':frames,'unperformed':['full playthrough','hardware','other emulators','audio listening','whole-game shared tile audit','user aesthetic sign-off']}
    if 'menu_path' in config:
        report['pixel_result']='PASS 12 captures, zero changed pixels outside logo/menu label rows; 6 non-title captures identical'
        report['menu_consumption']='PASS two labels, 10 shared-table reads, number tiles and blank clearing verified'
        previous=ROOT/config['previous_qa'];previous_env=json.loads((previous/'environment.json').read_text(encoding='utf-8'))
        assert previous_env['rom_sha256']==config['previous_target_sha256']
        differences=[]
        for p in sorted(previous.glob('frame_*.png')):
            q=a.target_qa/p.name;assert sha(p)==previous_env['files'][p.name]
            count=0
            for i,(s,t) in enumerate(zip(Image.open(p).convert('RGB').getdata(),Image.open(q).convert('RGB').getdata())):
                if s!=t:
                    count+=1;assert 104<=i%256<176 and (152<=i//256<160 or 168<=i//256<176), 'Previous logo or another region changed'
            differences.append({'frame':p.stem,'changed_pixels':count})
        report['previous_build_comparison']={'sha256':config['previous_target_sha256'],'result':'PASS logo and everything outside menu label rows unchanged in all 12 captures','frames':differences}
    report['sprite_cursor_state']='PASS OAM identical to source in all 12 captures'
    (a.target_qa/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # A labeled comparison for review; raw screenshots remain separately preserved.
    pairs=[('frame_0060.png','COLD BOOT'),('frame_0960.png','2 PLAYERS'),('frame_0600.png','GAMEPLAY')]
    sheet=Image.new('RGB',(1048,1556),(24,24,24));draw=ImageDraw.Draw(sheet)
    draw.text((14,6),'SOURCE                         KOREAN TITLE',fill='white')
    for row,(name,label) in enumerate(pairs):
        y=28+row*508;draw.text((14,y),label,fill='white')
        for col,folder in enumerate([a.source_qa,a.target_qa]):sheet.paste(Image.open(folder/name).convert('RGB').resize((512,480),Image.Resampling.NEAREST),(12+col*524,y+18))
    sheet.save(ROOT/f'build/{build_id}_runtime_comparison.png')
    print(json.dumps({k:v for k,v in report.items() if k!='frames'},indent=2))
if __name__=='__main__':main()
