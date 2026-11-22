# M8 第三片区域进度

## Supervisor preparation — 2026-11-10 22:43:37 EST
- 用户要求先修M7首次切图卡顿，再自然推进介绍信/醉仙楼/东溪村；所有开发由Codex执行，监督只监工与验收。
- Codex CLI存在，但127.0.0.1:38811无监听（复查一致）；按交接停止开发，待恢复Cockpit账户/代理。
- 任务书：../m7-work/CODEX_M7_FIX_M8_BRIEF.md。
- 尚未创建runtime副本、推进剧情或请求GPT新图；地图数量/新覆盖率/性能尚无新增结果，不冒充完成。

## Stage B authorized / Codex launch — 2026-11-11 04:24:17 EST
- StageA监督最终采用v3冻结runtime，带切图残差继续；STAGE_A_FINAL_DECISION_zh.md有全部数字/噪声/选择理由。
- 从m7-work/stage-a/v3/runtime隔离复制为m8-work/runtime，沿region2-story9-end.bin自然推进介绍信→醉仙楼→东溪村至下一剧情关口；本轮全部编码Codex，监督运行GPT/QA。
- 任务书CODEX_M8_REGION3_PROMPT.txt；nohup日志codex-m8-region3.log，末条codex-m8-region3-last.txt。此时未产生新地图/美术/预览，不声称已完成。

- 2026-11-11 04:24:32 EST：nohup已成功启动并完成一次启动检查，CLI PID869057（vendor子PID见pgrep）；session01a1c9ec-3f2e-78f3-aa1a-62349c57cf11，provider codex_local_access，workspace-write/high。没有启动重复M8任务；下次先读progress/log并检查现有进程，再运行Codex准备的外层命令。

## Supervisor continues M8 — 2026-11-11 04:25:06 EST
- 原Codex PID869057/869077正常，session01a1c9ec-3f2e-78f3-aa1a-62349c57cf11，不重复启动。38811/8765正常。
- 新验收要求：所有正确性必过，性能不得差于采用的区域2 v3；无平滑放大fallback，缺口逐项列出。终点为对照图与小于25MB实时预览完成，不能只因启动就报告完成。

## Stage B isolated base — 2026-11-11T09:26:34.496326+00:00
- 读取最终授权采纳v3（不是历史拒绝结论），546项冻结SHA全通过；runtime独立逐文件复制，ROM/core/所有代码逐字节相同。
- 原M5/M6/M7/StageA及web保护清单 21155项：integrity/pre-stage-b-protected-sha256.json；不修改历史证据。
- 起点frozen-starts/region2-story9-end.bin与原文件完全相同，SHA见manifest.json。尚未验证新地图/故事关口。
- 已知Node socket sandbox EPERM，不重试网络/浏览器；准备原版WASM离线自然按键探路和监督外层脚本。当前Codex PID 2；日志codex-m8-region3.log。

