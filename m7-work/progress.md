# M7 大名城区域进度

- 用户继续，沿用GPT整图方式；只发对照图和录像，不打包。
- 已读取M6报告、全部方法与清单。任务依赖箱内唯一ROM/自然存档，隔离复制 region1/runtime -> m7-work/runtime，本机处理，不改M6或web。
- 从 M6 council-mission-final/latest.bin 自然继续（story 6，赴大名城）。先确认连通地图/剧情关口，再并行GPT整图。
- 约束：人物/文字/ROM/core不改，严格原生证据，性能独占验收，所有失败/未完成如实保留。

- 静态warp表确认大名城外城00-12、内城00-17、大名府00-1e及10间相连室内00-13..16/18..1d。暂定13张整图，野道00-08已在M6，待自然验证。13图GPT medium并行worker启动，620秒硬截止/最多5次退避；仅发送无人物原生整图与已批准风格参考。

- 大名城13图已分批生成：00-12/13/14成功（medium），12/14首试上传超时，同接口退避重试成功；其余worker继续。已将样式参考压缩为JPEG减少上传体积，模型/medium质量不变。三图已目检布局，无人物。
- 自然路线已从史进家离开，经史家庄南口到00-08，正常遭遇野生神兽并用原生菜单逃跑；尚未抵达大名城。搜索器需保留移动/战斗相位，不用RAM跳图。

- 已从M6自然存档一路按键抵达大名城外城00-12，保存 webplay/city-gate.bin（story仍6）。中途两次野战均原生菜单逃跑；未改RAM/地图号/剧情。外城首个稳定视口22552/22552背景像素认证。完整自然输入链均在play与webplay JSON。旧全域BFS已因手动自然路线成功安全停止，避免占用后续验收CPU。

- 全部13地图均已从原生城门/房门按键自然可达：外城4屋、内城6屋、大名府；未出现该阶段专属地牢。00-1f等黄泥岗森林迷宫是野道向东支路，未属于本次大名城任务，因此未冒充已做。
- 已自然完成白胜任务 story6→7（原生对白约定吴用家会合）、出门新闻7→8，再步行入大名府观看鲁智深救小兰剧情8→9。结束存档play/region2-story9-end.bin；停止于这次重大剧情关口，尚未走回史家庄索介绍信/交给醉仙楼鲁智深/赴东溪村，后续不声称完成。
- 已连续从M6末存档重放6776帧自然按键，确实抵达00-12/story6。与分段快照序列化有少量内部字节差异，未断言原因；正式不变量验收将候选与基线使用同一起点/同输入逐动作全state+framebuffer对照，不用位置相同冒充哈希相同。

- GPT已成功12/13图；00-1e大名府首试失败，同接口第二次重试中。其余图已逐一目检整图布局/门窗/家具数量/无人物，参考图见shots/art-review-12.png。仅素材+JSON新增接入，所有既有M6运行文件逐项SHA不变（maps.json仅追加新地图）。
- 自然剧情最终story9存档与全部输入已落盘，严格QA冒烟在跑。正式QA改为浏览器内SHA256后只回传摘要，以减少无意义大数组序列化；不降低native/framebuffer或人物文字检查。

- 冒烟旧版QA在将每动作完整state/pixels大数组通过CDP回传时过慢，尚未落盘结果；已安全停止，不能当作通过。采用已准备好的浏览器内SHA256版重新完整运行，所有帧/输入/证据/人物mask不变。

- 独占M5.2基线4条1792原生帧性能已完成；冻结perf-states，防止QA输出新预览存档改变基线/候选起点。GPT最后一张00-1e第二试仍等待，保留620秒硬截止。若第二试失败，第三试同网关以low质量（<=medium）减轻请求负担；没有改接口或使用任何平滑原图补洞。现有12张返回10 medium/2 low（均请求medium）。

- 13/13张GPT整图均已成功。最后大名府00-1e第三次low请求成功，前两次分别504/620秒硬超时。全图已接入M7，第一片8图保留，共21张整图；正式web仍未覆盖，无ZIP。最后大名府已目检，无人物（两石狮为原图已有建筑装饰）。正在以最终13图源完整跑23条QA分支（M6末存档连续进城、13图步行、8图第一片回归、白胜+大名府story6→9）。

