from pathlib import Path
import json,zipfile,shutil,hashlib,gzip
from PIL import Image,ImageDraw,ImageFont
r=Path('/workspace/shawu');w=r/'web';m=r/'m4-work';s=json.load(open(m/'coverage-report.json'))
assert s['completedFrames']==29160 and s['stateHashComparisons']==243 and s['pixelHashComparisons']==243 and s['pass']
gaps={}
for line in open(m/'coverage-frames.jsonl'):
 a=json.loads(line)
 if a['uncoveredBackgroundPixels']:
  q=gaps.setdefault(a['scene'],{'frames':0,'pixels':0,'examples':[]});q['frames']+=1;q['pixels']+=a['uncoveredBackgroundPixels']
  if len(q['examples'])<4:q['examples'].append({'frame':a['frame'],'pixels':a['uncoveredBackgroundPixels'],'tiles':a['uncoveredTiles'][:4]})
json.dump(gaps,open(m/'remaining-gaps-final.json','w'),ensure_ascii=False,indent=2)
with open(m/'coverage-frames.jsonl','rb') as a,gzip.open(m/'coverage-frames.jsonl.gz','wb') as b:shutil.copyfileobj(a,b)
labels=[('title','标题'),('title_fade','标题淡出'),('intertitle','宋宣和二年'),('dialogue_opening','对话展开'),('dialogue_partial','局部对话框'),('impact_bg_effect','红色背景冲击'),('interior_top','室内对话'),('interior_no_ui','室内背景'),('cliff_top','悬崖'),('heaven_card','天庭字卡'),('shake_plus4','宫殿镜头 +4'),('shake_minus4','宫殿镜头 -4'),('palace_bottom','宫殿对话'),('palace_small','宫殿小框'),('left_top_residue','左上角过渡'),('disciples_top','弟子对话'),('disciples_clear','弟子场景'),('disciples_fade','弟子淡出'),('forest_clear','森林'),('forest_bottom','森林对话'),('forest_free_roam','自由移动检查点')]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18,index=2);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15,index=2)
contact=Image.new('RGB',(1280,64+len(labels)*232),'#101820');d=ImageDraw.Draw(contact);d.text((20,10),f'M4 最终重放｜原版 / 高清｜完整背景 {s["fullyHDBackgroundFrames"]}/29160；不声称无缺口',font=font,fill='white')
for i,(name,label) in enumerate(labels):
 y=64+i*232;d.text((12,y),label,font=font,fill='white')
 for j,mode in enumerate(['orig','hd']):
  p=r/f'shots/m4_scene_{name}_{mode}.png';im=Image.open(p).convert('RGB');im.thumbnail((560,202),Image.Resampling.LANCZOS);contact.paste(im,(100+j*620,y+25));d.text((100+j*620,y),['原版','高清'][j],font=small,fill='#ccddee')
contact.save(r/'shots/m4_cutscenes_contact.png')
percent=s['backgroundFramePercent'];pp=s['pixelWeightedPercent'];gapframes=29160-s['fullyHDBackgroundFrames']
remaining='；'.join(f'{k}: {v["frames"]}帧/{v["pixels"]}像素' for k,v in gaps.items()) or '无'
readme=f'''水浒神兽 M4（仅开场已实测范围）

Windows：安装Python3并勾选Add Python to PATH，解压后双击start.bat，保持窗口开启，浏览器访问http://127.0.0.1:8765。
Mac/Linux：bash start.sh。运行无需npm或外网。

最终实际同输入New Game完整重放29160帧（自由移动检查点定位精度120帧）。
完整HD背景 {s['fullyHDBackgroundFrames']}/29160 = {percent:.4f}%；背景与检测UI联合完整 {s['fullyHDBackgroundAndUIFrames']}/29160。
背景像素 {s['coveredPixels']}/{s['eligiblePixels']} = {pp:.4f}%。仍有缺口{gapframes}帧；没有冒称100%。
剩余：{remaining}。未被原生几何/实际扫描线像素完全验证的部分继续保持逐像素最近邻原版，因此保守计入缺口。黑屏、淡出、转场均保留在分母。

标题保留已验证区域的原生淡出、两张原文高清字卡、8原生像素对话边框、BG红色冲击、实际±4宫殿扩边与逐行混合已补实现并定向验证；仍有未解决相位/扫描线，不能据定向样本冒称全时段100%。原人物/头像/对话文字保留原版；仅宋宣和二年、天庭按用户授权改为高分辨率字体。无原图平滑兜底、无ROM/核心改动。
标题无菜单派生图的网关请求在590秒端到端上限内未返回，标题淡出y54..117继续保持原生像素并计入缺口，未把带菜单图冒称已清除。新美术仅经用户GPT网关gpt-image-2；既有冲击、宫殿扩边已复用，实际quality见assets/maps/provenance_m4.json。森林/城镇/弟子生成背景为同尺寸quality97 WebP，其余来源记录保留；原生像素素材未转码。

243/243模拟状态与243/243原生framebuffer哈希一致；人物/对话文字/原图回退像素、250次状态和电池导出、100次显示切换、键盘/触控/电池持久化测试通过。ROM/vendor字节与M3一致。干净解压离线验证采用Linux headless Chromium，不能代表真实Windows执行。
不是全游戏重制；未实测地图不声称覆盖。建议导出电池存档备份。
截图、联系图和逐帧审计报告单独交付，不包含于本运行ZIP。
'''
(w/'README_zh.md').write_text(readme)
release=m/'release/shuihu-hd-m4';release.mkdir(parents=True,exist_ok=True)
for name in ['index.html','app.js','renderer.js','map-renderer.js','observer.js','style.css','styles.css','start.sh','README_zh.md']:
 if (w/name).exists():shutil.copy2(w/name,release/name)
