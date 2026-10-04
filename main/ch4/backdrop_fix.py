import numpy as np, cv2
from PIL import Image
OUT='/home/claude/main/ch4/cut/'
bg=np.array(Image.open(OUT+'backdrop.png').convert('RGB')).astype(np.float32)
orig=np.array(Image.open('/home/claude/tides-of-magic/images/4-E.png').convert('RGB')).astype(np.float32)
H,W=bg.shape[:2]
st=np.zeros((H,W),np.float32)
import json; m=json.load(open(OUT+'meta.json'))
a=np.array(Image.open(OUT+'statue.png'))[...,3].astype(np.float32)/255
x0,y0,x1,y1=m['statue']; st[y0:y1,x0:x1]=a
# Goldschein der Statue aus dem Hintergrund nehmen
aura=cv2.GaussianBlur(cv2.dilate(st,np.ones((9,9))),(0,0),45); aura=np.clip(aura/aura.max()*2.2,0,1)
L=bg.mean(2,keepdims=True)+1e-3
warm=np.clip((bg[...,0:1]+bg[...,1:2])/2-bg[...,2:3],0,255)/80
target=np.minimum(L, 20+10*(1-aura[...,None]))
k=np.where(aura[...,None]>0.02, (target/L)**(aura[...,None]*np.clip(warm,0.3,1)), 1.0)
fixed=bg*k
fixed=fixed*(1-0.35*aura[...,None])+np.array([28,18,14],np.float32)*0.35*aura[...,None]
# Tigerfrau-Bereich: Boden von links hineinkopieren
t=np.zeros((H,W),np.float32); x0,y0,x1,y1=m['tiger']
t[y0:y1,x0:x1]=np.array(Image.open(OUT+'tiger.png'))[...,3].astype(np.float32)/255
tm=cv2.dilate((t>0.05).astype(np.uint8),np.ones((21,21))).astype(np.float32)
tm[:, 772:]=0
dx=-110
src=np.roll(orig,dx*-1,axis=1)*0  # placeholder
src=np.zeros_like(orig); src[:, :W+dx]=0; src[:, -dx:]=orig[:, :W+dx]
src=np.roll(orig, -dx, axis=1)
src=np.zeros_like(orig); src[:, -dx:] = orig[:, :W+dx]
src2=np.zeros_like(orig); src2[:, :]=orig; src2[:, 560:772]=orig[:, 560+dx:772+dx]
tmf=cv2.GaussianBlur(tm,(0,0),7)[...,None]
fixed=fixed*(1-tmf)+src2*tmf*0.85
Image.fromarray(np.clip(fixed,0,255).astype(np.uint8)).save(OUT+'backdrop2.png')
