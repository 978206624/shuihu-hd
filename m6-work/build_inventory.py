from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,collections,math,hashlib,datetime,zoneinfo
R=Path('/workspace/shawu');O=R/'m6-work';shots=R/'shots'
def load(n):return json.loads((O/n).read_text())
ms=load('raw_maps.json')['maps'];aa={a['id']:a for a in load('map_asset_analysis.json')};dyn={d['id']:d for d in load('dynamic_maps.json')};ts=load('tileset_catalog.json');wc=load('warp_catalog.json')
cn={'world':'野外','town':'城镇/院落','indoor':'室内','dungeon':'迷宫/塔/牢房','cutscene':'剧情专用景','unknown':'空白/未确认'}
classes={}
def ranges(g,kind,s):
 for part in s.split(','):
  a=part.strip().split('-');lo=int(a[0],16);hi=int(a[-1],16)
  for i in range(lo,hi+1):
   k=f'{g:02x}-{i:02x}';assert k not in classes,k;classes[k]=kind
ranges(0,'world','00,07-0b,24,2a,35');ranges(0,'indoor','01-06,0d-11,13-16,18-1d,29,2b-2c');ranges(0,'town','0c,12,17,1e,2d');ranges(0,'dungeon','1f-23,25-28,2e-30');ranges(0,'cutscene','31-34')
ranges(1,'world','00,03-04,0e-0f,21,48-49,4c-51,6e-70,7d,82-83');ranges(1,'town','08,10-12,20,22,3b-3f,42,5c-5e,60,71');ranges(1,'indoor','09-0d,13-1d,23-28,39-3a,40-41,52-5b,5f,61-6d,87');ranges(1,'dungeon','01-02,06-07,1e-1f,29-38,43-47,4a-4b,72-7c,7e-81,84-86');ranges(1,'cutscene','05')
ranges(2,'town','00,0d-10,4b');ranges(2,'indoor','01-0c,11-1a,23,31-33');ranges(2,'world','1b,24-26,2f-30,34-35,3a-3d,47-4a');ranges(2,'dungeon','1c-22,27-2e,36-39,3e-46,4c')
ranges(3,'town','00-04,0f-10,12-15,20');ranges(3,'indoor','11,17-1f,2c');ranges(3,'world','05,0c-0e,21');ranges(3,'dungeon','06-0b,16,22-28,2d');ranges(3,'cutscene','29-2a');ranges(3,'unknown','2b')
assert len(classes)==313
hdnames={'forest':'开场森林','interior':'开场室内','cliff':'断崖','palace':'天庭宫殿','disciples':'弟子群像背景'}
for m in ms:
 a=aa[m['id']];d=dyn[m['id']];h=a['best_hd_match'];involved=h['top_left_view_ratio']==1.0
 m.update(type=classes[m['id']],classification_basis='visual_manual_approximate',name_zh=hdnames[h['name']] if involved else f'{cn[classes[m["id"]]]} {m["id"]}',tileset_graphics_id=a['gfx_id'],tileset_graphics_attribute_id=a['tileset_geometry_id'],hd=dict(status='opening_viewport_only' if involved else 'not_covered',scene=h['name'] if involved else None,confirmed_area_tiles=h['matched_area_tiles'] if involved else 0,full_map_done=False,matching='exact native cellKeys FNV1a and verified bounds, 20x18 viewport' if involved else 'No full opening viewport match; incidental common tile matches are not counted'),dynamic=dict(verified=d['verified'],method='RAM map reload; not normal story reachability',best=d['best']),entrance_count=len(m['variants']))
