# M5.1 性能工作记录
已读取原验收进度与四个指定源码。原包独立解压 /tmp/shawu-perf-m5；修复在 /tmp/shawu-perf-fixed。
初查：audit()本身按需调用，但 gap逐像素对象记录默认开启；MapRenderer.faded 对所有候选重复扫描23040像素；Observer每帧重复解码1024格；UI/转场存在同步回读。保留识别和状态机逐帧运行。

## 隔离候选
仅 /tmp/shawu-perf-fixed 与 m5-work/perf-candidate 修改 observer.js/map-renderer.js；web 未修改。
1. Observer：帧内按完整16字节tile数据与属性缓存64像素解码及FNV签名；无跨帧陈旧缓存；背景像素复用解码。
2. MapRenderer：只懒加载实际绘制到的候选调色sheet，避免所有历史/参考候选都调用faded()扫描23040像素；palette pair用无碰撞整数0..63比较替代像素循环内JSON字符串化。
3. 不改模拟时钟、输入、核心步进、逐帧观察或HD转场状态机；没有跳渲染。
构造数据40组Observer输出逐字段严格相等；两文件ES module语法检查通过。这不是全回放验收。

## 环境阻断（2026-11-10）
exec HTTP独立19881/19882监听均被EPERM拒绝；Node REPL独立尝试也被EPERM拒绝。Playwright按指定NODE_PATH/BROWSERS_PATH启动Chromium后，sandbox_host_linux.cc shutdown Operation not permitted，SIGTRAP退出。未接触PID5001/8765。
perf-before.json / perf-after.json明确status=blocked、results=null，未编造ms/fps。已有coverage_browser复用为perf-coverage.cjs，改用19882与单独输出目录，保留原baseline哈希；未运行成功。
ROM/vendor/WASM SHA256原包、隔离候选、web三方一致，见perf-core-sha256.json。原start.bat 411byte已逐字节核对候选保持一致。
尚未完成：真实时间CDP/timings、完整29160帧回放、HD输出逐像素比较、默认audit成本剥离及其验证、接入web、正式M5.1打包与解压smoke test。没有将候选当成已验收发布。

## Phase 2 延续（收到外层真实基线）
外层已成功执行正常rAF：opening story游戏29.2374fps，renderer平均33.0772ms/p95 47.7ms，map平均30.8894ms，observer1.6699ms，core0.4440ms。以此确认为高清渲染热点；不覆盖该基线JSON。已阅读BASELINE_OBSERVATION.md、baseline-live.json并查看50秒截图（原生人物/黑底）；完整视频和3分钟结果外层仍在采集，未声称亲自完整观看视频。
候选继续在/tmp/shawu-perf-fixed更新：默认关闭gap对象统计，?audit=1或setAudit(true)/audit()恢复；保留coverage像素计数与逐帧状态机。UI边框缓存原始栅格化图，逐帧按原生actor/source/tile mask裁切；UI认证和close证据仍逐帧处理，只有严格数组/调色板/原生BG依赖完全相同才复用认证快照。
新增扫描线单行调色代替整sheet调色，tile相同帧内解码缓存、观察对象依赖缓存，原生参考BG取消每像素slice分配，无UI时复用不可变空UI缓冲。Title fade/card的144次全幅putImageData合成一次上传；有效行仍保持原判断；原画缩放参数未改。
app新增setFrameProbe稳定计时API（默认无performance.now调用），rAF保留完整墙钟积欠、每次最多4核心帧避免UI事件饿死，不跳过核心或渲染帧。
perf-realtime.cjs更新6段：title、card、opening story、impact、forest、normal walking；候选使用probe API，只有旧M5使用带兼容断言的响应内文本注入。记录每调用/每游戏帧累计timings和场景、无外网请求、真实墙钟fps及rAF pacing/drop；setup离线回放不计入测量。支持PERF_SEGMENTS/PERF_DURATION_MS减少外层迭代耗时。等待外层实测，不宣称<16ms已实现。
进一步取消UI快照和关闭转场的全画布回读：原生RGBA已由Observer提供，改为在临时native canvas上put一次，然后以imageSmoothingEnabled=false的1:4整数裁切覆盖当前OAM/新文字；原生像素与原4x4复制公式一致。冲击路径增加全依赖精确比对缓存（framebuffer、keys、attrs、indices、actorMask），仅完全相同的合成结果复用；Observer/Map状态机始终先逐帧运行。所有属于候选，须外层逐像素回归验证。

