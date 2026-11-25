"""Validate the accepted replays, then freeze the M12 supervisor run inputs."""

import hashlib
import json
from itertools import accumulate
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "m12-work"
M11 = ROOT / "m11-work"
INTEGRATION = WORK / "integration"
EVIDENCE = WORK / "play/region7-official"
START = M11 / "official-chain/official-region6-replay/end.bin"
START_SHA = "f8e87d6ae1b9b23261c2e0a2800151391dd93aed3bd0c4b6267985d32e22f428"
ACTIONS = WORK / "official-chain/official-region7-actions.json"
M11_PLAN = M11 / "integration/outer-plan.json"
M11_FREEZE = M11 / "integration/outer-freeze.json"
M11_PERF = M11 / "results/m11-region6-20261122T033051767758133Z/perf/comparison.json"
M11_HANDOVER = M11 / "official-chain/official-region6-replay/end.bin"
FRAMES_PER_SAMPLE = 1792

# Action numbers in the accepted one-based browser log.
CONTACTS = {"00-2e":73,"00-2f":244,"00-30":690,"00-19":827,"00-17":850,"00-12":880,
            "00-08":950,"00-00":1050,"00-09":1100,"00-0b":1200,"00-2d":1328}
CLIPS = [
 ("Story 23 in Stone Cave",56,59,{"00-2e"}),
 ("First prison key",236,240,{"00-2f"}),
 ("Freeing 戴宗",418,421,{"00-2e"}),
 ("Second prison key",626,630,{"00-2f"}),
 ("Returning through the stone corridor",703,710,{"00-30","00-2e"}),
 ("Arrival at the forest gate",1302,1306,{"00-2d"}),
 ("Settled endpoint",1325,1328,{"00-2d"}),
]
APPROACHES = {"00-2f":"action-0150","00-30":"action-0650","00-2d":"frame-069435"}
ENDPOINT = dict(frame=70186,map="00-2d",entry=0,cell=[7,8],story=24,bank=5,mode=0,
                dialogue=0,facing=0,script=0,banner=0,settled=True,
                DAA=["e6","52","be","33"], D2AC=["10","01"], D284=["06","01","07","01"],
                party=["02","17","24","6a","03"], hp=[0,0,25,27,34])
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


def validate_replay(spec, action_count, total_frames, record_count, pinned):
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
    assert len(records) == record_count
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
            assert frame == 0 and record == result["initial"]
            continue
        i = index - base
        assert actions[i] == record.get("action", actions[i])
        if name.startswith("frame-"):
            assert base == 1 and ends[i] < frame <= ends[i + 1]
            assert name == f"frame-{frame:06d}"
        else:
            assert frame == ends[i + 1]
        observed = observations[frame - 1]
        for key in ("map", "story", "ticks", "mode", "bank", "dialogue", "player", "camera", "scroll",
                    "entry", "cell", "facing", "script", "banner", "settled", "DAA", "D2AC", "D284", "party", "hp"):
            if key not in observed:
                continue
            assert record[key] == observed[key], (name, key)
    pinned.update([source, actions_file, result_file, frames_file, *action_files, *saves])
    if (start_copy := evidence / "start.bin").is_file():
        assert sha(start_copy) == sha(source)
        pinned.add(start_copy)
    return actions, ends, observations, result


def preview_clips(ends, observations):
    assert all(last < first for (_, _, last, _), (_, first, _, _) in zip(CLIPS, CLIPS[1:]))
    assert CLIPS[-1][2] == len(ends) - 1
    clips = []
    for name, first, last, maps in CLIPS:
        start, end = ends[first - 1], ends[last]
        rows = observations[start:end]
        assert maps <= {row["map"] for row in rows}, name
        assert all(row["mode"] == 0 and row["bank"] not in (0x2b, 0x2c, 0x2d)
                   for row in rows), name
        clips.append(dict(name=name, first=first - 1, last=last - 1, nativeFrames=end - start,
                          startFrame=start, endFrame=end, expectedMaps=sorted(maps)))
    return clips


