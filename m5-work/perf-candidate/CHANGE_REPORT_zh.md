# Phase 2 候选变更（待外层验收）

运行目录 `/tmp/shawu-perf-fixed`；本目录四个 JS 为相同字节副本。web 未接入，没有打包发布。manifest.json 对照不可变 perf-package-baseline.json，ROM/core/411byte launcher 均一致，35个资产文件均未改变。

外层基线已确认：opening story 29.2374 GBfps，renderer 平均33.0772ms/p95 47.7ms，map平均30.8894ms，observer1.6699ms，core0.4440ms。3分钟正常rAF录屏182.94秒，35.37 GBfps；最长回调约1.995秒。该录屏存在录制和短暂并行profile开销，用于复现，不与最终无录屏顺序测量直接算加速比。已阅读外层观察报告，并实际查看50秒截图和每15秒联系图，未声称完整观看webm。

## 优化与精确依赖

- Observer：帧内按完整16字节tile与属性缓存64像素解码、FNV signature，背景使用同一解码结果；无跨帧哈希推测，VRAM/OAM验证继续逐帧只读运行。
- MapRenderer：只在可见绘制run实际使用时生成候选调色sheet；用0..63编码代替像素循环里的palette pair JSON序列化。
- used-palettes：按不可变mask、attrs数组身份及scroll缓存使用集合；palette/attrs/cellKeys字符串对不可变数组缓存。背景参考解码直接复制RGBA通道，消除65536次slice/set小对象。
- 扫描线恢复：仍逐行、逐像素验证palette/index→RGB精确对应；临时RGB三元数组改为24位整数。对于rowPalettes仅对实际源行4个HD像素行做相同调色拟合、clamp及Uint8Clamped rounding，避免整张sheet逐行重算。缓存最多96行/地图。
- dialogue：原九宫格绘制参数、原图与栅格化结果不变，首次保留原get/put roundtrip。缓存由完整调色板6及所有矩形几何确定；每帧继续检查当前actor/source/tile mask，按整数区域裁切，移除每帧整屏getImageData/透明RGBA复制/putImageData。缓存最多8项。
- UI快照：认证、coherent验证、关闭progress/证据仍逐帧运行；仅在map、rect、完整keys/attrs/tiles/palettes和矩形内native BG每个字节全部一致、且非active时复用快照，更新认证ticks。不按帧数或计时器跳过状态机。
- UI OAM/新文字修补：使用已有原生RGBA在160x144临时canvas中put，再按1:4整数裁切覆盖；imageSmoothingEnabled=false，等同原4x4原生像素复制，不回读整张640x576画布。
- 没有native UI时复用不可变-1 sentinel缓冲，避免每帧创建1MB Int16Array；有效UI历史仍完整保存。
- title fade/card：原行验证和调色公式保持不变，互不相交行的变换先完成，再一次全幅putImageData。只绘制有效行；card背景plate先绘制与原相同的行。源图相同缩放栅格化结果只读缓存，不改变缩放参数或素材。
- impact：精确比较framebuffer、cellKeys、attrs、indices、actorMask，且scroll=0/无dialogue，才复用已合成的完整冲击帧；否则运行原路径。Observer/Map始终先运行，因此不吞转场或跳核心帧。
- audit：生产默认不创建gap Map/缺口对象，不重复统计诊断用raster mismatch。`?audit=1` 或 `shuihu.setAudit(true)` 恢复全量统计；`shuihu.audit()`首次调用会开启审计并重绘当前帧一次，保证当前帧缺口完整。覆盖分母、已覆盖像素计数和UI认证条件始终保留。默认meta中的rasterMismatchPixels为null，审计模式为原计数。
- pacing：移除84ms墙钟截断，欠下的核心帧保留到后续rAF；每回调最多4帧以保留事件响应。每个核心帧仍observe/render，不跳帧。若机器持续慢于59.7275fps，会累积欠账；本改动不能凭空弥补算力不足，需实测确认热点已足够降低。
- `shuihu.setFrameProbe(fn|null)`提供稳定显式低侵入timing；默认关闭时不调用performance.now。debug step(n)行为保持原样：n核心帧、一次draw。

## 已运行的局部检查

- 四个JS的ES module语法检查通过。
- perf-observer-equivalence.cjs：40组构造数据，Observer所有输出字段/数组逐字节与原版相等，含重复调用及VRAM变化。
- perf-row-equivalence.cjs：32组调色、使用集合和flat palette条件，96个源行与原整sheet调色逐字节相等。此为软件像素算术检查，不验证浏览器canvas后端。
- perf-pacing-check.cjs：30秒60Hz模拟时间戳与200ms停顿恢复后核心帧数精确对应70224/4194304秒；停顿回调不超过4帧；每个step仍有一次draw。
- ROM/core/launcher、全部资产校验通过。web仍与M5运行时四文件字节一致。

这些检查不等同于浏览器真实帧率、HD覆盖、243/243 state/framebuffer hashes或角色文字验收。目标render p95<16ms尚未确认。

## 外层执行顺序

请顺序执行、不要与录屏或另一个Chromium性能任务并行。基线不可变，建议新输出文件避免覆盖已有部分结果。

```bash
NODE_PATH=/home/box/opt/test-tools/node_modules PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers node m5-work/perf-realtime.cjs /tmp/shawu-perf-m5/shuihu-hd-m5 19881 m5-work/perf-before-phase2.json
NODE_PATH=/home/box/opt/test-tools/node_modules PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers node m5-work/perf-realtime.cjs /tmp/shawu-perf-fixed 19882 m5-work/perf-after-phase2.json
NODE_PATH=/home/box/opt/test-tools/node_modules PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers node m5-work/perf-visual-compare.cjs
```

perf-realtime包含title、card、opening story、impact、forest、normal walking六段。`PERF_SEGMENTS='opening story,card'`可用于短迭代；`PERF_DURATION_MS=12000`为默认，所有测量区间均为真实requestAnimationFrame/墙钟，step只用于前置状态准备。脚本保留每调用与每游戏帧累计timings（均为包含子调用的嵌套项，不应相加），记录场景分布、实际fps、rAF pacing和60Hz drop估算。title段位于原3300帧标题等待，可能包含剩余title fade；card段由故事offset100开始，12秒内自然跨场景，按scenes识别实际组成。normal walking在完整故事回放后按120游戏帧切换方向，须通过画面确认自由活动已进入、没有被剧情/UI阻塞。

比较器使用同一个核心/原生帧同时驱动原M5和候选renderer，代表窗口每帧比较RGBA与完整audit输出；窗口间仅核心快进并在窗口前180帧重建两边历史。它属于独立确定性验收，不作为性能数据；`PERF_COMPARE_ALL=1`可对全29160帧比较。首次不符会写原图/候选PNG和JSON位置。

全覆盖继续复用perf-coverage.cjs（19882/?audit=1），使用既有M3原生基线；其逐帧coverage和243次状态/原生像素/actor/text检查仍须全部验收。另需无audit模式输出与audit模式一致检查。所有GPU/画布后端的像素一致性以外层实际浏览器结果为准，特别关注半透明边框裁切、UI OAM覆盖和新单行调色。

Linux headless不是Windows Chrome GPU实机，最终报告必须保留此局限。本阶段不接入web、不打包，等待实测反馈后继续修正。

补充：perf-visual-compare.cjs同时运行第三个候选renderer（audit关闭），每个代表帧也检查audit开启/关闭RGBA完全一致，JSON包含defaultModeChecks。