- 最终13图运行源全套QA已完成：31396个原生帧、442/442完整state SHA256、442/442原生framebuffer SHA256、442/442人物/原文字呈现检查通过，页面错误0；包含第一片8图48处回归与story6→9自然任务。正在按已冻结起点独占跑M7性能，再录13图原速预览。

- 最终独占M7性能完成，4/4末state/framebuffer SHA与M5.2一致，平均游戏速度仍约59.7fps。必须保留尾延迟 caveat：外城/内城门路首次切图出现约95ms/74ms单帧，最大暂时欠债约164/218ms，p95分别10.6/9.9ms，较本轮基线8.7/9.4ms略高，不能声称所有指标无回退或零卡顿。平均渲染更快，未改时钟/丢帧/加速。准备13图原速录像。

## 本轮交付完成
- shots/m7_region2_contact.png：13图原生/高清整图对照，约2.6MB。
- m7-work/region2_preview.webm：100.16秒、16905508字节、VP9 640×600/25fps采集（完整640×576画布+24px标题），13个自然存档原速片段，模拟平均59.6819fps，页面错误0，无音轨。不是连续通关，未加速。
- 442/442玩法/原生framebuffer/人物文字检查通过；13图像素覆盖99.6636–99.9348%，加权99.7345%；第一片8图48处短回归通过，ROM/core/旧运行文件不改。
- 正式性能59.7417fps vs M5.2 59.7314fps，但两个首次切图的尾延迟比基线高（单帧约95/74ms、暂欠债164/218ms）；该严格子目标未完全达成，不能隐去。
- REPORT_region2_zh.md与DELIVERY.json含边界、逐图数据和所有路径。剧情停story9鲁智深救小兰后；介绍信/醉仙楼交信/东溪村尚未推进。无ZIP；正式web未覆盖；Windows实机未测。所有本轮长任务已结束。

## Supervisor availability check — 2026-11-10 22:43:37 EST
- 已按用户要求仅监工，读取M7报告与进度；Codex CLI已存在（/home/box/.local/bin/codex）。
- 两次ss检查确认127.0.0.1:38811无监听；pgrep未发现Codex/Cockpit进程。按交接要求停止启动开发，不自行写代码、不换代理/编码工具、不读凭据。CLI存在，故不运行reinstall.sh。
- M7尚未修复，442/442与99.7345%仅为既有M7结果，不是新复测。未改运行文件。
- 已备好CODEX_M7_FIX_M8_BRIEF.md（M7尾延迟验收与M8完整约束），等待上级在Cockpit GUI恢复/切换账户后启动Codex。

## Supervisor restart — 2026-11-10 22:45:22 EST
- 38811已恢复监听；tiny codex exec成功返回CODEX_SMOKE_OK（smoke日志与结果已存）。
- 以Codex执行全部编码，先做Stage A M7修复并停止于监督验收关口；通过后续跑M8。监督不手写代码。

## Stage A Codex 开始（仅本阶段）
- 编辑前完整保存 pre-fix M7 runtime、逐文件SHA256、旧QA/perf及冻结起点至 stage-a/baseline-m7/；旧证据不覆盖。
- 沙箱socket探测EPERM；通过/proc监听表只读核对38811，不改路由/认证，不启动嵌套Codex。浏览器验收准备交由外层监督运行。

