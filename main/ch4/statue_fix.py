import numpy as np, cv2, json
from PIL import Image
m=json.load(open('cut/meta.json')); x0,y0,x1,y1=m['statue']
orig=np.array(Image.open('/home/claude/tides-of-magic/images/4-E.png').convert('RGB')).astype(np.float32)
a=np.array(Image.open('cut/statue.png'))
al=a[...,3].astype(np.float32)/255
L=orig[y0:y1,x0:x1].mean(2)
# Träger entfernen (dunkel innerhalb ihrer Kästen)
for (bx0,by0,bx1,by1) in [(75,505,232,640),(286,505,388,630)]:
    sx0,sy0,sx1,sy1=max(bx0,x0)-x0,max(by0,y0)-y0,min(bx1,x1)-x0,min(by1,y1)-y0
    al[sy0:sy1,sx0:sx1]*=np.clip((L[sy0:sy1,sx0:sx1]-120)/60,0,1)
solid=(al>0.35).astype(np.uint8)
solid=cv2.morphologyEx(solid,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
# nur kleine Löcher füllen
inv=(1-solid).astype(np.uint8)
n,lab,stats,_=cv2.connectedComponentsWithStats(inv,connectivity=4)
for i in range(1,n):
    xx,yy,ww,hh,area=stats[i]
    touches = xx==0 or yy==0 or xx+ww>=solid.shape[1] or yy+hh>=solid.shape[0]
    if area<2500 and not touches: solid[lab==i]=1
soft=cv2.GaussianBlur(solid.astype(np.float32),(0,0),1.0)
new=np.where(solid>0, np.maximum(al,0.9), np.minimum(al,soft))
a[...,3]=(np.clip(new,0,1)*255).astype(np.uint8)
Image.fromarray(a).save('cut/statue.png'); print('ok')
