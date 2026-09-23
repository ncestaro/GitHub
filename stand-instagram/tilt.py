import cv2, numpy as np, glob, sys
sel=['0589','0604','0602','0607','0605','0564','0598','0600','0617']
for n in sel:
    im=cv2.imread(f'work/full/IMG_{n}.jpg',0); h,w=im.shape; s=1200/max(h,w); im=cv2.resize(im,None,fx=s,fy=s)
    e=cv2.Canny(im,60,160); L=cv2.HoughLinesP(e,1,np.pi/720,80,minLineLength=120,maxLineGap=6)
    H,W=im.shape; out=[]
    for x1,y1,x2,y2 in L.reshape(-1,4):
        dx,dy=x2-x1,y2-y1
        if abs(dy)>abs(dx)*4:
            a=np.degrees(np.arctan2(dx,dy)); a=a-180 if a>90 else a+180 if a<-90 else a
            xm=(x1+x2)/2/W; out.append((xm,a,np.hypot(dx,dy)))
    o=np.array(out)
    # angle vs x position -> tilt=intercept at center, keystone=slope
    A=np.vstack([o[:,0]-0.5,np.ones(len(o))]).T; wts=o[:,2]
    k,b=np.linalg.lstsq(A*wts[:,None],o[:,1]*wts,rcond=None)[0]
    print(f'{n}: n={len(o)} tilt_center={b:+.2f}deg keystone_slope={k:+.2f}deg/width median={np.median(o[:,1]):+.2f}')