## Stage A Codex 候选冻结 / REQUEST_READY — 2026-11-11T03:58:00.301102+00:00
- 调查：已有decode/prepareBase启动准备，不能简单归因未解码；低run数仍会触发整图宽palette strip。只改region-renderer.js，所有不透明整图复用既有viewport texel/LUT路径；startup准备不可变view/输出缓冲，不预跑core，不改mask/证据/分母/时钟。定位/行恢复等其他开销由独立diagnose脚本待外层确认。
- pre-fix M7 89文件快照原SHA再核对通过；原qa/perf/perf-states与快照字节一致。M5.2与15个唯一起点另冻结。
- 352文件freeze校验、JS/Python/shell语法与6类RGBA oracle（8847360字节）通过，透明fallback/零core startup通过；ROM/core/88个其他运行文件不变。证据stage-a/offline/checks.json与runtime.diff。
- 外层脚本已备：原442检查、31396帧HD/coverage逐帧比较、仪表归因、三版本×两协议×3次重复72个独占perf样本，首切/全部切图窗/冷帧/p95/max/debt/fps与startup/loadState单列。旧证据绝不覆盖，不运行旧verify-final.sh。
- 本沙箱socket EPERM且network namespace表仅表头；不是代理掉线证据，依据监督smoke继续离线，外层若38811检查失败立即BLOCKER停止。无嵌套Codex/路由认证更改。
- REQUEST_READY见STAGE_A_STATUS.md；精确命令SUPERVISOR_RUN_STAGE_A.md；中文调查与待测项目stage-a/REPORT_STAGE_A_zh.md。候选浏览器不变量/覆盖/视觉/独占性能未测，不能称Stage A通过。等监督接受后才可Stage B；本轮未动M8/美术/录像/ZIP。

- 交付前harness审查：perf在最终帧同时关闭rAF probe，与原协议一致，避免pause后空闲rAF混入debt分布；未改runtime。前版manifest及perf脚本保留stage-a/freeze-history/pre-handoff-v1.json与perf-pre-handoff-v1.cjs，当前freeze已明确更新并重新校验。

- 交付时发现监督外层已启动结果目录：candidate-v1-supervised首试HTTP8765 ERR_EMPTY_RESPONSE（失败日志保留）；candidate-v1-supervised-retry的QA已进到第20动作，最初21项state/native framebuffer相同。尚无完整验收结果。状态更新EXTERNAL_QA_IN_PROGRESS；停止本轮CPU验证/源码修改，让监督顺序完成，勿并发启动。

## Supervisor outer QA — 2026-11-10 23:02:07 EST
- 已审查Codex仅改region-renderer.js绘制与启动准备，候选冻结，352项离线检查通过。
- 首次外层QA因旧8765服务ERR_EMPTY_RESPONSE失败；检查旧PID5001服务根为web并且输出为过期socket。已正常重启同端口HTTP服务到项目根，HEAD 200；新结果目录candidate-v1-supervised-retry从头复测，旧失败证据保留。
- Codex沙箱EPERM不是代理掉线；外层38811持续有监听。未开始M8。

## Supervisor QA milestone — 2026-11-10 23:16:50 EST
- 外层真实Chromium新复测通过：442/442 state、原生framebuffer、人物文字；31396帧完整高清画面SHA与pre-fix M7逐帧完全一致，coverage逐帧计数零差异，页面错误0。未改变视觉，故不重录M7视频。
- 独占顺序性能测试已开始（三版本、两种协议、三次重复），尚未验收性能；38811仍有监听。M8仍等待Stage A验收。

## Supervisor resumed — 2026-11-10 23:35:27 EST
- 已确认旧外层perf仍在运行（PID535118，wrapper505837），不重复启动。已有32/72独占顺序样本，原QA/31396帧视觉通过证据保留。
- 38811仍监听、8765服务项目根。候选继续冻结；Stage A尚未验收，Stage B尚未开始。

- 2026-11-10 23:47:56 EST：同一perf顺序任务已到第3轮legacy；未发现停滞，不重启不并行。完整性能尚未结束，不以平均fps替代尾延迟验收。

## Stage A candidate v1 rejected — 2026-11-10 23:59:56 EST
- 外层72/72顺序性能样本已完成；442/442与31396帧完全视觉一致，但性能严格验收未通过，不能宣称修复完成。
- 重复均值：legacy外城max debt 163.504ms vs M5.2 40.243ms，cold内城切图窗max frame 31.000ms vs M5.2 13.067ms。需交Codex继续优化；M8仍等待Stage A。
- 证据：stage-a/results/candidate-v1-supervised-retry/REPORT_STAGE_A_zh.md与comparison.json，不覆盖。

