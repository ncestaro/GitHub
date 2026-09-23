# Grade v3: natural editorial look calibrated on reference stand photos.
# Neutral WB, local tone mapping (balanced highlights/shadows), tone curve
# matched to reference luminance percentiles, natural colour.
import cv2, numpy as np
from scipy.interpolate import PchipInterpolator
TA,TB=0.5,2.0                 # neutral target: true neutral, a hair warm
# target L percentiles (1,5,25,50,75,95,99.5) from the reference photos
TGT=np.array([2.5,6,24,44,62,85,96])
PCT=[1,5,25,50,75,95,99.5]
def s2l(x): return np.where(x<=0.04045,x/12.92,((x+0.055)/1.055)**2.4)
def l2s(x): x=np.clip(x,0,1); return np.where(x<=0.0031308,x*12.92,1.055*x**(1/2.4)-0.055)
def lab(bgr): return cv2.cvtColor(bgr.astype(np.float32),cv2.COLOR_BGR2LAB)
def neutral_mask(L):
    C=np.hypot(L[...,1],L[...,2]); return (C<14)&(L[...,0]>20)&(L[...,0]<90)
def white_balance(s):
    for _ in range(3):
        L=lab(s); m=neutral_mask(L)
        da=TA-np.median(L[...,1][m]); db=TB-np.median(L[...,2][m])
        ref=np.float32([[[0.5,0.5,0.5]]]); rl=lab(ref); rl[...,1]+=da*0.9; rl[...,2]+=db*0.9
        g=s2l(cv2.cvtColor(rl,cv2.COLOR_LAB2BGR))/s2l(ref); g=g/g.mean()
        s=l2s(s2l(s)*g.reshape(1,1,3))
    return s
def local_tonemap(Lc, strength=0.22, detail=1.08):
    # base/detail split in log domain; compress base range, boost detail
    lg=np.log(Lc/100+1e-3).astype(np.float32)
    r=max(Lc.shape)/80
    base=cv2.bilateralFilter(lg,d=0,sigmaColor=0.5,sigmaSpace=r)
    det=lg-base; mid=np.median(base)
    out=mid+(base-mid)*(1-strength)+det*detail
    return np.clip((np.exp(out)-1e-3)*100,0,100)
def tone_curve(Lc):
    src=np.percentile(Lc,PCT); src=np.maximum.accumulate(src+np.arange(len(src))*1e-3)
    x=np.concatenate([[0],src,[100]]); y=np.concatenate([[0],TGT,[100]])
    # blend 80% towards reference distribution, keep 20% of original character
    f=PchipInterpolator(x,y); return np.clip(0.8*f(Lc)+0.2*Lc,0,100)
def grade(f, exp_bias=0.0):
    s=cv2.imread(f).astype(np.float32)/255
    s=white_balance(s)
    Lab=lab(s); L0=Lab[...,0].copy()
    L1=local_tonemap(L0)
    L2=tone_curve(L1)+exp_bias
    Lab[...,0]=np.clip(L2,0,100)
    # colour: keep chroma proportional to the lightness change (avoids grey/washed look), natural saturation
    ratio=np.clip((L2+5)/(L0+5),0.7,1.4)**0.3
    a,b=Lab[...,1],Lab[...,2]; C=np.hypot(a,b); h=np.degrees(np.arctan2(b,a))%360
    k=ratio*1.02
    mag=np.exp(-((((h-330+180)%360)-180)/30)**2); k*=1-0.15*mag   # tame LED-screen magenta
    Lab[...,1]=a*k; Lab[...,2]=b*k
    out=cv2.cvtColor(Lab,cv2.COLOR_LAB2BGR)
    bl=cv2.GaussianBlur(out,(0,0),1.0); out=np.clip(out+0.22*(out-bl),0,1)
    return (out*255+0.5).astype(np.uint8)
