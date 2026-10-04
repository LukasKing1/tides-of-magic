"""Ebenen aus Tafel 4-E schneiden: Statue, Kaiser (+Arm), Stein, Tigerfrau, Hintergrund (retuschiert)."""
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
SRC='/home/claude/tides-of-magic/images/4-E.png'
OUT='/home/claude/main/ch4/cut/'
im=np.array(Image.open(SRC).convert('RGB'))
H,W=im.shape[:2]
boxes={'emperor':((380,428,562,712),'u2net'),'stone':((522,432,652,550),'u2net'),
       'tiger':((618,618,776,968),'u2net'),'statue':((88,82,462,628),'isnet-general-use')}
sess={m:new_session(m) for m in ('u2net','isnet-general-use')}
full={}
for k,(b,m) in boxes.items():
    cr=Image.fromarray(im[b[1]:b[3],b[0]:b[2]])
    a=np.array(remove(cr,session=sess[m],only_mask=True)).astype(np.float32)/255
    A=np.zeros((H,W),np.float32); A[b[1]:b[3],b[0]:b[2]]=a; full[k]=A
# Statue: dunkle Teile (Träger, Schatten) und dünne Seile weg
L=im.astype(np.float32).mean(2)
st=full['statue']*np.clip((L-55)/50,0,1)
body=(st>0.35).astype(np.uint8)
op=cv2.morphologyEx(body,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
n,lab,stats,_=cv2.connectedComponentsWithStats(op)
big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]); keep=(lab==big).astype(np.uint8)
keep=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
yy,xx=np.mgrid[0:H,0:W]
halo=((xx-357)**2+(yy-168)**2<95**2)&(yy<230)
st=st*np.maximum(keep,halo.astype(np.float32))
full['statue']=st
# Kaiser: Arm als eigenes Teil (Schulter bei 497,492)
emp=full['emperor']
armpoly=np.array([[494,500],[497,470],[512,446],[522,432],[540,432],[540,470],[533,520],[532,565],[514,566],[505,520]],np.int32)
armm=np.zeros((H,W),np.uint8); cv2.fillPoly(armm,[armpoly],1)
armm=cv2.GaussianBlur(armm.astype(np.float32),(5,5),0)
full['arm']=emp*armm; full['emperor']=emp*(1-armm)
def save(name,A,pad=0):
    ys,xs=np.where(A>0.02); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    rgba=np.dstack([im,(np.clip(A,0,1)*255).astype(np.uint8)])[y0:y1,x0:x1]
    Image.fromarray(rgba).save(OUT+name+'.png'); return (int(x0),int(y0),int(x1),int(y1))
meta={k:save(k,v) for k,v in full.items()}
# Hintergrund: alles Bewegliche + Träger + Seile retuschieren
M=np.zeros((H,W),np.uint8)
for k in ('statue','emperor','arm','stone','tiger'): M|=(full[k]>0.05).astype(np.uint8)
M|=(boxes and (cv2.dilate((full['statue']>0.02).astype(np.uint8),np.ones((3,3)))))
for (x0,y0,x1,y1) in [(75,512,230,634),(290,508,384,624),(150,612,215,634)]: M[y0:y1,x0:x1]=1
for p,q in [((385,322),(716,507)),((200,352),(58,442)),((276,356),(136,482)),((150,445),(98,520))]:
    cv2.line(M,p,q,1,9)
M=cv2.dilate(M,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
# grob auf kleiner Auflösung füllen, dann fein
small=cv2.resize(im,(W//4,H//4),interpolation=cv2.INTER_AREA); ms=cv2.resize(M,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
f_small=cv2.inpaint(small,ms,7,cv2.INPAINT_TELEA)
up=cv2.resize(f_small,(W,H),interpolation=cv2.INTER_CUBIC)
fine=cv2.inpaint(im,M,9,cv2.INPAINT_TELEA)
mb=cv2.GaussianBlur(M.astype(np.float32),(0,0),6)[...,None]
inner=cv2.GaussianBlur(cv2.erode(M,np.ones((25,25))).astype(np.float32),(0,0),10)[...,None]
bg=fine*(1-inner)+up*inner
rng=np.random.default_rng(3); noise=rng.normal(0,5,(H,W,1)).astype(np.float32)
noise=cv2.GaussianBlur(noise,(0,0),1.2)[...,None] if noise.ndim==2 else cv2.GaussianBlur(noise[...,0],(0,0),1.2)[...,None]
bg=np.clip(bg+noise*mb,0,255).astype(np.uint8)
Image.fromarray(bg).save(OUT+'backdrop.png')
Image.fromarray((M*255).astype(np.uint8)).save(OUT+'inpaint_mask.png')
import json; json.dump(meta,open(OUT+'meta.json','w')); print(meta)