## Stage A v2 开始 — 2026-11-11T05:00:39.458533+00:00
- 监督明确v1未接受：442不变量/31396帧视觉/覆盖通过，但外城legacy debt、内城cold switch tail有实质回退。全部编码继续由当前Codex完成，只做Stage A，不改测量定义/容差。
- 编辑前完整保存v1 runtime、freeze、scripts、offline、报告、所有results至stage-a/versions/v1/；逐文件SHA256保全清单preserved-sha256.json。原结果也原地保留。已知sandbox socket EPERM，不重复尝试浏览器网络。

- v2独立运行副本stage-a/v2/runtime/已建立，原m7-work/runtime恢复为v1并保持其历史freeze有效；v2所有脚本/输出/新freeze独立，原scripts/results不改。
- 完整读取v1报告、comparison、72样本raw perf、4份diagnostic，分析落盘v2/offline/v1-analysis.json。定位：v1legacy外城最大debt在约979帧且cold内城497帧反复慢；已有诊断漏计Region.draw主体/Observer/Canvas等，不把所有回退归为FPS噪声或已确定GC。
- 未改WASM的离线原生结构回放发现497等问题帧无对白UI；497帧69个恢复行变体仅21种palette，977帧94变体仅6种palette。v2在原生逐行验证后按完整32项seen映射（含未观测-1）复用源快照内变体，64项有界；identity plates按已认证source runs合并相邻矩形，复杂run/非identity仍走精确viewport。
- 9类RGBA oracle13271040字节、80组恢复palette/3种原生拒绝条件通过；2110个实际WASM原生帧与pre-fix M7完整source选择、行palette及metadata完全相同。非Chromium/非perf验收，不冒称改善。准备12样本小probe与完整442/31396/72样本复测，定义/阈值不变。

- v2候选/脚本冻结完成：364文件SHA检查及244文件v1历史保全检查通过，freeze SHA256 ff573a9166aa07527e66d80319ae735be86072f537baf276d792f5c1fee64eed。REQUEST_READY写STAGE_A_STATUS.md；精确命令SUPERVISOR_RUN_STAGE_A_V2.md（当前总入口文档指向v2）。先12样本6分钟以上probe，共享同一个measure()无定义变化；需要时扩大诊断，最终完整442/31396/72仍必需。候选尚无浏览器/性能改善结论，等待监督复测。

## Supervisor resume — 2026-11-11 13:27 CST (Asia/Hong_Kong)
- 已读取 m7-work/progress.md、STAGE_A_STATUS.md、SUPERVISOR_RUN_STAGE_A_V2.md、m8-work/progress.md 与 CODEX_M7_FIX_M8_BRIEF.md。
- 确认 127.0.0.1:38811（cockpit-tools pid 494245）与 127.0.0.1:8765（python3 pid 505785，服务项目根）仍在监听。未改服务、未杀进程。
- 已在跑的 12 样本探针未中断、未重启：PID 621968 bash m7-work/stage-a/v2/scripts/run.sh probe，node 622074，结果目录 m7-work/stage-a/v2/results/probe-supervised/。环境含 SUPERVISOR_CONFIRMED_EXCLUSIVE=1、STAGE_A_PROBE_REPEATS=2。
- Stage A v1 仍为 REJECTED；v2 候选冻结未验收；Stage B/M8 未开始。监督等待探针结束后再决定是否开完整验收。

