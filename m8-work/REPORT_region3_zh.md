# M8 区域3整合与验收报告

采用 Stage A v3；没有继续 Stage A 优化。新增 8 张完整地图（00-00、01、02、03、04、05、06、09），注册总数 29。8 张 PNG 原字节接入；CLI 元数据未改写。模型请求 gpt-image-2、请求 medium；服务器返回 quality 未获证明。

正式正确性：通过。84135 原生帧，1096 动作；完整 state 84135/84135，native framebuffer 84135/84135，人物/文字 SHA256 84135/84135。原区域 1/2：442/442 动作，HD RGBA + coverage 31396/31396 帧。每帧原始哈希见 qa/*.json.gz；开始字节与逐帧输入相同。

ROM/core/JS/CSS 与采用版字节相同；旧地图记录逐项相同，仅向清单追加8图。离线保护缺失为历史重启清理环境/字节码，不伪称旧清单全齐。全部开发/代码由 Codex 完成，监督负责运行既备脚本和视觉复核。

## 实测覆盖（分母为沿用的 eligible native-background pixels）

|新图|本图画作分子|原生背景分母|原生缺口|其他HD来源|覆盖率|残差原因|
|---|---:|---:|---:|---:|---:|---|
|00-00 东溪村|209451439|211961230|400087|2109704|98.81591978%|{"native raster/foreground not certified": 384143, "other verified HD source: map/history": 1602824, "other verified HD source: other scene verified-flat-transition": 506880, "native geometry changed": 15944}|
|00-01 东溪村室内 00-01|2543992|4189680|28482|1617206|60.72043688%|{"native raster/foreground not certified": 1549, "other verified HD source: map/history": 1409846, "other verified HD source: other scene verified-flat-transition": 207360, "legacy map renderer: uncertified native background": 22740, "native geometry changed": 4193}|
|00-02 东溪村室内 00-02|2526600|4172799|27375|1618824|60.54928598%|{"native raster/foreground not certified": 1174, "other verified HD source: map/history": 1411464, "other verified HD source: other scene verified-flat-transition": 207360, "legacy map renderer: uncertified native background": 22766, "native geometry changed": 3435}|
|00-03 东溪村室内 00-03|2549224|4151191|27844|1574123|61.40946056%|{"native raster/foreground not certified": 1518, "other verified HD source: map/history": 1366763, "other verified HD source: other scene verified-flat-transition": 207360, "legacy map renderer: uncertified native background": 22377, "native geometry changed": 3949}|
|00-04 东溪村室内 00-04|2521661|4197903|27433|1648809|60.06953948%|{"other verified HD source: map/history": 1441449, "other verified HD source: other scene verified-flat-transition": 207360, "legacy map renderer: uncertified native background": 22850, "native geometry changed": 3257, "native raster/foreground not certified": 1326}|
|00-05 东溪村会合屋|195244745|280019353|81538832|3235776|69.72544680%|{"native raster/foreground not certified": 513945, "other verified HD source: map/history": 2821056, "other verified HD source: other scene verified-flat-transition": 414720, "legacy map renderer: uncertified native background": 80982729, "native geometry changed": 42158}|
|00-06 东溪村庙宇|2544476|4166443|27256|1594711|61.07070228%|{"native raster/foreground not certified": 1477, "other verified HD source: map/history": 1387351, "other verified HD source: other scene verified-flat-transition": 207360, "legacy map renderer: uncertified native background": 22365, "native geometry changed": 3414}|
|00-09 村东南连通林道|2629130|4260569|22605|1608834|61.70842439%|{"native raster/foreground not certified": 36, "other verified HD source: map/history": 1401474, "other verified HD source: other scene verified-flat-transition": 207360, "legacy map renderer: uncertified native background": 22569}|

8图加权实测：420011267/517119168 = 81.22136888%；残差 97107901。

离线重算见 qa-coverage-attribution.json。00-05 原 undefined 中的 80,982,729 像素为旧地图渲染器缺少原因标签的原生缺口。覆盖分子、分母及残差计数与原 QA 一致。

路线：23 original region1/2 branches + 185-action letter chain + 281-action meeting chain + eight existing doorway surveys; all baseline/candidate pairs use identical byte starts and native-frame inputs.
分母沿用每帧原生背景的 eligible 计数，含路线内重访与缺乏匹配证据的转场帧。逐像素分子只计取自同一张新图画作的像素。原生缺口与其他已验证 HD 来源均单列。
缺口保留原生最近邻像素。战斗银行 2b–2d 和非零原生场景模式据既有路径规则记为排除帧，实际计数在 qa/report.json 的 region3Excluded。00-08、00-0b、00-35、黄泥岗及其他地图 ID 均不计入八图。全路线逐帧证据保留。

原区域2单独回归覆盖：
438411621/439578861；采用v3历史同路线 438411621/439578861（99.73446403%）。逐帧一致检查已单独执行。

## 性能

性能不得差于采用v3：未通过／有回退，不能宣布通过。样本 144/144；三次重复、相同起点/原生输入、冷启动与60原生帧旧预热，1792帧/样本；audit关，无视频。所有异常保留。严格失败数 165；性能末态不变量差异 0。
测量跨 2 个运行批次。批次和机器信息见 perf/report.json 中的 measurementRuns 与各样本字段。
下表为三次均值，完整每次数据、方差、范围、cold first60/first-switch、render/frame/switch/debt p95/max及配对失败见 perf/comparison.json。导航到ready与loadState另见原样本，不将加载成本藏入未报告阶段。

|模式/路线|FPS 采用/新|frame p95 采用/新|frame max 采用/新|debt max 采用/新|switch frame max 采用/新|
|---|---:|---:|---:|---:|---:|
|legacy/00-12|59.735/59.736|4.433/4.167|25.067/14.867|23.462/16.735|24.333/14.867|
|legacy/00-17|59.733/59.735|4.167/4.133|18.000/19.533|16.735/16.735|17.533/19.533|
|legacy/00-1b|59.735/59.735|4.333/4.433|8.700/10.667|16.732/16.735|无切图|
|legacy/00-0c|59.735/59.735|5.633/5.433|26.800/26.200|19.765/16.738|26.800/26.200|
|legacy/region3-00-00|59.732/59.740|8.367/3.367|31.833/16.467|24.907/16.732|无切图|
|legacy/region3-00-01|59.733/59.734|10.567/4.433|39.433/15.867|40.297/16.741|11.800/15.867|
|legacy/region3-00-02|59.734/59.736|9.633/3.900|42.900/14.867|38.429/19.565|无切图|
|legacy/region3-00-03|59.731/59.736|10.467/4.267|22.333/14.667|16.738/16.738|无切图|
|legacy/region3-00-04|59.733/59.736|8.667/3.667|15.267/12.067|16.732/16.732|无切图|
|legacy/region3-00-05|59.732/59.736|9.167/3.733|25.667/12.900|16.732/16.739|无切图|
|legacy/region3-00-06|59.736/59.735|8.433/4.367|23.733/21.767|23.323/24.800|无切图|
|legacy/region3-00-09|59.728/59.734|10.100/4.000|19.967/13.700|20.349/16.735|无切图|
|cold/00-12|59.719/59.709|4.833/5.000|16.800/16.500|16.738/16.729|16.467/16.500|
|cold/00-17|59.721/59.721|4.100/4.000|16.000/29.000|16.735/31.591|16.000/29.000|
|cold/00-1b|59.719/59.705|4.367/4.033|12.500/11.267|16.735/16.734|无切图|
|cold/00-0c|59.710/59.715|5.133/4.667|14.500/15.433|16.731/16.735|14.500/14.700|
|cold/region3-00-00|59.707/59.714|8.133/4.133|33.733/18.500|35.394/16.729|无切图|
|cold/region3-00-01|59.711/59.715|9.633/4.800|42.000/20.367|46.798/16.738|14.433/9.533|
|cold/region3-00-02|59.713/59.714|9.900/4.567|34.600/28.000|31.881/16.735|12.633/9.900|
|cold/region3-00-03|59.699/59.721|11.233/4.267|37.333/18.467|88.414/16.736|15.600/8.900|
|cold/region3-00-04|59.702/59.706|10.400/4.467|39.867/18.133|33.560/16.735|14.933/7.567|
|cold/region3-00-05|59.712/59.717|10.233/4.367|39.667/16.500|59.705/16.738|12.167/10.567|
|cold/region3-00-06|59.708/59.722|9.200/4.633|25.200/13.667|16.738/16.738|12.100/7.533|
|cold/region3-00-09|59.708/59.720|8.667/5.133|22.133/21.100|16.732/16.738|12.900/11.833|

Stage A前后历史：采用v3带残差继续，不是全绿。legacy内城switch max均值21.467ms vs同期M5.2 12.600ms，cold内城16.933 vs13.800ms；详见 m7-work/STAGE_A_FINAL_DECISION_zh.md，不能混作本次配对测量。

## 剧情与交付

原生终点为 story12 吴用会合；下一步黄泥岗客栈乔装掌柜/小二设伏，尚未进入或完成。原19596帧介绍信链精确结论保留。后26711帧/281动作连续与分段原生画面/ticks一致，但最终存档3字节不同（181192、181193、198376），原因未归因，未改core/save消除；正式QA始终对比相同字节起点。

对照：shots/m8_region3_contact.png（8图原生/整合后实际运行截图）；qa/story12-{native,hd}.png 为剧情原人物文字复核。
预览：m8-work/region3_preview.webm，小于25MB；原生rAF实时八段自然存档摘录，段间载档，无音频，未加速；不是连续旅程。raw及每段FPS见 recording/。
美术暂准并不等于碰撞几何像素证明；严格原生证据控制能替换的像素。最终运行视觉仍需监督审阅，尤其门路、道具数量及原生人物/对白。

本次原始结果目录：m8-work/results/outer-20261118T062207Z；freeze-sha256.json 锁定输入/runtime/scripts；integration/provenance.json 保存原CLI溯源；offline/integration-checks.json 保存历史缺失明细。
