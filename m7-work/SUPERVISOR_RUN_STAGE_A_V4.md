# Stage A v4 — final bounded iteration / REQUEST_READY

**V4_FROZEN / OFFLINE_PASS / OUTER_PROBE_PENDING / ACCEPTANCE_PENDING。v3尚未接受；不启动M8。**

运行目录：`m7-work/stage-a/v4/runtime/`。冻结：`m7-work/stage-a/v4/freeze-sha256.json`，SHA256 `d6553eb1c50fcefb655a38270d55557c72d4a13569602f5b43faeb1683f1b84d`，638文件。v3完整runtime/scripts/freeze/offline/probe/full/72 raw及当时命令/状态已在编辑前保存到`stage-a/versions/v3/`（270文件SHA清单），原v3仍原位、逐项相同。v1/v2与原m7-work/runtime亦未改。

v4仅优化Region camera候选准备，v3的paint/recover/history/coverage/startup整段不改。发现原结构oracle强制每帧Region.draw；实际Renderer在flat帧跳过Region，随后497发生21次locate/257次agreement并返回null，不能继续把该帧只归因于palette。v4复用同一不可变snapshot的cells、保留稳定top8 anchor顺序、在原>=.85已不可能达到时提前拒绝错误origin。所有可接受origin仍完整原评分；没有放宽匹配、mask或覆盖。剩余fallback/Canvas等成本尚无完整浏览器归因，不能预先保证尾部消除。

本沙箱已知socket EPERM，未重试browser/network/install或读取凭据配置。以下命令仅由**监督外层shell**运行。沿用已有38811代理与8765项目根HTTP服务，不启动或替换它们。入口代理检查失败写BLOCKER并停止；不改认证/路由，不嵌套Codex。

## 0. 确认独占

等待本Codex退出，再检查CPU；不要与其他QA、Profiler、原生重放、录屏或重CPU工作并行。所有模式共享`stage-a/exclusive.lock`；本次离线native检查也用此锁，当前没有后台测试。

```bash
cd /workspace/shawu
ps -eo pid,pcpu,comm --sort=-pcpu | head -n 25
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export SUPERVISOR_CONFIRMED_EXCLUSIVE=1
sha256sum m7-work/stage-a/v4/freeze-sha256.json
```

## 1. 同定义probe：18样本，约9分钟以上

```bash
cd /workspace/shawu
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v4/results/probe-$(date -u +%Y%m%dT%H%M%SZ)"
export STAGE_A_PROBE_REPEATS=2
bash m7-work/stage-a/v4/scripts/run.sh probe
```

只改变probe的case/version选择：原legacy 00-12、cold 00-17之外加入**既有legacy 00-17路线**；同期M5.2/v3/v4各2次，轮换顺序，共18样本。目的是直接观察v3 full两个内城协议的残余尾部，并检查外城debt改善。没有新造路线或修改任何动作。`measure()`仍直接来自与v3逐字节相同的`perf.cjs`；统计函数、startup/loadState、每样本1792原生帧、legacy60 idle预热、cold第1帧输入且前60帧计入、地图ID±60窗口、debt/FPS/p95/max/分母和零事后容差不变。audit off、fresh context，无截图/录像/trace/Profiler。

使用全新绝对目录，不预先mkdir。输出`probe/REPORT_PROBE_zh.md`、`probe/report.json`、18 raw、`probe.log`，以及当次`offline/checks.json`/`offline.log`/`preflight.log`。exit2仍代表严格配对至少一项回退；exit1代表异常。全部失败/噪声/原帧保留，不删除样本、不用平均FPS掩盖tail。

重点读legacy与cold 00-17的switch max与497/498，兼看408/412；legacy 00-12的maxDebt必须保留改善。v3 full参考：cold00-17 mean16.933ms[15.8,19] vs同期M5.2 13.8ms；legacy00-17 mean21.467ms[17.9,24.5] vs12.6ms；legacy00-12 debt27.058ms vs65.326ms。probe的`v3`是候选v3；下节full的`m7`是**pre-fix M7，不是v1/v3**。官方v1 31.000ms cold switch与163.504ms legacy外城debt仍单独保存，不能混用baseline。

probe通过本身不是接受。按本轮有界政策：若只剩小幅tail/严格噪声，可继续完整验收以供最终裁决，不因exit2自动开始下一轮编码；若出现大幅性能恶化、SHA不一致或运行异常，保留证据并交监督处理，不自动迭代v5。不要并行跑diagnostic或其他代码。

## 2. 完整442 / 31396 / 72

```bash
cd /workspace/shawu
unset STAGE_A_PROBE_REPEATS
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v4/results/full-$(date -u +%Y%m%dT%H%M%SZ)"
bash m7-work/stage-a/v4/scripts/run.sh full
```

依次：冻结/历史检查 → 原23分支442 state/native/actor-text（含区域1/2）→ 31,396帧实际HD RGBA/coverage对pre-fix M7逐帧零差异 → 原72样本 → 原严格中文comparison报告。`qa.cjs`、`visual.cjs`、`perf.cjs`与v3/v2逐字节相同；frozen QA/perf route文件和动作未改。summarize仅迁移v4输出/证据路径，严格判定/flags/阈值未改。full仍M5.2/pre-fix M7/v4 ×4路线×legacy/cold×3重复，顺序/机器/定义与v3完全一致。至少36分钟纯perf，另加QA与视觉；让既有进程自然完成，不另开重复任务。

结果：`qa/report.json`、`visual/report.json`/`frames.jsonl`、`perf/report.json`/72 raw、`comparison.json`、`REPORT_STAGE_A_zh.md`及logs。原13图必须仍为`438411621/439578861 = 99.73446403%`，逐图分子/分母/原因不变。任何视觉或覆盖差异立即失败检查，不继续perf，不制作视频或接受视觉改变。不要运行旧verify-final.sh。

## 3. 本轮结束后的监督裁决

**比较计算仍严格，所有回退仍列出，exit2/acceptanceReady=false不改。** 如完整证据只剩约<=20ms的小幅switch max尾部，而总体FPS/debt接近M5.2，442/31396/覆盖全部通过，监督可以按用户新授权明确接受为**NEAR-PARITY**，同时披露协议/地图、均值/范围、相对M5.2残差、所有原始严格flags/机器噪声。此为监督人工裁决，不是脚本把<=20ms改成阈值或自动通过，也不以很慢的M5.2噪声样本掩盖问题。

若尚不满足，由监督记录最终状态和剩余问题；本Codex不自行开启下一轮优化。无论数值如何，M8仍需监督明确接受Stage A后另行指示。所有v1/v2/v3/v4原始失败、freeze及证据保留；无ZIP/art/video。