unique={}
for m in ms:unique.setdefault(m['visual_sha256'],[]).append(m)
u=[]
for group in unique.values():
 m=group[0];u.append(dict(id=m['id'],aliases=[v['id'] for v in group],name_zh=m['name_zh'],type=m['type'],alias_types=sorted(set(x['type'] for x in group)),width_tiles=m['width_tiles'],height_tiles=m['height_tiles'],area_tiles=m['area_tiles'],data=m['data'],tileset_graphics_id=m['tileset_graphics_id'],tileset_graphics_attribute_id=m['tileset_graphics_attribute_id'],screenshot=m['screenshot'],dynamic_screenshot=(m['dynamic']['best'] or {}).get('screenshot'),dynamic_verified=any(x['dynamic']['verified'] for x in group),hd=m['hd'],has_scripted_layout_changes=any(x['layout_flag'] for x in group),visual_sha256=m['visual_sha256']))
assert len(u)==243
area=sum(x['area_tiles'] for x in u);hdarea=sum(x['hd']['confirmed_area_tiles'] for x in u);hdn=sum(x['hd']['status']!='not_covered' for x in u)
cat=[]
for k in cn:
 rows=[x for x in u if x['type']==k];slots=[x for x in ms if x['type']==k];n=sum(x['hd']['status']!='not_covered' for x in rows)
 cat.append(dict(type=k,label=cn[k],distinct=len(rows),slots=len(slots),hd_involved=n,not_involved=len(rows)-n,full_map_done=0,area_tiles=sum(x['area_tiles'] for x in rows),confirmed_hd_area_tiles=sum(x['hd']['confirmed_area_tiles'] for x in rows)))
mode_names={1:'接水果小游戏',2:'存档/重新开始确认',3:'GAME OVER',4:'罗汉答题小游戏',5:'轮盘赌小游戏',6:'飞行躲石小游戏',7:'木灵喝水小游戏',8:'世界地图总览',9:'六十年后字幕卡',10:'宋宣和二年字幕卡',11:'天庭字幕卡',12:'辰虎字幕卡',13:'此后二年字幕卡',14:'制作名单/结尾',15:'智多星展示卡',16:'严龙展示动画',17:'金色兽展示动画',18:'双兽水波展示',19:'三兽展示动画',20:'标题淡入',21:'标题',22:'VF广誉标志'}
screens=[]
for q in load('mode_survey.json'):
 i=q['mode'];kind='minigame' if i in [1,4,5,6,7] else 'world' if i==8 else 'menu' if i==2 else 'cutscene'
 status='background_covered' if i in [10,11,20,21] else 'not_covered';note='只确认背景/标题层；不代表角色精灵重绘。' if status!='not_covered' else ''
 if i in [9,12,13]:note='与开场字幕底板相似，但对应全文字卡的HD匹配未验证，不计已完成。'
 screens.append(dict(id=f'mode-{i:02d}',name_zh=mode_names[i],type=kind,entry=q['entry'],tileset='mode_specific_resources',width_tiles=20,height_tiles=18,screenshot=q['screenshot'],hd_status=status,note=note,exploration='RAM mode-entry probe',mode_after_sample=q['current_mode']))
menu_names=['菜单初始化/退出（复用）','主菜单脚本入口','神兽队伍列表','神兽操作：状态/队伍','神兽详细状态','技能列表','装备/属性面板','空操作/返回','道具分类','道具列表','道具使用/丢弃选择','神兽选择目标','学习技能提示','替换技能确认','放弃技能确认','放弃学习确认','技能次数/选择','装备选择目标','神录图鉴','寄存神兽/星位列表','寄存/返回过渡','存档询问/资料面板','存档成功','装备完成','此处无法存档']
for q in load('menu_survey.json'):
 screens.append(dict(id=f'menu-{q["id"]:02d}',name_zh=menu_names[q['id']],type='menu',entry=q['entry'],tileset='24/25 shared UI and native font',width_tiles=20,height_tiles=18,screenshot=q['screenshot'],hd_status='not_covered',exploration='RAM menu-script probe; context-dependent content',note='脚本入口不等于独立画面美术；可能叠加在当前地图上。'))