## Phase 2 候选冻结供外层测试
已保存4个候选JS、phase2.diff、manifest与CHANGE_REPORT_zh.md到perf-candidate/。局部检查：Observer 40组通过；行调色32组96行逐字节通过；rAF时间戳停顿恢复/每帧draw检查通过；4文件语法通过；不可变ROM/core/launcher SHA和35资产文件通过。web未改，未生成M5.1包。
外层3分钟录屏结果现已完成：182.94秒、35.37 GBfps、rAF18.01Hz、最长回调1994.5ms。已查看联系图：启动人物→标题→年份card→室内对话，结合时间戳支持渲染长停顿，不能归因于原动画较少的动作帧。录制与profile曾短暂并行，应与最后无录屏顺序对比区分。
新增perf-visual-compare.cjs：同一核心原生帧驱动原/候选，代表性窗口逐像素RGBA及audit对象比较，失败保存原/候选PNG；可PERF_COMPARE_ALL=1全帧。尚未在本受限shell启动浏览器，等待外层执行。
比较器补齐audit开/关的第三实例RGBA对照，每个代表帧必须与audit打开候选逐字节一致，统计defaultModeChecks；未运行浏览器不伪报结果。Phase2标记已写PERF_PHASE2_DONE.txt，候选代码冻结供外层。

最终逐帧重放 1200/29160，全背景覆盖1200帧，状态/原生像素对照10/10；测试进行中。

最终逐帧重放 2400/29160，全背景覆盖2396帧，状态/原生像素对照20/20；测试进行中。

最终逐帧重放 3600/29160，全背景覆盖3596帧，状态/原生像素对照30/30；测试进行中。

最终逐帧重放 4800/29160，全背景覆盖4796帧，状态/原生像素对照40/40；测试进行中。

最终逐帧重放 6000/29160，全背景覆盖5843帧，状态/原生像素对照50/50；测试进行中。

最终逐帧重放 7200/29160，全背景覆盖7024帧，状态/原生像素对照60/60；测试进行中。

最终逐帧重放 8400/29160，全背景覆盖8197帧，状态/原生像素对照70/70；测试进行中。

最终逐帧重放 9600/29160，全背景覆盖9386帧，状态/原生像素对照80/80；测试进行中。

最终逐帧重放 10800/29160，全背景覆盖10583帧，状态/原生像素对照90/90；测试进行中。

最终逐帧重放 12000/29160，全背景覆盖11769帧，状态/原生像素对照100/100；测试进行中。

最终逐帧重放 13200/29160，全背景覆盖12954帧，状态/原生像素对照110/110；测试进行中。

最终逐帧重放 14400/29160，全背景覆盖14152帧，状态/原生像素对照120/120；测试进行中。

最终逐帧重放 15600/29160，全背景覆盖15352帧，状态/原生像素对照130/130；测试进行中。

最终逐帧重放 16800/29160，全背景覆盖16552帧，状态/原生像素对照140/140；测试进行中。

最终逐帧重放 18000/29160，全背景覆盖17752帧，状态/原生像素对照150/150；测试进行中。

最终逐帧重放 19200/29160，全背景覆盖18950帧，状态/原生像素对照160/160；测试进行中。

最终逐帧重放 20400/29160，全背景覆盖20150帧，状态/原生像素对照170/170；测试进行中。

最终逐帧重放 21600/29160，全背景覆盖21336帧，状态/原生像素对照180/180；测试进行中。

最终逐帧重放 22800/29160，全背景覆盖22536帧，状态/原生像素对照190/190；测试进行中。

最终逐帧重放 24000/29160，全背景覆盖23623帧，状态/原生像素对照200/200；测试进行中。

最终逐帧重放 25200/29160，全背景覆盖24768帧，状态/原生像素对照210/210；测试进行中。

最终逐帧重放 26400/29160，全背景覆盖25954帧，状态/原生像素对照220/220；测试进行中。

最终逐帧重放 27600/29160，全背景覆盖27135帧，状态/原生像素对照230/230；测试进行中。

最终逐帧重放 28800/29160，全背景覆盖28320帧，状态/原生像素对照240/240；测试进行中。

## 外层完整验收与最终实测
冻结候选 /tmp/shawu-perf-release-candidate 全29160帧通过；243/243 state/native framebuffer/actor-text检查，覆盖28669帧，471663068/471723583像素，全部与M5精确相同。
顺序真实time6段见perf/comparison-final.json；opening渲染38.78→8.54ms/p9555.9→16.3，impact60.50→10.22/p95337.8→34.5，forest22.27→8.06/p9549.9→14.4；每段GBfps59.58（12秒首帧同步开销）。
从boot连续3min修复后录制perf/after/baseline-observation.json：总体58.81GBfps/rAF50.65，最长408ms；对话段稳定59.7，最后card-heaven段170→180秒43.43fps形成欠债。整帧card仍先maps.draw再覆盖，可能保留昂贵cliff历史无谓合成；须进一步优化被完整覆盖的特殊plate而不丢history。不能声称所有过场零卡顿。

