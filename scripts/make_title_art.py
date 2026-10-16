"""Original hand-drawn pixel Hangul; no third-party font or AI bitmap."""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PALETTE=[0,0,0,248,184,0,184,40,24,24,56,184]+[0]*756
def glyph(ch,small=False):
    im=Image.new('L',(7,10) if small else (11,13));d=ImageDraw.Draw(im)
    def lines(*paths):
        for path in paths:d.line(path,fill=255,width=1)
    if small and ch=='닌':lines([(0,0),(0,4),(3,4)],[(5,0),(5,4)],[(1,6),(1,9),(6,9)])
    elif small and ch=='자':lines([(0,0),(4,0)],[(2,1),(2,2),(0,6)],[(2,2),(4,6)],[(5,0),(5,9)],[(5,4),(6,4)])
    elif ch=='자':lines([(0,0),(6,0)],[(3,1),(3,3),(0,9)],[(3,3),(6,9)],[(8,0),(8,12)],[(8,5),(10,5)])
    elif ch=='마':lines([(0,0),(6,0),(6,12),(0,12),(0,0)],[(8,0),(8,12)],[(8,5),(10,5)])
    elif ch=='루':lines([(0,0),(10,0),(10,3),(0,3),(0,6),(10,6)],[(0,9),(10,9)],[(5,9),(5,12)])
    elif ch=='군':lines([(0,0),(10,0),(10,3)],[(0,5),(10,5)],[(5,5),(5,8)],[(1,9),(1,12),(10,12)])
    else:raise ValueError(ch)
    return im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)
def main():
    im=Image.new('P',(184,40),0);im.putpalette(PALETTE)
    def paste(ch,x,y,color,small=False):
        body=glyph(ch,small);mask=Image.new('L',(body.width+2,body.height+2));mask.paste(body,(1,1))
        outline=mask.filter(ImageFilter.MaxFilter(3));im.paste(1,(x,y),outline);im.paste(color,(x,y),mask)
    paste('닌',0,9,2,True);paste('자',19,9,2,True)
    for i,ch in enumerate('자자마루군'):paste(ch,42+i*28,5,3)
    out=ROOT/'assets/title';out.mkdir(parents=True,exist_ok=True);im.save(out/'title_kr_001.png')
    im.convert('RGB').resize((736,160),Image.Resampling.NEAREST).save(ROOT/'build/title_kr_001_art_preview.png')
    print('Created title_kr_001.png: 184x40 palette-indexed original pixel art')
if __name__=='__main__':main()
