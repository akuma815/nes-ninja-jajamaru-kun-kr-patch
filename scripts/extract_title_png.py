"""Extract the verified title logo directly from the declared ROM."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
from nes_graphics import decode_tile,encode_tile
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path);a=ap.parse_args()
    cfg=json.loads((ROOT/'config/source.json').read_text(encoding='utf-8'));src=a.source or ROOT/cfg['default_path'];rom=src.read_bytes()
    assert len(rom)==cfg['size'] and hashlib.sha256(rom).hexdigest()==cfg['sha256']
    spec=json.loads((ROOT/'config/title.json').read_text(encoding='utf-8'));m=rom[spec['map_file_offset']:spec['map_file_offset']+spec['map_size']]
    assert hashlib.sha256(m).hexdigest()==spec['map_sha256']
    im=Image.new('P',(184,40));im.putpalette([0,0,0,248,184,0,184,40,24,24,56,184]+[0]*756)
    for i,t in enumerate(m):
        tile=rom[spec['chr_base']+t*16:spec['chr_base']+(t+1)*16]
        assert encode_tile(decode_tile(tile))==tile
        im.paste(Image.frombytes('P',(8,8),decode_tile(tile)),((i%23)*8,(i//23)*8))
    out=ROOT/'analysis/raw';out.mkdir(parents=True,exist_ok=True)
    im.save(out/'title_original_indexed.png');im.convert('RGB').save(out/'title_original.png')
    ref=Image.new('RGB',(1104,480));ref.paste(im.convert('RGB').resize((1104,240),Image.Resampling.NEAREST),(0,120));ref.save(out/'title_original_reference_x6.png')
    print('Extracted native 184x40 logo + nearest-neighbor x6 reference')
if __name__=='__main__':main()
