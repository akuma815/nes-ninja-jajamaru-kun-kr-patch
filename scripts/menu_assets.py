"""Generate the two native title-menu glyphs and a validated immutable write plan."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from nes_graphics import encode_tile,decode_tile
def menu_writes(root,source,title_cfg,logo_slots):
    spec_path=root/title_cfg['menu_path'];spec=json.loads(spec_path.read_text(encoding='utf-8'))
    assert hashlib.sha256(source).hexdigest()==spec['source_sha256']
    font_path=root/spec['font']['path'];assert hashlib.sha256(font_path.read_bytes()).hexdigest()==spec['font']['sha256']
    assert (root/spec['font']['license_path']).is_file()
    font=ImageFont.truetype(str(font_path),spec['font']['size']);mapping={' ':title_cfg['blank_slot']};writes=[];glyphs=[]
    preview=Image.new('L',(16,8));known_slots=set(logo_slots.values())
    for i,g in enumerate(spec['glyphs']):
        ch=g['text'];slot=g['slot'];assert ch not in mapping and slot not in known_slots and title_cfg['first_slot']<=slot<=title_cfg['last_slot']
        assert font.getmask(ch).getbbox() and font.getbbox(ch)[2]<=8 and font.getbbox(ch)[3]<=8
        mask=Image.new('L',(8,8));ImageDraw.Draw(mask).text(tuple(spec['font']['origin']),ch,font=font,fill=255)
        binary=bytes(3 if p>=spec['font']['threshold'] else 0 for p in mask.getdata());assert any(binary)
        encoded=encode_tile(binary);assert decode_tile(encoded)==binary
        writes.append((title_cfg['chr_base']+slot*16,encoded,f'menu_glyph_{ord(ch):04X}'))
        mapping[ch]=slot;known_slots.add(slot);glyphs.append({'text':ch,'slot':slot,'pixel_hex':binary.hex(),'chr_hex':encoded.hex()})
        preview.paste(Image.frombytes('L',(8,8),bytes(255 if p else 0 for p in binary)),(i*8,0))
    table=spec['table'];offset=table['file_offset'];expected=bytes.fromhex(table['expected_hex']);assert source[offset:offset+len(expected)]==expected
    assert len(table['tokens'])==len(expected)==7
    try:data=bytes(mapping[ch] for ch in table['tokens'])
    except KeyError as e:raise ValueError(f'Unmapped menu glyph: {e}')
    writes.append((offset,data,'menu_shared_table'))
    for w in spec['literal_writes']:
        expected=bytes.fromhex(w['expected_hex']);final=bytes.fromhex(w['final_hex']);assert len(expected)==len(final)==1
        assert source[w['offset']:w['offset']+1]==expected
        inst=bytes.fromhex(w['instruction_hex']);assert source[w['instruction_offset']:w['instruction_offset']+len(inst)]==inst
        writes.append((w['offset'],final,'menu_literal_'+w['id']))
    assert len(spec['entries'])==2
    for entry in spec['entries']:
        assert entry['status']=='development' and entry['ko']==str(entry['number_tile'])+''.join(table['tokens'][:2])
    preview.save(root/'assets/menu/menu_glyphs.png');preview.resize((256,128),Image.Resampling.NEAREST).save(root/f"build/{title_cfg['build_id']}_menu_glyph_preview.png")
    return writes,{'spec_sha256':hashlib.sha256(spec_path.read_bytes()).hexdigest(),'font_sha256':spec['font']['sha256'],'glyphs':glyphs,'mapping':mapping,'entries':spec['entries'],'table_hex':data.hex(),'consumed_length':table['consumed_length'],'text_status':'development, not a full-game release'}
