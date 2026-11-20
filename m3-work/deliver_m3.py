from pathlib import Path
import json, hashlib, gzip, shutil, zipfile, collections, html, re
from PIL import Image, ImageDraw, ImageFont
R=Path('/workspace/shawu'); W=R/'web'; M=R/'m3-work'; S=R/'shots'
report=json.loads((M/'coverage-report.json').read_text())
assert report['totalFrames']==report['completedFrames']==29160 and report['pass']
assert report['stateHashComparisons']==report['pixelHashComparisons']==243
frozen=json.loads((M/'final-build-hashes.json').read_text())
for name,sha in frozen.items():
    assert hashlib.sha256((W/name).read_bytes()).hexdigest()==sha, 'Frozen runtime changed: '+name
rows=[json.loads(x) for x in (M/'coverage-frames.jsonl').read_text().splitlines()]
assert len(rows)==29160 and [r['frame'] for r in rows]==list(range(29160))
labels=[('title','标题 / 重新开始'),('title_fade','标题淡出（仍有原图）'),('intertitle','宋宣和二年 / 字体保留'),('dialogue_opening','室内 / 对话展开过渡'),('dialogue_partial','室内 / 部分展开'),('interior_top','室内 / 顶部对话'),('interior_no_ui','室内 / 无对话框'),('attack_transition','室内 / 黑场冲击过渡'),('impact_bg_effect','红色BG冲击效果（保留原图）'),('cliff_top','悬崖 / 孕妇剧情'),('heaven_transition','悬崖至天庭 / 转场'),('palace_bottom','天庭御座 / 底部对话'),('palace_small','天庭御座 / 窄对话框'),('disciples_opening','天庭弟子 / 开框过渡'),('disciples_top','天庭弟子 / 顶部对话'),('disciples_clear','天庭弟子 / 北斗星君、严龙、辰虎'),('disciples_fade','天庭弟子 / 调色板变化'),('forest_clear','森林 / 剧情'),('forest_bottom','森林 / 底部对话'),('forest_free_roam','森林 / 自由移动检查点')]
fontpath='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'; font=ImageFont.truetype(fontpath,19); small=ImageFont.truetype(fontpath,16); big=ImageFont.truetype(fontpath,28)
freeze=(M/'final-build-hashes.json').stat().st_mtime
for stem,_ in labels:
    for v in ['orig','hd']:
        p=S/f'm3_scene_{stem}_{v}.png'; assert p.exists() and p.stat().st_mtime>=freeze, 'Stale screenshot: '+str(p)
