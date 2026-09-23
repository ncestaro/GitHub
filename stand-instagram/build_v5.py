# Carousel v5: professional relighting (logo lit, floodlights removed), bokeh details,
# straightened panoramas; light finishing = neutral WB + saturation cap.
import cv2, os, shutil
from finish_ai import finish, fit
A='work/ai3/'
SEQ=[('01','hero_0589'),('pstand','panorama_stand'),('02','dettaglio_rubinetto_0607'),('03','piatti_doccia_0602'),('04b','dettaglio_felci_0603'),('05','parete_docce_0603'),('pgriglia','panorama_griglia'),('07','lavabo_0564'),('08','visitatori_0600'),('09','ritratto_0617')]
ALT=[('ppiatti','panorama_parete_piatti'),('pvisit','panorama_stand_visitatori')]
out,hd,alt='carosello_v5','carosello_v5_HD','alternative_v5'
for d in (out,hd,alt): shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
Q=[cv2.IMWRITE_JPEG_QUALITY,95]; n=1
for key,name in SEQ:
    g=finish(A+key+'.png')
    if key.startswith('p'):
        full=fit(g,2160,1440); cv2.imwrite(f'{hd}/{name}_intera.jpg',fit(g,2400,1600),Q)
        for part,sl in (('a',full[:,:1080]),('b',full[:,1080:])): cv2.imwrite(f'{out}/{n:02d}_{name}_{part}.jpg',sl,Q); n+=1
    else:
        cv2.imwrite(f'{out}/{n:02d}_{name}.jpg',fit(g,1080,1440),Q); cv2.imwrite(f'{hd}/{n:02d}_{name}.jpg',fit(g,1800,2400),Q); n+=1
for key,name in ALT:
    g=finish(A+key+'.png'); full=fit(g,2160,1440)
    cv2.imwrite(f'{alt}/{name}_intera.jpg',fit(g,2400,1600),Q)
    cv2.imwrite(f'{alt}/{name}_a.jpg',full[:,:1080],Q); cv2.imwrite(f'{alt}/{name}_b.jpg',full[:,1080:],Q)
print(sorted(os.listdir(out)), sorted(os.listdir(alt)))
