import cv2, numpy as np, json, sys, os
vp=json.load(open('work/vp.json'))
# per photo: (order, keystone_strength, extra_rot_deg, zoom, cx, cy)
P={
 '0589':(1,1.0,0,0.90,0.50,0.56),
 '0604':(2,1.0,0,0.96,0.50,0.52),
 '0602':(3,1.0,0,0.96,0.50,0.50),
 '0607':(4,0.8,0,0.98,0.50,0.50),
 '0605':(5,1.0,0,0.84,0.46,0.45),
 '0564':(6,1.0,0,0.94,0.50,0.52),
 '0598':(7,0.0,0,0.92,0.50,0.55),
 '0600':(8,0.8,0,0.72,0.64,0.385),
 '0617':(9,0.6,0,0.94,0.50,0.50),
}
os.makedirs('work/crop',exist_ok=True)
only=sys.argv[1:] or list(P)
for n in only:
    o,k,rot,z,cx,cy=P[n]
    im=cv2.imread(f'work/full/IMG_{n}.jpg'); H,W=im.shape[:2]
    T=np.eye(3)
    if vp.get(n) and k>0:
        vx,vy=vp[n][0]*H,vp[n][1]*H
        C=np.array([[1,0,-W/2],[0,1,-H/2],[0,0,1]]); Ci=np.linalg.inv(C)
        Hk=np.array([[1,-k*vx/vy,0],[0,1,0],[0,-k/vy,1]])
        T=Ci@Hk@C
    if rot:
        R=np.vstack([cv2.getRotationMatrix2D((W/2,H/2),rot,1),[0,0,1]]); T=R@T
    # valid region: warp mask
    out=cv2.warpPerspective(im,T,(W,H),flags=cv2.INTER_LANCZOS4)
    mask=cv2.warpPerspective(np.full((H,W),255,np.uint8),T,(W,H),flags=cv2.INTER_NEAREST)
    # find largest 3:4 box at (cx,cy) scaled by z, shrink until fully valid
    ch=min(H,W*4/3)*z
    while True:
        cw=ch*3/4; x0=int(cx*W-cw/2); y0=int(cy*H-ch/2)
        x0=max(0,min(W-int(cw),x0)); y0=max(0,min(H-int(ch),y0))
        if mask[y0:y0+int(ch),x0:x0+int(cw)].min()==255: break
        ch*=0.99
    crop=out[y0:y0+int(ch),x0:x0+int(cw)]
    crop=cv2.resize(crop,(1080,1440),interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'work/crop/{o:02d}_{n}.png',crop)
    print(n,'crop h frac',round(ch/H,3))