## 发布收口
M5.1采用已通过完整29160帧的冻结phase2四文件，未接入phase3探索性改动。附加HD逐字节等价调查耗时较长且不影响已通过的native/coverage验收，已停止；frame246一行小幅重绘背景色值差异尚未彻底解释，不宣称HD逐字节恒等。原生角色/文字/ROM/framebuffer严格检查均通过。
已打包shuihu-hd-m5.1-windows.zip 13903445字节，干净解压离线360帧smoke通过，GBK launcher/core逐字节不变。最终真实time数据和3min前后视频均保留；仍有少量字幕/转场峰值停顿，不能声称全程零掉帧或Windows实机已验证。

# M5.2：继续消除字幕/转场峰值
已冻结M5.1并解压隔离候选；目标启动预热、缓冲复用及余下峰值，保持所有core/coverage约束。

M5.2外层新增基线热点实测：perf/m52/m51-peaks.json（heaven-card/exit真实rAF12sec）。最大98ms由map96ms，其中fadedRow60ms+readback23ms；palace首帧82.9ms，faded57.6ms；card73ms中map38ms+card33ms。说明残留不只是首次图片decode，动态调色全图与行缓存物化仍在帧内重活。某些card后frame11080/11081/11240的faded峰值44–57ms。

## M5.2 首个隔离可测候选已准备
仅修改 /tmp/shawu-m52/shuihu-hd-m5.1 的 app/renderer/map-renderer/index，新增 asset-loader 和 tools；正式 web 与两个冻结目录未改。并发 decode、启动预缩放、LUT 调色、card 按行背景合成和缓冲复用已落地。完整卡片遮挡路径仍执行逐 native observer / source / coverage / rasterUI / history，只在严格无 UI 且底图 alpha 实证为255时免地图像素写入。rAF 保留完整欠债并增加追赶耗时预算。
本地单元通过：调色字节、decode 等待、全/部分卡/OAM、连续观察历史等价与 UI/opacity guards、零 core warmup。assets/vendor/start.bat 41 项 SHA 与冻结 M5.1 一致，observer 字节不变。Chromium/listen 按已知 sandbox 限制未尝试；不冒充性能/光栅验收。
可交给外层：perf/m52/CANDIDATE_READY.txt、CHANGES.md，候选 tools 下 pixel-source-m52（frame246 实际图集上传前后／缓存源像素）、完整 coverage-m52 / visual-m52 / boot3min realtime-m52。frame246 尚待实际 browser 诊断；完整29160和3min零>50ms均未宣称完成。未打正式包、未接入 web。

实际browser排查新增：pixel-draw-diagnostic.json显示原M5在y468画三段（192宽调色9,26,35 +384宽原色+64宽调色），M5.1只画整行原色2,21,29。faded返回的缓存canvas本身颜色正确；不是图集fit问题。
pixel-observer-diagnostic.json显示palettes/cellKeys/tiles/attrs/mask/actorMask/bg/indices全部相等，但mapResult rasterMismatchPixels分别3979 vs3926、rasterRecovered5152 vs5088。
pixel-history-diagnostic.json显示frame235到246所有历史key/bg/mask/rasterUI hash亦完全一致。因此怀疑对照harness共享WASM顺序a.draw;b.draw，原Observer的read_mem触发了延迟PPU更新，使b拿到不同p！正在pixel-input-diagnostic.cjs记录两Observer.sample(p)输入差异。若成立，这是对照工具不公平，不是M5.1作者背景调色代码错误。不要追无目标的缓存bug。

关键突破：M5.1单行HD差异已定位为对照工具伪差异！两renderer共享WASM顺序绘制时，原生RGBA输入在同一tick间发生143字节延迟PPU更新（行117）。见perf/m52/pixel-input-diagnostic.json。将对比工具改为每native帧先冻结同一份输入，再并列绘制验证；生产图集无需猜着改色。
候选收口补充：启动提前分配 card/late-impact 画布与 ImageData；每图复制后单独 readback，地图用一组 synthetic fit 预热 LUT/上传（不跑 core、不污染呈现 cache）。合成时钟单元另验证 200ms 积欠分批追赶不丢步且可排空。全部候选 JS/tool 语法通过；可重复 invariants-m52 工具再次确认41项同时对M5/M5.1 SHA、正式四JS冻结和 observer不变。真实浏览器门禁仍待外层，准备标记不代表通过。

