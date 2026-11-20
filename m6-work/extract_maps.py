from pathlib import Path
from PIL import Image
import struct,json,hashlib,collections
R=Path('/workspace/shawu');O=R/'m6-work';ROM=(R/'game.gbc').read_bytes()
def off(bank,addr):return bank*0x4000+addr-0x4000 if addr>=0x4000 else addr
def read(bank,addr,n):return ROM[off(bank,addr):off(bank,addr)+n]
def word(b,i=0):return int.from_bytes(b[i:i+2],'little')
def describe(bank,addr):
 h=read(bank,addr,20);w,he=h[:2];ptrs=list(struct.unpack('<9H',h[2:]));return w,he,ptrs
rows=[];bad=[]
for group,(hb,table) in enumerate([(7,0x4000),(7,0x4e60),(0x50,0x4000),(0x50,0x53b5)]):
 p0=word(read(hb,table,2));limit=p0
 for i in range(256):
  p=word(read(hb,table+2*i,2))
  if p<table or p>0x7fff:break
  limit=min(limit,p)
  if table+2*(i+1)>=limit:break
 count=(limit-table)//2
 print('GROUP',group,'count',count,'first',hex(limit),flush=True)
 ptrs=[word(read(hb,table+2*i,2)) for i in range(count)];end= [0x4e60,0x7fff,0x53b5,0x5a10][group]
 for mid,p in enumerate(ptrs):
  try:
   base=read(hb,p,6);bank=base[0];ad=word(base,4);w,h,ps=describe(bank,ad)
   assert 0<w<65 and 0<h<65 and w*h<=1600 and all(0x4000<=t<0x8000 for t in [ps[0],ps[1],ps[2],ps[3],ps[4],ps[7]])
   rawlayout=read(bank,ps[0],1+w*h);layout=rawlayout[1:];block32=read(bank,ps[1],1024);block16=read(bank,ps[2],1024);attrs=read(bank,ps[3],256)
   gfx=bytearray(0x2000);copies=[]
   if ps[5]:
    gfx[0x1000:0x1800]=read(bank,ps[5],0x800);gfx[0x800:0xb00]=read(bank,ps[6],0x300);copies=[dict(bank=bank,src=ps[5],dest=0x9000,length=0x800),dict(bank=bank,src=ps[6],dest=0x8800,length=0x300)]
   else:
    q=ps[6]
    for _ in range(50):
     c=read(0x3e,q,7)
     if c[0]==255:break
     bk=c[0];dest=word(c,1);length=word(c,3);src=word(c,5);assert 0x8000<=dest<0xa000 and 0<length<=0x2000 and dest+length<=0xa000
     gfx[dest-0x8000:dest-0x8000+length]=read(bk,src,length);copies.append(dict(bank=bk,src=src,dest=dest,length=length));q+=7
    else:raise ValueError('bad gfx list')
   palraw=read(bank,ps[4],64);pal=[]
   for j in range(32):
    v=word(palraw,2*j);pal.append(((v&31)*8,((v>>5)&31)*8,((v>>10)&31)*8))
   tiles=[]
   for tid in range(256):
    t=Image.new('RGB',(8,8));pix=t.load();po=(attrs[tid]&7)*4;addr=0x1000+(tid if tid<128 else tid-256)*16
    for y in range(8):
     a,b=gfx[addr+2*y:addr+2*y+2]
     for x in range(8):z=((a>>(7-x))&1)+2*((b>>(7-x))&1);pix[x,y]=pal[po+z]
    tiles.append(t)
   im=Image.new('RGB',(w*32,h*32));grid=[]
   for by in range(h):
    for bx in range(w):
     v=layout[by*w+bx]
     for sy in range(2):
      for sx in range(2):
       sub=block32[v*4+sy*2+sx]
       for ty in range(2):
        for tx in range(2):
         tid=block16[sub*4+ty*2+tx];x=bx*4+sx*2+tx;y=by*4+sy*2+ty;im.paste(tiles[tid],(x*8,y*8));grid.append([x,y,tid,attrs[tid]])
   code=f'{group:02x}-{mid:02x}';path=O/'screens'/f'map_{code}.png';im.save(path)
   geom=hashlib.sha256(bytes([w,h])+layout+block32+block16+attrs+gfx+palraw).hexdigest()
   visiblehash=hashlib.sha256(im.tobytes()).hexdigest()
   nextp=min([t for t in ptrs if t>p]+[end]);variants=[]
   for a in range(p+6,nextp-11,12):
    v=read(hb,a,12);variants.append(dict(offset=f'{hb:02x}:{a:04x}',raw=v.hex(' '),npc_bank=v[4],npc_pointer=word(v,8),warp_pointer=word(v,10)))
   rows.append(dict(id=code,group=group,map_index=mid,header=f'{hb:02x}:{p:04x}',data=f'{bank:02x}:{ad:04x}',header_raw=base.hex(' '),width_tiles=w*4,height_tiles=h*4,area_tiles=w*h*16,layout_flag=rawlayout[0],pointers=ps,tileset_graphics=copies,tileset_id=hashlib.sha256(gfx+attrs+palraw).hexdigest()[:12],visual_sha256=visiblehash,geometry_sha256=geom,screenshot=str(path),variants=variants))
  except Exception as e:bad.append(dict(group=group,map_index=mid,header=f'{hb:02x}:{p:04x}',error=str(e),raw=read(hb,p,20).hex(' ')))
(O/'raw_maps.json').write_text(json.dumps(dict(maps=rows,rejected=bad),indent=2));print('accepted',len(rows),'rejected',len(bad),'unique images',len(set(x['visual_sha256'] for x in rows)),'tilesets',len(set(x['tileset_id'] for x in rows)),flush=True)
