import cv2, numpy as np, json
sel=['0589','0604','0602','0607','0605','0564','0598','0600','0617']
res={}
for n in sel:
    g=cv2.imread(f'work/full/IMG_{n}.jpg',0); H,W=g.shape; s=1600/max(H,W); gs=cv2.resize(g,None,fx=s,fy=s)
    lsd=cv2.createLineSegmentDetector(0); L=lsd.detect(gs)[0].reshape(-1,4)
    h,w=gs.shape; segs=[]
    for x1,y1,x2,y2 in L:
        dx,dy=x2-x1,y2-y1; l=np.hypot(dx,dy)
        if l>h*0.06 and abs(dx)<abs(dy)*np.tan(np.radians(10)): segs.append((x1,y1,x2,y2,l))
    S=np.array(segs)
    # lines in homogeneous coords, normalized coords centered
    def line(r):
        p=np.array([r[0]-w/2,r[1]-h/2,w/2]); q=np.array([r[2]-w/2,r[3]-h/2,w/2]); c=np.cross(p,q); return c/np.linalg.norm(c[:2])
    Ls=np.array([line(r) for r in S]); wt=S[:,4]
    # RANSAC-ish: VP minimizing weighted |l.v|
    best=None
    rng=np.random.default_rng(0)
    for _ in range(2000):
        i,j=rng.choice(len(Ls),2,replace=False); v=np.cross(Ls[i],Ls[j])
        if abs(v[2])<1e-9: v=v/np.linalg.norm(v)
        else: v=v/np.linalg.norm(v)
        d=np.abs(Ls@v)/np.linalg.norm(v)
        # angular error: distance of line from vp direction; use angle between segment and direction to vp
        mids=np.c_[(S[:,0]+S[:,2])/2-w/2,(S[:,1]+S[:,3])/2-h/2]
        if abs(v[2])>1e-9: vp=v[:2]/v[2]*(w/2); dirs=vp-mids
        else: dirs=np.tile(v[:2],(len(S),1))
        seg=np.c_[S[:,2]-S[:,0],S[:,3]-S[:,1]]
        cosang=np.abs((dirs*seg).sum(1))/(np.linalg.norm(dirs,axis=1)*np.linalg.norm(seg,axis=1)+1e-9)
        err=np.degrees(np.arccos(np.clip(cosang,0,1)))
        inl=err<0.7; sc=(wt*inl).sum()
        if best is None or sc>best[0]: best=(sc,v,inl.sum())
    v=best[1]
    if abs(v[2])>1e-9:
        vp=v[:2]/v[2]*(w/2)  # pixels relative to center
        tilt=np.degrees(np.arctan2(vp[0],abs(vp[1])))  # rotation of vertical axis
        print(f'{n}: segs={len(S)} inliers={best[2]} vp=({vp[0]/h:+.2f}h,{vp[1]/h:+.2f}h) tilt={tilt:+.2f}')
        res[n]=[float(vp[0]/h),float(vp[1]/h)]
    else: print(n,'vp at infinity'); res[n]=None
json.dump(res,open('work/vp.json','w'))