### Natural return route checkpoint — 2026-11-11T09:35:36.051856+00:00
- 原版WASM可读取原199608字节存档；已自然出大名府00-1e→内城00-17→外城00-12→野道00-08。story仍9，没有写RAM/PC。
- 每步按键/原生帧日志play/*/frames.jsonl.gz；各动作末state/native framebuffer SHA与原生PNG齐存。
- 探路search/inner-exit-search、inner-exit-search-02、inner-south-search均未找到目标，原尝试/输入/分支/队列保留，不冒充连续游戏；成功手动绕树/行人路线亦原样保留。
- 当前任务：离线只读坐标启发式自然按键返史家庄，PID见logs/field-town-hinted-search.log及search/field-town-hinted-search/provenance.json。脚本v1原件已另存；新hint/positional key沿用M7门路搜索逻辑，不影响runtime。
- 尚无新地图名/数量、美术、浏览器正式QA/性能或录像结论。下一步重放成功输入→核对原对白→冻结外层浏览器复核命令。

- 2026-11-11 04:48:27 EST：同一Codex仍在自然按键推进；日志已记录取得介绍信后story10并返回大名城（未作正式浏览器验收，不提前认定剧情通关）。原始尝试/成功链保留在play/search，尚未有新GPT图或预览。

### Letter obtained and delivered (native) — 2026-11-11T09:53:54.732103+00:00
- 史家庄史进原生对白后story9→10，得到介绍信；醉仙楼00-1b鲁智深对话后story10→11。证据story/introduction-letter-contact.png、story/lu-letter-contact.png及play/逐页原PNG。
- 29段自然输入边界逐字节核对通过，catalog checkpoints/letter-natural-chain-segmented.json；合并输入letter-natural-actions.json，搜索失败不纳入。普通酒客误寻亦保留，不当作交信。
- 下步对原始冻结起点做不载档的连续原生复走，及后续门路；浏览器正确性/覆盖/性能尚未测。

- 2026-11-11 05:11:42 EST：同一Codex仍正常推进，无重启/重复；原生剧情已交信story11，现探查南口自然到达00-00及相连房门，地图正式名称/区域范围尚待原对白确认。所有尝试/按键/存档保留；未进行新生图、正式浏览器QA或性能验收。

### Native continuous story / new doorway — 2026-11-11T10:11:45.940462+00:00
- continuous-letter-chain-v1从最初原始字节存档连续19596原生帧/185动作，无中途载档，story9→10→11，最后stateSHA/native framebuffer与29段链完全一致。
- 交信后自然出城、原菜单逃跑、经野道河桥南行，实际进入00-00。当前仅称南侧村庄00-00，村名待原对白；ROM表不能单独证明东溪村命名/新增数量。
- 大名府交信后探索为隔离支线，未触发新故事，不纳入主链。story11村口小孩神兽决斗菜单明确选“否”并退出；按B的无效菜单尝试全保留。
- 现离线门路搜索logs/south-village-doors.log，队列/动作/原生帧与自然成功回放分开。新图/GPT/浏览器QA/覆盖/性能/录像均未开始。

- 2026-11-11T10:13:22.459972+00:00 原生门路独立回放 00-04 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-04.log；下一项自动续跑，已有成功不重复。

- 2026-11-11T10:13:22.825624+00:00 原生门路独立回放 00-02 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-02.log；下一项自动续跑，已有成功不重复。

- 2026-11-11T10:13:23.291573+00:00 原生门路独立回放 00-01 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-01.log；下一项自动续跑，已有成功不重复。

- 2026-11-11T10:13:23.756989+00:00 原生门路独立回放 00-03 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-03.log；下一项自动续跑，已有成功不重复。

- 2026-11-11T10:13:24.322894+00:00 原生门路独立回放 00-06 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-06.log；下一项自动续跑，已有成功不重复。

- 2026-11-11T10:13:24.939586+00:00 原生门路独立回放 00-05 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-05.log；下一项自动续跑，已有成功不重复。

- 2026-11-11T10:13:25.556518+00:00 原生门路独立回放 00-09 完成；非连续主线，PID 3，日志 m8-work/logs/survey-00-09.log；下一项自动续跑，已有成功不重复。

## BLOCKER / supervisor return — 2026-11-11 05:26:32 EST
- 短周期复查发现原Codex PID869057/869077均消失，pgrep无Codex/Cockpit；38811与8765两次检查均无监听。日志停在原生NPC对话搜索，没有正常末条结果。停止开发，不绕代理、不自行改代码、不重复起任务；需先恢复Cockpit原账户/38811，再从此断点续跑。
- 已完成原生证据：最初冻结存档连续19596帧/185动作自然取得介绍信story9→10、醉仙楼交鲁智深story10→11；末state/native framebuffer与29段成功链完全一致。此为自然路线证据，不冒充正式M8浏览器不变量验收。
- 已自然到南侧村庄00-00，并完成00-01/02/03/04/05/06/09共7个相连地图的独立门路回放（合计8个已探索地图；不自动等于8张最终新增高清图）。村名是否东溪村、后续剧情关口尚未核实；story仍11。
- 新GPT图0张；M8覆盖率/正式state/native/actor-text QA/性能均尚未测。shots/m8_region3_contact.png与m8-work/region3_preview.webm不存在；没有可交付的新片区预览。没有使用平滑放大fallback。
- 关键恢复文件：checkpoints/letter-natural-actions.json、letter-natural-chain-segmented.json、survey-00-*-actions.json；play/continuous-letter-chain-v1、play/accepted-10-lu-letter-delivered、play/survey-00-*、search/talk-search-00-*；所有原生PNG/输入/帧记录保留。
- 原Codex session01a1c9ec-3f2e-78f3-aa1a-62349c57cf11，日志codex-m8-region3.log；代理恢复后先检查无已有任务，再用同一session resume，要求读本progress、继续原NPC/村名/关口核实，准备GPT与外层QA命令，不重复已成功原生链。现不启动resume。StageA最终v3带残差采用不变。

## Reboot recovery / resume — 2026-11-11 05:30:01 EST
- 上级确认箱重启；Cockpit已重装并切回原账户，监督复查38811/8765均监听、无Codex既有任务。/tmp清空；持续脚本/存档/QA证据保留。
- 使用原session01a1c9ec-3f2e-78f3-aa1a-62349c57cf11 resume；日志codex-m8-region3-resume1.log，末条codex-m8-region3-resume1-last.txt，任务书CODEX_M8_REBOOT_RESUME_PROMPT.txt。从story11和村庄NPC调查断点继续，不重做成功链。

- 2026-11-11 05:30:10 EST：resume启动检查成功，CLI PID13542；同一session/provider codex_local_access，未新建/重复任务。

## Codex reboot continuation — 2026-11-11T10:31:41.844956+00:00
- 监督确认38811/8765已恢复，不检查凭据、不改服务；runtime89项与采用v3完全相同，freeze SHA仍49d58407…。/tmp已清空，本轮不依赖临时目录。
- 重启前talk-search-00-04/05/06其实均完成，已找到原生对话路径（provenance COMPLETE）；直接从持久goal-actions续接，不重复搜索或19596帧已验链。
- 下一步自然重放这三段独立房门NPC对白，确认地图名称与故事gate；logs/room-dialogue-survey.log。

- 2026-11-11 05:45:08 EST：恢复后同一Codex继续NPC调查；已提出8张美术候选（00-00村庄、00-01..06室内、00-09林道），尚未请求GPT。新主线/村名/剧情gate以原对白继续核对；正式QA、覆盖率、性能未测。不将候选数量当成完成数量。

### Story12 natural gate / scope preparation — 2026-11-11T10:51:02.618510+00:00
- 吴用原生会合story11→12；下一任务黄泥岗客栈乔装掌柜/小二设伏，未进入/完成黄泥岗。00-00东溪村由M6“至东溪村会合”原对白 + 此次自然门路 + 00-05吴用会合交叉确认，不虚称现场地图标题。
- 24段281动作26711原生帧从冻结story11不载档复走，确到story12。与分段链state SHA存在差异，未伪称相同；各检查点实际比对与末态逐字节差异见checkpoints/story11-to12-continuous-proof.json（不是浏览器正式验收）。原19596帧185动作已验链未重跑。
- 冻结新原生终点frozen-starts/story12-meeting-end.bin；范围region3-scope.json：00-00、00-01..06、00-09共8图候选，不是全部连通世界；未进入00-0b/35/黄泥岗。不混淆独立门路调查与主线。
- 8张ROM直接解码无人物整图、精确4倍最近邻INPUT参考及V4提示词已备art/；没有生成/集成新HD图，runtime仍与v3的89文件一致。下一步outer GPT任务，逐图人工审查后才冻结候选QA/perf。

- 2026-11-11 06:04:49 EST：同一Codex仍在整理外层GPT关口；story12新段26711帧/281动作已自然达到下一任务（黄泥岗客栈设伏，尚未进入）。与分段链281处原生画面/ticks/地图/剧情一致，但末state有3字节序列化差异，明确保留；正式QA仍需同字节起点基线比较。8图输入已备，尚无生成，38811正常。

- 2026-11-11 06:11:44 EST：监督读取art-preflight汇总：129项美术输入冻结，89运行文件与v3零差异，21155受保护项changed=0/missing=3168。缺失分组为m6-work/venv（3164项）及4个__pycache__，属于重启清理的环境/字节码；ROM/core/运行/历史美术未在missing组中。缺失原表保留，不能伪称21155全部通过，不为此绕网或读凭据。尚无新图。

## Outer GPT CLI generation starts — 2026-11-11 06:20:50 EST
- 上级明确要求由监督运行gpt_image.py edit，8图各自nohup并行，medium/gpt-image-2，使用已备原生布局+V4风格双参考和prompt，输出*_gpt.png；已有成功输出跳过。GPT_IMAGE_ENV仅由程序读取指定.image_api.env，不打印。
- 每图最多3次、620秒每次、2100秒外层硬截止；记录独立log/meta/PID与输入SHA。此批次不使用尚未交付的art/generate.py，后续Codex按CLI meta接入溯源。
- 监督实查Codex PID13542仍活着（与交接“无Codex”不同），不启动重复resume；其禁网准备工作与图片API等待无性能验收并行。生成/目检后等该进程结束再resume集成/QA。
- 本批路径：m8-work/art/cli-generation/20261111T112050Z。

- 2026-11-11 06:23:28 EST：00-01已首试生成；监督逐张目检原生与GPT：两床、两柜、五瓮、四屏、桌椅/三盆栽、门口大致对齐，无人物/文字；美术可进入集成预览复核，不把目检当几何像素证明。尺寸由原始PNG另核，不做原图平滑补洞。其它7任务继续。

- 2026-11-11 06:26:41 EST：8图nohup批次已有00-01/03/04/06四图成功，另四图仍在同一CLI有界重试（408/504/断连记log），不重复启动。逐张与原生参考目检：00-03双段狭屋/隔墙门、床/炉/柜/瓮/屏/柜台布局相符；00-04三客房+横廊+下柜台厅、6床及门路保留；00-06祭坛香炉/6装饰牌/红毯/边柜/瓮瓶与门路保留，未造人物/神像/可读文字。均暂准集成复核，严格遮罩/原生文字保护仍待QA；实出PNG尺寸可能高于请求（00-01为1374x1145，纵横比同原图），只记录请求medium，不宣称服务器回显quality。Codex13542仍活且日志显示Reconnecting1/5；38811/8765均监听，未起重复resume。

- 2026-11-11 06:29:26 EST：00-00与00-09第二试成功，累计6/8；逐图原生对照目检已完成：村庄7屋/单河桥/双井/3告示牌/门路主布局保留；林道分岔/中央岩石/左上1木告示牌保留（牌顶绘成盖檐，非新增房屋）。细植被/材质有绘画变化，不虚称碰撞像素级证明；正式QA仍待。00-02/05同批原任务重试中。

- 2026-11-11 06:32:15 EST：GPT 8/8全部成功，00-02/05第二试完成；进程已结束，无生成任务重开。全部8图与各自原生参考逐张目检，00-02单床/隔墙/屏瓮门路与00-05双床/上下厅/8屏/桌椅门路基本吻合，均无人物/可读文字。详细人工观察art/SUPERVISOR_VISUAL_REVIEW.md，原始输出/CLI meta及output-sha256/output-dimensions均保留。此为美术关口，不虚称已集成或验收；正式覆盖/不变量/性能/视频仍待Codex。Codex旧resume仍只有Reconnecting1/5，38811健康，先判断是否真正挂起后再同session恢复，绝不并行复制。

- 2026-11-11 06:33:01 EST：旧resume1在最后外层dry-run后连续约20分钟无正常回答，记录两次Reconnecting（1/5、2/5，单轮约10分钟），38811/8765仍健康。8张GPT已完成；为避免旧上下文继续等已过时的美术关口，判定客户端请求挂起并仅对本session的CLI/子进程作TERM，从持久checkpoint同session恢复一次，携带新艺术溯源/集成任务书；不碰Cockpit/代理/账户/路由，原log原样保留。

- 2026-11-11 06:33:08 EST：旧Codex三个进程已退出，38811/8765健康；同session nohup resume2集成/QA准备启动，CLI PID75349，日志codex-m8-region3-resume2.log，任务书CODEX_M8_ART_INTEGRATION_PROMPT.txt，末条codex-m8-region3-resume2-last.txt。GPT8/8成功输出不重跑；浏览器/性能必须由监督外层执行时独占。

- 2026-11-11 06:40:12 EST：resume2启动检查成功，PID75349/vendor75370，同session。至今约7分钟仅请求首部、暂无工具输出或REQUEST_READY；代理两端口仍健康，未重复启动任何生图或Codex；准备完整性/QA/perf/视频仍需Codex交付。新8图及meta冻结16项SHA复核全通过。

## BLOCKED: Codex stream stalled after completed art — 2026-11-11 06:46:00 EST
- GPT阶段已完成：8/8 map PNG + 原始CLI meta；13次请求（3图首试、5图第二试），全部medium请求，同一授权网关。逐图原生参考对照目检完成，art/SUPERVISOR_VISUAL_REVIEW.md；输入/输出SHA、实际尺寸均在art/cli-generation/20261111T112050Z。监督未写开发代码、未平滑原图、未生成替代/占位交付物。
- Codex旧resume1约20分钟仅两次Reconnecting；安全结束旧CLI后，按用户要求同session nohup resume2（75349/75370）携完整集成任务书，又在首个约10分钟请求后Reconnecting1/5，12分钟仍无首个工具动作/正常回答。旧/新log原样保留，没有集成结果或REQUEST_READY。
- 38811/8765一直监听；这不是已证实的端口宕机，也不能仅凭重连推断账户/模型根因。对本session挂起CLI作TERM，停止重复请求，不改认证/代理/路由或换coding provider。下次先验证同session无旧进程及代理实际可用，再用CODEX_M8_ART_INTEGRATION_PROMPT.txt resume（无需任何生图重跑）。
- 新正式QA/覆盖率/性能尚未测；不能声称正确性/不差于region2 v3已通过。shots/m8_region3_contact.png与m8-work/region3_preview.webm尚不存在。下游集成、严格原生覆盖/人物文字hash、regions1-2回归、独占冷切图perf、实时视频仍缺。原生剧情到吴用会合story12，黄泥岗未进入；后段连续/分段save的3字节差异仍保留披露。
- 有界排障研究已查已有记忆、公开网页及X：未找到适用于此Codex/Cockpit挂起的已验证公共方法。近似案例是Cursor CLI的SSH插件同步故障，明确Codex在该例正常，不适用本故障；未擅改git/network。参考：https://forum.cursor.com/t/grok-bot-computer-cursor-cli-agent-p-stuck-on-connection-lost-reconnecting-since-oct-19-codex-works-from-same-machine/175385 ；X检索未得同故障可靠修复。根因待Cockpit上游核实。

- 2026-11-11 06:46:08 EST：退出复查：本session Codex/GPT进程均无残留，38811/8765仍正常监听；最终两项交付物仍不存在。断点m8-work/SUPERVISOR_STATUS.md与本progress已保存，等待恢复可正常回答的Codex上游后继续；8张成功图不得重跑。

## Fresh Codex authorized — 2026-11-11 06:47:27 EST
- 用户实测fresh exec约10秒正常；明确禁止再resume旧01a1c9ec。监督确认无既有任务、38811/8765健康，以fresh exec/high/workspace-write/never/skip-git-repo-check nohup启动PID97135，log codex-m8-fresh1.log，last codex-m8-fresh1-last.txt，任务书CODEX_M8_FRESH_INTEGRATION_PROMPT.txt（继承完整集成任务，末尾明确覆盖旧same-session指令）。
- 上一上游不可用的推断未获证实；大旧session是用户新假设。新运行只从文件取上下文，不加载旧会话，不重跑8图。若约10分钟无log新活动，杀本fresh并仅再起一次更窄子任务。

- 2026-11-11 06:47:48 EST：fresh1在约10秒内已产生正常exec工具输出（session01a1ca6f-3387-7563-9e40-f738e86f9f31），印证fresh请求可用；旧session挂起而不是监听端口故障。PID97135/vendor97156正常，继续本fresh集成，不再resume旧session。

- 2026-11-11 06:52:34 EST：fresh1正常集成完成：8张原始PNG逐字节复制入runtime；注册地图21→29，既有ROM/core/JS/CSS改动0，仅追加地图清单+新资产（Codex integration/provenance.json）。接下来Codex准备旧442项回归与新区域冻结同起点QA/覆盖/独占perf/录像命令。尚未提前标记正式验收通过；本fresh保持活跃，未触发10分钟空闲重启。

- 2026-11-11 20:02:49 CST 用户要求暂停：GPT 8/8已完成，集成未完成；Codex 已停止。恢复时从 CODEX_M8_ART_INTEGRATION_PROMPT.txt 开新会话。

## Fresh Codex integration resume — 2026-11-18 01:15:13 EST
- 用户要求继续，并再次确认只监工。GPT 8/8 与先前 fresh1 的逐字节集成/脚本/freeze 均保留，不重跑生图。
- 因旧会话会挂起，本轮开全新 exec（不 resume 01a1c9ec / 01a1ca6f）。任务书 CODEX_M8_INTEGRATE_FRESH2_PROMPT.txt（完整集成要求 + 当前文件状态）。日志 codex-m8-integrate.log，末条 codex-m8-integrate-last.txt。
- 已知断点：offline-check --freeze 已通过（freezeSHA256 26fce049…，324 项；保护项 changed=0，missing=3168 为 m6-work/venv 与 __pycache__，已披露），但 REQUEST_READY 未写出；正式浏览器 QA/覆盖/性能/对照图/预览仍未测。
- 38811/8765 当前监听；8765 根目录仍是 /workspace/shawu。若约 10 分钟日志无新活动，将结束本 fresh 并只再开一次更窄子任务。

## Fresh file-only verification — 2026-11-18

- `offline-check.py --verify-only` verified the existing 324-file freeze `26fce049289b63c6b84d4aceed852865ccc4d91378a75e90764a56150f65c3eb`. Eight source/runtime PNG pairs matched, registry 21→29; only the registry differs among the 89 original runtime files. Protected history changed 0; 3,168 known environment/bytecode paths are absent. Original freeze copied to `offline/freeze-sha256-20261111.json` before any harness repairs.
- All 33 QA route starts, 12 performance route starts, and eight preview sources are present in the freeze. QA plan totals 1,096 actions and 84,135 frames, including 442 actions and 31,396 frames for regions 1/2. Planned counts are not results.
- Static review found concrete outer harness defects: performance passed `null` idle keys to the runtime and inserted an extra frame for zero waits; QA captured CSS-sized screenshots rejected by the 640×576 contact builder; the report promised world-only coverage while summing all frames by map ID. Repair confined to outer harness/evidence. No browser or HTTP requests run in the sandbox; host listener check belongs to supervisor.

## REQUEST_READY — 2026-11-18

- 修复限于外层 harness 四文件：`qa.cjs` 按原生 640×576 画布导出对照，并按已认证来源准确归属逐像素新图覆盖，单列非世界帧、原生缺口和其他已认证 HD 来源。区域 1/2 保留历史重绘序列，采用同一原生分母。 `perf.cjs` 精确处理空键、零等待；`summarize.py` 输出基于实测的中文分子/分母与差异；`run-outer.sh` 先确认视频大小/时长/无音频再发布，并保留阶段与启动记录。
- 离线 mock 检查 12 条性能路线的两种模式均按原冻结按键及空帧顺序运行 1792 帧。8 张画作的尺寸、取整纵横比、全不透明性、CLI 元数据和运行 PNG 字节均通过复核。Playwright、Chromium 路径、Pillow、CJK 字体、FFmpeg VP9 和 flock 已查本地文件/依赖。未运行网页、未发网络请求或重跑剧情及美术。
- 原 SHA 清单保留在 `offline/freeze-sha256-20261111.json`；更新仅含上述 4 个 harness 文件的摘要。复验通过 324 项，SHA-256 `765674d74521fbb624783a8a4a4fdf378126f10ab489300ba34124671727857b`。运行时 89 旧文件仅地图清单变更，新增 8 PNG；保护历史 changed=0，已披露 missing=3168。
- 精确外层 host 指令、独占条件、nohup 日志/PID/manifest 与恢复点见 `REQUEST_READY.md`。本次 Codex 于关口结束，外层监督确认 38811/8765 后执行。浏览器不变量、覆盖和性能仍未测；对照图、原速无音频预览及实测中文报告待外层运行。
- 原生剧情到 story12 吴用会合，下一步黄泥岗客栈设伏未进入。19596 帧信件链原证据保留；后段 26711 帧/281 动作连续与分段画面/ticks 一致，末态档 3 字节不同。正式 QA 始终比较同字节起点。

## Supervisor outer launch — 2026-11-18 01:22:07 EST
- Fresh Codex 已结束并写出 REQUEST_READY.md；无残留 Codex 进程。38811/8765 仍监听，8765 根目录 /workspace/shawu，runtime index 200。
- 按交接在确认无 M8/M7 QA、录像或 Codex 后启动独占外层：`SUPERVISOR_CONFIRMED_EXCLUSIVE=1 bash m8-work/scripts/launch-outer.sh`。环境 NODE_PATH=/home/box/opt/test-tools/node_modules，PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers。
- 机器上现存 Chrome/Playwright 为桌面与平台进程，不是本项目验收任务。监督不改网关/路由/凭据。正式 QA/性能/对照图/预览仍待本轮实测。

Outer stage qa finished: /workspace/shawu/m8-work/results/outer-20261118T062207Z

## BLOCKER: box reboot mid-perf — 2026-11-18 02:44:25 EST
- 外层独占任务 `results/outer-20261118T062207Z`（run-outer PID 219503）在性能阶段被机器重启打断。系统启动时间 2026-11-18 15:29 CST（02:29 EST）。Cockpit 38811 与项目 HTTP 8765 均已不在监听。按既定规则：38811 掉线则停止并上报，不绕行恢复网关/路由，也不重跑已开始且留下部分结果的性能阶段。
- QA 已在重启前完整结束并落盘（`qa.done`，`qa/report.json` SHA-256 42575581d9f543208324ba932f5c891cbd95ac5d44644f76a2e0bca487654fca）：33 条路线、1096 动作、84135 帧；state / native framebuffer / actor-text 均为 84135/84135 通过；区域 1/2 回归 442 动作、31396 帧，画面逐帧一致 31396/31396；errors 为空。无平滑放大 fallback。
- 第三区 8 图加权覆盖 420011267/517119168 = 81.22136888%。分图：00-00 209451439/211961230（98.81591978%）；00-01 2543992/4189680（60.72043688%）；00-02 2526600/4172799（60.54928598%）；00-03 2549224/4151191（61.40946056%）；00-04 2521661/4197903（60.06953948%）；00-05 195244745/280019353（69.72544680%）；00-06 2544476/4166443（61.07070228%）；00-09 2629130/4260569（61.70842439%）。残差含原生缺口、其他已认证 HD 来源（map/history 与 verified-flat-transition）、native geometry changed，以及 00-05 的大量 undefined（80982729 像素）。室内图约 60% 主要因“其他已认证 HD 来源”不计入本图画作分子。region3Excluded 为空。这些是实测覆盖，不是验收通过声明。
- 性能未完成：仅保存 20/144 个样本（legacy 第 1 次，路线 00-12、00-17、00-1b、00-0c、region3-00-00..05 的 adopted+candidate）。缺 region3-00-06/00-09、全部 cold、以及第 2/3 次重复。无 `perf.done`、无 comparison/report。部分样本的 frame p95 看起来不差于 adopted v3，但 00-1b 候选 p95 4.20 vs 3.90、max 12.9 vs 6.9，00-02/00-04 候选 max 更高；不完整集不能判定“不差于 v3”。原始样本保留在 `perf/`。
- 交付物不存在：`shots/m8_region3_contact.png`、`m8-work/region3_preview.webm`、`m8-work/REPORT_region3_zh.md`。无 exit-code（进程被重启杀死，EXIT trap 未执行）。
- 按 REQUEST_READY：已开始并留下部分结果的阶段，保留证据，先交 Codex 检查再考虑重试。下次恢复需先有可用的 38811/8765，再开新的 Codex 会话审查部分 perf 并给出是否/如何续跑的精确命令。不要 resume 旧 Codex 会话，也不要无检查地重跑 QA（`qa.done` 已在）。

## Fresh Codex perf-resume / coverage inspect — 2026-11-18 02:48:46 EST
- 上级确认重启后 38811/8765 已恢复（8765 根目录仍是 /workspace/shawu），Cockpit 已切回账户。按计划开全新 exec，不 resume 任何旧会话。任务书 CODEX_M8_PERF_RESUME_PROMPT.txt；日志 codex-m8-perf-resume.log，末条 codex-m8-perf-resume-last.txt。
- Codex 需：1）检查已保存的 20/144 性能样本是否可继续使用，并改外层 harness，使同一结果目录跳过已完成 QA、保留既有 perf 文件、只测剩余样本，再进入对照图/预览；2）用已有 QA 产物判断 00-05 的 80,982,729 像素 undefined 是分类问题还是真缺口，不得无证据重跑 84135 帧浏览器 QA，不得改分母/遮罩来“修好”覆盖率。
- 监督在其写出 REQUEST_READY 并退出后再独占跑外层。若约 10 分钟日志无新活动，结束本 fresh 并只再开一次更窄子任务。38811 若再掉线则停止上报，不绕行。

## Fresh Codex resume checkpoint — 2026-11-18T07:49:16Z
- Read persisted handoff and harness. QA report SHA-256 matches the supervisor checkpoint. No prior session loaded. Host ports were confirmed by the supervisor; sandbox cannot inspect host sockets, so no network probe was attempted.

- Sample integrity checkpoint. All 20 expected legacy repeat 1 files parsed and matched their route, mode, variant and repeat. Each has exactly 1,792 ordered raw frame records, no errors and nonzero 64-hex terminal state and framebuffer hashes. All 20 match their copies in perf/progress.json. Terminal state and framebuffer match adopted versus candidate for all 10 saved pairs. 124 samples remain. No performance acceptance result.
- Coverage forensics checkpoint. Scanned all 1,096 saved action dumps. The 80,982,729 reasonless 00-05 pixels are 80,960,008 on formal-meeting-11-to12 and 22,721 on formal-door-00-05. The legacy map renderer emits tiles with screenBounds and no reason; qa.cjs coerces the omitted reason to the key undefined. Example formal-meeting-11-to12 action 219 frame 24 (zero based), ticks 9392741560, mode 0 bank 33, scene unsupported, no mapResult.mapId or source pixels: 280 such tiles sum to all 16,992 native-gap pixels (eligible 16,992, covered 0). This is a label bug over a real uncertified native gap. Preserve all pixel counts and QA evidence; derive the label offline.

- Coverage recomputation checkpoint. Generated qa-coverage-attribution.json outside qa/ by reading the saved 1,096 actions and 84,135 frames. Every Region 3 coverage total, same-plate numerator, native denominator, native gap, other-HD count, and exclusion count matches the published QA. The 00-05 label moves 80,982,729 pixels across 3,786 frames to legacy map renderer: uncertified native background. 00-05 stays 195,244,745/280,019,353 (69.72544680%), with 81,538,832 native-gap pixels and 3,235,776 other-HD pixels. Region 3 stays 420,011,267/517,119,168 (81.22136888%). No browser QA rerun.
- Harness checkpoint. Added explicit outer resume mode, validated sample inventory, atomic no-replace sample publication, compact resume progress, final report only after all 144 samples, per-launch measurement provenance, and summary integration of the offline attribution. Original QA, perf/progress.json and perf.log remain in place. Offline mock interruption/recovery and freeze verification follow.

- Offline verification checkpoint. Simulated a stop after one newly completed sample (21/144), a corrupt saved sample, a stale partial temp file, and restart through 144/144 in a temporary mock directory. Only 123 samples were measured on the second mock launch; the 21 prior samples and original progress checked byte-exact. A restart with the complete report opened no browser. Unreadable samples stopped before browser launch and were left in place. Real inventory still 20/144.
- Archived QA-era freeze as offline/freeze-sha256-outer-20261118T062207Z.json. New active SHA-256 07aac456b160969f987e6d5d77b34209453bc6867281ee51c2d814318bd89c8e. Offline verification passed on 325 paths; four changed harness files and one new reporting helper are the complete manifest delta. Runtime and art hashes match the QA-era freeze. Historical protected changes 0; the same 3,168 venv/bytecode paths are missing.

- REQUEST_READY checkpoint. The supervisor launch and monitoring blocks parse, QA report/attribution/freeze digests match, and an isolated summary smoke test consumed the sidecar with exact coverage counts. The real directory remains at 20/144 with no perf.done, perf/report.json, comparison, contact or preview. Supervisor has the exact same-directory nohup commands and reboot procedure in REQUEST_READY.md. No browser/network QA, perf, art generation or recording was run by Codex.

## Supervisor outer resume launch — 2026-11-18 02:55:11 EST
- Fresh Codex 已结束并更新 REQUEST_READY.md。20 个已保存性能样本经其核验可继续使用；将在同一结果目录 `outer-20261118T062207Z` 以 `run-outer.sh resume` 跳过 QA，只测剩余 124 个样本，再做对照图/预览/汇总。
- 00-05 的 undefined 80,982,729 像素经既有 QA 回放确认：是标签问题叠加真实未认证原生缺口（legacy 渲染器 gap 记录缺 reason 字段，qa.cjs 写成 undefined）。离线重标为 “legacy map renderer: uncertified native background”，覆盖率数字不变：00-05 195244745/280019353（69.72544680%），第三区 420011267/517119168（81.22136888%）。未重跑浏览器 QA，未改分母/遮罩。
- 38811/8765 仍监听，8765 根目录 /workspace/shawu，无残留 Codex/外层任务。按交接命令启动独占 resume。
- 外层 resume 仍在跑（PID 16470）。性能库存 34/144，剩余 110。已跳过 QA，原 20 个样本保留。当前测到 cold region3-00-00 candidate r1。38811/8765 正常。时间 2026-11-18 03:03:54 EST。
- 外层 resume 仍在跑（PID 16470）。性能库存 51/144，剩余 93。已进入 legacy 第 2 次（newest legacy-00-17-candidate-r2.json）。38811/8765 正常。时间 2026-11-18 03:14:01 EST。
- 外层 resume 仍在跑（PID 16470）。性能库存 67/144，剩余 77。当前 legacy 第 2 次 region3-00-05 candidate。38811/8765 正常。时间 2026-11-18 03:24:06 EST。
- 外层 resume 仍在跑（PID 16470）。性能库存 84/144，剩余 60。当前 cold 第 2 次 region3-00-01 adopted。38811/8765 正常。时间 2026-11-18 03:34:12 EST。
- 外层 resume 仍在跑（PID 16470）。性能库存 89/144，剩余 55。当前 cold 第 2 次 region3-00-04 candidate。38811/8765 正常。时间 2026-11-18 03:36:48 EST。
- 外层 resume 仍在跑（PID 16470）。性能库存 106/144，剩余 38。当前 legacy 第 3 次 region3-00-00 candidate。38811/8765 正常。时间 2026-11-18 03:47:06 EST。
- 外层 resume 仍在跑（PID 16470）。性能库存 123/144，剩余 21。当前 cold 第 3 次 00-17 adopted。38811/8765 正常。时间 2026-11-18 03:57:12 EST。

Outer stage perf finished: /workspace/shawu/m8-work/results/outer-20261118T062207Z

Outer stage record finished: /workspace/shawu/m8-work/results/outer-20261118T062207Z

Outer resume EXIT_2: /workspace/shawu/m8-work/results/outer-20261118T062207Z; inspect measured reports; acceptance pending review.

## Supervisor outer resume completed — 2026-11-18 04:15:23 EST
- 同一结果目录 `results/outer-20261118T062207Z` 的 resume 已结束，未重跑、未新开任务。exit 2 / acceptance-exit 2。`acceptance.json`：correctness true，recording true，performance false，performanceFailures 165，coverage 420011267/517119168，supervisorVisualReview 现由监督审阅对照图与 story12。
- 交付物已产出：`shots/m8_region3_contact.png`（1320×5170，约 5.36MB）；`m8-work/region3_preview.webm`（7,142,400 字节，65.44 秒，VP9 640×624，无音轨，8 段实时摘录约 59.66 FPS）；`m8-work/REPORT_region3_zh.md`。
- 正确性维持 QA 结论：84135 帧 state/native/actor-text 全过；区域 1/2 回归画面 31396/31396。性能严格规则未过（144/144 样本，165 项 paired 不回归失败）。三次均值上，区域 3 frame p95 明显优于 adopted v3（约 8–11ms → 3.3–5.1ms）；区域 2 frame p95 仍在约 4.0–5.4ms。最显著回退是 cold/00-17：frame/switch max 均值 +13.0ms（16.0→29.0），debt.max +14.9ms（16.7→31.6）。另有 legacy/00-17、00-1b 及 region3-00-01 切图 max 约 +2–4ms 等。165 项中 85 项均值其实更好、只是单次重复略差；37 项均值回退幅度很小。不能宣布性能通过。
- 视觉：对照图左原版右运行高清，人物精灵为原版，门路与室内家具布局大体对齐，不像平滑放大原图。00-06 庙宇红毯与两侧牌匾上的原版背景字在高清整图中更接近纹饰，字形不忠实，记为美术缺口（不改变已通过的 actor-text 哈希，那是游戏文字层）。story12 吴用会合画面人物与布局对齐。黄泥岗未进入。

## Supervisor next steps after M8 accept-as-disclosed — 2026-11-18 04:17:47 EST
- 监督决定：第三区正确性与覆盖率按已披露结果接受。接下来只做两件有界事项，然后再进入黄泥岗：1）一轮全新 Codex，只修 M8 引入的 cold/00-17 回退（frame/switch max 均值 16.0→29.0ms，debt 16.7→31.6；主要由第 3 次 51.6/61.3ms 尖峰拉高）。若三次均值 max 回到 v3 的约 3ms 以内且正确性仍过，则接受；否则回退到当前 M8 并披露残差，不再迭代。2）监督外层用 gpt_image.py edit 重做 00-06 庙宇整图，提示词明确要求红毯与牌匾字形忠于原版；目检更好再交 Codex 接入。
- 本轮先启动全新 Codex（不 resume），任务书 CODEX_M8_COLD_0017_PROMPT.txt，日志 codex-m8-cold-0017.log，末条 codex-m8-cold-0017-last.txt。同时准备 00-06 v2 生图，不覆盖现用 00-06_gpt.png。38811/8765 当前监听。若 38811 掉线则停止上报。

## Cold/00-17 bounded round — file evidence checkpoint

- Fresh exec using workspace files. Read the supervisor and adopted-v3 decisions, current progress and formal runners. Saved outer QA/perf and the accepted M8 runtime are the reference. Runtime tree comparison against v3 shows only the map registry and added Region 3 assets differ.
- The sandbox listener query failed with netlink EPERM. No HTTP or browser checks will run here. The supervisor's latest checkpoint records both listeners; current host status requires the outer gate. No gateway, routes or credentials touched.

- Diagnosis checkpoint. The frozen 00-17 cold replay reproduced all 1,792 map IDs and the saved native endpoint hashes with the bundled WASM and a headless Canvas stub. The map ID changes to 00-19 at frame 450. At frame 497 the region renderer has no source, calls locate on 29 plates and performs 322 agreement checks. At frame 504 it uses continuous-camera native geometry for 00-19 and paints via the pixel path, with no transition search. Saved repeat 3 measured 51.1 ms render + 0.5 ms core there and peaked at 61.291 ms debt. M8 also adds 32.125 MiB of allocated but unused full-sheet scratch across its eight warm plates. The saved samples have no allocation/GC or compositor trace, so the exact browser stall remains unproven.

- Candidate checkpoint. `runtime-fix-0017/` is an isolated copy. Its only changes are `region-renderer.js` (reuse the observed cells and skip impossible 95% exact-match plates) and `map-renderer.js` (allocate full-sheet scratch only for the legacy full-sheet consumer and its existing startup warmup). This also avoids unused scratch in old full-world plates. Frozen runtime, map data, assets, ROM/core and harness remain byte-identical. Acceptance pending outer measurement.

- Outer harness checkpoint. The locked runner invokes the original QA with the isolated candidate path and reuses the original perf measurement function. It will measure only 00-17 in cold and legacy modes, three fresh repeats each for adopted v3, the candidate and original M8, keeping same-run controls and the historic data. The runner uses a new directory and a local listener watchdog. Formal QA must match the accepted coverage attribution, including the 00-05 relabel, before perf.

- Offline verification checkpoint. In both frozen 1,792-frame 00-17 modes, candidate and original match native map IDs on every frame, saved endpoint state/framebuffer hashes and every renderer metadata record with a stubbed Canvas. Frame 497 drops from 29 locate calls / 322 agreement checks to 1 / 1. The candidate removes 99 MiB of unused full-world scratch (32.125 MiB attributable to the eight M8 additions), with identical legacy full-sheet warmup. The bundled m52 unit script has a pre-existing missing region warmup stub in both trees; all 10 checks pass with that stub supplied in memory. Original 325-file freeze and the isolated runtime digest check pass. The decision harness passes offline acceptance/rejection smoke tests using saved samples and rejects a simulated coverage loss. Browser correctness and performance remain pending.

- REQUEST_READY checkpoint. `m8-work/REQUEST_READY.md` now has the exact locked supervisor launch, monitor/stop, and accept/revert commands. Candidate and original are separate, so rejecting the experiment leaves the accepted runtime in service without file writes. No live browser runs or new result directories were created here. Fresh exec complete at the handoff; the next action is supervisor launch, with acceptance pending.

## Supervisor item1 launch and item2 visual — 2026-11-18 04:23:26 EST
- Fresh Codex 已结束并写出 cold/00-17 REQUEST_READY。候选在隔离目录 `runtime-fix-0017/`，原 M8 `runtime/` 未改。按交接在新结果目录独占跑完整正确性 QA + 仅 00-17 cold/legacy、adopted/candidate/原 M8 共 18 个性能样本。通过门限：cold 三次均值 frame/switch max ≤ 19.0ms，且 84135 帧不变量与覆盖数字保持。不通过则继续使用原 runtime 并披露残差。
- 00-06 v2 GPT 已生成（75.8s，medium，`art/00-06_gpt_v2.png`，未覆盖 v1）。目检：布局仍对齐，无人物；红毯与六块牌匾已从 v1 花纹改回文字，回纹边框与配色正确。牌匾现为「月/市/同」，红毯为「勅令闕」，比 v1 明显更接近原版字形；原版像素很低，顶部/中字仍有少许辨认空间。对比裁图：`art/00-06_glyphs_before_after.png`。待 item1 外层跑完后再开新 Codex 接入 v2。
2026-11-18T09:23:26Z cold/00-17 outer preflight started /workspace/shawu/m8-work/results/outer-cold-0017-20261118T092326742885874Z
2026-11-18T09:23:31Z cold/00-17 outer formal QA started /workspace/shawu/m8-work/results/outer-cold-0017-20261118T092326742885874Z
- cold-0017 外层仍在跑（PID 72715），正式 QA 进行中，约 5902 帧。38811/8765 正常。时间 2026-11-18 04:30:20 EST。
- cold-0017 QA 仍在跑（PID 72715），约 24300/84135 帧（story-6-to-9）。38811/8765 正常。时间 2026-11-18 04:40:27 EST。
- cold-0017 QA 仍在跑（PID 72715），约 42540/84135 帧（formal-letter-9-to11）。38811/8765 正常。时间 2026-11-18 04:50:35 EST。
- cold-0017 QA 仍在跑（PID 72715），约 58302/84135 帧（formal-meeting-11-to12）。38811/8765 正常。时间 2026-11-18 05:00:41 EST。
- cold-0017 外层仍在跑（PID 72715），未重开。QA 约 65062/84135 帧（formal-meeting-11-to12 action 180/281）。38811/8765 正常。时间 2026-11-18 05:06:31 EST。
- cold-0017 QA 仍在跑（PID 72715），约 74383/84135 帧（formal-meeting action 260/281）。38811/8765 正常。时间 2026-11-18 05:16:37 EST。
2026-11-18T10:25:35Z cold/00-17 outer formal QA and coverage passed /workspace/shawu/m8-work/results/outer-cold-0017-20261118T092326742885874Z
2026-11-18T10:25:35Z cold/00-17 outer 00-17 cold and legacy perf started /workspace/shawu/m8-work/results/outer-cold-0017-20261118T092326742885874Z
- cold-0017 正式 QA 已通过（qa.done / qa-check.json）：84135/84135 state、native、actor-text；回归画面 31396/31396；覆盖 420011267/517119168。性能 18 样本已于 10:25:35Z 开始，runner PID 72715 仍在。时间 2026-11-18 05:26:06 EST。
2026-11-18T10:36:39Z cold/00-17 outer 18 focused perf samples saved /workspace/shawu/m8-work/results/outer-cold-0017-20261118T092326742885874Z
2026-11-18T10:36:39Z cold/00-17 outer EXIT_2 at decision /workspace/shawu/m8-work/results/outer-cold-0017-20261118T092326742885874Z

## Item 1 gate applied — 2026-11-18 05:41:07 EST
- 外层 `results/outer-cold-0017-20261118T092326742885874Z` 已结束，exit 2，`decision.json` meetsRoundGate=false。未重开、未再迭代。
- 正确性与覆盖率保持：84135/84135 state、native framebuffer、actor-text；区域 1/2 画面 31396/31396；第三区 420011267/517119168。native 不变量差异 0。
- cold/00-17 三次均值（本轮实测）：candidate frame/switch/firstSwitch max **24.100ms**（31.800、13.200、27.300），未达到 ≤19.0ms 门限（对照已保存 v3 16.000）。debt.max 为 16.738（已保存 M8 为 31.591，已保存 v3 为 16.735），债务尖峰消失，但不足以过门。
- 同机对照也偏吵：本轮 cold adopted（v3）均值 26.067，original M8 20.567；已保存 M8 29.000。按预定规则 **继续使用原 `m8-work/runtime/`**，不把 `runtime-fix-0017/` 设为正式 runtime；候选树与结果保留备查。cold/00-17 切图 max 残差维持披露。
- 接下来开全新 Codex（不 resume）把已目检更好的 `art/00-06_gpt_v2.png` 接入正式 runtime，并准备校验命令。不开始黄泥岗。


## 00-06 v2 first Codex session died — 2026-11-18 05:50:40 EST
- Fresh exec PID 118904 (log `m8-work/codex-m8-00-06-v2.log`) ended after Reconnecting 5/5 and 503 `连接上游服务失败` from 38811 `/v1/responses`. `codex-m8-00-06-v2-last.txt` remains 0 bytes.
- No integration landed: `runtime/assets/region3/00-06_hd.png` is still v1 SHA-256 prefix `3a5a9c9d132690fd`. v2 remains `91125e14a469c162` at `art/00-06_gpt_v2.png`. `REQUEST_READY.md` is still the prior cold/00-17 handoff (mtime unchanged).
- 38811 and 8765 are listening again after the 503. Per standing rule, launching one narrower fresh exec (not a resume) to copy v2 bytes, update provenance/freeze, and write verify commands only. No dump exploration. Do not promote `runtime-fix-0017/`. Do not start 黄泥岗.

## 00-06 v2 live integration

- Copy checkpoint. Verified the v1 runtime SHA-256 `3a5a9c9d132690fd38c5ac2836ffa7272ea839737b5148adacfddf52393ce11d` and the reviewed v2 art SHA-256 `91125e14a469c162db6454acd0d573b812d9908ae8c1c45a90a26fb39676316a` before copying. The live `runtime/assets/region3/00-06_hd.png` now has the v2 SHA-256 and is byte-identical to `art/00-06_gpt_v2.png`.

- Provenance checkpoint. Updated the live 00-06 entry in `integration/provenance.json` to v2 using the existing CLI metadata and PNG dimensions. Preserved the whole v1 entry under `previousVersion`, including the original art and runtime hashes. Linked the v2 prompt and supervisor comparison crop.

- Freeze checkpoint. Updated the active `freeze-sha256.json` with the live asset, integration provenance, and four v2 art files. Updated the offline inventory checker to include those four files. The checker uses this manifest directly. The art input freeze and historical freeze archives retain their original scope.

- Scope checkpoint. Every active freeze entry matches disk. The runtime change is limited to the 00-06 PNG. The rejected runtime tree, original v1 art, historical result directories, and HTTP service were left in place.

- Verification plan checkpoint. The official natural temple replay `formal-door-00-06` has 35 actions and 1,092 native frames. The outer command will scope the official QA runner to this route and use the accepted aggregate report to check that the replay accounts for the official 00-06 visits and plate selection. The repository offline checker passed with 329 frozen files and no protected-file changes. Outer browser verification is pending.

- REQUEST_READY checkpoint. Replaced the cold/00-17 handoff with the v2 integration provenance and exact outer verification commands. The commands use both exclusive locks and a fresh result directory. Validated their shell and Node syntax, exact frozen route selection, and scoped QA compilation offline. The supervisor owns the outer replay and its verdict.
2026-11-18T10:55:20Z 00-06 v2 outer preflight started /workspace/shawu/m8-work/results/outer-00-06-v2-20261118T105520392404006Z
2026-11-18T10:55:25Z 00-06 v2 outer EXIT_1 /workspace/shawu/m8-work/results/outer-00-06-v2-20261118T105520392404006Z

## 00-06 v2 preflight diagnosis — 2026-11-18 05:57:20 EST
- Failed result dir `results/outer-00-06-v2-20261118T105520392404006Z` exit 1 after ~5s, during preflight, before any browser QA. Locks were acquired; SHA/cmp of the live v2 plate passed. `ports.log` empty; no `port-stop.txt`.
- Cause: `offline-check.py --verify-only` reported `Frozen inventory/hash mismatch`. Actual inventory was 330 vs frozen 329. The only extra path was `m8-work/scripts/run-outer-00-06-v2.sh`, a supervisor-extracted copy of the REQUEST_READY bash block placed under the frozen `m8-work/scripts/` tree after Codex's offline check had already passed at 329.
- All previously frozen hashes still matched, including v2 `00-06_hd.png` `91125e14a469c162…`. Not a lock issue and not a runtime regression. Historical result dirs and `offline/freeze-sha256-outer-20261118T062207Z.json` untouched.
- Fix (no Codex/code change): moved the helper to `m8-work/outer-runs/run-outer-00-06-v2.sh` (outside inventory). Re-running scoped official formal-door-00-06 verification in a NEW result directory.
2026-11-18T10:57:44Z 00-06 v2 outer preflight started /workspace/shawu/m8-work/results/outer-00-06-v2-20261118T105744118606584Z
2026-11-18T10:57:50Z 00-06 v2 outer formal-door-00-06 started /workspace/shawu/m8-work/results/outer-00-06-v2-20261118T105744118606584Z
2026-11-18T10:59:04Z 00-06 v2 outer EXIT_1 /workspace/shawu/m8-work/results/outer-00-06-v2-20261118T105744118606584Z

## 00-06 v2 scoped verification complete — 2026-11-18 06:04:15 EST
- First preflight (`outer-00-06-v2-20261118T105520392404006Z`, exit 1 in 5s) was caused by supervisor helper `m8-work/scripts/run-outer-00-06-v2.sh` landing inside the frozen scripts inventory (330 vs 329). Helper moved to `m8-work/outer-runs/`. Offline-check then passed (329, freeze SHA `bbae184e21cc0758…`).
- Rerun: `results/outer-00-06-v2-20261118T105744118606584Z`. Official `qa.cjs` formal-door-00-06 passed: **1092/1092** state, native framebuffer, actor-text; `pass: true`; errors []. 35 actions. Endpoint map `00-06`, story 11.
- Coverage counts hold vs accepted full QA: 2544476/4166443 covered/eligible, 188 frames, gap 1621967, nativeGap 27256, otherHD 1594711, source frames 00-00:62 / 00-06:116 / no-region-source:10. The only coverage object difference is the known 22365 px reason label `undefined` → `legacy map renderer: uncertified native background`.
- In-game native evidence PNG is byte-identical to the accepted run. All 35 endpointChecks native/actor/text hashes match accepted and cold-0017. startState and final action-34 state match history.
- REQUEST_READY wrapper CHECK exited 1: `deepEqual(qa.routes, historical)` failed on 23 intermediate `endpointChecks.state` hashes and `startNativeSHA256`. This is cross-run absolute-hash instability, not a failed pairwise invariant (candidate still matched adopted v3 on every frame). Did not treat that as a correctness regression. Did not overwrite official `qa-check.json`. Notes in `supervisor-acceptance.json`.
- In-game plaque crop written to `m8-work/art/00-06_glyphs_ingame_before_after.png` (native | HD v1 | HD v2). Did not overwrite frozen plate crop `m8-work/art/00-06_glyphs_before_after.png`. Live runtime plate remains v2 SHA `91125e14a469c162…`. No next-region work. Item 1 revert unchanged.

2026-11-21T04:10:41.828260+00:00 Stage 2 blocked in M8 offline preflight before run allocation. Missing 97 frozen files and 9,334 required protected-history paths. No samples started. See /tmp/codex-stage2-report.md.

## Freeze amendment — 8 art CLI logs removed (owner decision) — 2026-11-21 05:04 UTC
- Owner confirmed the 8 GPT art generation CLI logs are unrecoverable (not in the repo, not on the desktop workspace). They were CLI stdout from the 2026-11-11 `gpt_image.py edit` runs; no sample or template exists, so the exact bytes cannot be reconstructed, and re-running generation would produce different images and break the frozen PNGs.
- Owner decision (2026-11-21): remove the 8 log entries from the active `freeze-sha256.json` (329 → 321 entries) so M8 QA/perf can run. Pre-amendment manifest archived at `m8-work/offline/freeze-sha256-20261121T050407Z.json` (SHA-256 `bbae184e21cc075817b08dddc3862d79d7127e039b75c749b1a6c5dbb8d7e3c1`). Amended manifest SHA-256 `772bdf6e2bc046b97f5a1e382b582435161af76014f703d2af68b6b3259baeb3`. Removed entries and their recorded hashes:
  - `m8-work/art/cli-generation/20261111T112050Z/00-00.log` ce054df8dcf230de757af45b3f4388c1f3e8f02f807450e73f8bfbe25dc10f05
  - `m8-work/art/cli-generation/20261111T112050Z/00-01.log` a56664e47e3d96048dd42b21f61a7e5a69abff603bcfc393fb4f61aa2ee5d87d
  - `m8-work/art/cli-generation/20261111T112050Z/00-02.log` 364043198fb6c042564f35c9a08b6d8247ed2b02a3d29663eb8a0afa58f2e2d7
  - `m8-work/art/cli-generation/20261111T112050Z/00-03.log` 677aec1feddf14d74673978e6898c2b2d567769d7eba0ebcb8df2ed4825361e5
  - `m8-work/art/cli-generation/20261111T112050Z/00-04.log` 3427a27f99d1863ca45259ffb2cc6c0d64ab2e5f46524fd194007278177b2931
  - `m8-work/art/cli-generation/20261111T112050Z/00-05.log` c96af3e339c236ac697263ba2a49bafc844935deba1de1b067af4e6610881668
  - `m8-work/art/cli-generation/20261111T112050Z/00-06.log` 2a935fc6521cac552765801a218f2fec329f04f529978d1cf47682d8d7dfdff8
  - `m8-work/art/cli-generation/20261111T112050Z/00-09.log` 1f5b4270901025dd8deef0cdfcbd9968bb9eba46f0f1f5b1f2a6137527b68b06
- What survives frozen: the 8 GPT PNGs, their `.png.meta.json` CLI metadata, `jobs.tsv`, `input-sha256.txt`, `output-sha256.txt`, `output-dimensions.txt`, and the supervisor visual review. No script reads the log contents; only `verifyFreeze()` checked their hashes.
- Verification after amendment: hash audit 321/321 present and matching, `verifyFreeze()` passes, `offline-check.py` freeze portion clean (frozenFiles 321, runtimeChanges only `assets/region1/maps.json`, codeROMCoreUnchanged true, protectedChanged 0). The check still reports the 9,245 desktop-only protected-history paths as missing — that part is bypassed per the owner-approved plan (run `qa.cjs`/`perf.cjs` directly; their own `verifyFreeze()` gate still applies).
- No other manifest entry was changed. The git diff of the amendment is exactly the 8 removed lines.
Stage 2b /home/hatch/workspace/shawu/m8-work/results/outer-20261121T050659Z. Owner approved direct QA/perf because the wrapper additionally requires desktop-only protected history. Freeze 321/321, both exclusive locks held, live Tailscale CONNECT verified.

2026-11-21T05:08:20.940178+00:00 outer-20261121T050659Z stopped on confirmed cold-0017 manifest pin conflict in check.cjs:32. Last QA checkpoint 600 frames. Partial evidence retained, zero perf samples. See /tmp/codex-stage2-report.md.

Stage 2c /home/hatch/workspace/shawu/m8-work/results/outer-20261121T051507Z. M8 freeze 321/321 and verifyFreeze passed. M11 673/674, only historical M10 comparison missing. Direct QA and perf under both runner locks and SUPERVISOR_CONFIRMED_EXCLUSIVE=1 with Tailscale-forwarded gate. Owner approved bypassing run-outer.sh because its offline-check additionally requires 9,245 desktop protected-history files absent from the clone. Measurement freeze gates retained.

# Stage 2c stopped before M8 QA completion

Fresh M8 run `outer-20261121T051507Z`. Its last published QA progress was 31 actions and 2040 frames. QA did not pass or produce a completion marker. The partial run is preserved. M8 perf 0/144, M9 perf 0/276, M10 perf 0/252. No downstream RUN_IDs, fresh cold-0017 decision, or measured gate outcome. The approved cold method would compare fresh adopted and retained M8 samples, with original and candidate sharing the retained runtime.

M8 matched 321/321 and verifyFreeze() passed. M11 matched 673/674 with only the historical M10 comparison missing. All three play evidence directories existed. Neither inventory changed. Direct M8 QA used both runner locks and the Tailscale-forwarded gate. The owner approved running QA and perf directly because run-outer.sh requires an additional 9,245 desktop-only protected-history files.

The stock M9 prepare script cannot re-point the plan in the required symlinked environment. Its line 89 calls relative(Path(r["source"])) on the frozen perf routes. Its first input starts with /workspace/shawu/m8-work/inputs/05e9bb670eff6994-05e9bb670eff6994-00-12.bin. At line 40, Path.relative_to(ROOT) raises ValueError because ROOT resolves to /home/hatch/workspace/shawu. Reproduced directly with the unmodified function and frozen input. This happens before either approved path constant is consumed. No M9, M10 or M11 prepare was run and no plan was edited. To unblock, provide /workspace/shawu as the physical checkout path for prepare, or authorize resolving the input before relative_to.

M9 also lacks m9-work/runtime/assets/game.gbc, required by prepare's runtime hash check. Its pinned SHA-256 exactly matches the verified local M8 ROM (ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95). Restore that existing inventory entry or authorize its restoration under the frozen runtime tree. No ROM was staged. No commit or push.

Elapsed wall time 240 seconds through measurement shutdown.

Stage 2d /workspace/shawu/m8-work/results/outer-20261121T052144Z. Direct QA and perf under both runner locks with verifyFreeze. The desktop audit in run-outer.sh needs 9,245 protected-history files outside the checkout.

Stage 2e launched /workspace/shawu/m8-work/results/outer-20261121T055349Z under both exclusive locks. Using direct QA and perf with verifyFreeze because the desktop-only offline audit requires 9,245 protected-history files. M8 321/321 and M11 673/674 verified.
QA passed /workspace/shawu/m8-work/results/outer-20261121T055349Z
Perf verified 144 samples /workspace/shawu/m8-work/results/outer-20261121T055349Z

Stage 2e 2026-11-21T08:56:33.064014+00:00 outer-cold-0017-20261121T085632Z used 12 fresh paired 00-17 samples. savedV3 uses adopted. original and candidate share measurements of the retained original M8 runtime after the fix was reverted. No savedM8 reference or historical certification. Gate False at 19 ms, cold means {'frame.max': 67.30000000043462, 'switchAggregate.frame.max': 67.30000000043462, 'firstSwitch.frame.max': 67.30000000043462}, native mismatches [].
