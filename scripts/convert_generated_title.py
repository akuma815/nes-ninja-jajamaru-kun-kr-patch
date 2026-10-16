"""Convert an ImageGen logo to native NES palette/geometry, no dithering."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
COLORS=[(0,0,0),(248,184,0),(184,40,24),(24,56,184)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--name',default='title_kr_ai_001');a=ap.parse_args()
    if not a.name.replace('_','').isalnum():raise ValueError('Invalid artifact name')
    original=Image.open(a.input).convert('RGB')
    mask=Image.new('L',original.size);mask.putdata([255 if max(p)>80 else 0 for p in original.getdata()]);box=mask.getbbox();assert box
    crop=original.crop(box);ratio=min(182/crop.width,38/crop.height);size=(round(crop.width*ratio),round(crop.height*ratio))
    small=crop.resize(size,Image.Resampling.LANCZOS)
    values=[]
    for r,g,b in small.getdata():
        if max(r,g,b)<70:values.append(0)
        elif b>r*1.25 and b>g*1.12:values.append(3)
        elif r>g*1.6:values.append(2)
        else:values.append(1)
    content=Image.new('P',size);content.putdata(values)
    candidates=[];center=((184-size[0])//2,(40-size[1])//2)
    for y in range(41-size[1]):
        for x in range(185-size[0]):
            candidate=Image.new('P',(184,40));candidate.paste(content,(x,y))
            count=len({bytes(candidate.crop((tx,ty,tx+8,ty+8)).getdata()) for ty in range(0,40,8) for tx in range(0,184,8)}-{bytes(64)})
            if count<=94:candidates.append((abs(x-center[0])+abs(y-center[1]),count,x,y,candidate))
    if not candidates:raise ValueError('Generated art exceeds the verified 94-tile budget')
    _,_,offset_x,offset_y,im=min(candidates,key=lambda c:c[:4]);im.putpalette([c for p in COLORS for c in p]+[0]*756)
    out=ROOT/f'assets/title/{a.name}_nes.png';im.save(out)
    im.convert('RGB').resize((1104,240),Image.Resampling.NEAREST).save(ROOT/f'build/{a.name}_art_preview.png')
    tiles=[bytes(im.crop((x,y,x+8,y+8)).getdata()) for y in range(0,40,8) for x in range(0,184,8)]
    report={'schema_version':1,'input':str(a.input),'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'input_size':original.size,'foreground_bbox':box,'resized_content_size':size,'content_offset':[offset_x,offset_y],'packing':'Closest-to-center placement fitting original tile budget; no glyph edits','native_size':im.size,'palette':'original NES title palette indices 0..3, no dithering','unique_nonblank_tiles':len(set(tiles)-{bytes(64)}),'available_tiles':94,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'format conversion only; lettering design is the generated image'}
    (ROOT/f'build/{a.name}_conversion.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