## Stage A v2 probe finished — REJECTED at probe gate — 2026-11-11 13:34 CST (Asia/Hong_Kong)
- 已等待原 PID 621968/622074 的 12 样本探针自然结束，未杀、未重启。`V2_probe_EXIT_2`。结果保留在 m7-work/stage-a/v2/results/probe-supervised/，含 REPORT_PROBE_zh.md、report.json 与 12 个 raw 样本。
- 未启动完整 442/31396/72 验收：探针在 v1 已失败的 cold 内城 switchFrameMax 上相对 M5.2 仍有实质回退，按 SUPERVISOR_RUN_STAGE_A_V2.md 先交 Codex 迭代，不花时间跑 72 样本。
- 官方 v1（72 样本）对照：legacy 00-12 maxDebt 均值 163.504ms vs M5.2 40.243ms；cold 00-17 switchFrameMax 均值 31.000ms vs M5.2 13.067ms。
- 本次探针关键数字（同 measure()，无定义变化）：
  - 干净的 cold/00-17/v2/r2：switchFrameMax 30.9ms vs 同期 M5.2 r1/r2 的 11.6/12.2ms（配对 +18.7ms）。尖峰在第 412 帧，render 30.2ms，地图仍是 00-17，切图窗 390–510。第 497 帧 16.4ms（好于 v1 的 14.9/20.9，仍差于 M5.2 约 5ms）。
  - cold/00-17/v2/r1：switchFrameMax 172ms（第 408 帧），maxDebt 2106ms，早期第 119/128 帧也有 51.7/139.4ms，可能含机器干扰。
  - legacy/00-12 干净样本债务看起来有改善（v2 r1/r2：16.733/42.242，对比官方 v1 163.504），但不足以接受。
  - 干扰样本，不作单侧证明：legacy/00-12/m52/r2 FPS 42.211、maxDebt 21480ms。
- 各路线结束 state/framebuffer SHA 在 m52/v1/v2 之间一致，不能代替 442/31396。
- 详细帧级分析：m7-work/stage-a/v2/results/probe-supervised/SUPERVISOR_PROBE_ANALYSIS.md。
- 38811 与 8765（项目根）仍在监听。监督不手写渲染代码，准备启动 Codex 做隔离 v3 迭代，测量定义保持不变。Stage B/M8 仍等待 Stage A 接受。

## Codex v3 launched — 2026-11-11 13:34 CST (Asia/Hong_Kong)
- 已用现有 Cockpit 路由启动 `codex exec`（approval never，sandbox workspace-write，reasoning high）。PID 629753 / 子进程 629761，session 01a1c91a-1dfb-7d12-a171-ae2227eeb00b。
- 日志：m7-work/codex-stage-a-v3.log；末条输出：m7-work/codex-stage-a-v3-last.txt；任务书：m7-work/CODEX_STAGE_A_V3_PROMPT.txt。
- 监督不手写渲染代码，等待 v3 冻结/REQUEST_READY 后再跑新探针。38811 与 8765 保持原样。

## Stage A v3 开始 — 2026-11-11T05:36:43.243801+00:00
- v2 12样本probe明确拒绝，未启动full/M8。已逐文件复制全部v2 runtime、scripts、freeze、offline、所有probe/results及监督分析到stage-a/versions/v2/，132文件SHA256保全。原v1/v2/runtime及历史证据不编辑。
- v3独立runtime/scripts/results/offline已建立；只做Stage A。已知sandbox socket EPERM，不尝试浏览器/网络/安装；保留8765服务，监督外层检查38811，失败记录BLOCKER并停止。
- 独立调查cold 408–412帧与497帧，区分原生证据匹配、矩形/Canvas提交、palette描述符/内存分配及外围render成本；不把hitch或单一palette假说当结论。

- v3已读取全部12份v2 raw sample、官方v1 comparison及72样本/4份旧诊断，生成v3/offline/probe-analysis.json与v1-analysis.json。原生结构显示cold412首次引入96个恢复行、仅6种palette且所选fit全identity；497为非identity、69行/21palette。只能支持路径区分，不能确认为GC/JIT/Canvas根因。
- v3实现：identity矩形改用固定typed-array计划，取消每帧288个Map及矩形对象分配；恢复palette仍逐行执行全部证据检查，完整32项映射用数字hash+逐项精确比较缓存（碰撞只miss），保留64项有界；非identity按认证连续run遍历RGBA/LUT，移除每像素引用和4×4嵌套层。ROM/Observer/时钟/输入/窗口/coverage代码未改。首轮9类13271040字节oracle与80组恢复映射通过，继续扩大实际原生路线验证，尚无浏览器/perf改善声明。