公平输入对照已通过！M5.1 vs M5前730帧：730帧RGBA逐字节一致、audit metadata一致、default/audit显示一致，errors0。见m51-fair-pixel-comparison.json。旧frame246差异仅由共享WASM顺序读取native framebuffer不同造成，无需生产改色。

M5.2第一次独占180秒无录屏实测未达门禁：59.6133fps，累计欠约20.6帧，max rAF gap387.4ms、callback176.5ms，84条>50ms事件（不同类型会重复记录同次卡顿）。主要长帧在boot flat/intertitle（1266=176ms、2171=104ms）、cliff9023=111ms；不是只剩heaven卡。phase1冻结/tmp/shawu-m52-phase1，继续压实plate全屏遮挡优化与缓冲GC。旧单行差异已用公平730帧逐字节对照证实是测试伪差异，生产无需改色。

M5.2 phase1 的公平730帧M5原版对照通过（RGBA、audit元数据、default/audit画面均730/730）。额外80秒CPU/Timeline诊断（仅定位，不当性能验收）：主要持续成本是MapRenderer.draw/eq与Observer.sample；确有MajorGC约51ms、MinorGC40ms、mark启动59ms，first-UI全图recolor/readback/upload约125ms。若干100–159ms长帧只落在单个CPU profiler采样间隔，不能武断全归因GC或图像解码。证据保留perf/m52/phase1-trace/（trace-summary、stall-attribution、原始trace/profile）；phase2正在以8行小条带替代整张1024图集染色/上传并复用安全临时缓冲，不更换艺术素材。

## M5.2 phase2 实施中（phase1 冻结不动）
已核对 realtime-first：global1266 的176ms渲染与约178ms browser long task对应，因此不是单纯回调之间的gap；当前报告无法拆分GC/Canvas等待/业务CPU，外层trace入口将进一步区分。承认phase1独占3min未达门禁，不以batch预算修饰singleFrame峰值。
已落地第二阶段代码：uniform flat与验证成功的impact先在私有画布准备，再与完整card共用安全occlusion钩子；仍保留map candidates/source/coverage/rasterUI/history/UI状态计算。plate改字节LUT并预热32个中性CGB色阶，动态颜色采用16项LRU逐项回收，不全清缓存。地图动态调色改8-native行strip物化（scanline仍4HD行），只上传使用的带区，row/strip画布立即消费后可LRU复用。UI认证画布/native/键数组和close修补nativeCanvas复用；map当帧sources/coverage、每anchor扫描线scratch、card验证双槽复用。Observer仅复用未返回的bus/VRAM临时数组并移除未使用boxes；保留全部返回快照独立分配，避免WeakMap陈旧键问题。
公平HD比较脚本已改每帧固定p给A/B/C；不改生产色值修复旧伪差异。现有单元通过，正在补实际WASM无浏览器依赖/逐快照一致性测试和GC trace采集脚本。还没有phase2真实浏览器性能/像素结果。

phase2单测通过后冻结/tmp/shawu-m52-release-candidate做最终全量QA：新增8行图集条带替代全图palette upload、32级常用转场底图启动预热与有界LRU、UI native/snapshot复用、回收已退出6帧历史的UIBG；Observer仅sample-local VRAM/OAM临时缓冲与精确地址key（不缓存跨帧VRAM）。早期浏览器发现typedRGB.map产生0的bug，已修为Array.from并单测；早期QA因随后代码更新主动作废，最终要从0重放29160。

phase2公平RGBA确实发现新调色回归（不是原117行伪差异）：frame266柜子青蓝变品红。已定位旧M5的RGB-only全图调色FIFO key会跨palette索引别名；拆条带后若每band各自“首次fit”就改变了既有颜色。/tmp/shawu-m52-palette-fix增加轻量全图fit FIFO（8项），沿用每帧candidate/variant首次fit语义，再只上传所需条带；不会重做大图。修复后公平730帧RGB/audit/default全等。继续多场景和最终全重放。

## M5.2 接续验收
已完整读取进度；保留 PID307427/308017，两项仍正常推进（后段公平对比840帧无差异，coverage5880/29160、49/49 hash，无错误）。候选仍为 /tmp/shawu-m52-palette-fix，不修改冻结目录。等待两项结束后再独占180秒无录屏实测，随后独占录屏；不打包。

后段公平逐像素对照完成：1690/1690 RGBA、audit元数据、默认/audit画面全等，errors0（m52-palette-fixed-later.json）。加先前730帧共2420抽样帧，不冒充29160帧全部HD逐像素比较。coverage推进13920/29160、116/116 state/native hash/actor检查，无错误。

