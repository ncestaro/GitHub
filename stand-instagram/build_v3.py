# Carousel v3: verticals + panoramas split into two slides
import shutil, os
from PIL import Image
F='finali_editoriale/'; P='panorami/'
SEQ=[F+'aeffe_01_hero_0589_hf.jpg',P+'panorama_stand_slide_a.jpg',P+'panorama_stand_slide_b.jpg',F+'aeffe_02_dettaglio_rubinetto_0607.jpg',F+'aeffe_03_piatti_doccia_0602_hf.jpg',F+'aeffe_04_dettaglio_felci_0603.jpg',F+'aeffe_05_parete_docce_0603_hf.jpg',P+'panorama_griglia_slide_a.jpg',P+'panorama_griglia_slide_b.jpg',F+'aeffe_07_lavabo_0564_hf.jpg',F+'aeffe_08_visitatori_0600_hf.jpg',F+'aeffe_09_ritratto_0617.jpg']
out='carosello_v3'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
for i,s in enumerate(SEQ,1):
    b=os.path.basename(s).replace('aeffe_',''); b=b[3:] if b[:2].isdigit() else b
    shutil.copy(s,f'{out}/{i:02d}_{b}')
fs=sorted(os.listdir(out)); T=[Image.open(f'{out}/{f}').resize((300,400)) for f in fs]
c=Image.new('RGB',(6*300+7*8,2*400+3*8),(245,244,241))
for i,t in enumerate(T):
    r,k=divmod(i,6); x=8+k*308-(8 if i in (2,3,4,5,8,9,10,11) else 0); c.paste(t,(x,8+r*408))
c.save('anteprima_carosello_v3.jpg',quality=90)