- v3扩大验证通过：4路线×legacy/cold各1792原生帧（含载档/旧预热共14584帧）与pre-fix M7 sources/恢复palette/metadata逐帧相同；另80个实际原生选择帧在合成美术texels/真实地图尺寸上paint输出117964800字节相同。不是Chromium实际美术/性能验收。
- v3冻结：546文件，freeze SHA256 49d5840720f3174f78556441b7c0f6aeef02b8ca62bc54374be2199937120cf7；16类软件RGBA共23592960字节、80组palette、3种证据拒绝/hash碰撞精确核验/工作区复用/startup零core访问通过。v1 244/v2 132历史文件与原件再次核验，perf/qa/visual与v2逐字节相同。
- REQUEST_READY：新命令m7-work/SUPERVISOR_RUN_STAGE_A_V3.md，中文候选报告stage-a/v3/REPORT_STAGE_A_V3_zh.md。先12样本同measure probe；仍有实质回退则保留交回修订，不启动full。可选诊断加入同期v2及408/412/497 focus/native map/heap/CPU profile。最终仍需442/31396/72及监督明确接受；v3未声称性能改善，M8未开始。旧V2命令及所有历史结果未改，无网络重试/环境安装/认证路由变更/视频/ZIP/美术。

## Supervisor v3 probe started — 2026-11-11 13:52 CST (Asia/Hong_Kong)
- Codex v3 已结束并 REQUEST_READY。冻结 SHA256 复核为 49d5840720f3174f78556441b7c0f6aeef02b8ca62bc54374be2199937120cf7，与 SUPERVISOR_RUN_STAGE_A_V3.md 一致。离线 546 文件 / 14584 原生帧结构 / 16 类 RGBA oracle 已由候选报告记录，不能代替浏览器验收。
- 已确认 38811、8765 仍服务 /workspace/shawu 项目根，exclusive.lock 无占用，无并发 QA/Codex。未改或替换 HTTP 服务。
- 已按文档启动全新目录 12 样本探针：STAGE_A_RESULTS=/workspace/shawu/m7-work/stage-a/v3/results/probe-20261111T055247Z，STAGE_A_PROBE_REPEATS=2，SUPERVISOR_CONFIRMED_EXCLUSIVE=1。PID 659402 bash run.sh probe，node 659541 probe.cjs。不并行诊断或 full。
- 接受标准不变：需相对 M5.2 无实质回退，且改善 v1/v2 已失败的 cold 00-17 switch tail；同时确认 legacy 00-12 maxDebt 改善未丢失。若探针仍有实质回退，不启动 72 样本。

## Stage A v3 probe finished — starting full acceptance — 2026-11-11 14:02 CST (Asia/Hong_Kong)
- 探针自然结束，`V3_probe_EXIT_2`（无容差配对仍会列回退）。结果：m7-work/stage-a/v3/results/probe-20261111T055247Z/。分析见该目录 SUPERVISOR_PROBE_ANALYSIS.md。
- 相对被拒绝的 v1/v2，切图尾延迟和债务看起来有改善，因此启动完整 442/31396/72 验收，而不是在此停止：
  - cold 00-17 switchFrameMax：v3 均值 17.4ms（16.0/18.8）对同期 M5.2 11.95ms（11.8/12.1），官方 v1 31.000、v2 干净样本 30.9。v2 第 412 帧 30.2ms 尖峰已消失（v3 为 3.3/4.9ms）。剩余尖峰回到第 497 帧（16.0/18.8 vs M5.2 约 5ms、v1 25.3/16.6）。
  - legacy 00-12 maxDebt：v3 均值 39.33ms，对同期 M5.2 38.92、官方 v1 163.504，债务改善保留。v3 r1 切图窗内第 543/516 帧有 37.5/33.6ms，r2 同帧仅 13.0/12.1；是否稳定回退交给 72 样本判断。
- 探针不是最终验收。完整验收将用全新目录，不并行诊断。接受仍要求相对 M5.2 无实质回退且切图尾延迟改善，以及 442/31396/覆盖完全一致。
- 机器上另有其他桌面 Chrome（Fork-4/Fork-6），与以往正式验收环境类似，未结束他人浏览器会话。38811 与 8765 项目根保持不变。

