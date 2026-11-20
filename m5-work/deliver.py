from pathlib import Path
from collections import defaultdict
import json,zipfile,shutil,hashlib,gzip
from PIL import Image,ImageDraw,ImageFont
r=Path('/workspace/shawu'); w=r/'web'; m=r/'m5-work'; a=m/'browser-audit'
s=json.loads((a/'coverage-report.json').read_text())
assert s['completedFrames']==29160 and s['stateHashComparisons']==243 and s['pixelHashComparisons']==243 and s['pass']
frozen=json.loads((m/'frozen-sha256.json').read_text())
assert all(hashlib.sha256((w/f).read_bytes()).hexdigest()==h for f,h in frozen.items()),'runtime drift'
core=json.loads((r/'m4-work/runtime-core-sha256.json').read_text())
assert all(hashlib.sha256((w/f).read_bytes()).hexdigest()==h for f,h in core.items()),'ROM/core changed'
reasons=json.loads((m/'gap-reasons.json').read_text()) if (m/'gap-reasons.json').exists() else {}
gaps={}; transitions=[]; scroll=defaultdict(set); rows=[]
for line in (a/'coverage-frames.jsonl').open():
 x=json.loads(line);rows.append(x);scroll[x['scene']].add(tuple(x['scroll']))
 if x['uncoveredBackgroundPixels'] or not x['observerValid']:
  q=gaps.setdefault(x['scene'],dict(frames=0,pixels=0,intervals=[],examples=[],reason=reasons.get(x['scene'],'原生瞬态像素尚无严格对应证据；保留原版并诚实计入缺口。')))
  q['frames']+=1;q['pixels']+=x['uncoveredBackgroundPixels']
  if q['intervals'] and q['intervals'][-1][1]==x['frame']-1:q['intervals'][-1][1]=x['frame']
  else:q['intervals'].append([x['frame'],x['frame']])
  if len(q['examples'])<6:q['examples'].append(x)
 if x.get('uiTransition'):
  t=x['uiTransition'];key=(x['scene'],t['kind'],json.dumps(t['rect'],sort_keys=True))
  if transitions and transitions[-1]['key']==key and transitions[-1]['end']==x['frame']-1:transitions[-1]['end']=x['frame']
  else:transitions.append(dict(key=key,start=x['frame'],end=x['frame'],scene=x['scene'],kind=t['kind'],rect=t['rect']))
assert len(rows)==29160 and [x['frame'] for x in rows]==list(range(29160))
(m/'remaining-gaps-final.json').write_text(json.dumps(gaps,ensure_ascii=False,indent=2))
for t in transitions:t.pop('key');t['frames']=t['end']-t['start']+1
(m/'transition-intervals.json').write_text(json.dumps(transitions,ensure_ascii=False,indent=2))
(m/'observed-scroll.json').write_text(json.dumps({k:sorted(v) for k,v in scroll.items()},ensure_ascii=False,indent=2))
with (a/'coverage-frames.jsonl').open('rb') as src,gzip.open(m/'coverage-frames.jsonl.gz','wb') as dst:shutil.copyfileobj(src,dst)
labels=[('title','标题'),('title_fade','标题淡出'),('intertitle','宋宣和二年'),('dialogue_partial','对话展开'),('partial_ui_361','等时高清对话擦除'),('impact_bg_effect','前期冲击'),('late_impact_5411','晚期四团冲击'),('late_impact_5440','冲击调色转场'),('impact_end_5476','冲击结束'),('cliff_top','悬崖'),('heaven_card','天庭字卡'),('shake_plus4','宫殿镜头 +4'),('palace_bottom','宫殿对话'),('disciples_top','弟子对话'),('disciples_clear','弟子场景'),('disciples_fade','弟子淡出'),('forest_ui_open','森林对话收起'),('forest_partial_ui','森林高清擦除'),('forest_clear','森林'),('forest_bottom','森林对话'),('forest_free_roam','自由移动检查点')]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18,index=2); small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15,index=2)
contact=Image.new('RGB',(1280,64+len(labels)*232),'#101820');d=ImageDraw.Draw(contact)
d.text((20,10),f'M5 实测｜原版 / 高清｜完整背景 {s["fullyHDBackgroundFrames"]}/29160 ({s["backgroundFramePercent"]:.4f}%)',font=font,fill='white')
for i,(name,label) in enumerate(labels):
 y=64+i*232;d.text((12,y),label,font=font,fill='white')
 for j,mode in enumerate(['orig','hd']):
  p=r/f'shots/m5_scene_{name}_{mode}.png'; im=Image.open(p).convert('RGB');im.thumbnail((560,202),Image.Resampling.NEAREST);contact.paste(im,(100+j*620,y+25));d.text((100+j*620,y),['原版','高清'][j],font=small,fill='#ccddee')
