"""Trace fixed title menu consumer and check spare title slots in observed scenes."""
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
def main():
    cfg=json.loads((ROOT/'config/source.json').read_text(encoding='utf-8'));rom=(ROOT/cfg['default_path']).read_bytes();assert hashlib.sha256(rom).hexdigest()==cfg['sha256']
    table=rom[0x2c2a:0x2c31];assert table==bytes.fromhex('30 19 15 0a 22 0e 1b')
    rows=[r for r in csv.DictReader((ROOT/'qa/original/cold_boot_001/prg_reads.csv').open()) if r['pc']=='AC11' and 0x2c1a<=int(r['prg_offset'],16)<0x2c21]
    assert len(rows)==14 and bytes(int(r['value'],16) for r in rows)==table*2
    cpu=MPU();cpu.memory[0x8000:0xc000]=rom[16:0x4010];cpu.memory[0xc000:]=rom[16:0x4010];dis=Disassembler(cpu);listing=[];addr=0xabe2
    while addr<0xac1a:
        size,text=dis.instruction_at(addr);assert text!='???';listing.append({'address':addr,'bytes':rom[addr-0x8000+16:addr-0x8000+16+size].hex(),'instruction':text});addr+=size
    (ROOT/'analysis/menu_disassembly.json').write_text(json.dumps({'profile':'py65 1.2.0 documented NMOS 6502; analyzed fixed consumer extent only, no complete call graph claim','instructions':listing},indent=2)+'\n',encoding='utf-8')
    uses=[]
    for p in sorted((ROOT/'qa/title_kr_ai_002/cold_boot_001').glob('*_ppu.bin')):
        ppu=p.read_bytes()
        # Only the visible title-bank background table is relevant to these slots.
        if ppu[0x1000:0x2000]!=rom[0x7010:0x8010]:
            target=(ROOT/'build/title_kr_ai_002/Ninja_Jajamaru_kun_KR_title_ai_002.nes').read_bytes()
            if ppu[0x1000:0x2000]!=target[0x7010:0x8010]:continue
        for y in range(30):
            for x in range(32):
                if ppu[0x2000+y*32+x] in (0x8a,0x8b):uses.append([p.name,x,y])
    assert not uses, 'Spare slots have a visible reference in observed title-bank scenes'
    report={'source_sha256':cfg['sha256'],'menu_table_file_offset':0x2c2a,'menu_table_expected_hex':table.hex(),'menu_table_cpu_address':'0xAC1A','reader_next_pc':'0xAC11','source_read_count':len(rows),'original_labels':['1 PLAYER','2 PLAYERS'],'translation':['1인용','2인용'],'original_ppu_addresses':['0x226D','0x22AD'],'new_ppu_addresses':['0x226F','0x22AF'],'menu_glyph_slots':['0x8A','0x8B'],'original_literal_writes':[{'file_offset':0x2bf8,'expected_hex':'6d','new_hex':'6f','meaning':'one-player row start'},{'file_offset':0x2c0a,'expected_hex':'ad','new_hex':'af','meaning':'two-player row start'},{'file_offset':0x2c17,'expected_hex':'1c','new_hex':'30','meaning':'remove final S'}],'spare_slot_observed_uses':uses,'scope':'two title menu states and captured transitions; no whole-game tile audit claim'}
    (ROOT/'analysis/menu_survey.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
