# Carousel v4: AI re-render (Higgsfield, reference-style) + light finishing
# (neutral white balance, saturation cap) and split panoramas.
import cv2, numpy as np, os, shutil
from PIL import Image
from grade import white_balance, lab
def finish(src, cmax=24):
    s=cv2.imread(src).astype(np.float32)/255
    s=white_balance(s); L=lab(s); C=np.hypot(L[...,1],L[...,2]); p90=np.percentile(C,90)
    if p90>cmax: k=cmax/p90; L[...,1]*=k; L[...,2]*=k
    return (np.clip(cv2.cvtColor(L,cv2.COLOR_LAB2BGR),0,1)*255+.5).astype(np.uint8)
def fit(img,w,h):
    H,W=img.shape[:2]; r=w/h
    if W/H>r: nw=int(H*r); img=img[:,(W-nw)//2:(W-nw)//2+nw]
    else: nh=int(W/r); img=img[(H-nh)//2:(H-nh)//2+nh]
    return cv2.resize(img,(w,h),interpolation=cv2.INTER_AREA)
if __name__=='__main__':
    A="work/ai2/out/"
    SEQ=[('01','hero_0589'),('pstand','panorama_stand'),('02','dettaglio_rubinetto_0607'),('03','piatti_doccia_0602'),('04','dettaglio_felci_0603'),('05','parete_docce_0603'),('pgriglia','panorama_griglia'),('07','lavabo_0564'),('08','visitatori_0600'),('09','ritratto_0617')]
    out='carosello_v4'; hd='carosello_v4_HD'
    for d in (out,hd): shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    n=1
    for key,name in SEQ:
        g=finish(A+key+'.png')
        if key.startswith('p'):
            full=fit(g,2160,1440); cv2.imwrite(f'{hd}/{name}_intera.jpg',fit(g,2400,1600),[cv2.IMWRITE_JPEG_QUALITY,95])
            for part,sl in (('a',full[:,:1080]),('b',full[:,1080:])):
                cv2.imwrite(f'{out}/{n:02d}_{name}_{part}.jpg',sl,[cv2.IMWRITE_JPEG_QUALITY,95]); n+=1
        else:
            cv2.imwrite(f'{out}/{n:02d}_{name}.jpg',fit(g,1080,1440),[cv2.IMWRITE_JPEG_QUALITY,95])
            cv2.imwrite(f'{hd}/{n:02d}_{name}.jpg',fit(g,1800,2400),[cv2.IMWRITE_JPEG_QUALITY,95]); n+=1
    print(sorted(os.listdir(out)))