cw,ch=664,350; contact=Image.new('RGB',(cw*2,115+ch*((len(labels)+1)//2)), '#121d28'); d=ImageDraw.Draw(contact)
d.text((20,12),'水浒神兽 M3 · 开场剧情实机对比',font=big,fill='#f2daaa')
d.text((20,56),f"每组左原版 | 右高清；全背景帧 {report['backgroundFramePercent']:.2f}%，背景像素 {report['pixelWeightedPercent']:.2f}%",font=font,fill='white')
d.text((20,85),'人物、头像、中文字保留原像素；未覆盖处保留原图，不使用平滑回退。',font=small,fill='#bdc7d2')
for n,(stem,label) in enumerate(labels):
    x=(n%2)*cw+12;y=115+(n//2)*ch
    d.text((x,y),f'{n+1:02d}  {label}',font=font,fill='#f2daaa')
    d.text((x,y+27),'原版',font=small,fill='white');d.text((x+324,y+27),'高清',font=small,fill='white')
    for j,v in enumerate(['orig','hd']):
        im=Image.open(S/f'm3_scene_{stem}_{v}.png').convert('RGB').resize((320,288),Image.Resampling.NEAREST)
        contact.paste(im,(x+j*324,y+51))
contact.save(S/'m3_cutscenes_contact.png',optimize=True)
for stem in ['cliff_top','disciples_clear','forest_free_roam']:
    ims=[Image.open(S/f'm3_scene_{stem}_{v}.png').convert('RGB') for v in ['orig','hd']]
    w,h=ims[0].size; pair=Image.new('RGB',(w*2,h+58),'#14212b');p=ImageDraw.Draw(pair)
    p.text((12,8),dict(labels)[stem]+'  ·  原版',font=big,fill='white');p.text((w+12,8),'高清（人物/文字原像素）',font=big,fill='white')
    pair.paste(ims[0],(0,58));pair.paste(ims[1],(w,58));pair.save(S/f'm3_compare_{stem}.png',optimize=True)
progress=M/'progress.md';progress.write_text(progress.read_text()+f"\n最终29160帧重放完成：全背景 {report['fullyHDBackgroundFrames']}/29160={report['backgroundFramePercent']:.4f}%，像素 {report['pixelWeightedPercent']:.4f}%；243/243状态、243/243原始像素哈希一致。已刷新20组截图及正式联系图，未混入旧截图。\n")
# Final catalogue derived from the final replay, not stale native capture IDs.
states={};segments=[];ui=collections.Counter(); invalid=sum(not r['observerValid'] for r in rows)
for r in rows:
    key=(r['scene'],r['geometry'],r['structural'],r['palette'],tuple(r['scroll'] or []),json.dumps(r['dialogueRects'],sort_keys=True),r['classification'])
    if key not in states:states[key]={k:r[k] for k in ['scene','geometry','structural','palette','scroll','dialogueRects','classification','pixelHash']}|{'id':f'final_{len(states):04d}','representativeFrame':r['frame'],'frameRanges':[],'frameCount':0}
    q=states[key];q['frameCount']+=1
    if q['frameRanges'] and q['frameRanges'][-1][1]==r['frame']-1:q['frameRanges'][-1][1]=r['frame']
    else:q['frameRanges'].append([r['frame'],r['frame']])
    if segments and segments[-1]['scene']==r['scene']:segments[-1]['last']=r['frame']
    else:segments.append({'scene':r['scene'],'first':r['frame'],'last':r['frame']})
    ui[json.dumps(r['dialogueRects'],sort_keys=True)]+=1
(M/'catalog/final_states.json').write_text(json.dumps(list(states.values()),ensure_ascii=False,indent=2))
(M/'catalog/final_segments.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))
(M/'catalog/final_window_placements.json').write_text(json.dumps([{'rects':json.loads(k),'frames':v} for k,v in ui.items()],ensure_ascii=False,indent=2))
gaps=collections.defaultdict(lambda:{'frames':0,'pixels':0,'examples':[]})
for r in rows:
    if r['uncoveredBackgroundPixels']:
        q=gaps[r['scene']];q['frames']+=1;q['pixels']+=r['uncoveredBackgroundPixels']
        if len(q['examples'])<4:q['examples'].append({'frame':r['frame'],'pixels':r['uncoveredBackgroundPixels'],'tiles':r['uncoveredTiles'][:8]})
(M/'remaining-gaps-final.json').write_text(json.dumps(dict(gaps),ensure_ascii=False,indent=2))
head=f"""# 水浒神兽 M3 最终实测

实际从重新开始到首次经移动分支证明的自由移动检查点，完整重放 **29160帧**（自由移动定位精度120帧，不声称精确解锁帧）。

- 全背景完整HD：**{report['fullyHDBackgroundFrames']}/29160 = {report['backgroundFramePercent']:.4f}%**。
- 背景及检测到的边框联合完整：**{report['fullyHDBackgroundAndUIFrames']}/29160 = {report['jointFramePercent']:.4f}%**。
- 背景像素：**{report['coveredPixels']}/{report['eligiblePixels']} = {report['pixelWeightedPercent']:.4f}%**。
- 含缺口：**{29160-report['fullyHDBackgroundFrames']}帧**。观察器无效{invalid}帧，仍在总分母内。
- 检测到的完整对话边框覆盖：{report['fullyCoveredDialogueFrames']}/{report['dialogueFrames']}帧；{report['coveredDialoguePixels']}/{report['dialoguePixels']}个边框像素。
- Original/HD同输入模拟状态SHA256：**243/243一致**；原生framebuffer哈希：**243/243一致**。本次使用已有Original全重放基准，HD每帧实际运行并记录。
- 冻结版10项不变量测试通过：原作人物、文字、头像、未覆盖区域逐像素保留，100次显示切换不影响游戏状态，250次状态/电池导出无OOM，键盘/触控与浏览器电池持久化通过。
- ROM和所有vendored核心SHA256一致；未修改ROM或模拟器核心。Linux Chromium验证不代表已经在真实Windows执行过。

## 剩余原图及原因

并非100%，也不是全游戏重制。标题淡出部分扫描行、纪年切换、对话展开/关闭的少量扫描线混合或VRAM先行改写，以及红色BG冲击特效仍存在原像素。红色冲击已确认属于BG而非人物精灵，作为背景缺口计数。宫殿/悬崖/弟子场景美术界限为160×144，镜头震动露出的未验证边缘也不伪造补画。室内和森林使用已有256×256整图，后续未实测地图不声称覆盖。

所有未验证像素保持原作最近邻显示并记入coverage-frames.jsonl.gz与remaining-gaps-final.json；不含Scale2x/xBRZ/ScaleFX或任何平滑原图回退。人物、精灵、头像、中文字按要求不重画。没有为提高数字而把未知场景像素当人物排除。背景候选按验证后的原生OAM/UI/纪年文字遮罩排除；检测到的边框单独报告。

palette-change仅表示所用原生调色板不同，不代表所有这些帧都在淡入淡出。blank、unsupported与转场始终保留在29160帧分母。

|分类|帧数|背景全覆盖帧|
|---|---:|---:|
"""
head+=''.join(f"|{k}|{v['frames']}|{v['fullyHD']}|\n" for k,v in report['classifications'].items())
head+='\n## 素材及运行\n\n本轮交付未再生成美术。复用的背景与边框全部来自获准GPT网关gpt-image-2；实际quality与来源见assets/maps/provenance_m3.json，未冒称更高质量。\n\nWindows解压后双击start.bat；需要Python3（安装时勾选Add Python to PATH）。Mac/Linux运行bash start.sh。浏览器访问http://127.0.0.1:8765，保持服务窗口开启；不需要npm或外网。\n\n完整游戏内存档/关机/继续流程尚未通关验证，建议导出电池存档备份。开发重放：NODE_PATH=/home/box/opt/test-tools/node_modules PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers node tools/coverage_m3.cjs（开发工具留在工作区，不是发行运行依赖）。\n'
(M/'REPORT_zh.md').write_text(head)
catalog=f"""# M3 开场剧情目录（最终冻结版）

完整输入重放29160帧。最终分类{len(states)}个独特背景/相机/调色板/UI/扫描线状态，见catalog/final_states.json；纯逐字变化可在场景总览合并，但逐帧记录不合并。最终场景标签的连续区间见catalog/final_segments.json。旧审计保留于本地，不把旧native截图ID误配到最终状态。

|实际剧情|约略帧范围|说明|
|---|---|---|
|标题、宋宣和二年|0–205|标题淡出、纪年中文字保留|
|室内袭击|206–5485|夫妻、闯入者、红色BG冲击，顶部对话|
|悬崖|5486–7282|孕妇、石台、云山|
|天庭御座|7283–11464|玉帝、天兵，底部/窄框|
|天庭弟子|11465–18300|北斗星君、严龙、辰虎，顶部/窄框|
|森林剧情至自由移动|约18301–29159|剧情至移动验证检查点|

这些是可见内容的约略边界，加载/黑场时旧tilemap仍留存，不能仅凭哈希定义精确切换。没有编造未观察到的城镇或高俅场景。原生BG缓存256×256不等于完整已观察地图。室内/森林使用有来源的256×256素材；悬崖/御座为带留白的256坐标系素材，有效区160×144；弟子为实际160×144，已分别使用宽高，不再拉伸为正方形。实际相机SCY=0、+4、−4，未验证边缘仍为原图。

对话主要绘入BG tilemap而非硬件window。最终全部位置尺寸和帧数见catalog/final_window_placements.json。顶部/底部160×64、窄88×64及展开中16/24/32/40/48/56高度分别记录。GPT边框替换完整8原生像素边缘，框中文字/肖像不变，原生调色板驱动边框变化。

screenshots中20组原版/HD配对全来自最终冻结版这次重放；m3_cutscenes_contact.png亦由这些配对组成，包含仍有缺口的转场，未混入旧截图作为修复证明。remaining-gaps-final.json列出剩余缺口场景和例子。
"""
(M/'CATALOG_zh.md').write_text(catalog)
# Chinese launcher instructions carry the real final statistics.
readme=f"""# 水浒神兽高清场景版 M3（本地Windows包）

1. 右键压缩包 → 全部解压缩。
2. 如未安装Python3：从https://www.python.org/downloads/安装，勾选Add Python to PATH。
3. 在解压出的shuihu-hd-m3文件夹双击start.bat。别关闭黑色服务窗口。
4. 浏览器打开http://127.0.0.1:8765。如页面打开过早，等几秒刷新。请勿直接双击index.html。

本地离线运行，无需npm或联网。Mac/Linux：bash start.sh，然后打开上述地址。

方向键移动，X=A，Z=B，Enter=START，Shift=SELECT，空格暂停；也有触控按钮。点击开始/继续。高清/原版切换只影响显示。声音需要手动开启。

本版为开场场景重制，非全游戏100%高清。实测29160帧中{report['fullyHDBackgroundFrames']}帧背景全高清（{report['backgroundFramePercent']:.2f}%）；背景像素覆盖{report['pixelWeightedPercent']:.2f}%。标题淡出、部分对话展开/扫描线切换、BG红色冲击和少量震动边缘仍有原版像素，详见reports/REPORT_zh.md。人物、头像、中文字保留原作，没有平滑放大兜底。

存档保存在此浏览器+主机名+端口的localStorage。请在原作游戏内存档，并导出电池存档备份；完整游戏内存档后重开继续未完整通关验证。

screenshots/m3_cutscenes_contact.png为最终实机总览；reports含逐帧统计、缺口和一致性测试。离线包在Linux无外网Chromium验证通过，但不是实际Windows运行测试。ROM和模拟器核心未修改。仅限本地私用。
"""
(W/'README_zh.md').write_text(readme)
# Refresh sanitized metadata only after proving frozen runtime matches test.
provpath=W/'assets/maps/provenance_m3.json';prov=json.loads(provpath.read_text())
prov['coverage']={k:report[k] for k in ['totalFrames','fullyHDBackgroundFrames','backgroundFramePercent','pixelWeightedPercent']}
meta=json.loads((M/'art/intertitle_m3-gap_meta.json').read_text());prov['new_assets']['intertitle']=meta
prov['alignment'].update({'cliff':'256x256 padded coordinate master; verified usable bounds [0,0,160,144]','palace':'256x256 padded coordinate master; verified usable bounds [0,0,160,144]','disciples':'160x144 with independent width/height; shake edges outside verified bounds remain original'})
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2))
# Keep compressed traces; huge raw reference caches stay in the workspace.
for name in ['coverage-frames.jsonl','frames.jsonl']:
    with (M/name).open('rb') as a,gzip.open(M/(name+'.gz'),'wb') as b:shutil.copyfileobj(a,b)
stage=M/'release/shuihu-hd-m3';stage.mkdir(parents=True,exist_ok=True)
for p in W.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(W)
    if 'tools' in rel.parts or any(x.startswith('.') or x=='node_modules' for x in rel.parts):continue
    dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
source=next(iter(Path('/tmp/m2pkg').glob('*/start.bat')),None);assert source
shutil.copyfile(source,stage/'start.bat');assert (stage/'start.bat').read_bytes()==source.read_bytes()
(stage/'使用说明.txt').write_text(readme,encoding='utf-8')
rpt=stage/'reports';rpt.mkdir(exist_ok=True)
for name in ['REPORT_zh.md','CATALOG_zh.md','coverage-report.json','invariants-report.json','integrity-final.json','remaining-gaps-final.json','original-state-hashes.json','original-pixel-hashes.json','coverage-frames.jsonl.gz','frames.jsonl.gz']:
    shutil.copy2(M/name,rpt/name)
(rpt/'catalog').mkdir(exist_ok=True)
for name in ['final_states.json','final_segments.json','final_window_placements.json']:
    shutil.copy2(M/'catalog'/name,rpt/'catalog'/name)
page='<meta charset="utf-8"><title>M3剧情对比</title><style>body{font:18px system-ui;background:#14212b;color:white;margin:24px}img{max-width:48%;height:auto}a{color:#cef}</style><h1>M3开场剧情最终截图</h1><p>左原版，右高清；包括尚有原图缺口的过渡。人物/文字不重画。</p><p><a href="../REPORT_zh.md">实测报告</a> | <a href="final_states.json">完整状态目录</a></p>'
for stem,label in labels:page+=f'<h2>{html.escape(label)}</h2><img src="../../screenshots/m3_scene_{stem}_orig.png"><img src="../../screenshots/m3_scene_{stem}_hd.png">'
(rpt/'catalog/index.html').write_text(page)
sc=stage/'screenshots';sc.mkdir(exist_ok=True)
for stem,_ in labels:
    for v in ['orig','hd']:shutil.copy2(S/f'm3_scene_{stem}_{v}.png',sc)
for name in ['m3_cutscenes_contact.png','m3_compare_cliff_top.png','m3_compare_disciples_clear.png','m3_compare_forest_free_roam.png']:shutil.copy2(S/name,sc)
# Reject private files and accidental embedded credential-like material; never print values.
for p in stage.rglob('*'):
    if not p.is_file():continue
    assert not any(x.startswith('.') or x in ['node_modules','m3-work','.aws','.codex','.agents','.git'] for x in p.relative_to(stage).parts)
    if p.suffix in ['.json','.js','.md','.txt','.html','.css']:
        t=p.read_text(errors='replace')
        assert not re.search(r'\bsk-[A-Za-z0-9_-]{20,}|\bBearer\s+[A-Za-z0-9_.-]{20,}',t), 'Credential-like content in '+str(p.relative_to(stage))
manifest={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*')) if p.is_file()}
(stage/'reports/release-file-hashes.json').write_text(json.dumps(manifest,indent=2))
z=R/'shuihu-hd-m3-windows.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
    for p in sorted(stage.rglob('*')):
        if p.is_file():f.write(p,str(p.relative_to(stage.parent)))
with zipfile.ZipFile(z) as f:assert f.testzip() is None;f.extractall(M/'extracted-final')
progress.write_text(progress.read_text()+'\n正式联系图及3张完整横向对比图已生成；Windows包已用python zipfile打包并通过CRC，start.bat为原411字节GBK文件的逐字节副本。下一步仅验解压包离线加载，不再改游戏运行代码。\n')
print(json.dumps({'zip':str(z),'bytes':z.stat().st_size,'contact':str(S/'m3_cutscenes_contact.png'),'stage':str(stage),'states':len(states),'coverage':report['backgroundFramePercent'],'pixels':report['pixelWeightedPercent']},ensure_ascii=False))