def perf_routes(old, actions, ends, observations, records, pinned):
    inherited = [{**route, "controls": ["m11"]} for route in old["perf"]]
    assert len(inherited) == 27
    prior = read(M11_PERF)
    assert prior["samples"] == 324 and not prior["nativeMismatches"]
    assert {(row["mode"], row["route"]) for row in prior["comparisons"]} == {
        (mode, route["id"]) for mode in ("legacy", "cold") for route in inherited
    }
    by_name = {row["name"]: row for row in records}
    perf = inherited[:]
    for map_id, name in APPROACHES.items():
        record = by_name[name]
        index, frame = record["index"], record["frame"]
        suffix = ends[index] - frame
        replay = actions[index:]
        if suffix:
            # These two transition saves are already in the released-key phase.
            assert frame >= ends[index - 1] + actions[index - 1][1]
            replay = [[None, suffix, 0], *replay]
        remaining = FRAMES_PER_SAMPLE
        window = []
        for key, hold, wait in replay:
            hold = min(hold, remaining)
            wait = min(wait, remaining - hold)
            window.append([key, hold, wait])
            remaining -= hold + wait
            if remaining == 0:
                break
        if remaining:
            window.append([None, remaining, 0])
        first_target = next(i for i, row in enumerate(observations[frame:frame + FRAMES_PER_SAMPLE], 1)
                            if row["map"] == map_id)
        perf.append(dict(id=f"region7-{map_id}", target=map_id,
                         source=relative(EVIDENCE / (name + ".bin")), sourceFrame=frame,
                         nextAction=index, releasedFramesBeforeNextAction=suffix, coldFirstTarget=first_target,
                         actions=window, controls=["m11"], allowRow4=True))
    assert len({route["id"] for route in perf}) == len(perf) == 30
    assert all(hold > 0 and wait >= 0 for route in perf for _, hold, wait in route["actions"])
    pinned.update(ROOT / route["source"] for route in perf)
    return perf


