import os, glob
from PIL import Image, ImageOps, ImageDraw
import pillow_heif; pillow_heif.register_heif_opener()
os.makedirs('work/full',exist_ok=True); os.makedirs('work/thumb',exist_ok=True)
for p in sorted(glob.glob('src/*')):
    n=os.path.splitext(os.path.basename(p))[0]
    im=ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    exif=Image.open(p).getexif()
    print(n, im.size, exif.get(306), exif.get(272))
    im.save(f'work/full/{n}.jpg',quality=95)
    t=im.copy(); t.thumbnail((800,800)); t.save(f'work/thumb/{n}.jpg',quality=85)
