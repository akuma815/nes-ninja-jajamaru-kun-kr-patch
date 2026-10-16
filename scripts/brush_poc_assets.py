"""Direct-raster brush typeface on five existing 16x16 glyphs only."""
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from nes_graphics import encode_tile,decode_tile

def brush_poc_writes(root,source,cfg):
    path=root/cfg['brush_poc_path'];spec=json.loads(path.read_text(encoding='utf-8'))
    assert hashlib.sha256(source).hexdigest()==spec['source_sha256']
    fontpath=root/spec['font']['path'];assert hashlib.sha256(fontpath.read_bytes()).hexdigest()==spec['font']['sha256'] and (root/spec['font']['license_path']).is_file()
    f=ImageFont.truetype(str(fontpath),spec['font']['size']);cmap=TTFont(fontpath).getBestCmap();writes=[];glyphs=[];mapping={};masks={};used=set()
    folder=path.parent
    for g in spec['glyphs']:
        ch=g['text'];slot=g['slot'];assert ord(ch) in cmap and ch not in mapping and not used.intersection(range(slot,slot+4));used.update(range(slot,slot+4));mapping[ch]=slot
        scratch=Image.new('L',(48,48));ImageDraw.Draw(scratch).text((16+spec['font']['origin'][0],16+spec['font']['origin'][1]),ch,font=f,fill=255)
        scratch=scratch.point(lambda p:255 if p>=spec['font']['threshold'] else 0);box=scratch.getbbox();assert box and 16<=box[0]<box[2]<=32 and 16<=box[1]<box[3]<=32,'Thresholded brush glyph clipped'
        mask=scratch.crop((16,16,32,32));pixels=bytes(3 if p else 0 for p in mask.getdata());masks[ch]=pixels
        raw=[]
        for k in range(4):
            tile=bytes(3 if p else 0 for p in mask.crop(((k%2)*8,(k//2)*8,(k%2+1)*8,(k//2+1)*8)).getdata());data=encode_tile(tile);assert decode_tile(data)==tile
            writes.append((spec['chr_base']+(slot+k)*16,data,f'brush_poc_glyph_{ord(ch):04X}_{k}'));raw.append(data.hex())
        mask.save(folder/f'U{ord(ch):04X}.png')
        glyphs.append({'text':ch,'slot':slot,'cmap_glyph':cmap[ord(ch)],'ink_bbox':[v-16 for v in box],'pixel_hex':pixels.hex(),'chr_hex':''.join(raw),'ink_pixels':sum(bool(v) for v in pixels)})
    assert used==set(spec['contract']['allowed_slots']) and len(masks)==len(set(masks.values()))==5
    entries=[]
    for e in spec['entries']:
        expected=bytes.fromhex(e['expected_hex']);assert source[e['offset']:e['offset']+len(expected)]==expected
        assert bytes(mapping[ch] for ch in e['ko'])+b'\0'==expected,'PoC must preserve original name code lists'
        im=Image.new('L',(16,16*len(e['ko'])))
        for y,ch in enumerate(e['ko']):im.paste(Image.frombytes('L',(16,16),bytes(255 if p else 0 for p in masks[ch])),(0,16*y))
        png=folder/(e['id']+'_kr.png');im.save(png);entries.append({**e,'encoded_hex':expected.hex(),'png':png.relative_to(root).as_posix()})
    report={'spec_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'font_sha256':spec['font']['sha256'],'font_size':spec['font']['size'],'origin':spec['font']['origin'],'threshold':spec['font']['threshold'],'glyph_count':5,'tile_count':20,'mapping':mapping,'glyphs':glyphs,'entries':entries,'scope':spec['scope'],'checks':{'actual_precomposed_cmap':'PASS 5 syllables','thresholded_bounds':'PASS common origin; no scaling or artificial stroke expansion','unchanged_prg':'PASS no text/pointer/code edits for PoC','allocated_tiles':'PASS exactly original five glyph quads'},'font_audit_note':'Standalone jongseong audit recorded separately; only five actual precomposed syllables are used'}
    return writes,report