def main():
    provenance_path = INTEGRATION / "provenance.json"
    provenance = read(provenance_path)
    official = dict(name="official-region7", source=relative(START), sourceSHA256=START_SHA,
                    actions=relative(ACTIONS), result=relative(EVIDENCE / "result.json"),
                    frames=relative(EVIDENCE / "frames.jsonl"), indexBase=1,
                    contacts={map_id: n - 1 for map_id, n in CONTACTS.items()}, endpoint=ENDPOINT)
    old = read(M11_PLAN)
    region6 = {key: value for key, value in old["official"].items() if key != "contacts"}
    region5 = old["region5Regression"]
    region4 = old["region4Regression"]
    pinned = {M11_PLAN, M11_FREEZE, M11_PERF, M11_HANDOVER, START, WORK / "official-chain/official-region7-replay/end.bin"}

    actions, ends, observations, evidence = validate_replay(official, 1328, 70186, 43, pinned)
    assert (evidence["totalActions"], evidence["totalFrames"]) == (1328, 70186)
    assert sha(START) == sha(M11_HANDOVER) == evidence["sourceSHA256"] == START_SHA
    assert ENDPOINT == {key: evidence["end"][key] for key in ENDPOINT}
    assert sha(ACTIONS) == "406c3574987d1270d0d90c5d615330ddebda00322ff0866708676c8e16cd6f3c"
    assert sha(WORK / "official-chain/official-region7-replay/end.bin") == "4efec8a79dc2f305e812df5533da3632bb062a3281637989057af7a8b6340af8"
    for map_id, n in CONTACTS.items():
        row = observations[ends[n] - 1]
        assert row["map"] == map_id and row["settled"], (map_id, n)

    r6_actions, _, _, r6_evidence = validate_replay(region6, 717, 63131, 42, pinned)
    r5_actions, _, _, r5_evidence = validate_replay(region5, 1669, 55206, 52, pinned)
    r4_actions, _, _, r4_evidence = validate_replay(region4, 262, 14572, 262, pinned)
    assert r4_evidence["end"]["stateSHA256"] == r5_evidence["sourceSHA256"]
    assert endpoint_flags(ROOT / region5["result"].replace("result.json", "end.bin"),
                          r5_evidence["end"]) == region5["endpoint"]
    for key in ("map", "story", "ticks", "mode", "bank", "dialogue", "player", "camera", "scroll"):
        assert evidence["initial"][key] == r6_evidence["end"][key], key

    qa_path = ROOT / old["oldQA"]
    history = read(qa_path)
    pinned.add(qa_path)
    pinned.update(ROOT / route["source"] for route in history)
    qa_totals = dict(routes=len(history) + 4,
                     actions=len(actions) + len(r6_actions) + len(r5_actions) + len(r4_actions) +
                     sum(len(route["actions"]) for route in history),
                     frames=frame_count(actions) + frame_count(r6_actions) + frame_count(r5_actions) + frame_count(r4_actions) +
                     sum(frame_count(route["actions"]) for route in history))
    assert qa_totals == dict(routes=37, actions=5072, frames=287230)
    assert len({official["name"], region6["name"], region5["name"], region4["name"],
                *(route["name"] for route in history)}) == qa_totals["routes"]
    perf = perf_routes(old, actions, ends, observations, evidence["records"], pinned)
    clips = preview_clips(ends, observations)

    runtime = {}
    m11_hashes = read(M11_FREEZE)
    assert len(m11_hashes) == 674
    for name, digest in m11_hashes.items():
        assert sha(ROOT / name) == digest, name
    for base, key in ((M11, "m11RuntimeSHA256"), (WORK, "m12RuntimeSHA256")):
        root = base / "runtime"
        expected = provenance[key]
        assert set(expected) == {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        for name, digest in expected.items():
            file = root / name
            assert sha(file) == digest, file
            if base == M11:
                assert m11_hashes[relative(file)] == digest, file
            runtime[relative(file)] = digest
    for file in pinned:
        if relative(file) in m11_hashes:
            assert sha(file) == m11_hashes[relative(file)], file
    new_maps = [row["id"] for row in provenance["newMaps"]]
    assert set(new_maps) == set(APPROACHES)
    assert set(CONTACTS) == set(new_maps) | {row["id"] for row in provenance["reusedMaps"]}
    unplated_maps = sorted({row["map"] for row in observations} - CONTACTS.keys())
    pinned.update(ROOT / row[key] for row in provenance["newMaps"]
                  for key in ("source", "originalCLIMetadata"))
    pinned.update(ROOT / row["source"] for row in provenance["reusedMaps"])
    scope_path = WORK / "region7-scope.json"
    pinned.update(ROOT / row["nativePNG"] for row in read(scope_path)["maps"])
    pinned.update([scope_path, provenance_path, WORK / "art/batch-manifest.json",
                   WORK / "outer-runs/m12-region7-watch-resume.sh"])
    pinned.update(WORK / "scripts" / name for name in (
        "prepare-outer.py", "prepare-art.py", "integrate.py", "outer-common.cjs",
        "coverage-attribution.cjs", "region7-qa.cjs", "region7-perf.cjs",
        "region7-perf-summary.py", "region7-preview.cjs", "region7-contact.py", "run-region7-outer.sh"))
    publish("outer-plan.json", dict(official=official, region6Regression=region6, region5Regression=region5,
                                   region4Regression=region4, newMaps=new_maps,
                                   unplatedOfficialMaps=unplated_maps, oldQA=relative(qa_path),
                                   qaTotals=qa_totals, perf=perf, savedM11=relative(M11_PERF), clips=clips))
    pinned.add(INTEGRATION / "outer-plan.json")
    publish("outer-freeze.json", {**m11_hashes, **runtime, **{relative(p): sha(p) for p in sorted(pinned)}})
    print("Verified 1328 official actions, 70186 frames, 43 records and the story-24 endpoint.")
    print(f"Frozen {len(runtime)} runtime files and {len(pinned)} inputs for 37 QA routes and 30 perf routes.")


if __name__ == "__main__":
    main()
