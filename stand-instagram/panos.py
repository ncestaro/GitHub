# Panoramas 2160x1440 split into two 1080x1440 slides (Higgsfield relit)
import cv2, os
from PIL import Image
from grade import grade
P=[('p0_0560','panorama_stand'),('p2_0549','panorama_griglia'),('p3_0553','panorama_parete_piatti'),('p1_0560people','panorama_stand_visitatori')]
os.makedirs('work/v2/tmp',exist_ok=True); os.makedirs('panorami',exist_ok=True)
for src,name in P:
    im=Image.open(f'work/hf/out/{src}.png').convert('RGB'); W,H=im.size
    h=int(W/1.5); h=min(h,H); w=int(h*1.5); im=im.crop(((W-w)//2,(H-h)//2,(W-w)//2+w,(H-h)//2+h)).resize((2160,1440),Image.LANCZOS)
    t=f'work/v2/tmp/{src}.png'; im.save(t); g=grade(t)
    cv2.imwrite(f'panorami/{name}_intera.jpg',g,[cv2.IMWRITE_JPEG_QUALITY,95])
    cv2.imwrite(f'panorami/{name}_slide_a.jpg',g[:,:1080],[cv2.IMWRITE_JPEG_QUALITY,95])
    cv2.imwrite(f'panorami/{name}_slide_b.jpg',g[:,1080:],[cv2.IMWRITE_JPEG_QUALITY,95])
print(sorted(os.listdir('panorami')))
