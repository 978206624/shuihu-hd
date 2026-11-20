from pathlib import Path
import json,collections,hashlib,gzip,html
from PIL import Image,ImageDraw
R=Path('/workspace/shawu/m3-work');rows=[json.loads(x) for x in open(R/'coverage-frames.jsonl')];states={};segments=[]
for r in rows:
 key=(r['scene'],r['geometry'],r['structural'],r['palette'],tuple(r['scroll'] or []),str(r['dialogueRects']),r['classification'])
 if key not in states:states[key]={**{k:r[k] for k in ['scene','geometry','structural','palette','scroll','dialogueRects','classification','pixelHash']},'id':'native_%04d'%len(states),'representativeFrame':r['frame'],'frameRanges':[],'frameCount':0}
 s=states[key];s['frameCount']+=1
 if s['frameRanges'] and s['frameRanges'][-1][1]==r['frame']-1:s['frameRanges'][-1][1]=r['frame']
 else:s['frameRanges'].append([r['frame'],r['frame']])
 if not segments or segments[-1]['scene']!=r['scene']:segments.append({'scene':r['scene'],'first':r['frame'],'last':r['frame']})
 else:segments[-1]['last']=r['frame']
json.dump(list(states.values()),open(R/'catalog/native_states.json','w'),ensure_ascii=False,indent=2);json.dump(segments,open(R/'catalog/segments.json','w'),indent=2)
ui=collections.Counter(tuple((q['x'],q['y'],q['w'],q['h']) for q in r['dialogueRects']) for r in rows);json.dump([{'rects':k,'frames':n} for k,n in ui.items()],open(R/'catalog/window_placements.json','w'),indent=2)
report=json.load(open(R/'coverage-report.json'));doc='''# M3 逐帧覆盖实测\n\n全开场分母 **29160 帧**，从实际标题选择重新开始到首个经移动分支证明的自由移动点；不加载选定存档替代完整重放。\n\n''';doc+=f"- 完整 GPT 背景：**{report['fullyHDBackgroundFrames']} / 29160 = {report['backgroundFramePercent']:.4f}%**。\n- 背景及已检测 UI 联合完整：**{report['fullyHDBackgroundAndUIFrames']} / 29160 = {report['jointFramePercent']:.4f}%**。\n- 像素加权：**{report['coveredPixels']} / {report['eligiblePixels']} = {report['pixelWeightedPercent']:.4f}%**。\n- 有覆盖缺口的帧：**{29160-report['fullyHDBackgroundFrames']}**；逐帧坐标、图块签名、数量见 coverage-frames.jsonl（发行包为 gzip）。\n- 已验证边框的 UI 帧：{report['fullyCoveredDialogueFrames']} / {report['dialogueFrames']}；边框格像素 {report['coveredDialoguePixels']} / {report['dialoguePixels']}。这不是所有转场/加载状态的 UI 完整性保证；未验证的状态保留原图并计入背景缺口。\n\n"
doc+='|分类|总帧|背景全覆盖帧|\n|---|---:|---:|\n';doc+=''.join(f"|{k}|{v['frames']}|{v['fullyHD']}|\n" for k,v in report['classifications'].items())
doc+='''\n## 计数规则\n\n- 每帧实际绘制并记录；不是稀疏截图。分母包括标题退场、空白、淡入淡出、加载与光栅转场，没有静默排除。空白帧也单独列出；少数已识别背景经原生调色板变为纯色，仍记录其素材路径覆盖，其余原像素回退不计 HD。\n- 背景候选像素为全部 160×144 像素减去已验证可见 OAM 非透明像素及已验证对话框/硬件窗口。文字、肖像和原作精灵不属于重画目标。\n- UI 边框候选是完整矩形验证后的 border tiles 161/162/163/164 内像素，排除 OAM 非透明像素；框内 bitmap 字与肖像保持原图。不能仅凭 tile 编号把场景物件当 UI。\n- 未识别格、素材范围以外的相机边缘、原生调色板重建与实际 framebuffer 不一致的光栅像素，都逐像素保留原图，并记录缺口。没有任何 Scale2x 或平滑原图回退。\n- 最终观察器有效 29160/29160 帧；第一遍旧校验的 163 个失败帧仍保留在原始审计中，最终修正了 VBK 银行校验。\n\n## 游戏一致性\n\n在完全相同的冷启动和 A 键序列下，Original 与 HD 每 120 帧保存一次模拟状态：243/243 组 SHA256 完全一致；243/243 组原始 framebuffer 哈希一致。原始模拟输入、ROM 与核心均未改动。最终一次 HD 密集重放使用前一遍已通过的 Original 状态基准，基准文件保留供核验；默认测试命令会重新生成 Original 基准。\n\n同页 100 次切换显示模式不改变模拟状态。原作精灵、框内文字/肖像、未知背景的放大像素在代表场景比较均零差异；键盘、触控、电池存档持久化、250 次反复状态与电池导出通过。详见 invariants-report.json。\n\n## 尚未完成到 100% 的部分\n\n本次结果不是 100% 开场覆盖。主要剩余缺口是原生扫描线转场、加载中的混合 tilemap、少量未验证状态及相机 ±4 像素边缘。稳态分类仍有少数格未覆盖；所有缺口都保留原作。不会将这些像素标记为 GPT 画面，也不会把地图缓存中的垃圾区域扩画成假地图。\n'''
(R/'REPORT_zh.md').write_text(doc)
for name in ['coverage-frames.jsonl','frames.jsonl']:
 with open(R/name,'rb') as src,gzip.open(R/(name+'.gz'),'wb') as dst:dst.write(src.read())
