"""Fail-closed Chinese report from measured files, never art status."""
from pathlib import Path
import hashlib,json,os,statistics,sys
R=Path(__file__).resolve().parents[2];W=R/'m8-work';O=Path(os.environ['M8_RESULTS'])
read=lambda p:json.loads(p.read_text())
qa=read(O/'qa/report.json');perf=read(O/'perf/report.json');rec=read(O/'recording/report.json')
coverage=qa['region3Coverage']
coverage_note=''
attribution=O/'qa-coverage-attribution.json'
if attribution.is_file():
    derived=read(attribution)
    assert derived['qaReportSHA256']==hashlib.sha256((O/'qa/report.json').read_bytes()).hexdigest()
    assert (derived['actions'],derived['frames'])==(qa['actions'],qa['frames'])
    updated=derived['region3Coverage']
    assert updated.keys()==coverage.keys()
    for map_id, row in updated.items():
        original=coverage[map_id]
        assert {k:v for k,v in row.items() if k!='reasons'}=={k:v for k,v in original.items() if k!='reasons'}
        assert sum(row['reasons'].values())==row['gap']
    coverage=updated
    gap=derived['reclassifiedUndefined'].get('00-05',{}).get('pixels',0)
    coverage_note=f'离线重算见 qa-coverage-attribution.json。00-05 原 undefined 中的 {gap:,} 像素为旧地图渲染器缺少原因标签的原生缺口。覆盖分子、分母及残差计数与原 QA 一致。'
dis=read(W/'inputs/route-disclosures.json');scope=read(W/'region3-scope.json')
groups={}
for s in perf['samples']:groups.setdefault((s['mode'],s['id']),{}).setdefault(s['which'],[]).append(s)
def get(s,path):
    for k in path.split('.'):
        if s is None:return None
        s=s.get(k)
    return s
metrics={'gameFPS':1,'render.p95':-1,'render.max':-1,'frame.p95':-1,'frame.max':-1,
 'debt.p95':-1,'debt.max':-1,'switchAggregate.render.p95':-1,'switchAggregate.render.max':-1,
 'switchAggregate.frame.p95':-1,'switchAggregate.frame.max':-1,'firstSwitch.frame.p95':-1,
 'firstSwitch.frame.max':-1,'firstSwitch.debt.max':-1,'initial60.frame.p95':-1,'initial60.frame.max':-1}
comparisons=[];failures=[];native_errors=[]
for key,g in groups.items():
    a=sorted(g.get('adopted',[]),key=lambda x:x['repeat']);c=sorted(g.get('candidate',[]),key=lambda x:x['repeat'])
    if len(a)!=3 or len(c)!=3:failures.append([list(key),'missing repeats']);continue
    for x,y in zip(a,c):
        if x['stateSha256']!=y['stateSha256'] or x['framebufferSha256']!=y['framebufferSha256']:
            native_errors.append([list(key),x['repeat']])
    row={'mode':key[0],'route':key[1],'metrics':{}}
    for metric,direction in metrics.items():
        av=[get(x,metric) for x in a];cv=[get(x,metric) for x in c]
        if all(v is None for v in av+cv):continue
        if any(v is None for v in av+cv):failures.append([list(key),metric,'switch present only on one side']);continue
        summarize=lambda xs:dict(mean=statistics.mean(xs),min=min(xs),max=max(xs),stddev=statistics.pstdev(xs),values=xs)
        aa,cc=summarize(av),summarize(cv)
        delta=cc['mean']-aa['mean'];mean_ok=delta*direction>=0
        pair_ok=[(v-u)*direction>=0 for u,v in zip(av,cv)]
        # No unrequested tolerance or deleted outlier. Report both mean and paired strict checks.
        row['metrics'][metric]=dict(adopted=aa,candidate=cc,delta=delta,meanNotWorse=mean_ok,pairedNotWorse=pair_ok)
        if not mean_ok or not all(pair_ok):failures.append([list(key),metric,delta,pair_ok])
    comparisons.append(row)
