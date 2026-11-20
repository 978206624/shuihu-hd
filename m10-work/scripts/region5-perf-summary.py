"""Compare each M10 sample with its fresh M9 control and show saved M9 metrics."""

import json
import os
import statistics
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
METRICS = (
    "gameFPS", "render.mean", "render.p95", "render.max", "frame.mean", "frame.p95", "frame.max",
    "debt.p95", "debt.max", "switchAggregate.render.p95", "switchAggregate.render.max",
    "switchAggregate.frame.p95", "switchAggregate.frame.max", "firstSwitch.frame.p95",
    "firstSwitch.frame.max", "firstSwitch.debt.max", "initial60.frame.p95", "initial60.frame.max",
)
STARTUP = ("startup.navigationToReadyMs", "loadState.durationMs")
MODES = ("legacy", "cold")
REPEATS = (1, 2, 3)
VARIANTS = ("m9", "candidate")


def read(path):
    with path.open() as handle:
        return json.load(handle)


def metric(sample, name):
    for key in name.split("."):
        if sample is None:
            break
        sample = sample.get(key)
    return sample


def describe(values):
    if None in values:
        return dict(values=values, mean=None, min=None, max=None, stddev=None)
    return dict(values=values, mean=statistics.mean(values), min=min(values),
                max=max(values), stddev=statistics.pstdev(values))


def main():
    run = Path(os.environ["M10_RESULTS"]).resolve()
    assert run.parent == WORK / "results"
    out = run / "perf"
    assert (out / "report.json").is_file()
    plan = read(WORK / "integration/outer-plan.json")
    saved = read(WORK.parent / plan["savedM9"])
    previous = {(row["mode"], row["route"]): row["metrics"] for row in saved["comparisons"]}
    rows, mismatches, mean_flags, cross_attempt = [], [], [], []
    for route in plan["perf"]:
        route_id = route["id"]
        for mode in MODES:
            pairs, by_variant = [], {which: [] for which in VARIANTS}
            for repeat in REPEATS:
                label = [mode, route_id, repeat]
                pair = {}
                for which in VARIANTS:
                    sample = read(out / f"{mode}-{route_id}-{which}-r{repeat}.json")
                    assert (sample["which"], sample["id"], sample["mode"], sample["repeat"],
                            sample["frames"]) == (which, route_id, mode, repeat, 1792)
                    by_variant[which].append({name: metric(sample, name) for name in METRICS + STARTUP})
                    pair[which] = {key: sample[key] for key in (
                        "stateSha256", "framebufferSha256", "switchWindows", "over50")}
                    pair[which]["target"] = sample.get("target")
                    pair[which]["measurementRun"] = sample["measurementRun"]["id"]
                control, candidate = (pair[which] for which in VARIANTS)
                if any(control[key] != candidate[key] for key in ("stateSha256", "framebufferSha256")):
                    mismatches.append(label)
                if control["measurementRun"] != candidate["measurementRun"]:
                    cross_attempt.append(label)
                pairs.append(dict(repeat=repeat, **pair))

            comparisons = {}
            for name in METRICS + STARTUP:
                a, b = ([sample[name] for sample in by_variant[which]] for which in VARIANTS)
                direction = -1 if name == "gameFPS" else 1
                deltas = [None if x is None or y is None else y - x for x, y in zip(a, b)]
                data = {key: describe(values) for key, values in zip(VARIANTS, (a, b))}
                mean_delta = describe(deltas)["mean"]
                data.update(pairedDeltas=deltas, pairedWorse=[
                    None if delta is None else direction * delta > 0 for delta in deltas],
                    meanWorse=None if mean_delta is None else direction * mean_delta > 0)
                old = previous.get((mode, route_id), {}).get(name, {}).get("candidate")
                if old is not None:
                    data["savedM9"] = old
                if name in METRICS and data["meanWorse"]:
                    mean_flags.append([mode, route_id, name])
                comparisons[name] = data
            rows.append(dict(mode=mode, route=route_id, metrics=comparisons, pairs=pairs))

    report = dict(samples=len(rows) * len(REPEATS) * len(VARIANTS), nativeMismatches=mismatches,
                  m9GameplayMeanRegressionCandidates=mean_flags, crossAttemptPairs=cross_attempt,
                  comparisons=rows, savedM9Source=plan["savedM9"],
                  m9Cold0017History=saved["cold0017History"],
                  note="Timing flags use paired fresh M9 controls. Review the repeat spread, switch windows and host attempts.")
    pending = out / "comparison.partial"
    pending.write_text(json.dumps(report, indent=2) + "\n")
    pending.replace(out / "comparison.json")
    print(f"Compared {report['samples']} samples. Native mismatches {len(mismatches)}. "
          f"M9 mean timing flags {len(mean_flags)}. Cross-attempt pairs {len(cross_attempt)}.")
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
