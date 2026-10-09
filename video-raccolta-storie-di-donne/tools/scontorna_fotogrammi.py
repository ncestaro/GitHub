import sys, time, pathlib
from rembg import remove, new_session
from PIL import Image
src = pathlib.Path(sys.argv[1]); dst = pathlib.Path(sys.argv[2])
s = new_session('birefnet-general-lite')
files = sorted(src.glob('*.png'))
t0 = time.time()
for i, f in enumerate(files):
    o = dst / f.name
    if o.exists(): continue
    m = remove(Image.open(f).convert('RGB'), session=s, only_mask=True)
    m.save(o)
    if i % 10 == 0: print(i, round(time.time() - t0), flush=True)
print('done', round(time.time() - t0))