expected=12*2*3*2
if len(perf['samples'])!=expected:failures.append(['sample count',len(perf['samples']),expected])
accept=dict(performanceNotWorse=not failures and not native_errors and not perf.get('error'),
 strictPerformanceFailures=failures,perfNativeMismatches=native_errors,comparisons=comparisons,
 rawSampleCount=len(perf['samples']),requiredSampleCount=expected,
 rule='No deleted anomalies. Report three-repeat means, ranges, standard deviations, each paired repeat. Strict no-regression requires all listed actual metrics, including every paired repeat. Startup/load measured separately; no loading cost hidden as gameplay.')
(O/'perf/comparison.json').write_text(json.dumps(accept,indent=2)+'\n')
lines=['# M8 区域3整合与验收报告','',
 '采用 Stage A v3；没有继续 Stage A 优化。新增 8 张完整地图（00-00、01、02、03、04、05、06、09），注册总数 29。8 张 PNG 原字节接入；CLI 元数据未改写。模型请求 gpt-image-2、请求 medium；服务器返回 quality 未获证明。',
 '',f"正式正确性：{'通过' if qa['pass'] else '未通过'}。{qa['frames']} 原生帧，{qa['actions']} 动作；完整 state {qa['statePassed']}/{qa['frames']}，native framebuffer {qa['nativePassed']}/{qa['frames']}，人物/文字 SHA256 {qa['actorTextPassed']}/{qa['frames']}。原区域 1/2：{qa['regressionActions']}/442 动作，HD RGBA + coverage {qa['regressionVisualPassed']}/31396 帧。每帧原始哈希见 qa/*.json.gz；开始字节与逐帧输入相同。",
 '', 'ROM/core/JS/CSS 与采用版字节相同；旧地图记录逐项相同，仅向清单追加8图。离线保护缺失为历史重启清理环境/字节码，不伪称旧清单全齐。全部开发/代码由 Codex 完成，监督负责运行既备脚本和视觉复核。',
 '', '## 实测覆盖（分母为沿用的 eligible native-background pixels）','',
 '|新图|本图画作分子|原生背景分母|原生缺口|其他HD来源|覆盖率|残差原因|',
 '|---|---:|---:|---:|---:|---:|---|']
total=[0,0,0]
for s in scope['maps']:
    v=coverage.get(s['id'],dict(covered=0,eligible=0,gap=0,nativeGap=0,otherHD=0,reasons={}))
    for i,k in enumerate(['covered','eligible','gap']):total[i]+=v[k]
    pct=f"{100*v['covered']/v['eligible']:.8f}%" if v['eligible'] else '未测'
    lines.append(f"|{s['id']} {s['name']}|{v['covered']}|{v['eligible']}|{v['nativeGap']}|{v['otherHD']}|{pct}|{json.dumps(v['reasons'],ensure_ascii=False)}|")
lines += ['',f"8图加权实测：{total[0]}/{total[1]} = {100*total[0]/total[1]:.8f}%；残差 {total[2]}。" if total[1] else '8图覆盖未测；不据美术状态推算。']
if coverage_note:lines += ['',coverage_note]
lines += [
 '', '路线：'+dis['route'], '分母沿用每帧原生背景的 eligible 计数，含路线内重访与缺乏匹配证据的转场帧。逐像素分子只计取自同一张新图画作的像素。原生缺口与其他已验证 HD 来源均单列。',
 '缺口保留原生最近邻像素。战斗银行 2b–2d 和非零原生场景模式据既有路径规则记为排除帧，实际计数在 qa/report.json 的 region3Excluded。00-08、00-0b、00-35、黄泥岗及其他地图 ID 均不计入八图。全路线逐帧证据保留。',
 '', '原区域2单独回归覆盖：']
