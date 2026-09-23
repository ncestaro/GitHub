# Editorial v2 carousel: AI-cleaned (Higgsfield) + detail crops + unified grade
import cv2, numpy as np, os, shutil
from PIL import Image
from grade import grade
SEQ=[('01','work/v2/01_hero.jpg','hero_0589_hf'),
     ('02','work/v2/d_0607_faucet.jpg','dettaglio_rubinetto_0607'),
     ('03','work/hf/out/t2_0602.png','piatti_doccia_0602_hf'),
     ('04','work/v2/d_0603_fern.jpg','dettaglio_felci_0603'),
     ('05','work/hf/out/t1_0603.png','parete_docce_0603_hf'),
     ('06','work/hf/out/v2_0605.png','griglia_piatti_0605_hf'),
     ('07','work/hf/out/v2_0564.png','lavabo_0564_hf'),
     ('08','work/hf/out/v2_0600.png','visitatori_0600_hf'),
     ('09','work/crop/09_0617.png','ritratto_0617')]
os.makedirs('work/v2/tmp',exist_ok=True)
out='finali_editoriale'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
for n,src,name in SEQ:
    im=Image.open(src).convert('RGB'); W,H=im.size
    if W/H>0.75: w=int(H*0.75); im=im.crop(((W-w)//2,0,(W-w)//2+w,H))
    else: h=int(W/0.75); im=im.crop((0,(H-h)//2,W,(H-h)//2+h))
    im=im.resize((1080,1440),Image.LANCZOS); tmp=f'work/v2/tmp/{n}.png'; im.save(tmp)
    g=grade(tmp, 2 if n in ('02','04') else 0)
    cv2.imwrite(f'{out}/aeffe_{n}_{name}.jpg',g,[cv2.IMWRITE_JPEG_QUALITY,95])
T=[Image.open(f'{out}/'+f).resize((360,480)) for f in sorted(os.listdir(out))]
c=Image.new('RGB',(3*370+10,3*490+10),(245,244,241))
for i,t in enumerate(T): c.paste(t,(10+(i%3)*370,10+(i//3)*490))
c.save('anteprima_editoriale.jpg',quality=90); print(sorted(os.listdir(out)))
