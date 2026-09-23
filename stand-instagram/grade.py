import cv2, numpy as np, glob, os, sys
os.makedirs('work/graded',exist_ok=True)
TA,TB=0.3,2.0          # neutral target (slightly warm)
TMED=55.0              # target median L
def s2l(x): return np.where(x<=0.04045,x/12.92,((x+0.055)/1.055)**2.4)
def l2s(x): x=np.clip(x,0,1); return np.where(x<=0.0031308,x*12.92,1.055*x**(1/2.4)-0.055)
def lab(bgr): return cv2.cvtColor(bgr.astype(np.float32),cv2.COLOR_BGR2LAB)
def grade(f, exp_bias=0.0):
    s=cv2.imread(f).astype(np.float32)/255
    # 1) white balance: gains in linear light so neutral surfaces hit target
    for _ in range(3):
        L=lab(s); C=np.hypot(L[...,1],L[...,2]); m=(C<14)&(L[...,0]>25)&(L[...,0]<90)
        da=TA-np.median(L[...,1][m]); db=TB-np.median(L[...,2][m])
        ref=np.float32([[[0.5,0.5,0.5]]]); rl=lab(ref); rl[...,1]+=da*0.9; rl[...,2]+=db*0.9
        tgt=cv2.cvtColor(rl,cv2.COLOR_LAB2BGR)
        g=s2l(tgt)/s2l(ref); g=g/g.mean()
        s=l2s(s2l(s)*g.reshape(1,1,3))
    # 2) exposure: match median L
    L=lab(s)[...,0]; med=np.median(L)
    lin=s2l(s); k=(s2l(np.float32((TMED+exp_bias)/100))/s2l(np.float32(med/100)))**0.8
    s=l2s(lin*k)
    # 3) tone curve on L: black/white points + soft S + lifted blacks
    Lab=lab(s); L=Lab[...,0]/100
    lo,hi=np.percentile(L,0.5),np.percentile(L,99.7)
    x=np.clip((L-lo)/(hi-lo),0,1)
    sc=x + 0.35*x*(1-x)*(x-0.5)            # gentle S
    y=0.025+0.955*np.clip(sc,0,1)             # matte blacks, soft whites
    # 4) clarity: local contrast on L (large radius)
    blur=cv2.GaussianBlur(y.astype(np.float32),(0,0),25)
    y=np.clip(y+0.18*(y-blur)*(1-np.abs(y-0.5)*1.4).clip(0,1),0,1)
    Lab[...,0]=y*100
    # 5) chroma: global -10%, magenta/pink (LED screens) -35%, greens slightly toward natural
    a,b=Lab[...,1],Lab[...,2]; C=np.hypot(a,b); h=np.degrees(np.arctan2(b,a))%360
    f_=np.full_like(C,0.90)
    mag=np.exp(-((((h-340+180)%360)-180)/30)**2); f_*=1-0.35*mag
    grn=np.exp(-((((h-140+180)%360)-180)/35)**2); f_*=1-0.05*grn
    Lab[...,1]=a*f_; Lab[...,2]=b*f_
    out=cv2.cvtColor(Lab,cv2.COLOR_LAB2BGR)
    # 6) output sharpening
    bl=cv2.GaussianBlur(out,(0,0),1.0); out=np.clip(out+0.35*(out-bl),0,1)
    return (out*255+0.5).astype(np.uint8)
bias={'0589':0,'0607':3,'0605':3}
for f in sorted(glob.glob('work/crop/*.png')):
    n=f.split('_')[-1][:4]
    out=grade(f,bias.get(n,0))
    cv2.imwrite('work/graded/'+os.path.basename(f)[:-4]+'.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,95])
    L=lab(out.astype(np.float32)/255); C=np.hypot(L[...,1],L[...,2]); m=(C<14)&(L[...,0]>25)&(L[...,0]<90)
    print(os.path.basename(f), f'Lmed={np.median(L[...,0]):.1f} a={np.median(L[...,1][m]):+.2f} b={np.median(L[...,2][m]):+.2f}')
