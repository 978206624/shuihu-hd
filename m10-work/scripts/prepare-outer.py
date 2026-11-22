"""Validate the accepted replay inputs and freeze the supervisor handoff."""

import hashlib
import json
from itertools import accumulate
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "m10-work"
M9 = ROOT / "m9-work"
INTEGRATION = WORK / "integration"
EVIDENCE = WORK / "play/m10-region5-official-evidence"
START = WORK / "checkpoints/story14-inn-end.bin"
START_SHA = "f389cebc3fc59a310571c66538d38808c32483c7632164f35d207f0738e8d6c0"
CHAIN = WORK / "official-chain"
ACTIONS = CHAIN / "official-region5-actions.json"
M9_PLAN = M9 / "integration/outer-plan.json"
M9_PERF = M9 / "results/m9-region4-20261121T085635276998948Z/perf/comparison.json"

# Action numbers in the accepted one-based browser log.
CONTACTS = {"00-2c": 344, "00-2b": 8, "00-24": 22, "00-21": 37,
            "00-23": 74, "00-0a": 1554, "00-0b": 1578, "00-2a": 1669}
CLIPS = [
    ("Enter the west forest", 71, 79),
    ("West forest story scene", 107, 113),
    ("Story 19 at the inn exterior", 1535, 1540),
    ("Exit path", 1551, 1566),
    ("Forest mountain road", 1567, 1584),
    ("Stone stairs arrival", 1664, 1669),
]
APPROACHES = {
    "00-23": (73, "official-region5-replay/a-0072.bin"),
    "00-0a": (1551, "official-region5-replay/a-1550.bin"),
    "00-0b": (1554, "rec-s19-to-0b/start.bin"),
    "00-2a": (1665, "rec-s19-to-2a/start.bin"),
}
ENDPOINT = dict(frame=55206, map="00-2a", entry=0, cell=[5, 8], story=19,
                daa=[0x52, 0x06], d284=[4, 1], bank=4, mode=0, dialogue=0,
                facing=1, script=0)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def publish(name, data):
    target = INTEGRATION / name
    pending = target.with_suffix(".partial")
    pending.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(target)


def frame_count(actions):
    return sum(action[1] + action[2] for action in actions)


def endpoint_flags(path, observation):
    save = path.read_bytes()
    high = lambda address: 199440 + address - 0xff80
    work = lambda address: 147568 + address - 0xc000
    word = lambda address: int.from_bytes(save[high(address):high(address) + 2],
                                           "little", signed=True)
    x, y = observation["camera"]
    py, px, _, facing, *_ = observation["player"]
    return {**{k: observation[k] for k in ("frame", "map", "story", "bank", "mode", "dialogue")},
            "entry": save[high(0xff9c)], "facing": facing, "script": save[high(0xffd6)],
            "cell": [2*x + (word(0xffae) + px - 8)/16, 2*y + (word(0xffb0) + py - 16)/16],
            "daa": list(save[work(0xdaa1):work(0xdaa1) + 2]),
            "d284": list(save[work(0xd284):work(0xd284) + 2])}


def validate_replay(spec, action_count, total_frames, pinned):
    source, actions_file, result_file, frames_file = (
        ROOT / spec[key] for key in ("source", "actions", "result", "frames")
    )
    evidence = result_file.parent
    actions = read(actions_file)
    result = read(result_file)
    action_files = [evidence / name for name in ("actions.json", "planned-actions.json")]
    saves = []
    assert result["status"] == "COMPLETE" and not result["errors"]
    assert sha(source) == result["sourceSHA256"]
    assert len(actions) == action_count and frame_count(actions) == total_frames
    assert all(actions == read(file) for file in action_files)
    ends = list(accumulate((hold + wait for _, hold, wait in actions), initial=0))
    assert all(a < b for a, b in zip(ends, ends[1:]))
    with frames_file.open(encoding="utf-8") as log:
        observations = [row for line in log if (row := json.loads(line))["type"] == "frame"]
    assert len(observations) == total_frames
    base = spec["indexBase"]
    for i, (start, end) in enumerate(zip(ends, ends[1:])):
        for frame, row in enumerate(observations[start:end], start + 1):
            assert (row["frame"], row["index"]) == (frame, i + base)
    records = result["records"]
    assert len(records) == (52 if base == 1 else action_count)
    assert len({r["frame"] for r in records}) == len(records)
    assert result["end"] == records[-1]
    assert result["initial"]["frame"] == 0
    initial_save = evidence / "initial.bin"
    assert sha(initial_save) == result["initial"]["stateSHA256"]
    saves.append(initial_save)
    for record in records:
        name, index, frame = (record[key] for key in ("name", "index", "frame"))
        save = evidence / (name + ".bin")
        assert sha(save) == record["stateSHA256"], save
        saves.append(save)
        if name == "initial":
            assert frame == 0
            continue
        i = index - base
        assert actions[i] == record.get("action", actions[i])
        if name.startswith("frame-"):
            assert base == 1 and ends[i] < frame <= ends[i + 1]
            assert name == f"frame-{frame:06d}"
        else:
            assert frame == ends[i + 1]
        observed = observations[frame - 1]
        for key in ("map", "story", "ticks", "mode", "bank", "dialogue", "player", "camera", "scroll"):
            assert record[key] == observed[key], (name, key)
    pinned.update([source, actions_file, result_file, frames_file, *action_files, *saves])
    if (start_copy := evidence / "start.bin").is_file():
        assert sha(start_copy) == sha(source)
        pinned.add(start_copy)
    return actions, ends, observations, result


