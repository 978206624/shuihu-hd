# Stage A v2：先跑12样本小探针，再决定完整复测

**REQUEST_READY。v1明确未接受；只做Stage A。不要运行旧v1入口。**

v2 runtime独立于v1：`m7-work/stage-a/v2/runtime/`；新freeze：`m7-work/stage-a/v2/freeze-sha256.json`，SHA256 `ff573a9166aa07527e66d80319ae735be86072f537baf276d792f5c1fee64eed`。v1所有runtime/freeze/scripts/results完整备份在 `stage-a/versions/v1/`（244文件保全清单），原results亦未修改，原 `m7-work/runtime/`保持v1。

本沙箱已知socket EPERM；没有再尝试浏览器网络。监督确认38811和8765仍正常，以下脚本仅在**外层shell**运行。脚本检查代理，若失败写BLOCKER并停止；不安装环境、不改认证/路由、不启动嵌套Codex。

先检查CPU，停止其他QA/重放/录屏/重CPU工作，不与本Codex离线检查并行跑perf：

```bash
cd /workspace/shawu
ps -eo pid,pcpu,comm --sort=-pcpu | head -n 25
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export SUPERVISOR_CONFIRMED_EXCLUSIVE=1
```

## 第一阶段：小探针，约6分钟以上

```bash
cd /workspace/shawu
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v2/results/probe-$(date -u +%Y%m%dT%H%M%SZ)"
export STAGE_A_PROBE_REPEATS=2
bash m7-work/stage-a/v2/scripts/run.sh probe
```

12样本：legacy外城00-12、cold内城00-17，M5.2/v1/v2各2次，顺序轮换。每样本1792原生帧，legacy仍60空闲预热，cold仍第1帧输入；**直接复用完整perf.cjs的measure()，没有改定义/窗口/分母/容差**。audit off、无录屏截图trace，各样本独立context，保留startup/loadState。

输出 `$STAGE_A_RESULTS/probe/REPORT_PROBE_zh.md`、`probe/report.json`、每样本raw json、`probe.log`。所有指标回退都列出，退出码2表示至少一个严格配对回退；不要据此只看均值或略去失败。重点检查v1已失败的legacy外城debt、cold内城switch p95/max/debt，同时保留其他frame/render/FPS指标。即使小探针改善，也不能宣称Stage A通过。

如果小探针仍有实质回退，保留结果并交Codex继续修订，先不花时间重复完整72样本。可运行下一节诊断；监督只运行脚本，不手改实现。

## 可选归因诊断（单独新目录）

```bash
cd /workspace/shawu
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v2/results/diagnostic-$(date -u +%Y%m%dT%H%M%SZ)"
bash m7-work/stage-a/v2/scripts/run.sh diagnostic
```

M5.2/v1/v2、legacy/cold、两条问题路线，覆盖Observer.sample、Renderer.prepare*、Region.draw主体/定位/恢复行/绘制、Map/UI/调色和Canvas draw/upload/readback，保存每帧归因和 `.cpuprofile`。这些有仪表/Profiler开销，**不能计作perf验收数据**。其目的包括解释v1原diagnostic漏计的大段render时间，而非先定论是GC/调度/UI。

## 第二阶段：完整验收，探针值得继续时运行

```bash
cd /workspace/shawu
unset STAGE_A_PROBE_REPEATS
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v2/results/full-$(date -u +%Y%m%dT%H%M%SZ)"
bash m7-work/stage-a/v2/scripts/run.sh full
```

顺序运行离线freeze检查→原23分支442 state/native/actor-text检查→31,396帧HD RGBA/coverage与pre-fix M7逐帧零差异→原72样本perf→中文报告。没有并行QA/诊断/录屏；同一全局exclusive.lock防重入，已有8765服务项目根目录，不启动新服务器。

full perf三版本仍为M5.2/pre-fix M7/v2，4路线×legacy/cold×3重复=72；没有改变v1完整测量的native帧数、输入、预热、统计、地图ID切图±60帧窗口、debt、FPS或版本顺序。v1的完整72样本历史证据保留；小探针另提供同期v1对照。

完整结果：`qa/report.json`、`visual/report.json`/`frames.jsonl`、`perf/report.json`/72个raw sample、`comparison.json`、`REPORT_STAGE_A_zh.md`及对应log。summarize继续所有严格回退明列且exit 2；不引入事后容差。真实原13图覆盖应保持 `438411621/439578861 = 99.73446403%`。

每次probe/diagnostic/full使用**全新**目录；错误时停止且日志保留。脚本会向STAGE_A_STATUS.md追加退出状态。不要同时启动两个模式，不运行旧verify-final.sh，不覆盖旧结果/冻结文件。修订代码必须新建版本后再跑。

所有编码由Codex完成。ROM/core/时钟/输入/mask/原生证据与覆盖分母不改。没有美术/ZIP/新录像；若逐帧视觉不同则立即停止检查，不能当作通过。Stage B仅在监督明确接受Stage A后才可开始。