old=[v for k,v in qa['regressionCoverage'].items() if k in [f'00-{i:02x}' for i in range(0x12,0x1f)]]
lines += [f"{sum(v['covered'] for v in old)}/{sum(v['eligible'] for v in old)}；采用v3历史同路线 438411621/439578861（99.73446403%）。逐帧一致检查已单独执行。",'', '## 性能','',
 f"性能不得差于采用v3：{'通过' if accept['performanceNotWorse'] else '未通过／有回退，不能宣布通过'}。样本 {len(perf['samples'])}/{expected}；三次重复、相同起点/原生输入、冷启动与60原生帧旧预热，1792帧/样本；audit关，无视频。所有异常保留。严格失败数 {len(failures)}；性能末态不变量差异 {len(native_errors)}。",
 f"测量跨 {len(perf.get('measurementRuns',[]))} 个运行批次。批次和机器信息见 perf/report.json 中的 measurementRuns 与各样本字段。",
 '下表为三次均值，完整每次数据、方差、范围、cold first60/first-switch、render/frame/switch/debt p95/max及配对失败见 perf/comparison.json。导航到ready与loadState另见原样本，不将加载成本藏入未报告阶段。','',
 '|模式/路线|FPS 采用/新|frame p95 采用/新|frame max 采用/新|debt max 采用/新|switch frame max 采用/新|','|---|---:|---:|---:|---:|---:|']
for row in comparisons:
    def pair(k):
        v=row['metrics'].get(k)
        return f"{v['adopted']['mean']:.3f}/{v['candidate']['mean']:.3f}" if v else '无切图'
    lines.append('|'+row['mode']+'/'+row['route']+'|'+'|'.join(pair(k) for k in ['gameFPS','frame.p95','frame.max','debt.max','switchAggregate.frame.max'])+'|')
lines += ['', 'Stage A前后历史：采用v3带残差继续，不是全绿。legacy内城switch max均值21.467ms vs同期M5.2 12.600ms，cold内城16.933 vs13.800ms；详见 m7-work/STAGE_A_FINAL_DECISION_zh.md，不能混作本次配对测量。',
 '', '## 剧情与交付','',
 '原生终点为 story12 吴用会合；下一步黄泥岗客栈乔装掌柜/小二设伏，尚未进入或完成。原19596帧介绍信链精确结论保留。后26711帧/281动作连续与分段原生画面/ticks一致，但最终存档3字节不同（181192、181193、198376），原因未归因，未改core/save消除；正式QA始终对比相同字节起点。',
 '', '对照：shots/m8_region3_contact.png（8图原生/整合后实际运行截图）；qa/story12-{native,hd}.png 为剧情原人物文字复核。',
 '预览：m8-work/region3_preview.webm，小于25MB；原生rAF实时八段自然存档摘录，段间载档，无音频，未加速；不是连续旅程。raw及每段FPS见 recording/。',
 '美术暂准并不等于碰撞几何像素证明；严格原生证据控制能替换的像素。最终运行视觉仍需监督审阅，尤其门路、道具数量及原生人物/对白。',
 '',f'本次原始结果目录：{O.relative_to(R)}；freeze-sha256.json 锁定输入/runtime/scripts；integration/provenance.json 保存原CLI溯源；offline/integration-checks.json 保存历史缺失明细。']
report='\n'.join(lines)+'\n';(O/'REPORT_region3_zh.md').write_text(report)
dest=W/'REPORT_region3_zh.md';assert not dest.exists(),'Do not overwrite prior final report';dest.write_text(report)
result={'correctness':qa['pass'],'performance':accept['performanceNotWorse'],'recording':rec['pass'],'coverageNumerator':total[0],'coverageDenominator':total[1],'performanceFailures':len(failures),'supervisorVisualReview':'PENDING'}
(O/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));sys.exit(0 if qa['pass'] and accept['performanceNotWorse'] and rec['pass'] else 2)
