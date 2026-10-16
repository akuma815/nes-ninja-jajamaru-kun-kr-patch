"""Build from immutable source with prevalidated Expected Writes and IPS apply check."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from PIL import Image
from nes_graphics import decode_tile,encode_tile
from menu_assets import menu_writes
from enemy_assets import enemy_writes
from brush_poc_assets import brush_poc_writes
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def make_ips(source,target):
    out=bytearray(b'PATCH');i=0
    while i<len(source):
        if source[i]==target[i]:i+=1;continue
        start=i
        while i<len(source) and source[i]!=target[i] and i-start<65535:i+=1
        out+=start.to_bytes(3,'big')+(i-start).to_bytes(2,'big')+target[start:i]
    return bytes(out+b'EOF')
def apply_ips(source,patch):
    if patch[:5]!=b'PATCH':raise ValueError('Invalid IPS')
    out=bytearray(source);p=5
    while patch[p:p+3]!=b'EOF':
        if p+5>len(patch):raise ValueError('Truncated IPS')
        offset=int.from_bytes(patch[p:p+3],'big');n=int.from_bytes(patch[p+3:p+5],'big');p+=5
        if not n:
            n=int.from_bytes(patch[p:p+2],'big');data=patch[p+2:p+3]*n;p+=3
        else:data=patch[p:p+n];p+=n
        if len(data)!=n or offset+n>len(out):raise ValueError('IPS range invalid')
        out[offset:offset+n]=data
    if p+3!=len(patch):raise ValueError('Unexpected IPS tail')
    return bytes(out)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path);ap.add_argument('--output',type=Path);ap.add_argument('--config',type=Path,default=ROOT/'config/title.json');a=ap.parse_args()
    source_cfg=json.loads((ROOT/'config/source.json').read_text(encoding='utf-8'));cfg=json.loads(a.config.read_text(encoding='utf-8'));src=a.source or ROOT/source_cfg['default_path'];source=src.read_bytes()
    build_id=cfg.get('build_id','title_kr_ai_001');assert build_id.startswith('title_kr_') and build_id.replace('_','').isalnum()
    basename='Ninja_Jajamaru_kun_KR_title_'+build_id.removeprefix('title_kr_')
    if len(source)!=source_cfg['size'] or sha(source)!=source_cfg['sha256']:raise ValueError('Unsupported source ROM size/SHA-256')
    assert source[:16].hex()==source_cfg['header_hex']
    m=cfg['map_file_offset'];n=cfg['map_size'];first=cfg['first_slot'];last=cfg['last_slot'];base=cfg['chr_base'];low=base+first*16;high=base+(last+1)*16
    assert sha(source[m:m+n])==cfg['map_sha256'] and sha(source[low:high])==cfg['original_chr_sha256']
    assert all(encode_tile(decode_tile(source[i:i+16]))==source[i:i+16] for i in range(0x4010,0x8010,16))
    art=ROOT/cfg['art_path'];im=Image.open(art);assert im.mode=='P' and im.size==(184,40) and max(im.getdata())<=3
    style_checks={}
    if 'suffix_constraints' in cfg:
        s=cfg['suffix_constraints'];sx,sy,sw,sh=s['region'];mx,my,mw,mh=s['main_region']
        suffix=im.crop((sx,sy,sx+sw,sy+sh));main=im.crop((mx,my,mx+mw,my+mh));sb=suffix.getbbox();mb=main.getbbox()
        assert sb and mb
        counts=Counter(p for p in suffix.getdata() if p);yellow_fraction=counts[1]/sum(counts.values());height=sb[3]-sb[1];main_height=mb[3]-mb[1]
        assert yellow_fraction>=s['min_yellow_fraction'] and not counts[2], 'Suffix must be yellow, without red fill'
        assert height<=main_height*s['max_height_ratio'], 'Suffix must remain small'
        style_checks={'suffix_bbox':[sx+sb[0],sy+sb[1],sb[2]-sb[0],height],'main_height':main_height,'suffix_height_ratio':height/main_height,'suffix_yellow_fraction':yellow_fraction,'result':'PASS small yellow suffix'}
    slots={bytes(64):cfg['blank_slot']};map_out=bytearray();tile_writes=[]
    for y in range(0,40,8):
        for x in range(0,184,8):
            tile=bytes(im.crop((x,y,x+8,y+8)).getdata())
            if tile not in slots:
                slot=first+len(slots)-1
                if slot>last:raise ValueError('Exceeded original logo tile budget')
                slots[tile]=slot;encoded=encode_tile(tile);assert decode_tile(encoded)==tile
                tile_writes.append((base+slot*16,encoded,f'logo_chr_slot_{slot:02X}'))
            map_out.append(slots[tile])
    writes=[(m,bytes(map_out),'title_logo_map')]+tile_writes
    menu_report={};menu_ranges={}
    if 'menu_path' in cfg:
        additional,menu_report=menu_writes(ROOT,source,cfg,slots)
        menu_ranges={owner:(offset,offset+len(data)) for offset,data,owner in additional}
        writes+=additional
    enemy_report={};enemy_ranges={}
    if 'enemy_path' in cfg:
        additional,enemy_report=enemy_writes(ROOT,source,cfg)
        enemy_ranges={owner:(offset,offset+len(data)) for offset,data,owner in additional}
        writes+=additional
    elif 'brush_poc_path' in cfg:
        additional,enemy_report=brush_poc_writes(ROOT,source,cfg)
        enemy_ranges={owner:(offset,offset+len(data)) for offset,data,owner in additional}
        writes+=additional
    # Freeze and validate the complete plan before touching the output image.
    touched=set();plan=[]
    for offset,data,owner in writes:
        if owner in enemy_ranges:
            allowed=enemy_ranges[owner]==(offset,offset+len(data))
        elif owner in menu_ranges:
            allowed=menu_ranges[owner]==(offset,offset+len(data))
        else:allowed=(m<=offset and offset+len(data)<=m+n) if owner=='title_logo_map' else (low<=offset and offset+len(data)<=high)
        assert allowed and not touched.intersection(range(offset,offset+len(data)))
        touched.update(range(offset,offset+len(data)))
        plan.append({'owner':owner,'coordinate':'absolute file byte offset','offset':offset,'length':len(data),'expected_original_hex':source[offset:offset+len(data)].hex(),'final_hex':data.hex()})
    target=bytearray(source)
    for w in plan:
        offset=w['offset'];data=bytes.fromhex(w['final_hex']);assert source[offset:offset+len(data)].hex()==w['expected_original_hex'];target[offset:offset+len(data)]=data
    target=bytes(target);diff={i for i,(s,t) in enumerate(zip(source,target)) if s!=t}
    assert len(source)==len(target) and diff<=touched and source[:16]==target[:16]
    protected_ranges=[(m,m+n),(low,high)]+list(menu_ranges.values())+list(enemy_ranges.values())
    assert all(source[i]==target[i] for i in range(len(source)) if not any(start<=i<end for start,end in protected_ranges))
    # Reconstruct pixels from the final ROM, independent of the slicing used above.
    reconstructed=bytearray(184*40)
    for cell,t in enumerate(target[m:m+n]):
        pixels=decode_tile(target[base+t*16:base+(t+1)*16])
        for py in range(8):
            for px in range(8):reconstructed[((cell//23)*8+py)*184+(cell%23)*8+px]=pixels[py*8+px]
    assert bytes(reconstructed)==bytes(im.getdata()), 'Final ROM pixels differ from artwork'
    if enemy_report:
        for e in enemy_report['entries']:
            pos=e['offset'];assert target[pos:pos+len(bytes.fromhex(e['encoded_hex']))].hex()==e['encoded_hex']
        for g in enemy_report['glyphs']:
            restored=bytearray(256)
            for k in range(4):
                offset=cfg['chr_base']+(g['slot']+k)*16;tile=decode_tile(target[offset:offset+16])
                for y in range(8):restored[((k//2)*8+y)*16+(k%2)*8:((k//2)*8+y)*16+(k%2)*8+8]=tile[y*8:y*8+8]
            assert restored.hex()==g['pixel_hex'],'Final ROM enemy pixels differ from font input'
    patch=make_ips(source,target);assert apply_ips(source,patch)==target
    out=(a.output or ROOT/'build'/build_id).resolve();out.mkdir(parents=True,exist_ok=True);rom_path=out/(basename+'.nes');rom_path.write_bytes(target)
    patch_dir=ROOT/'patches';patch_dir.mkdir(exist_ok=True);patch_path=patch_dir/(basename+'.ips');patch_path.write_bytes(patch)
    (out/'expected_writes.json').write_text(json.dumps({'schema_version':1,'source_sha256':sha(source),'writes':plan},indent=2)+'\n',encoding='utf-8')
    report={'schema_version':1,'build_id':build_id,'text':cfg['text'],'source_sha256':sha(source),'target_sha256':sha(target),'rom_path':str(rom_path),'size':len(target),'art_sha256':sha(art.read_bytes()),'patch_sha256':sha(patch),'patch_path':str(patch_path),'unique_nonblank_tiles':len(slots)-1,'available_tiles':last-first+1,'changed_bytes':len(diff),'write_count':len(writes),'checks':{'source_identity':'PASS','all_chr_roundtrip':'PASS 1024 tiles','expected_write_plan':'PASS','no_unregistered_diff':'PASS','protected_bytes_and_header':'PASS','rom_pixels_equal_art':'PASS','ips_apply_equals_build':'PASS'},'runtime':'Not performed by this builder; see qa evidence','scene_visual':'Not performed by this builder'}
    report['style_checks']=style_checks;report['menu']=menu_report
    report['total_title_slots_used']=len(slots)-1+len(menu_report.get('glyphs',[]))
    if enemy_report:report['enemy']=enemy_report
    (out/'build_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