## Supervisor continuation — 2026-11-11 01:18:14 EST
- 已接手原PID680299 v3 full验收；没有杀进程、重启或并行重任务。442/442 state/native/actor-text、31396帧HD与coverage完全一致已落盘；正在原任务内顺序跑72独占样本，性能尚未验收。Stage B仍等待。

- 01:45:59 EST：原v3 full仍顺序运行，已有47个左右样本，未并行重任务/改候选。442/31396及coverage零差异保持；等最终报告后判定。

## Stage A v3 full complete — v4 final bounded iteration — 2026-11-11 02:01:56 EST
- 原PID680299自然结束；442/442三项、31396帧HD/coverage完全一致；72样本已齐。
- v3尚不接受：legacy00-17切图max均值21.467ms（17.9–24.5）vs同期M5.2 12.6；cold00-17 16.933vs13.8。legacy00-12债务已改善27.058vs65.326，平均FPS正常。证据full-20261111T060217Z不改。
- 交同一Codex做最后一次隔离v4；测量定义不改。若仅剩约20ms以内小尾延迟且fps/debt与M5.2相当，届时可明确披露near-parity接受，不无限循环。M8仍未开始。

## Final bounded Stage A v4 开始 — 2026-11-11T07:04:02.708346+00:00
- 监督确认v3 full自然结束且无并发QA；442/31396/coverage全相同，但cold00-17 switch max16.933ms vs13.8ms、legacy00-17 21.467ms vs12.6ms仍未接受。legacy00-12 debt27.058ms vs M5.2 65.326ms改善保留。
- 编辑前完整保存v3 runtime/scripts/freeze/offline及所有probe/full/raw/results到stage-a/versions/v3/，270文件SHA保全；原v3不编辑，v4独立runtime/scripts/offline/results。只做这一次有界v4，不启动M8/美术/视频/ZIP。已知socket EPERM，不尝试browser/network/install、不读凭据配置。
- 严格比较阈值/measure/路线/窗口/分母不改；v4后若仅小幅约<=20ms切图尾残差且fps/debt/全部正确性接近M5.2，是否以NEAR-PARITY接受由监督决定，必须披露所有严格失败，不能自动改写为全通过。

- 2026-11-11 02:08:04 EST：中断后接续确认v4同一Codex PID770379仍运行，不重复启动；38811与8765正常。v3 full已完成而非仍在跑；v4有界迭代未验收，M8继续等待。

- 2026-11-11 02:21:57 EST：v4同一Codex仍在调查，已输出v3-full-analysis/native-path-trace；尚无冻结/REQUEST_READY。未重复启动任务，38811正常，M8尚未启动。

### v4 路径归因与有界方案 — 2026-11-11T07:36:51.877986+00:00
- 读取v3完整72raw/comparison，保留所有worst frame/debt/严格失败到v4/offline/v3-full-analysis.json。cold00-17三次max均在497，legacy三次为497/498/497；同期m7明确是pre-fix M7，不是v1。
- 发现旧结构oracle强制每帧Region.draw，未模拟Renderer.prepareFlat跳过Region的调用门控；其497 palette归因不代表外层路径。加入与原prepareFlat相同门控后，497的Region为21次locate、257次agreement、无prepareGeometry/recover/paint，返回null后由原fallback处理；与旧浏览器诊断的21次locate吻合。两种离线trace均保留，不以Node计时宣称Chromium性能改善。
- v4只优化camera候选准备：同一不可变Observer快照复用原cell列表；稳定top8 anchors保持原排序与同权顺序；错误cell数已使>=.85数学上不可能时提前拒绝，所有可接受origin仍完整评分。v3整套paint/recover/history/coverage逐字节保留，无core预跑/素材变动。CPU离线任务使用既有exclusive.lock，不与监督QA并行。

