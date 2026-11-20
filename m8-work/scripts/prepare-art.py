"""ROM-only, character-free full-map references; no emulation or RAM edits.
Cell-key metadata uses the unchanged M7 build_region_data.py definition.
"""
from pathlib import Path
from PIL import Image
import struct,json,hashlib,shutil
R=Path('/workspace/shawu'); W=R/'m8-work'; A=W/'art'; A.mkdir(exist_ok=True)
rom=(W/'runtime/assets/game.gbc').read_bytes()
assert hashlib.sha256(rom).hexdigest()=='ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95'
def read(b,a,n):
    off=b*0x4000+a-0x4000 if a>=0x4000 else a
    return rom[off:off+n]
def immutable(path,data):
    if path.exists(): assert path.read_bytes()==data,str(path)
    else: path.write_bytes(data)
def js(p,v): immutable(p,(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
styles={'town':R/'m6-work/region1/art/00-0c_gpt.png',
        'room':R/'m7-work/art/room_style.png',
        'forest':R/'m6-work/region1/art/forest_style.png'}
for key,p in styles.items(): immutable(A/f'{key}_style.png',p.read_bytes())
rows={m['id']:m for m in json.loads((R/'m6-work/raw_maps.json').read_text())['maps']}
names={'00-00':'东溪村','00-05':'东溪村会合屋','00-06':'东溪村庙宇','00-09':'村东南连通林道'}
specs=[]; manifest=[]; evidence=[]
codes=['00-00','00-01','00-02','00-03','00-04','00-05','00-06','00-09']
for code in codes:
    row=rows[code];b,a=[int(x,16) for x in row['data'].split(':')]
    w,h=read(b,a,2);ps=list(struct.unpack('<9H',read(b,a+2,18)))
    layout=read(b,ps[0]+1,w*h);blocks=read(b,ps[1],1024);subs=read(b,ps[2],1024);attrs=list(read(b,ps[3],256));gfx=bytearray(8192)
    for cp in row['tileset_graphics']:
        gfx[cp['dest']-0x8000:cp['dest']-0x8000+cp['length']]=read(cp['bank'],cp['src'],cp['length'])
    palettes=[]
    for j in range(32):
        v=int.from_bytes(read(b,ps[4]+j*2,2),'little');palettes.extend([(v&31)*8,((v>>5)&31)*8,((v>>10)&31)*8,255])
    keys=[];tileAttrs=[];tiles=[];im=Image.new('RGB',(w*32,h*32));pixels=im.load()
    for y in range(h*4):
        for x in range(w*4):
            big=layout[(y//4)*w+x//4]
            sub=subs[blocks[big*4+(y%4)//2*2+(x%4)//2]*4+(y%2)*2+(x%2)]
            at=attrs[sub];q=0x1000+(sub if sub<128 else sub-256)*16;hh=2166136261
            hh=((hh^(at&7))*16777619)&0xffffffff
            for yy in range(8):
                for xx in range(8):
                    cx=7-xx if at&32 else xx;cy=7-yy if at&64 else yy
                    ci=((gfx[q+cy*2]>>(7-cx))&1)|(((gfx[q+cy*2+1]>>(7-cx))&1)<<1)
                    hh=((hh^ci)*16777619)&0xffffffff
                    pi=((at&7)*4+ci)*4;pixels[x*8+xx,y*8+yy]=tuple(palettes[pi:pi+3])
            keys.append(hh);tileAttrs.append(at);tiles.append(sub)
    native=A/f'{code}_native.png'; ref=A/f'{code}_native_4x.png'
    if not native.exists(): im.save(native)
    else: assert Image.open(native).tobytes()==im.tobytes()
    # Nearest-neighbor enlargement is INPUT geometry reference only; it is
    # never used as an HD background or to fill runtime gaps.
    if not ref.exists(): im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(ref)
    scale=4 if im.width*im.height*16>=655360 else 5
    target=[im.width*scale,im.height*scale]
    kind='town' if code=='00-00' else 'forest' if code=='00-09' else 'room'
    specifics=''
    if code=='00-00': specifics='Exactly SEVEN existing thatched-roof building footprints, ONE river and ONE stone bridge, TWO wells, THREE notice boards. Retain all seven roof/door facades even though only six interiors were entered in this story state. Do not add an eighth building or a second bridge.'
    if code=='00-05': specifics='Preserve BOTH connected rooms, the narrow internal doorway, all visible tables/benches and existing bed, pot and cupboard groups. The people visible during play are NOT in the character-free input and must NOT be added.'
    if code=='00-06': specifics='Preserve the original central ceremonial altar fixture as inanimate architecture, the red runner, wall panel footprints, vessels and offering furniture. Do not introduce an animated deity, person, portrait or human-shaped statue. Existing written signs must be blank decorative panels. This shrine fixture requires especially careful human review against the native reference.'
    prompt=f'''Use case: style-transfer; Asset type: ONE complete authored HD 2D JRPG world background plate, never a tileset.
Image 1 is a character-free ORIGINAL ROM full map, native size {im.width}x{im.height}, shown at exact integer 4x nearest-neighbor ONLY as an input geometry reference. Map {code}. Image 2 is an approved existing V4 remaster full-map style reference ONLY.
Produce a newly hand-PAINTED premium V4 JRPG environment at {target[0]}x{target[1]} pixels, same exact {im.width}:{im.height} aspect ratio. Lock the full uncropped overhead orthographic rectangle and every normalized coordinate to image 1. No camera tilt, perspective, borders, vignettes or panels. Fine deliberate material texture, crisp painted detail, warm upper-left light, coherent original colors and Song dynasty environment materials; not photorealistic 3D, not pixel art, not smoothing or filtering the original.
GEOMETRY IS ABSOLUTE: retain the exact identity, count, x/y positions, widths/heights and footprint boundaries of EVERY building, door, closed door, window, road, shoreline, tree, shrub, rock, wall, floor, bridge, well, step, furniture and decoration. Preserve exit openings and walkable ground. Never widen roofs over roads, move stairs, invent rooms, add furniture or remove obstacles. Existing pure black outside-room regions stay pure black in their exact shape. {specifics}
Image 2 controls ONLY V4 brushwork, lighting and material richness. Do not copy its map layout or any people. Preserve the original identity of green/cool stone floor vs brown timber when present.
ZERO CHARACTERS OR MONSTERS: no people, animals, gods as characters, creatures, sprites, silhouettes, faces, portraits, speech bubbles, character shadows, UI, dialogue boxes, text, letters, numbers, watermarks or coordinate labels. Existing signboards remain same-count same-position blank boards. All real actors and game text will remain original native pixels from the unchanged game engine.
Output ONE full map only at the original aligned geometry, never a comparison sheet or tileset. Do not guess hidden native pixels or make an upscaled fallback. Layout fidelity has priority over decoration.
'''
    immutable(A/f'{code}_prompt.txt',prompt.encode())
    spec=dict(id=code,name=names.get(code,'东溪村室内 '+code),width=im.width,height=im.height,
      widthTiles=w*4,heightTiles=h*4,image=f'assets/region3/{code}_hd.png',
      imageNativeSize=im.width,imageNativeHeight=im.height,cellKeys=keys,tiles=tiles,
      attrs=tileAttrs,palettes=palettes,geometrySHA256=row['geometry_sha256'],
      native=str(native),gptSource=str(A/f'{code}_gpt.png'),artReady=False)
    specs.append(spec)
    manifest.append(dict(id=code,refs=[ref.name,f'{kind}_style.png'],prompt=f'{code}_prompt.txt',
      output=f'{code}_gpt.png',size=f'{target[0]}x{target[1]}',quality='medium',model='gpt-image-2',
      nativeSize=[im.width,im.height],requestedSize=target,reviewRequired=True))
    if code=='00-00': source=W/'play/south-village-settled'
    else: source=W/'play'/f'survey-{code}'
    result=json.loads((source/'result.json').read_text()); assert result['end']['map']==code
    evidence.append(dict(id=code,name=spec['name'],nativeSize=[im.width,im.height],
      geometrySHA256=row['geometry_sha256'],naturalReplay=str(source.relative_to(R)),
      nativeEndSHA256=hashlib.sha256((source/'latest.bin').read_bytes()).hexdigest(),
      independentDoorSurvey=code!='00-00',nameBasis='任务对白 + 00-08南口自然进入 + 00-05吴用会合；非现场地图标题' if code=='00-00' else '自然房门/图像或对白，仅描述已证实用途，无额外专名'))
js(A/'native-map-metadata.json',specs); js(A/'batch-manifest.json',manifest)
js(W/'region3-scope.json',dict(candidateMapCount=len(codes),maps=evidence,
 identificationEvidence=['m6-work/region1/council-mission/page_55.png：吴用要求至东溪村会合',
 'm8-work/play/south-village-arrival：00-08南门→00-00',
 'm8-work/play/survey-00-05：自然房门00-00→00-05',
 'm8-work/play/room05-left-npc-dialogue/page_0003.png：吴用',
 'm8-work/play/room05-left-npc-pages：吴用会合后story11→12'],
 nextStoryGate='story12：前往黄泥岗客栈会合，乔装掌柜、小二，埋伏生辰纲队伍；尚未进入该客栈或完成劫取',
 exclusions=['00-08既有M6野道沿用','黄泥岗00-1f..23及客栈为下一个任务，不属于本次八图',
 '00-09另一端00-0b及更远外域未自然进入，不声称已探索全部连通世界',
 '00-35未自然打开/进入，不计为已完成新图',
 '战斗/系统菜单/未绘地图不计八图分母；最终逐帧计数须另测，不能提前宣称覆盖率'],
 artStatus='PREPARED_NOT_GENERATED',notAllConnectedWorldMaps=True))
print(json.dumps(dict(prepared=len(manifest),runtimeUnmodified=True,outputs=str(A))))