# Normal button-driven main menu image, separate from script probing.
screens.append(dict(id='menu-main',name_zh='主菜单：神兽/道具/神录/存档',type='menu',entry='05:4b64 -> 24:4090',tileset='shared UI',width_tiles=20,height_tiles=18,screenshot=str(O/'screens/menu_probe_00_start.png'),hd_status='not_covered',exploration='normal Start press after enabling menu in sandbox RAM'))
for n,idx in [('遭遇/出场',50),('战斗主界面',53),('战斗道具与队伍',58),('战斗神兽状态',110),('战斗技能',116)]:
 screens.append(dict(id=f'battle-{idx}',name_zh=n,type='battle',entry='05 field submode -> 2b:4419',tileset='fixed battle UI 2b/2c + beast gfx 27/28/29/2a/63',width_tiles=20,height_tiles=18,screenshot=str(O/f'screens/wild_{idx:03d}.png'),hd_status='not_covered',exploration='natural random encounter on 00-08; bot button play'))
impact=O/'screens/impact_late_native.png';Image.open(R/'m5-work/art/impact_late_native.png').resize((160,144),Image.Resampling.NEAREST).save(impact)
screens.append(dict(id='effect-impact',name_zh='开场冲击特效（含后段）',type='cutscene',entry='opening script, renderer impact signatures',tileset='opening effect',width_tiles=20,height_tiles=18,screenshot=str(impact),hd_status='background_covered',exploration='existing m5 native capture downscaled from exact 2x'))
beasts=load('beast_catalog.json');actors=load('actor_catalog.json')
summary=dict(map_slots=len(ms),distinct_base_backgrounds=len(u),distinct_nonblank_backgrounds=242,blank_unconfirmed_map='03-2b',map_slots_by_group=[54,136,77,46],dynamic_verified_slots=sum(d['verified'] for d in dyn.values()),hd_involved_distinct_backgrounds=hdn,hd_uninvolved_distinct_backgrounds=len(u)-hdn,hd_involved_map_slots=sum(m['hd']['status']!='not_covered' for m in ms),full_maps_hd_complete=0,unique_area_tiles=area,slot_area_tiles=sum(m['area_tiles'] for m in ms),confirmed_hd_area_tiles=hdarea,remaining_unique_area_tiles=area-hdarea,hd_map_involvement_pct=hdn/len(u)*100,hd_area_pct=hdarea/area*100,graphics_bundles=len(ts['graphics_bundles']),graphics_attribute_bundles=len(ts['graphics_attribute_bundles']),unique_used_native_bg_8x8_patterns=ts['unique_native_bg_patterns'],layout_change_slots=sum(m['layout_flag']!=0 for m in ms),parsed_entrance_candidates=sum(len(m['variants']) for m in ms),warp_tables=len(wc['warp_tables']),warp_records=sum(len(t['records']) for t in wc['warp_tables'].values()),actor_resource_ids=105,actor_first_frame_unique=99,beast_portrait_slots=131,beast_nonzero_images=130,beast_recognizable_images=129,beast_empty_slots=[0],beast_near_empty_slots=[109],battle_human_portraits=2,top_level_mode_entries=23,menu_script_entries=25,menu_unique_script_pointers=24)
notes=[
'243按原生整图RGB基础状态去重，含03-2b空白占位；不是243个城市或已证实可达地点。',
'312/313是独立RAM跳图显示验证，不是正常剧情通关；实际仅继续了早期地图、菜单和一场野战。',
'77个槽位的layout_flag触发bank1e脚本改变基础布局；所有机关、破坏/血迹/剧情变体尚未穷举。',
'5种HD涉及背景各确认360个8x8 tile：是开场视口面积，不是5张整图画完。完整地图完成数为0。',
'面积按完整矩形地图存储范围计算，包含边界/空白与重复地块；并非全部需要独立绘制的像素或美术工时。',
'139是graphics bundle字节内容去重；144再区分属性表；并不等于139种美术环境主题。',
'833条入口候选按头部边界及FF终止warp表解析；剔除了末表后非入口数据；未声称所有剧情入口均完整解码。',
'每图类型是视觉人工粗分类，真实地名未逐一通过游戏文本核实。地图可含多种场景用途，统计按首个别名分类。',
'105个actor资源混合人类、神兽、物件、效果，不是105个人物；99是首帧去重，不是全部动画帧数。',
'兽大图131槽中0号全空、109号近空，129张可辨识；外部108神兽+23妖兽说法不能直接等同131张可用图。',
'战斗已确认白底界面1套；静态跟踪2b:6767/6869固定模板、2c:4000人物图与00:09da兽图。未定位独立地形背景选择表，Boss/最终战与技能全动画未通关验证，故全游戏battle_backdrop_total=null。',
'非地图屏幕清单覆盖全部顶层模式及主菜单脚本入口，但商店交易、旅店、隐藏剧情/结局分支和所有战斗特效未逐页自然触发；屏幕总数不能视为封顶。',
'开场29160帧约8.1分钟；资料称全流程12小时以上，时间占比约1.1%或更低，仅粗估，不是本次测得通关时长或整体美术完成百分比。']
result=dict(schema_version=1,game='水浒神兽 GBC',created_at=datetime.datetime.now(zoneinfo.ZoneInfo('America/New_York')).isoformat(),rom=dict(path=str(R/'game.gbc'),sha256=hashlib.sha256((R/'game.gbc').read_bytes()).hexdigest()),read_only_runtime=True,scope='all ROM base field-map tables; partial dynamic story and non-map UI audit',summary=summary,category_summary=cat,unique_maps=u,map_slots=ms,screen_types=screens,battle_backdrops=dict(confirmed_count=1,total=None,confirmed=[dict(id='white-battle-field',name_zh='白底战斗底板',screenshot=str(O/'screens/wild_053.png'),hd_covered=False)],evidence=['2b:6767 state dispatcher','2b:6869 fixed UI palette/graphics/map loads','2c:4000 switches 2 human portraits, not terrain backdrops','00:09da switches beast portrait banks, not backgrounds'],note='已确认1套白底；全游戏总数未知，未通关全部Boss与技能效果。'),sprite_assets=dict(actors_catalog=str(O/'actor_catalog.json'),actors_contact_sheet=str(O/'actor_catalog.png'),beasts_catalog=str(O/'beast_catalog.json'),beasts_contact_sheet=str(O/'beast_catalog.png'),battle_human_portraits=[dict(id=i,graphics=f'2c:{a:04x}',screenshot=str(O/f'screens/battle_trainer_{i}.png')) for i,a in enumerate([0x4079,0x42b9])],all_hd_covered=False),playtime_estimate=dict(opening_frames=29160,opening_minutes=29160/59.7275/60,external_total_lower_bound_hours=12,estimated_opening_fraction_pct=29160/59.7275/43200*100,measured_full_playthrough=False),uncertainties=notes,sources=[dict(url='https://vfamewiki.miraheze.org/wiki/Shui_Hu_Shen_Shou',use='108+23资料口径、6章与12小时以上时长；不是本次测得'),dict(url='http://baike.wangchao.net.cn/detail_749424.html',use='旧攻略地点、六塔和5小游戏交叉参照'),dict(path=str(R/'CHARACTER_RESEARCH_zh.md')),dict(path=str(R/'REPORT_zh.txt')),dict(path=str(R/'DEVELOPER_BRIEF.txt')),dict(path=str(R/'web/map-renderer.js')),dict(path=str(R/'web/assets/maps/m3_signatures.json'))])
(O/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
# Large native contact sheet; no generated art.
fontfile='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(fontfile,13);small=ImageFont.truetype(fontfile,11);title=ImageFont.truetype(fontfile,24)
cols=8;cw=180;ch=144;maprows=math.ceil(len(u)/cols);screenrows=math.ceil(len(screens)/cols);W=cols*cw;offset=125+maprows*ch+65;H=offset+screenrows*ch+50
sheet=Image.new('RGB',(W,H),(20,23,29));d=ImageDraw.Draw(sheet)
d.text((16,12),'水浒神兽：全游戏原生背景与屏幕盘点',font=title,fill='white');d.text((16,49),f'313地图槽位 → 243种基础背景；HD涉及5种（绿色），238种尚未涉及；整张地图全HD：0',font=font,fill='white');d.text((16,75),'绿色仅表示开场20×18视口已绘，不是全图完成。橙色：空白未确认。图像为原生完整地图缩略图。',font=font,fill=(190,200,215));d.text((16,99),'编号为 地图组-地图号（十六进制）；类别为视觉粗分类；同图复用别名见JSON/报告。',font=font,fill=(170,180,195))
def thumb(path,x,y,hd=False,unknown=False,label='',sub=''):
 color=(49,191,119) if hd else (222,160,55) if unknown else (64,72,86);d.rounded_rectangle((x+2,y+2,x+cw-3,y+ch-3),5,outline=color,width=3 if hd or unknown else 1)
 img=Image.open(path).convert('RGB');img.thumbnail((168,104),Image.Resampling.NEAREST);sheet.paste(img,(x+(cw-img.width)//2,y+5+(104-img.height)//2));d.text((x+7,y+111),label,font=font,fill=(70,235,145) if hd else 'white');d.text((x+7,y+128),sub,font=small,fill=(185,195,210))
for i,m in enumerate(u):
 thumb(m['screenshot'],i%cols*cw,125+i//cols*ch,m['hd']['status']!='not_covered',m['type']=='unknown',f'{m["id"]} {cn[m["type"]]}'+(' ✓HD局部' if m['hd']['status']!='not_covered' else ''),f'{m["width_tiles"]}×{m["height_tiles"]}格 / 复用{len(m["aliases"])}')
d.text((16,offset-52),'非地图屏幕：顶层模式、菜单脚本、自然遇敌战斗（不是最终封顶数量）',font=title,fill='white');d.text((16,offset-22),'绿色为已重绘背景/标题/卡；其余原生。菜单入口可能复用或仅一条提示。',font=font,fill=(190,200,215))
for i,s in enumerate(screens):thumb(s['screenshot'],i%cols*cw,offset+i//cols*ch,s['hd_status']=='background_covered',False,s['id']+' '+s['name_zh'][:9],s['type']+' / '+('HD背景' if s['hd_status']=='background_covered' else '未重绘'))
sheet.save(shots/'m6_scene_inventory.png')
# Chinese report with complete distinct-map index and local image links.
lines=['# 水浒神兽：全游戏场景与素材盘点','', '> 本次为只读 ROM/模拟器研究，未修改 web/、ROM 或原存档。地图基础表已全量枚举；非地图系统仍有未自然触发页面，不能等同完整通关。','', '## 核心结论','',f'- **313个地图槽位，去重243种基础背景**（242种非空 + 1种空白未确认）。4组分别54、136、77、46项。',f'- **已有HD涉及5/243种背景，约{hdn/len(u)*100:.2f}%**；复用后对应9/313个槽位。其余**238种尚未涉及**。',f'- 这5种都只是开场视口已映射，**完整地图全HD完成数为0/243**。',f'- **按8×8格面积：已确认{hdarea:,} / {area:,}格，约{hdarea/area*100:.2f}%**；剩余{area-hdarea:,}格。以去重完整地图为分母，不按开场镜头停留时间加权。', '- 标题、两张开场文字卡、冲击特效及对话边框另计，不能加进地图张数；角色、战斗、菜单、小游戏及后续内容仍未重绘。', '', '## 按类别：已涉及 vs 剩余','', '| 类别（视觉粗分） | 槽位 | 去重背景 | 已涉及HD | 未涉及 | 完整图已完成 | 面积格 | 已确认HD格 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for c in cat:lines.append(f'| {c["label"]} | {c["slots"]} | {c["distinct"]} | {c["hd_involved"]} | {c["not_involved"]} | 0 | {c["area_tiles"]:,} | {c["confirmed_hd_area_tiles"]:,} |')
lines+=['','同图不同用途只按首个ID计一次；开场室内按“剧情专用景”计，其后室内别名不重复计数。分类不代表经剧情文本核实的地名。','','## 已有HD地图的精确对应','','| 原生ID（含别名） | HD场景 | 全图尺寸（8×8格） | 已确认HD面积 | 局部比例 |','|---|---|---:|---:|---:|']
for m in u:
 if m['hd']['status']!='not_covered':lines.append(f'| {", ".join(m["aliases"])} | {m["hd"]["scene"]} | {m["width_tiles"]}×{m["height_tiles"]} | {m["hd"]["confirmed_area_tiles"]} | {m["hd"]["confirmed_area_tiles"]/m["area_tiles"]*100:.2f}% |')
lines+=['','以 `web/map-renderer.js` 同一FNV1a规则计算原生tile索引+palette属性签名，逐位置对照 `m3_signatures.json` 的 cellKeys/bounds/verifiedYRanges。只把完整20×18开场视口精确命中的图列为“涉及”；别的地图零散共用空白/树木tile不冒充已绘地图。宫殿的纵向环绕边界也按 verifiedYRanges 处理。','','## 图块、角色与战斗素材量','',f'- **139种图形bundle**；连同属性表区分为**144种组合**；全地图实际使用的原始8×8、2bpp图案去重**3,848种**（不合并翻转，不把palette变色计为新图案）。这不是139个环境主题。', '- **105个地图actor动画资源ID，首帧去重99种**：人类、兽形、物件和特效混合，不能解读为105名人物。当前均未HD重绘；完整动画帧数尚未统计。', '- **兽战斗大图131个资源槽（48×48）**：0号全空，109号仅近空占位，130张含非零像素，其中129张可辨识。资料站的“108神兽+23妖兽”是种类口径，不能当作131张可用大图。', '- **另有2张战斗人物背像**（严龙/辰虎，bank2c），不是地形战斗背景。', '- **战斗底板已确认1套：白底**。实际从00-08走动自然遇敌，操作了战斗、道具/队伍/技能子页。静态追踪主要战斗引擎2b:4419/6767/6869、固定UI资源及兽图加载，并未发现地图地形背景选择表。**全游戏独立战斗背景总数仍标未知**：未自然验证全部Boss/最终战与全部技能效果，不能保证“全游戏只有1套”。', '', '资源联络表：[地图actor](actor_catalog.png)、[兽大图](beast_catalog.png)、[菜单脚本](menu_script_contact.png)、[顶层模式](mode_contact.png)、[实际野战过程](wild_contact.png)。','','## 非地图屏幕类型','','顶层分派 `00:0257` 共23项（含field）；已探测其余22项。主菜单 `24:40c3` 有25个脚本入口、24个不同指针；并非25套独立美术。下面每项都有原生截图（RAM入口探测可能受当前剧情上下文影响）：','','| ID | 屏幕/系统 | 类型 | HD状态 | 原生截图 |','|---|---|---|---|---|']
for s in screens:lines.append(f'| {s["id"]} | {s["name_zh"]} | {s["type"]} | {"背景/标题已绘" if s["hd_status"]=="background_covered" else "未重绘/未确认覆盖"} | [图]({Path(s["screenshot"]).relative_to(O)}) |')
lines+=['','商店交易、旅店、隐藏结局分支、所有技能动画/道具效果尚未逐页自然触发；因此不报“全游戏屏幕总数已封顶”。五个小游戏、世界总览、宣传动画、logo、GAME OVER和credits均另列，不能被地图统计掩盖。','','## 方法与可信度','', '- 静态地图索引：`07:4000`、`07:4e60`、`50:4000`、`50:53b5`。原生loader `00:1ba8` 用FF9A/FF9B/FF9C选组、地图、入口/剧情变体。', '- 每张图包含宽高（32×32大格，换算成8×8格）、layout、32→16→8图块组合、attribute、CGB palette、直接graphics或bank3e复制清单。所有313个头部及图形描述符通过校验并渲染。',f'- 修正了末表后数据被误判入口的边界问题；当前解析**{summary["parsed_entrance_candidates"]}条入口候选、{summary["warp_tables"]}张去重warp表、{summary["warp_records"]}条去重表内记录**。6字节warp中有转地图、脚本与条件触发，不能把所有记录都当门。详见 `warp_catalog.json`。', '- 动态：从旧state继续，独立沙盒改RAM加载313目标，312项有目标ID且非空的画面；03-2b未确认。正常按键另打开菜单、野外走动自然遇敌并对战。**跳图验证不证明正常剧情可达，也不代表通关**。', '- 原生完整图不带NPC/人物；动态截图含实际角色/对话。静态图是基础布局；77槽有剧情layout修改，尚未穷举机关状态。', '- 兽大图表 `00:0a22..0b28` 131指针，分布bank27/28/29/2a/63；palette表 `26:4d45`。actor分派 `00:1e68`、bank04/22/14/0c。', '', '### 关键不确定性','']
for n in notes:lines.append('- '+n)
lines+=['','## 按游玩时长的粗估','',f'29160帧 / 59.7275Hz ≈ **{29160/59.7275/60:.1f}分钟**。资料站称主流程**12小时以上**，因此开场大约占时间**1.1%或更低**。这是外部时长推算，本次没有通关实测；也不是美术完成率。重复战斗、探索、同一地图停留时长均会影响结果。', '', '## 243种去重背景完整索引','', '每行的ID及别名均为十六进制“组-地图”；TS为图形bundle内容hash前12位，完整属性/指针/入口/动态状态见JSON。尺寸单位均8×8格。绿色/“局部HD”只表示已匹配开场视口。','','| 主ID / 复用别名 | 类型 | 尺寸 | TS | HD | 完整原生图 |','|---|---|---:|---|---|---|']
for m in u:lines.append(f'| {", ".join(m["aliases"])} | {cn[m["type"]]} | {m["width_tiles"]}×{m["height_tiles"]} | `{m["tileset_graphics_id"]}` | {"局部HD" if m["hd"]["status"]!="not_covered" else "未绘"} | [图]({Path(m["screenshot"]).relative_to(O)}) |')
lines+=['','## 交付文件','', '- 结构化总清单：`/workspace/shawu/m6-work/inventory.json`（243去重图 + 313槽位 + 屏幕类型 + 素材/不确定性）', '- 本报告：`/workspace/shawu/m6-work/inventory_zh.md`', '- 标记版总联络图：`/workspace/shawu/shots/m6_scene_inventory.png`', '- 原生图/动态截图：`/workspace/shawu/m6-work/screens/`', '- 可恢复进度：`/workspace/shawu/m6-work/progress.md`', '- 底层证据：`raw_maps.json`、`dynamic_maps.json`、`map_asset_analysis.json`、`tileset_catalog.json`、`warp_catalog.json`、`actor_catalog.json`、`beast_catalog.json`。', '', '## 参考资料','', '- [VFameWiki Shui Hu Shen Shou](https://vfamewiki.miraheze.org/wiki/Shui_Hu_Shen_Shou)：资料口径、章节/时长。', '- [旧攻略转录](http://baike.wangchao.net.cn/detail_749424.html)：地点、塔与小游戏交叉参照。', '- 本地 `CHARACTER_RESEARCH_zh.md`、`REPORT_zh.txt`、`DEVELOPER_BRIEF.txt`，以及当前HD renderer/signature资源。','',f'ROM SHA256：`{result["rom"]["sha256"]}`（与研究前一致）。']
(O/'inventory_zh.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2));print('contact sheet',W,H,'screens',len(screens));print('category',cat)
