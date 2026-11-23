from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
root=Path(__file__).resolve().parent
W,H=1460,530
im=Image.new('RGB',(W,H),'#fbfcfe'); d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(n,b=False): return ImageFont.truetype(bold if b else font,n)
colors={'m-sealed':'#c5665d','p-public':'#718faf','z-owned':'#3e907d','zz-scratch':'#9481b6','a-pub':'#718faf','b-pub':'#718faf'}
cases=[('REVISION 0', [('m-sealed',64),('p-public',48),('z-owned',64),('zz-scratch',128)]),('MODIFIED BUNDLE',[('a-pub',48),('b-pub',64),('m-sealed',64),('z-owned',64),('zz-scratch',64)])]
d.text((38,23),'A ticket authorizes byte positions 112-175, not an immutable record',font=ft(28,True), fill='#1b2b42')
for idx,(title,records) in enumerate(cases):
 y=115+idx*185
 d.text((44,y-34),title,font=ft(21,True),fill='#244261')
 start=0
 for key,size in records:
  x0=45+round(start/304*1368);x1=45+round((start+size)/304*1368)-2
  d.rounded_rectangle((x0,y,x1,y+75),radius=9,fill=colors[key]);
  label=key.replace('zz-scratch','scratch')
  tw=d.textbbox((0,0),label,font=ft(19,True))[2]
  if tw<(x1-x0-12): d.text(((x0+x1-tw)/2,y+16),label,font=ft(19,True),fill='white')
  start+=size
 d.text((45,y+83),'0',font=ft(16),fill='#586777')
 d.text((1360,y+83),'304',font=ft(16),fill='#586777')
 x0=45+round(112/304*1368);x1=45+round(176/304*1368)
 d.rectangle((x0-3,y-4,x1+1,y+79),outline='#0b1c30',width=4)
 d.text((x0,y-27),'TICKET: 112-175',font=ft(16,True),fill='#1d2f47')
d.text((45,487),'Outlined region = the same byte offsets; the record occupying them changes.',font=ft(18),fill='#43566e')
im.save(root/'images'/'layout_comparison.png')