for name in ['assets','vendor']:
 shutil.copytree(w/name,release/name,dirs_exist_ok=True)
bat=Path('/tmp/m2pkg/shuihu-hd-m2/start.bat');assert len(bat.read_bytes())==411;shutil.copyfile(bat,release/'start.bat');assert (release/'start.bat').read_bytes()==bat.read_bytes()
z=r/'shuihu-hd-m4-windows.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for p in sorted(release.rglob('*')):
  if p.is_file():archive.write(p,p.relative_to(release.parent))
assert z.stat().st_size<25000000,z.stat().st_size
with zipfile.ZipFile(z) as a:
 assert a.testzip() is None
 assert not any(any(k in Path(n).parts for k in ['screenshots','reports','tools','node_modules','.git']) for n in a.namelist())
 extract=m/'extracted-final';shutil.rmtree(extract,ignore_errors=True);a.extractall(extract)
summary=f'''M4最终实测：完整HD背景 {s['fullyHDBackgroundFrames']}/29160 = {percent:.4f}%；背景/UI联合完整 {s['fullyHDBackgroundAndUIFrames']}/29160。
背景像素 {s['coveredPixels']}/{s['eligiblePixels']} = {pp:.4f}%。剩余缺口 {gapframes}帧：{remaining}。
原因：标题清菜单请求590秒超时；后续冲击相位及局部UI/动态扫描线未满足完整原生证据匹配。所有未验证原生扫描线/几何匹配保留原版最近邻，无阈值放宽、无场景猜测、无角色重画、无ROM/核心修改。
同输入完整重放243/243状态及243/243原生像素哈希一致；10项不变量通过，250次状态/电池导出无OOM。
ZIP: {z}，{z.stat().st_size}字节（不含截图/报告），CRC通过；411字节GBK start.bat原样复制。
联系图: {r/'shots/m4_cutscenes_contact.png'}。
最佳原版/HD截图：{r/'shots/m4_scene_palace_bottom_orig.png'} | {r/'shots/m4_scene_palace_bottom_hd.png'}；{r/'shots/m4_scene_heaven_card_orig.png'} | {r/'shots/m4_scene_heaven_card_hd.png'}；{r/'shots/m4_scene_dialogue_partial_orig.png'} | {r/'shots/m4_scene_dialogue_partial_hd.png'}。
离线干净解压加载测试结果单列package-verification.json；Linux测试不代表真实Windows执行。
'''
(m/'finish-result.txt').write_text(summary);(m/'REPORT_zh.md').write_text(readme+'\n剩余原因说明：标题清菜单图请求超时，y54..117保留原版；红色冲击后续相位尚未被复用素材/已验证原生签名完整接入；其它场景的极短局部UI、旧/新扫描线和动态像素未通过完整8像素原生证据匹配，不能确定归属时按背景缺口计入，而不是扩张人物豁免。宫殿实际±4扩边样本通过，但不声称其它未观察地图边界已补齐。逐帧位置与缺口签名见remaining-gaps-final.json及coverage-frames.jsonl.gz。\n')
print(summary)