调色修复候选全29160帧验收完成：243/243 state/native framebuffer/actor-text检查，覆盖28669帧、471663068/471723583像素，与M5一致，errors0。两项旧进程自然完成，开始独占180秒无录屏真实rAF性能测试。

独占无录屏180秒测试已以nohup启动，日志 perf/m52/realtime-palette-fixed.log；不同时运行coverage、对照、ffmpeg或其他性能测试。

独占180秒无录屏实测完成：59.72094fps，欠1.18帧，render均6.95ms/p95 11.5ms；仍有25次rAF gap>50ms，最长363.8ms，16次native帧>50ms、最长166.6ms（总57条为同次不同类型重复计数）。严格零>50ms门禁未过。已另复制/tmp/shawu-m52-spike-reduction做一次小步降峰；公平/完整验收通过的palette-fix保持不动。

## M5.2 小步降峰候选（2026-11-11）
仅 /tmp/shawu-m52-spike-reduction/map-renderer.js 修改生产代码：dialogue 原图 readback 提前到现有启动 warmup，保留不可变源像素；palette miss 用私有 ImageData scratch + 同等字节 LUT，避免反复全图 draw/readback/分配与逐像素浮点运算。未动 RGB-only first-fit per-variant FIFO 修复、source sampling、Observer、history、core/render 步数或时钟。uiArt 原 roundtrip 保留。依据 phase1 first-UI trace；不声称已解释 frame3689 或所有 gap。
新增 tools/dialogue-spike-unit.cjs 通过65调色/全字节/alpha/缓存独立性/单次启动readback检查；既有 m52-unit 与41项 invariants/正式web冻结、语法均通过。实际本机 WASM native-contract 通过4153 sample、3673 metadata/history、250 occluded、432 certified UI与保留快照不可变检查。生成候选根目录 invariants-spike.json/native-contract-spike.json。Canvas stub不冒充HD或性能验收。
原 palette-fix 冻结源未修改，既有2420公平与29160完整验收仍归原候选；新改动浏览器等价及覆盖尚待外层。结果与“仅独占录屏”命令在 perf/m52/spike-reduction-result.md；未在sandbox启动浏览器、未生成视频、未新增无录屏benchmark、未打包/接web。

Codex小步降峰已完成，仅map-renderer.js对话图集解码/readback移至启动，后续palette miss用等价LUT+私有scratch；本地单元/4153样本WASM契约通过。外层已nohup同时启动公平前730、多场景1690和完整29160 correctness重验（日志 visual-spike-first/later、coverage-spike-reduction）；此阶段不是性能测试。测完才独占重测真实rAF。

小步对话图集候选公平浏览器对照通过：前730+后1690，共2420代表帧RGBA、audit metadata、default/audit显示全等，errors0。完整coverage推进16680/29160、139/139 state/native/actor检查，无错误。

小步候选完整29160浏览器回放通过：243/243 state/native framebuffer/actor-text，覆盖28669帧、471663068/471723583像素与M5完全一致，errors0；前后2420代表帧HD RGBA亦全等。开始独占180秒无录屏性能重测，之后录屏。

小步降峰后独占180秒无录屏重测：59.72122fps，欠1.13帧，native均7.64ms/p95 12.1ms，render均7.17ms/p95 11.5ms；首UI3689峰从166.6降至51.1ms，但最大native仍159.4ms，rAF gap最大278.9ms、>50ms22次（native>50ms14次、callback>50ms15次，不能加总为独立停顿）。严格零>50ms未达到；不宣称彻底无卡顿。现在停止改动，独占录制180秒正常速度开场，保留真实停顿，不剪辑加速。

首轮960x900录屏出现异常104.4秒同步长帧（global7809），总275秒、44.83fps，raw67MB，不能作为正常3分钟录屏交付；原始数据完整保留在recording-spike-reduction。不把该长帧删除、也不拿无录屏数据冒充录屏表现。无录屏完整180秒无此异常。仅测试录制尺寸改为640x600（和M5.1预览相同构图/尺寸），仍原960x900页面和同一生产JS，降低录屏编码开销，独占重新录制；不修改游戏时序/素材。异常原因未定位，不武断归因编码器。

640x600独占录屏完成，180.15秒正常播放59.72129fps、欠1.12帧、rAF最大157.5ms、>50ms27次；native最大154.8ms、>50ms14次。raw视频21,780,624字节，可直接满足25MB。无错误/外网请求。与M5.1旧960x900录屏不能当严格A/B；额外独占补跑M5.1同样640x600录屏作公平before比较，未更改旧生产代码；只测试脚本允许M5.1 header、缺少可选rAF probe。