### v4 验证进展 — 2026-11-11T07:51:30.328095+00:00
- 65341组完整整数score/denominator门槛、1083组实际agreement（包含前/后/混排不匹配）、128组稳定anchor tie-order oracle全部通过；同snapshot列表复用与载档新snapshot独立通过。16类RGBA共23592960字节及80组恢复palette/3拒绝/碰撞/启动零core访问仍通过。
- 扩大原生结构oracle同时跑强制Region与原prepareFlat门控两种调用序列，逐帧对照pre-fix M7；只作离线正确性验证，不代替浏览器442/31396/perf。仍在exclusive.lock内，未运行浏览器/Profiler或网络。
- v4 probe只调整样本选择：加入原有legacy00-17路线，同期M5.2/v3/v4各2次，共18样本；measure/指标/阈值保持原件。原完整QA/visual/perf脚本和冻结routes逐字节不变；full仍M5.2/pre-fix M7/v4 72样本。监督手动NEAR-PARITY政策不进入严格比较计算。

### v4 离线完成/冻结前复核 — 2026-11-11T07:54:21.109775+00:00
- 两种Region调用门控共29168个真实WASM帧与pre-fix M7 sources/palette/metadata相同；157个真实native选择的合成texel绘制oracle共231505920字节相同。旧16类RGBA/80palette/3拒绝继续通过；不代表Chromium实际美术/性能通过。
- 冻结前保护检查一度把summarize报告中的v3→v4证据路径识别为逻辑变化；已保留失败预检manifest/log/check/script到v4/freeze-history/preflight-report-path-guard/，只修正路径规范化保护规则，runtime未改、测量/阈值未改。最终freeze另行生成，不覆盖任何已发布或历史v3冻结文件。

### v4 final freeze / REQUEST_READY — 2026-11-11T07:58:11.141431+00:00
- 最终638文件freeze通过，SHA256 d6553eb1c50fcefb655a38270d55557c72d4a13569602f5b43faeb1683f1b84d；v1/v2/v3保全244/132/270文件及原件相同。全部离线任务结束，未启动外层browser/profiler/perf，不与监督QA竞争。
- 新命令SUPERVISOR_RUN_STAGE_A_V4.md：18样本同measure probe（原路线补legacy00-17，同期M5.2/v3/v4），之后完整442/31396/72（m7为pre-fix M7不是v1）。严格阈值不改、全部失败保留，只有监督可以按新有界政策明确接受NEAR-PARITY并披露残差；当前仍未接受，不自动下一轮或M8。
- 候选报告stage-a/v4/REPORT_STAGE_A_V4_zh.md；runtime/scripts/freeze/results全部隔离，v3原件未动，无network/install/config/credentials、ZIP/art/video。

- 2026-11-11 02:58:47 EST：已将Step1逐项分析/决定写入STAGE_A_STATUS.md。v3正确性全过但legacy00-17 switch max+8.867ms/70.4%，拒绝性能尾；有界v4 REQUEST_READY，外层测试未跑；本次按上级要求先返回Step1决定。M8不冒充已开始。

- 2026-11-11 03:00:42 EST：v4 18样本probe已nohup启动，PID797528；路径见stage-a/v4/PROBE_PATH.txt。未与Codex或其他QA并行。

- 2026-11-11 03:14:40 EST：v4 probe结束，18样本结果保存；现启动唯一nohup full（442/31396/72），目录见stage-a/v4/FULL_PATH.txt。不并行重任务，M8等待最终采用。

- 2026-11-11 03:33:38 EST：v4 full正确性/逐帧视觉阶段已过；PID804949继续唯一72样本性能，原候选冻结不改。

- 2026-11-11 04:09:55 EST：原v4 full仍运行，已约50/72 raw；未停、未重启、未并行。下一步只读最终comparison/REPORT按已授权策略择优采用，不再迭代，然后启动已备M8 brief。

## Stage A final decision — 2026-11-11 04:24:17 EST
- v4 full已完成，全部正确性/视觉/coverage通过但有性能异常；依新授权停止迭代，保守采用v3并披露legacy内城+8.867ms、cold内城+3.133ms切图残差。不是严格全绿。完整理由/表格STAGE_A_FINAL_DECISION_zh.md。开始M8，自然剧情与GPT整图，全部编码继续Codex。
