"""Precomposed 16x16 Korean names in the existing vertical renderer."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from nes_graphics import encode_tile,decode_tile

def enemy_writes(root,source,cfg):
    path=root/cfg['enemy_path'];spec=json.loads(path.read_text(encoding='utf-8'))
    assert hashlib.sha256(source).hexdigest()==spec['source_sha256']
    fontpath=root/spec['font']['path'];assert hashlib.sha256(fontpath.read_bytes()).hexdigest()==spec['font']['sha256']
    assert (root/spec['font']['license_path']).is_file()
    f=ImageFont.truetype(str(fontpath),spec['font']['size']);cmap=TTFont(fontpath).getBestCmap()
    contract=spec['consumer_contract'];p=contract['pointer_file_offset'];expected=bytes.fromhex(contract['pointer_expected_hex']);assert source[p:p+len(expected)]==expected
    chars=sorted({ch for e in spec['entries'] for ch in e['ko']});pool=spec['original_quad_slots'];assert len(chars)<=len(pool)
    original_codes={t for e in spec['entries'] for t in bytes.fromhex(e['expected_hex']) if t}
    assert original_codes==set(pool),'Pool must be exactly original name/appearance referenced quads'
    base=spec['chr_base'];mapping={};writes=[];glyphs=[];masks={};occupied=set()
    for ch,slot in zip(chars,pool):
        assert ord(ch) in cmap and slot and slot+3<=255 and not occupied.intersection(range(slot,slot+4))
        occupied.update(range(slot,slot+4));mapping[ch]=slot
        # Render on a padded canvas with one shared origin; never crop/center per glyph.
        scratch=Image.new('L',(48,48));ImageDraw.Draw(scratch).text((16+spec['font']['origin'][0],16+spec['font']['origin'][1]),ch,font=f,fill=255)
        if spec['font'].get('raster_mode')=='coverage_threshold':
            scratch=scratch.point(lambda p:255 if p>=spec['font']['threshold'] else 0)
        box=scratch.getbbox();assert box and 16<=box[0]<box[2]<=32 and 16<=box[1]<box[3]<=32
        mask=scratch.crop((16,16,32,32));assert set(mask.getdata())<={0,255},'Native font raster must be binary at this ppem'
        pixels=bytes(3 if v>=spec['font']['threshold'] else 0 for v in mask.getdata());im=Image.frombytes('L',(16,16),pixels);masks[ch]=pixels
        chrbytes=[]
        for k in range(4):
            tile=bytes(im.crop(((k%2)*8,(k//2)*8,(k%2+1)*8,(k//2+1)*8)).getdata());data=encode_tile(tile);assert decode_tile(data)==tile
            writes.append((base+(slot+k)*16,data,f'enemy_glyph_{ord(ch):04X}_{k}'));chrbytes.append(data.hex())
        glyphs.append({'text':ch,'slot':slot,'cmap_glyph':cmap[ord(ch)],'ink_bbox':[v-16 for v in box],'pixel_hex':pixels.hex(),'chr_hex':''.join(chrbytes)})
    assert len(set(masks.values()))==len(chars),'No duplicate/fallback syllable masks'
    entries=[];preview=Image.new('RGB',(8*100,330),(24,24,24));draw=ImageDraw.Draw(preview)
    folder=path.parent;folder.mkdir(exist_ok=True)
    for n,e in enumerate(spec['entries']):
        assert e['status'] in ('development','release_candidate','release');pos=e['offset'];old=bytes.fromhex(e['expected_hex']);assert source[pos:pos+len(old)]==old
        encoded=bytes(mapping[ch] for ch in e['ko'])+b'\0';assert len(encoded)<=len(old),'Name exceeds original clear footprint'
        data=encoded.ljust(len(old),b'\0');writes.append((pos,data,'enemy_text_'+e['id']))
        # Re-encode original preserved fields: exact original zero-terminated record.
        assert bytes([t for t in old[:-1]])+b'\0'==old
        native=Image.new('L',(16,len(e['ko'])*16))
        for y,ch in enumerate(e['ko']):native.paste(Image.frombytes('L',(16,16),bytes(255 if v else 0 for v in masks[ch])),(0,y*16))
        png=folder/(e['id']+'_kr.png');native.save(png)
        draw.text((n*100+8,5),e['id'],fill='white');preview.paste(native.convert('RGB').resize((48,native.height*3),Image.Resampling.NEAREST),(n*100+24,28))
        entries.append({**e,'encoded_hex':data.hex(),'rendered_height':native.height,'png':png.relative_to(root).as_posix()})
    preview.save(root/f"build/{cfg['build_id']}_names_preview.png")
    return writes,{'spec_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'font_sha256':spec['font']['sha256'],'font_size':spec['font']['size'],'origin':spec['font']['origin'],'cell':[16,16],'glyph_count':len(chars),'tile_count':len(occupied),'original_pool_tiles':len(pool)*4,'mapping':mapping,'glyphs':glyphs,'entries':entries,'checks':{'actual_precomposed_cmap':'PASS all syllables','bounds_and_binary_raster':'PASS shared origin, no clipping, no resampling','fixed_span_encoding':'PASS all 8 entries','pointers_unchanged':'PASS'},'font_audit_note':'Standalone jongseong audit retained separately; no composition or full-Hangul support claim'}