contact.save(r/'shots/m5_cutscenes_contact.png')
remaining='；'.join(f'{k}: {v["frames"]}帧/{v["pixels"]}像素' for k,v in gaps.items()) or '无'
gapframes=29160-s['fullyHDBackgroundFrames']
readme=f'''水浒神兽 M5（仅开场已实测范围）

Windows：安装Python3并勾选Add Python to PATH，解压后双击start.bat，保持窗口开启，浏览器访问http://127.0.0.1:8765。
Mac/Linux：bash start.sh。运行无需npm或外网。Windows批处理保持M4原版411字节GBK编码。

真实Chromium、同输入New Game逐帧完整重放29160帧；黑屏、淡出、转场保留在分母。
完整HD背景 {s['fullyHDBackgroundFrames']}/29160 = {s['backgroundFramePercent']:.4f}%；背景与检测UI联合完整 {s['fullyHDBackgroundAndUIFrames']}/29160。
背景像素 {s['coveredPixels']}/{s['eligiblePixels']} = {s['pixelWeightedPercent']:.4f}%。仍有缺口{gapframes}帧；没有冒称100%。
剩余：{remaining}。未有严格对应证据的瞬态像素保留原版最近邻，不作平滑放大。

M5已接入成功生成的无菜单标题背景、GPT晚期四团冲击；标题淡出、冲击动态调色和真实局部UI收起改用渲染层高清转场。原始触发、模拟时间、输入和状态不变，不跳帧、不延长事件。局部UI擦除仅在原生证据识别的区间启用，当前原生角色保留，不缓存旧角色。新美术只使用用户授权GPT网关gpt-image-2及既有GPT作品，未用其它生图接口。
人物、头像、常规对话文字保留原版；仅既有授权字卡采用高清字体。无ROM/核心修改；未实测地图不声称覆盖。

243/243模拟状态与243/243原生framebuffer哈希一致；{s.get('actorPreservationComparisons',0)}次角色/非转场文字抽查无变化。10项显示、角色、文字、存档、键盘/触控不变量通过，250次状态/电池导出无OOM。
干净解压离线加载验证采用Linux headless Chromium，不能代表真实Windows执行；验证详情单列交付。建议导出电池存档备份。
截图、联系图、逐帧审计报告不包含于运行ZIP。不是全游戏重制。
'''
(w/'README_zh.md').write_text(readme)
provenance={'title_clear_hd.png':{'source':'m4-work/art/title_clear_compact_hd.png','model':'gpt-image-2','gateway':'owner-authorized','status':'successful existing generation reused'},'maps/impact_late_hd.png':{'source':'m5-work/art/impact_late_hd.png','model':'gpt-image-2','gateway':'owner-authorized','quality':'low','attempts':1,'elapsed_seconds':62.8},'constraints':{'native_sprites_redrawn':False,'native_smoothing':False,'ROM_core_changed':False},'transitions':'render-layer only; actual native event evidence and time unchanged'}
(w/'assets/maps/provenance_m5.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
frozen['README_zh.md']=hashlib.sha256((w/'README_zh.md').read_bytes()).hexdigest();frozen['assets/maps/provenance_m5.json']=hashlib.sha256((w/'assets/maps/provenance_m5.json').read_bytes()).hexdigest();(m/'frozen-sha256.json').write_text(json.dumps(frozen,indent=2)+'\n')
release=m/'release/shuihu-hd-m5';release.mkdir(parents=True,exist_ok=True)
for f in frozen:
 dst=release/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(w/f,dst)
with zipfile.ZipFile(r/'shuihu-hd-m4-windows.zip') as old:
 bat=old.read('shuihu-hd-m4/start.bat');sh=old.read('shuihu-hd-m4/start.sh')
assert len(bat)==411;bat.decode('gbk');(release/'start.bat').write_bytes(bat);(release/'start.sh').write_bytes(sh)
assert hashlib.sha256(sh).hexdigest()==frozen['start.sh']
z=r/'shuihu-hd-m5-windows.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as arc:
 for p in sorted(release.rglob('*')):
  if p.is_file():arc.write(p,p.relative_to(release.parent))
assert z.stat().st_size<25000000
with zipfile.ZipFile(z) as arc:
 assert arc.testzip() is None
 assert not any(set(Path(n).parts)&{'screenshots','reports','tools','node_modules','.git','.codex','.aws','.agents'} for n in arc.namelist())
 extract=m/'extracted-final';extract.mkdir(exist_ok=True);arc.extractall(extract)
 assert all(hashlib.sha256(arc.read('shuihu-hd-m5/'+f)).hexdigest()==h for f,h in frozen.items())
summary=f'''M5最终实测：完整HD背景 {s['fullyHDBackgroundFrames']}/29160 = {s['backgroundFramePercent']:.4f}%；背景/UI联合完整 {s['fullyHDBackgroundAndUIFrames']}/29160。
背景像素 {s['coveredPixels']}/{s['eligiblePixels']} = {s['pixelWeightedPercent']:.4f}%。剩余缺口 {gapframes}帧：{remaining}。
同输入完整重放243/243状态及243/243原生像素哈希一致；{s.get('actorPreservationComparisons',0)}次角色/非转场文字抽查，10项不变量通过，250次状态/电池导出无OOM。ROM/core与M4字节一致。
ZIP: {z}，{z.stat().st_size}字节（不含截图/报告/工具），CRC与{len(frozen)}项冻结SHA256通过；411字节GBK start.bat、start.sh原样复制。
联系图: {r/'shots/m5_cutscenes_contact.png'}。
剩余原因详见remaining-gaps-final.json。高清转场识别区间见transition-intervals.json；观测卷屏见observed-scroll.json。
离线干净解压加载结果单列package-verification.json；Linux测试不代表真实Windows执行。
'''
(m/'finish-result.txt').write_text(summary)
(m/'REPORT_zh.md').write_text(readme+'\n## 剩余缺口原因\n'+('\n'.join(f'- {k}：{v["reason"]}' for k,v in gaps.items()) or '无')+'\n\n局部UI转场共'+str(len(transitions))+'段，区间由逐帧原生证据确定，不使用固定故事计数器。背景像素分母排除原生角色/文字及已验证原生UI内容；UI边框单列。M5的精确原生UI识别改进使分母与M4略有不同，不能将两版本像素分母直接混用。\n森林实测SCX/SCY：'+str(sorted(scroll.get('forest',set())))+'；只声称此次开场重放观测到的几何范围，不假称已覆盖全游戏森林卷屏。\n')
(m/'delivery-final.json').write_text(json.dumps({'zip':str(z),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'frozen_files':len(frozen),'CRC':True,'contact':str(r/'shots/m5_cutscenes_contact.png')},ensure_ascii=False,indent=2))
print(summary)
