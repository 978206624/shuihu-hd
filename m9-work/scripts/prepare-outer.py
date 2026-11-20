"""Validate official replay inputs and freeze the offline handoff."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "m9-work"
M8 = ROOT / "m8-work"
EVIDENCE = WORK / "play/m9-huangnigang-official-evidence"
INTEGRATION = WORK / "integration"
START = WORK / "checkpoints/story12-meeting-end.bin"
START_SHA = "2a3551ad5082236ce2b3223323d6fff983a984a3839ff2e6fa2359c1321edea2"
ACTIONS = WORK / "outer-runs/huangnigang-inn-actions.json"
V3 = ROOT / "m7-work/stage-a/v3/runtime"
SAVED_PERF = M8 / "results/outer-20261118T062207Z/perf/report.json"
COLD_DECISION = M8 / "results/outer-cold-0017-20261118T092326742885874Z/decision.json"
CONTACTS = {"00-1f": 111, "00-21": 150, "00-24": 197, "00-2b": 204, "00-2c": 234}
APPROACH = {"00-1f": 103, "00-21": 144, "00-24": 186, "00-2b": 199, "00-2c": 232}
CLIPS = [
    ("Huangnigang arrival and forest path", 104, 114),
    ("Wooded passage", 145, 157),
    ("Inn exterior and entrance", 187, 203),
    ("Wu Yong at the front hall", 206, 212),
    ("The front-hall talk concludes", 223, 227),
    ("From the front hall to the rear room", 231, 241),
    ("Shi Jin and the rear-room talk", 253, 261),
]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def publish(name, data):
    (INTEGRATION / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def frames(actions):
    return sum(a[1] + a[2] for a in actions)


def save_for(record):
    return EVIDENCE / f"{record['name']}.bin"


def main():
    provenance = read(INTEGRATION / "provenance.json")
    assert sha(START) == START_SHA == sha(EVIDENCE / "start.bin")
    evidence_result = EVIDENCE / "result.json"
    evidence_frames = EVIDENCE / "frames.jsonl"
    official = read(evidence_result)
    actions = read(ACTIONS)
    assert actions == read(EVIDENCE / "actions.json") == read(EVIDENCE / "planned-actions.json")
    assert official["status"] == "COMPLETE" and not official["errors"]
    assert official["sourceSHA256"] == START_SHA
    assert len(actions) == len(official["records"]) == 262 and frames(actions) == 14572
    assert sha(EVIDENCE / "initial.bin") == official["initial"]["stateSHA256"]
    expected_frame = 0
    for i, (action, rec) in enumerate(zip(actions, official["records"])):
        assert action == rec["action"] and rec["index"] == i and rec["name"] == f"action-{i:04d}"
        expected_frame += frames([action])
        assert rec["frame"] == expected_frame
        assert sha(save_for(rec)) == rec["stateSHA256"]
    end = official["end"]
    assert end == official["records"][-1] and (end["map"], end["story"]) == ("00-2c", 14)
    end_save = save_for(end).read_bytes()
    offset = 147568 + 0x1000
    assert (end_save[offset + 0xaa1], end_save[offset + 0xaa2]) == (0x72, 1)

    events = [json.loads(line) for line in evidence_frames.read_text().splitlines()]
    observations = [e for e in events if e["type"] == "frame"]
    assert len(observations) == 14572
    assert all(o["frame"] == i for i, o in enumerate(observations, 1))
    assert {o["map"] for o in observations}.issuperset(CONTACTS)

    qa_path, perf_path = (M8 / "inputs" / name for name in ("qa-routes.json", "perf-routes.json"))
    old = read(qa_path)
    assert len(old) == 33 and sum(len(r["actions"]) for r in old) == 1096
    assert sum(frames(r["actions"]) for r in old) == 84135
    perf = [{**r, "source": relative(Path(r["source"])), "controls": ["adopted", "m8"]}
            for r in read(perf_path)]
    assert len(perf) == len({r["id"] for r in perf}) == 12
    pinned = {START, ACTIONS, evidence_result, evidence_frames, qa_path, perf_path, SAVED_PERF, COLD_DECISION}
    pinned.update(Path(r["source"]) for r in old)
    pinned.update(ROOT / r["source"] for r in perf)
    for map_id, start in APPROACH.items():
        source = save_for(official["records"][start])
        sequence = actions[start + 1:]
        assert frames(sequence) >= 1792
        assert any(o["map"] == map_id and o["mode"] == 0 and o["bank"] == 5
                   for o in observations[official["records"][start]["frame"]:][:1792])
        perf.append(dict(id=f"region4-{map_id}", target=map_id, source=relative(source),
                         firstAction=start + 1, actions=sequence, controls=["m8"]))
        pinned.add(source)
    clips = []
    for name, first, last in CLIPS:
        source = save_for(official["records"][first - 1])
        clips.append(dict(name=name, first=first, last=last, source=relative(source)))
        pinned.add(source)
    for map_id, i in CONTACTS.items():
        r = official["records"][i]
        assert r["map"] == map_id and r["mode"] == 0 and r["dialogue"] == 0 and r["bank"] == 5

    v3 = read(M8 / "integrity/adopted-runtime-sha256.json")
    assert v3.keys() == {str(p.relative_to(V3)) for p in V3.rglob("*") if p.is_file()}
    runtime = {}
    for root, entries in [(V3, v3), (M8 / "runtime", provenance["m8RuntimeSHA256"]),
                          (WORK / "runtime", provenance["m9RuntimeSHA256"])]:
        for name, digest in entries.items():
            path = root / name
            assert sha(path) == digest, path
            runtime[relative(path)] = digest
    pinned.update(ROOT / r[key] for r in provenance["newMaps"] for key in ("source", "originalCLIMetadata"))
    pinned.update([WORK / "region4-scope.json", WORK / "art/batch-manifest.json",
                   WORK / "art/SUPERVISOR_VISUAL_REVIEW.md", INTEGRATION / "provenance.json"])
    publish("outer-plan.json", dict(
        official=dict(name="official-huangnigang-inn", source=relative(START), actions=relative(ACTIONS),
                      result=relative(evidence_result), frames=relative(evidence_frames), contacts=CONTACTS),
        oldQA=relative(qa_path), perf=perf, clips=clips, savedV3=relative(SAVED_PERF),
        coldDecision=relative(COLD_DECISION)))
    pinned.add(INTEGRATION / "outer-plan.json")
    pinned.update(WORK / "scripts" / name for name in (
        "outer-common.cjs", "region4-qa.cjs", "region4-perf.cjs", "region4-preview.cjs",
        "region4-contact.py", "region4-perf-summary.py", "run-region4-outer.sh"))
    pinned.add(M8 / "scripts/coverage-attribution.cjs")
    pinned.add(M8 / "scripts/common.cjs")
    publish("outer-freeze.json", {**runtime, **{relative(p): sha(p) for p in sorted(pinned)}})
    print("Verified 262 official actions, 14572 frames, 263 save hashes, WRAM 72/01, and 17 perf routes.")


if __name__ == "__main__":
    main()
