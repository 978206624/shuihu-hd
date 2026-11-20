# Stage A v3 — REQUEST_READY：先12样本probe，再决定full

**v1和v2均已拒绝。当前仅Stage A v3候选冻结，未接受。不得启动M8/Stage B。**

新runtime：`m7-work/stage-a/v3/runtime/`。冻结清单：`m7-work/stage-a/v3/freeze-sha256.json`，SHA256：`49d5840720f3174f78556441b7c0f6aeef02b8ca62bc54374be2199937120cf7`（546文件）。当前代码只改region-renderer.js；原m7-work/runtime及v1/v2历史原件未改。v2全量保全：`m7-work/stage-a/versions/v2/`（132文件，含全部probe/raw/监督分析、runtime/scripts/freeze/offline及当时状态/命令文档）。

本沙箱已知socket EPERM，不重试浏览器/网络、不安装环境。以下命令仅供**监督外层shell**运行；使用现有127.0.0.1:8765根目录服务，不启动/替换服务器。各入口检查38811；代理失败写STAGE_A_STATUS.md的BLOCKER并停止，不改认证/路由、不嵌套Codex。

## 0. 监督确认独占

检查CPU；先等待当前Codex离线工作结束，再停下其他QA、重放、录屏或重CPU任务。不要与本次探针并行运行诊断或full。保留代理与现有HTTP服务。

```bash
cd /workspace/shawu
ps -eo pid,pcpu,comm --sort=-pcpu | head -n 25
export NODE_PATH=/home/box/opt/test-tools/node_modules
export PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers
export SUPERVISOR_CONFIRMED_EXCLUSIVE=1
sha256sum m7-work/stage-a/v3/freeze-sha256.json
```

## 1. 12样本probe（约6分钟以上）

```bash
cd /workspace/shawu
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v3/results/probe-$(date -u +%Y%m%dT%H%M%SZ)"
export STAGE_A_PROBE_REPEATS=2
bash m7-work/stage-a/v3/scripts/run.sh probe
```

每次使用全新绝对结果目录，脚本拒绝已有目录及v3/results以外路径；不预先mkdir该目录。全局`stage-a/exclusive.lock`防重入。离线复核写入该次`offline/`，不覆盖候选本地offline证据。

12个exclusive样本仍为legacy 00-12、cold 00-17 × M5.2/v1/v3 × 2重复，顺序轮换。`perf.cjs`与v2**逐字节相同**；probe仅标题由v2改v3，继续直接调用同一个measure()。每样本1792原生帧，legacy 60空闲帧预热，cold第1帧输入/前60帧计入；原地图ID切图±60窗、FPS/debt/p95/max/分母/容差完全不变。audit off、无录屏/截图/trace、fresh context，startup/loadState仍单列。

输出：`$STAGE_A_RESULTS/probe/REPORT_PROBE_zh.md`、`report.json`、12份raw json、`probe.log`、`preflight.log`、`offline.log`、`offline/checks.json`。严格配对回退exit 2，异常exit 1；退出状态追加STAGE_A_STATUS.md。不要只看均值或FPS，也不要删除噪声样本。

**先看gate，再决定是否full。** 重点与M5.2及同期v1对比cold 00-17 switchFrameMax/切图p95/debt，逐帧看408、412、497（窗口390–510）；同时确认legacy 00-12 maxDebt改善未丢失，其他回退全部保留。官方v1 cold switchFrameMax均值31.000 vs M5.2 13.067ms、legacy maxDebt均值163.504 vs40.243ms已失败。v2 clean r2帧412=30.9ms、帧497=16.4ms仍不能接受。

若v3仍有实质回退，保留结果交当前Codex继续修订，不启动昂贵72样本。legacy M5.2 v2 probe r2的21480ms机器hitch和v2 cold r1的2106ms debt不能单侧证明改善；也不能用它们忽略干净frame412失败。探针无论结果如何都不是最终验收。

## 2. 可选归因诊断（独立新目录，不计验收）

```bash
cd /workspace/shawu
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v3/results/diagnostic-$(date -u +%Y%m%dT%H%M%SZ)"
bash m7-work/stage-a/v3/scripts/run.sh diagnostic
```

M5.2/v1/v2/v3 × legacy/cold × 两条问题路线。保存`.cpuprofile`、所有帧的Observer/Renderer准备/Region.draw主体、定位、恢复行、identity计划/绘制、Map调色/UI、Canvas draw/upload/readback、heapBytes、原生map ID与408/412/497等focusFrames。当前没有证据能确定v2 frame412全部30.2ms属于GC、JIT、Canvas或某单一环节；诊断用于区分这些可能性。仪表和Profiler有开销，不能替代无仪表perf或据此调整验收定义。

## 3. 完整验收（probe值得继续后才运行）

```bash
cd /workspace/shawu
unset STAGE_A_PROBE_REPEATS
export STAGE_A_RESULTS="$PWD/m7-work/stage-a/v3/results/full-$(date -u +%Y%m%dT%H%M%SZ)"
bash m7-work/stage-a/v3/scripts/run.sh full
```

依次：冻结/历史保全检查 → 原23分支442 state/native/actor-text检查（含区域1/2回归）→ 31,396帧HD RGBA/coverage与pre-fix M7逐帧零差异 → 原72样本 → 中文报告。qa.cjs、visual.cjs、perf.cjs与v2逐字节相同；summarize只改新版本输出路径。全量仍为M5.2/pre-fix M7/v3 ×4路线×legacy/cold×3重复；所有旧输入/起点、版本顺序、时钟/测量/窗口/分母/阈值不变。至少36分钟纯perf，另加QA/视觉时间；不要运行旧verify-final.sh。

结果：`qa/report.json`、`visual/report.json`/`frames.jsonl`、`perf/report.json`/72份raw、`comparison.json`、`REPORT_STAGE_A_zh.md`及各log。所有严格回退明列，未引入事后容差。原13图覆盖必须仍为`438411621/439578861 = 99.73446403%`，逐图分母/分子/原因不变。视觉/coverage不同立即失败检查，不继续perf。

任何新编码必须再建下一版本，不能改当前freeze或v1/v2证据。无ZIP、video/art或M8。最终接受需要442/31396/72全部证据并由监督明确接受Stage A。
