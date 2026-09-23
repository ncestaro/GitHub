# Carousel v6 (final): GPT Image 2.5 editorial edit, elements unchanged, no extra grading.
import cv2, os, shutil
from finish_ai import fit
A='work/ai4/'; Q=[cv2.IMWRITE_JPEG_QUALITY,95]
SEQ=[('hero_gpt','copertina'),('pano_gpt','panorama_stand'),('rubinetto','dettaglio_rubinetto'),('piatti','piatti_doccia'),('felci','dettaglio_felci'),('docce','parete_docce'),('pgriglia','panorama_griglia'),('lav_gpt','lavabo_logo'),('visitatori','visitatori'),('ritratto','ritratto')]
ALT=[('pparete','panorama_parete_piatti'),('pvisit','panorama_stand_visitatori')]
out,hd,alt='carosello_v6','carosello_v6_HD','alternative_v6'
for d in (out,hd,alt): shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
n=1
for key,name in SEQ:
    g=cv2.imread(A+key+'.png')
    if key in ('pano_gpt','pgriglia'):
        full=fit(g,2160,1440); cv2.imwrite(f'{hd}/{name}_intera.jpg',fit(g,2400,1600),Q)
        for part,sl in (('a',full[:,:1080]),('b',full[:,1080:])): cv2.imwrite(f'{out}/{n:02d}_{name}_{part}.jpg',sl,Q); n+=1
    else:
        cv2.imwrite(f'{out}/{n:02d}_{name}.jpg',fit(g,1080,1440),Q); cv2.imwrite(f'{hd}/{n:02d}_{name}.jpg',fit(g,1740,2320),Q); n+=1
for key,name in ALT:
    g=cv2.imread(A+key+'.png'); full=fit(g,2160,1440)
    cv2.imwrite(f'{alt}/{name}_intera.jpg',fit(g,2400,1600),Q); cv2.imwrite(f'{alt}/{name}_a.jpg',full[:,:1080],Q); cv2.imwrite(f'{alt}/{name}_b.jpg',full[:,1080:],Q)
print(sorted(os.listdir(out)))
