"""Summarize the full adopted-v3 protocol without dropping any repeats."""

import json
import os
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ["M9_RESULTS"]) / "perf"
METRICS = (
    "gameFPS", "render.p95", "render.max", "frame.p95", "frame.max",
    "debt.p95", "debt.max", "switchAggregate.render.p95", "switchAggregate.render.max",
    "switchAggregate.frame.p95", "switchAggregate.frame.max", "firstSwitch.frame.p95",
    "firstSwitch.frame.max", "firstSwitch.debt.max", "initial60.frame.p95", "initial60.frame.max",
)
DISCLOSED = {
    "frame.max": 24.100, "switchAggregate.frame.max": 24.100,
    "firstSwitch.frame.max": 24.100, "debt.max": 16.738,
}


def read(path):
    return json.loads(path.read_text())


def metric(sample, name):
    for key in name.split("."):
        if sample is None:
            break
        sample = sample.get(key)
    return sample


def describe(values):
    if None in values:
        return None
    return dict(values=values, mean=statistics.mean(values), min=min(values),
                max=max(values), stddev=statistics.pstdev(values))


def main():
    config = read(ROOT / "m9-work/integration/outer-plan.json")
    groups = defaultdict(dict)
    samples = read(OUT / "report.json")["samples"]
    assert len(samples) == 276
    for sample in samples:
        group = groups[sample["mode"], sample["id"]]
        key = sample["which"], sample["repeat"]
        assert key not in group and sample["frames"] == 1792
        group[key] = sample
    saved = [s for s in read(ROOT / config["savedV3"])["samples"] if s["which"] == "adopted"]
    saved.sort(key=lambda s: s["repeat"])
    prior_cold = read(ROOT / config["coldDecision"])["summary"]["cold"]

    rows, native_mismatches, m8_mean_flags, disclosed_failures = [], [], [], []
    for route in config["perf"]:
        route_id = route["id"]
        for mode in ("legacy", "cold"):
            group = groups[mode, route_id]
            variants = route["controls"] + ["candidate"]
            runs = {v: [group[v, repeat] for repeat in (1, 2, 3)] for v in variants}
            assert len(group) == 3 * len(variants)
            for control in route["controls"]:
                for c, m9 in zip(runs[control], runs["candidate"]):
                    if any(c[k] != m9[k] for k in ("stateSha256", "framebufferSha256")):
                        native_mismatches.append([mode, route_id, control, c["repeat"]])
            saved_v3 = [s for s in saved if s["id"] == route_id and s["mode"] == mode]
            metrics = {}
            for name in METRICS + ("startup.navigationToReadyMs", "loadState.durationMs"):
                values = {v: [metric(s, name) for s in runs[v]] for v in variants}
                if saved_v3:
                    values["savedV3"] = [metric(s, name) for s in saved_v3]
                if all(value is None for value in values["candidate"] + values["m8"]):
                    continue
                direction = 1 if name == "gameFPS" else -1
                data = {v: describe(vs) for v, vs in values.items()}
                candidate = data["candidate"]
                for v in route["controls"]:
                    control = data[v]
                    data["vs_"+v] = dict(
                        meanNotWorse=None if candidate is None or control is None else
                        (candidate["mean"]-control["mean"])*direction >= 0,
                        pairedNotWorse=[None if a is None or b is None else (b-a)*direction >= 0
                                        for a, b in zip(values[v], values["candidate"])])
                cold_0017 = (mode, route_id) == ("cold", "00-17")
                if cold_0017 and name in DISCLOSED:
                    mean = candidate["mean"]
                    data["disclosedLimitMs"] = DISCLOSED[name]
                    if name != "debt.max":
                        data["originalGateMs"] = 19.0
                        data["savedV3"] = prior_cold["savedV3"][name]
                    if round(mean, 3) > DISCLOSED[name]:
                        disclosed_failures.append([name,mean,DISCLOSED[name]])
                elif name in METRICS and data["vs_m8"]["meanNotWorse"] is not True:
                    m8_mean_flags.append([mode,route_id,name])
                metrics[name] = data
            rows.append(dict(mode=mode, route=route_id, metrics=metrics,
                             targetSamples={v: [s.get("target") for s in runs[v]] for v in variants}))

    report = dict(samples=len(samples), nativeMismatches=native_mismatches,
                  cold0017DisclosedLimitExceeded=disclosed_failures,
                  m8GameplayMeanRegressionCandidates=m8_mean_flags, comparisons=rows,
                  cold0017History=dict(rejectedCandidate=prior_cold["candidate"],
                                       retainedM8=prior_cold["original"], savedV3=prior_cold["savedV3"]),
                  note="Report every result. Review paired repeats and same-host M8 controls before attributing changes to M9.")
    pending = OUT / "comparison.partial"
    pending.write_text(json.dumps(report, indent=2) + "\n")
    pending.replace(OUT / "comparison.json")
    print(f"Compared {len(samples)} samples. Native mismatches {len(native_mismatches)}. "
          f"Residual exceedances {len(disclosed_failures)}. M8 mean flags {len(m8_mean_flags)}.")
    if native_mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