# Simple browser catalog with complete machine-readable state links.
labels={'interior':'室内袭击','cliff':'悬崖','palace':'天庭御座','disciples':'天庭弟子','forest':'森林','unsupported':'未验证/转场','title':'标题'}
page='<meta charset="utf-8"><title>M3 开场审计目录</title><style>body{font:16px system-ui;margin:32px;background:#14212b;color:#eee}table{border-collapse:collapse;width:100%}td,th{border:1px solid #678;padding:8px}a{color:#bde}img{max-width:320px;image-rendering:pixelated}</style><h1>M3 开场逐帧目录</h1><p>29160 帧；完整原始记录及哈希保留。人物、文字、肖像不重绘；未知区域最近邻原图。</p><p><a href="../CATALOG_zh.md">中文审计说明</a> · <a href="../REPORT_zh.md">定量报告</a> · <a href="native_states.json">全部独特状态与帧范围</a> · <a href="window_placements.json">所有窗口位置/尺寸</a> · <a href="../coverage-frames.jsonl.gz">逐帧覆盖 gzip</a></p><table><tr><th>场景</th><th>实际原图</th><th>无角色地图参考</th></tr>'
for name in ['interior','cliff','palace','disciples','forest']:
 page+=f'<tr><td>{labels[name]}</td><td><img src="../references/master_{name}_orig.png"></td><td><img src="../references/master_{name}_bg.png"><br>原生 256×256 缓冲，不能将未观察区域视为地图。有效美术界限 [0,0,160,144]。</td></tr>'
page+='</table><h2>所有状态</h2><table><tr><th>ID/场景</th><th>代表帧/范围</th><th>几何 / 调色板 hash</th><th>相机 / 对话框</th></tr>'
for s in states.values():page+=f"<tr><td>{s['id']} {labels.get(s['scene'],s['scene'])}<br>{s['classification']}</td><td>{s['representativeFrame']}<br>{html.escape(str(s['frameRanges']))}</td><td>{s['geometry']} / {s['structural']}<br>{s['palette']}</td><td>{s['scroll']}<br>{html.escape(str(s['dialogueRects']))}</td></tr>"
(R/'catalog/index.html').write_text(page+'</table>');print('states',len(states),'UI placements',len(ui))
