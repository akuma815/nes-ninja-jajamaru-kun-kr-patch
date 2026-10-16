"""Check seven original/translated native renderer roots and protected pixels."""
import argparse,csv,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,default=ROOT/'config/title.json');ap.add_argument('--source-qa',type=Path,default=ROOT/'qa/title_kr_enemy_004/roots_source_001');ap.add_argument('--target-qa',type=Path);a=ap.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf-8'));build_id=cfg['build_id'];build=json.loads((ROOT/'build'/build_id/'build_report.json').read_text(encoding='utf-8'));spec=json.loads((ROOT/cfg['enemy_path']).read_text(encoding='utf-8'))
    folders=[a.source_qa,a.target_qa or ROOT/'qa'/build_id/'roots_target_001'];envs=[json.loads((p/'environment.json').read_text(encoding='utf-8')) for p in folders]
    assert [e['rom_sha256'] for e in envs]==[build['source_sha256'],build['target_sha256']]
    for key in ('exe_sha256','settings_sha256','lua_sha256','input_sequence'):assert envs[0][key]==envs[1][key]
    for q,e in zip(folders,envs):
        assert e['exit_code']==0 and all(sha(q/name)==h for name,h in e['files'].items())
    roms=[Path(e['rom_path']).read_bytes() for e in envs];assert [hashlib.sha256(r).hexdigest() for r in roms]==[build['source_sha256'],build['target_sha256']]
    logs=[list(csv.DictReader((p/'name_reads.csv').open())) for p in folders]
    glyphs={g['text']:g for g in build['enemy']['glyphs']};results=[]
    for n in range(7):
        entries=[spec['entries'][n],spec['entries'][-1]]
        for j,(q,rom) in enumerate(zip(folders,roms)):
            ppu=(q/f'root_{n}_label_ppu.bin').read_bytes();assert ppu[:0x2000]==rom[0x6010:0x8010]
            seen=[r for r in logs[j] if int(r['root'])==n]
            expected=[]
            for e in entries:
                codes=rom[e['offset']:].split(b'\0',1)[0]
                expected += [(e['offset']+k,t) for k,t in enumerate(codes+b'\0')]
                dst=e['ppu_address'];max_len=(len(bytes.fromhex(e['expected_hex']))-1)
                for k in range(max_len*4):
                    character=k//4;sub=k%4;value=codes[character]+sub if character<len(codes) else 0x30
                    assert ppu[dst+character*64+(sub//2)*32+sub%2]==value
            assert [(int(r['file_offset'],16),int(r['value'],16)) for r in seen]==expected,'Unexpected consumer reads or terminator'
        source=Image.open(folders[0]/f'root_{n}_label.png').convert('RGB');target=Image.open(folders[1]/f'root_{n}_label.png').convert('RGB');changes=0
        for i,(s,t) in enumerate(zip(source.getdata(),target.getdata())):
            if s!=t:
                changes+=1;assert any(x<=i%256<x+w and y<=i//256<y+h for x,y,w,h in (e['bounds'] for e in entries))
        for e in entries:
            x,y,_,_=e['bounds']
            for k,ch in enumerate(e['ko']):
                binary=bytes(3 if pixel!=(0,0,0) else 0 for pixel in target.crop((x,y+k*16,x+16,y+(k+1)*16)).getdata())
                assert binary.hex()==glyphs[ch]['pixel_hex'],'Screenshot syllable mask differs from source font'
        assert (folders[0]/f'root_{n}_label_oam.bin').read_bytes()==(folders[1]/f'root_{n}_label_oam.bin').read_bytes()
        for suffix in ('png','ppu.bin','oam.bin'):
            name=f'root_{n}_after'+('.png' if suffix=='png' else '_'+suffix)
            assert (folders[0]/name).read_bytes()==(folders[1]/name).read_bytes(),f'Post-label transition differs: {name}'
        results.append({'root':n,'ko':entries[0]['ko'],'changed_pixels':changes,'outside_bounds':0,'chr_map_trace_and_screenshot_mask':'PASS','after_transition':'PASS source-identical screen, PPU and OAM'})
    # Verify new writes cannot alter level-layout data, English patterns, cursor or prior logo/menu.
    prior=(ROOT/'build/title_kr_menu_003/Ninja_Jajamaru_kun_KR_title_menu_003.nes').read_bytes();plan=json.loads((ROOT/'build'/build_id/'expected_writes.json').read_text(encoding='utf-8'))['writes']
    allowed={i for w in plan if w['owner'].startswith('enemy_') for i in range(w['offset'],w['offset']+w['length'])}
    assert all(s==t or i in allowed for i,(s,t) in enumerate(zip(prior,roms[1])))
    assert roms[0][0x4010:0x7010]==roms[1][0x4010:0x7010],'Game bank0 or bank1 layout data changed'
    assert roms[0][0x7010:0x7350]==roms[1][0x7010:0x7350],'English pattern changed'
    assert roms[0][0x7dd0:0x7e10]==roms[1][0x7dd0:0x7e10],'Cursor quad DC..DF changed'
    table=roms[0][0xca9:0xcb1];layout_ranges=[(int.from_bytes(table[i:i+2],'little'),int.from_bytes(table[i:i+2],'little')+1024) for i in range(0,8,2)]
    assert all(0<=lo<hi<=0x1000 for lo,hi in layout_ranges)
    report={'schema_version':1,'target_sha256':build['target_sha256'],'result':'PASS 7 controlled renderer roots, 8 translations, original English and other assets protected','mode':'CPU A injected 0..6 at native $8751; not natural all-stage progression','roots':results,'level_layout_ppu_read_ranges':layout_ranges,'static_protection':'PASS game bank0, bank1 low pattern/layout region, English font, DC..DF cursor, previous Korean title/menu','unperformed':['Natural encounters of enemies 1..6','Full playthrough','Hardware','Audio listening','User aesthetic sign-off']}
    out=ROOT/'qa'/build_id;(out/'roots_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sheet=Image.new('RGB',(7*256,2*260),(24,24,24));draw=ImageDraw.Draw(sheet)
    for n in range(7):
        for row,q in enumerate(folders):
            x=n*256;y=row*260;draw.text((x+5,y+3),f'ROOT {n} '+('SOURCE' if row==0 else 'KOREAN'),fill='white');sheet.paste(Image.open(q/f'root_{n}_label.png').convert('RGB'),(x,y+20))
    sheet.save(ROOT/f'build/{build_id}_runtime_names.png');print(json.dumps(report,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
