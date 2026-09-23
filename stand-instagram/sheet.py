import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
files=sorted(glob.glob('work/thumb/*.jpg'))
os.makedirs('work/sheets',exist_ok=True)
T=520; per=6; cols=3
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',28)
except: font=ImageFont.load_default()
for s in range(0,len(files),per):
    grp=files[s:s+per]; rows=(len(grp)+cols-1)//cols
    sh=Image.new('RGB',(cols*T,rows*(T+10)),'white'); d=ImageDraw.Draw(sh)
    for i,f in enumerate(grp):
        im=Image.open(f); im.thumbnail((T-10,T-10))
        x=(i%cols)*T+(T-im.width)//2; y=(i//cols)*(T+10)+5
        sh.paste(im,(x,y)); n=os.path.basename(f)[:-4].replace('IMG_','')[:8]
        d.rectangle([x,y,x+140,y+38],fill='black'); d.text((x+6,y+3),n,fill='yellow',font=font)
    sh.save(f'work/sheets/s{s//per:02d}.jpg',quality=85)
print(len(files))
