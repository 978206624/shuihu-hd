import ast,sys
from pathlib import Path
x=ast.parse(Path('/workspace/shawu/m1-work/binjgb/scripts/disasm.py').read_text());v={}
for n in x.body:
 if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['OPCODE_BYTES','OPCODE_MNEMONIC','CB_OPCODE_MNEMONIC']:v[n.targets[0].id]=ast.literal_eval(n.value)
b=Path('/workspace/shawu/game.gbc').read_bytes()
def dis(start,end,bank=0):
 a=start
 while a<end:
  i=a+(bank-1)*0x4000 if bank else a;op=b[i];n=v['OPCODE_BYTES'][op] or 1;ss=v['OPCODE_MNEMONIC'][op]
  if op==0xcb:n=2;ss=v['CB_OPCODE_MNEMONIC'][b[i+1]]
  elif n==3:ss=ss%f'${int.from_bytes(b[i+1:i+3],"little"):04x}'
  elif n==2:
   val=b[i+1]
   if op in [0x18,0x20,0x28,0x30,0x38]:ss=ss%f'${a+2+(val if val<128 else val-256):04x}'
   elif '%s' in ss:ss=ss%f'${val:02x}'
   else:ss=ss%val
  print(f'{bank:02x}:{a:04x} {b[i:i+n].hex(" "):8s} {ss}');a+=n
if __name__=='__main__':dis(int(sys.argv[1],16),int(sys.argv[2],16),int(sys.argv[3],16) if len(sys.argv)>3 else 0)
