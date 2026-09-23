from PIL import Image, ImageDraw
sel=['0589','0604','0602','0607','0605','0564','0598','0600','0617']
ims=[]
for n in sel:
    im=Image.open(f'work/full/IMG_{n}.jpg'); im.thumbnail((900,900)); d=ImageDraw.Draw(im)
    for x in range(0,im.width,im.width//12): d.line([(x,0),(x,im.height)],fill=(255,0,0),width=1)
    for y in range(0,im.height,im.height//12): d.line([(0,y),(im.width,y)],fill=(255,0,0),width=1)
    d.text((10,10),n,fill='yellow'); ims.append(im)
for k in range(0,9,3):
    g=ims[k:k+3]; W=sum(i.width for i in g)+20; c=Image.new('RGB',(W,900),'white'); x=0
    for i in g: c.paste(i,(x,0)); x+=i.width+10
    c.save(f'work/sheets/g{k//3}.jpg',quality=85)