def main():
    provenance = read(INTEGRATION / "provenance.json")
    official = dict(name="official-region5", source=relative(START), actions=relative(ACTIONS),
                    result=relative(EVIDENCE / "result.json"), frames=relative(EVIDENCE / "frames.jsonl"),
                    indexBase=1, contacts={map_id: n - 1 for map_id, n in CONTACTS.items()},
                    endpoint=ENDPOINT)
    old = read(M9_PLAN)
    region4 = {key: value for key, value in old["official"].items() if key != "contacts"}
    region4["indexBase"] = 0
    pinned = {M9_PLAN, M9_PERF}
    actions, ends, observations, evidence = validate_replay(official, 1669, 55206, pinned)
    assert evidence["sourceSHA256"] == START_SHA
    assert endpoint_flags(EVIDENCE / "end.bin", evidence["end"]) == ENDPOINT
    old_actions, _, _, old_evidence = validate_replay(region4, 262, 14572, pinned)
    assert old_evidence["end"]["stateSHA256"] == START_SHA

    for map_id, n in CONTACTS.items():
        row = observations[ends[n] - 1]
        assert (row["map"], row["mode"], row["dialogue"], row["bank"]) == (
            map_id, 0, 0, 4 if map_id == ENDPOINT["map"] else 5)
    assert all(last < first for (_, _, last), (_, first, _) in zip(CLIPS, CLIPS[1:]))
    assert CLIPS[-1][2] == len(actions)
    clips = [dict(name=name, first=first - 1, last=last - 1, nativeFrames=ends[last] - ends[first - 1])
             for name, first, last in CLIPS]

    qa_path = ROOT / old["oldQA"]
    history = read(qa_path)
    pinned.add(qa_path)
    pinned.update(Path(route["source"]) for route in history)
    qa_totals = dict(routes=len(history) + 2, actions=len(actions) + len(old_actions) +
                     sum(len(route["actions"]) for route in history),
                     frames=frame_count(actions) + frame_count(old_actions) +
                     sum(frame_count(route["actions"]) for route in history))
    assert qa_totals == dict(routes=35, actions=3027, frames=153913)
    assert len({official["name"], region4["name"], *(r["name"] for r in history)}) == qa_totals["routes"]

    perf = [{**route, "controls": ["m9"]} for route in old["perf"]]
    assert len(perf) == 17
    prior = read(M9_PERF)
    assert {(r["mode"], r["route"]) for r in prior["comparisons"]} == {
        (mode, route["id"]) for mode in ("legacy", "cold") for route in perf
    }
    for map_id, (offset, file) in APPROACHES.items():
        source = CHAIN / file
        replay = actions[offset:]
        if frame_count(replay) < 1792:
            replay = [*replay, [None, 1792, 0]]
        perf.append(dict(id=f"region5-{map_id}", target=map_id, source=relative(source),
                         firstAction=offset, actions=replay, controls=["m9"]))
    assert len({route["id"] for route in perf}) == len(perf) == 21
    assert all(action[1] > 0 and action[2] >= 0 for route in perf for action in route["actions"])
    pinned.update(ROOT / route["source"] for route in perf)

    runtime = {}
    for base, key in ((M9, "m9RuntimeSHA256"), (WORK, "m10RuntimeSHA256")):
        root = base / "runtime"
        expected = provenance[key]
        assert set(expected) == {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        for name, digest in expected.items():
            file = root / name
            assert sha(file) == digest, file
            runtime[relative(file)] = digest
    new_maps = [row["id"] for row in provenance["newMaps"]]
    assert set(new_maps) == set(APPROACHES)
    pinned.update(ROOT / row[key] for row in provenance["newMaps"]
                  for key in ("source", "originalCLIMetadata"))
    pinned.update([WORK / "region5-scope.json", WORK / "art/batch-manifest.json",
                   WORK / "art/REGION5_PLATE_SHEET.md", INTEGRATION / "provenance.json"])
    pinned.update(WORK / "scripts" / name for name in (
        "prepare-outer.py", "prepare_art_ref.py", "integrate.py", "outer-common.cjs",
        "coverage-attribution.cjs", "region5-qa.cjs", "region5-perf.cjs",
        "region5-perf-summary.py", "region5-preview.cjs", "region5-contact.py", "run-region5-outer.sh"))
    publish("outer-plan.json", dict(official=official, region4Regression=region4,
                                   newMaps=new_maps, oldQA=relative(qa_path), qaTotals=qa_totals,
                                   perf=perf, savedM9=relative(M9_PERF), clips=clips))
    pinned.add(INTEGRATION / "outer-plan.json")
    publish("outer-freeze.json", {**runtime, **{relative(p): sha(p) for p in sorted(pinned)}})
    print("Verified 1669 official actions, 55206 frames, 52 saved checkpoints and the story-19 endpoint.")
    print(f"Frozen {len(runtime)} runtime files, {len(pinned)} inputs, {qa_totals['routes']} QA routes and 21 perf routes.")


if __name__ == "__main__":
    main()
