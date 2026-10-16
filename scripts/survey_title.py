"""Verify the observed fixed-revision title map and CHR consumer."""
import argparse,csv,hashlib,json
from pathlib import Path
from nes_graphics import decode_tile,encode_tile
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);ap.add_argument('--qa',type=Path,default=ROOT/'qa/original/cold_boot_001');a=ap.parse_args()
    cfg=json.loads((ROOT/'config/source.json').read_text());src=a.source or ROOT/cfg['default_path'];rom=src.read_bytes()
    assert len(rom)==cfg['size'] and hashlib.sha256(rom).hexdigest()==cfg['sha256']
    ppu=(a.qa/'frame_0060_ppu.bin').read_bytes();m=rom[0x317f:0x31f2]
    assert len(m)==115 and all(m[y*23:(y+1)*23]==ppu[0x2000+(y+6)*32+4:0x2000+(y+6)*32+27] for y in range(5))
    assert ppu[0x1000:0x2000]==rom[0x7010:0x8010], 'Observed BG CHR mapping differs'
    assert all(encode_tile(decode_tile(rom[a:a+16]))==rom[a:a+16] for a in range(0x4010,0x8010,16))
    rows=[r for r in csv.DictReader((a.qa/'prg_reads.csv').open()) if r['pc']=='AAC6' and 0x316f<=int(r['prg_offset'],16)<0x31e2]
    assert len(rows)==115 and bytes(int(r['value'],16) for r in rows)==m
    slots=sorted(set(m)-{0x30});assert slots==list(range(0x34,0x92))
    outside=[]
    for y in range(30):
        for x in range(32):
            if not (4<=x<27 and 6<=y<11) and ppu[0x2000+y*32+x] in slots:outside.append([x,y])
    assert not outside,'Title logo slots used outside logo'
    report={'schema_version':1,'source_sha256':cfg['sha256'],'mapper':87,'prg_offset':16,'prg_size':16384,'chr_offset':16400,'chr_size':16384,'title_chr_bank':1,'background_ppu_base':4096,'title_chr_file_base':28688,'logo_bounds':[32,48,184,40],'map_file_offset':12671,'map_bytes':115,'map_width':23,'map_height':5,'blank_tile':48,'logo_tile_slots':slots,'map_sha256':hashlib.sha256(m).hexdigest(),'logo_chr_sha256':hashlib.sha256(rom[0x7350:0x7930]).hexdigest(),'consumer_cpu_pc':'0xAAC6','consumer_read_count':len(rows),'consumer_cpu_data_start':'0xB16F','consumer_ppu_start':'0x20C4','consumer_stride':32,'consumer_row_width':23,'roundtrip':'PASS all 1024 CHR tiles','title_outside_slot_uses':outside,'observed_palette_indices':{'0':'universal black','1':'yellow 0x28','2':'red 0x16','3':'blue 0x12'},'scope':'Observed title only. Whole-game shared-asset coverage is not asserted.'}
    out=ROOT/'analysis/title_survey.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
