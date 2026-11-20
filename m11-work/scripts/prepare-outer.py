"""Validate the accepted replays, then freeze the M11 supervisor run inputs."""

import hashlib
import json
from itertools import accumulate
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "m11-work"
M10 = ROOT / "m10-work"
INTEGRATION = WORK / "integration"
EVIDENCE = WORK / "play/region6-official"
START = WORK / "checkpoints/story19-00-2a-official.bin"
START_SHA = "c41b4188203bc45d2d0c5eeb24f8b307040be0644ce861ffbcc6281d4060c8f1"
ACTIONS = WORK / "official-chain/official-region6-actions.json"
M10_PLAN = M10 / "integration/outer-plan.json"
M10_FREEZE = M10 / "integration/outer-freeze.json"
M10_PERF = M10 / "results/m10-region5-20261119T021341364667010Z/perf/comparison.json"
M10_HANDOVER = M10 / "official-chain/official-region5-replay/end.bin"
FRAMES_PER_SAMPLE = 1792

# Action numbers in the accepted one-based browser log.
CONTACTS = {"00-25": 694, "00-26": 403, "00-27": 409, "00-28": 614,
            "00-29": 619, "00-2e": 717, "00-2a": 313, "00-0b": 75,
            "00-09": 100, "00-00": 150, "00-06": 175}
CLIPS = [
    ("Row-4 item gate", 311, 317, {"00-2a"}),
    ("Cloud Tower Gate entrance", 347, 358, {"00-25", "00-26"}),
    ("From the Cloister Maze to the Cloud Terrace Maze", 401, 415, {"00-26", "00-27"}),
    ("Cloud Terrace passage", 609, 617, {"00-28"}),
    ("Twin Statue Hall and the fan encounter", 618, 624, {"00-29"}),
    ("Return from the hall", 675, 695, {"00-29", "00-28", "00-27", "00-26", "00-25", "00-2a"}),
    ("Stone Cave arrival and settled endpoint", 714, 717, {"00-2e"}),
]
APPROACHES = {
    "00-25": "action-0350",
    "00-26": "frame-027622",
    "00-27": "action-0400",
    "00-28": "action-0600",
    "00-29": "frame-052345",
    "00-2e": "action-0700",
}
ENDPOINT = dict(frame=63131, map="00-2e", entry=3, cell=[25, 5], story=22, bank=5, mode=0,
                dialogue=0, facing=2, script=0, banner=0, settled=True,
                DAA=["e6", "52", "3e", "30"], D2AC=["10", "01"], D284=["00", "00"],
                party=["02", "17", "24"], hp=[0, 13, 34])


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


def region6_endpoint(path, frame):
    save = path.read_bytes()
    assert len(save) == 199608
    high, work = 199440, 147568

    def read_at(address, size=1):
        offset = high + address - 0xff80 if address >= 0xff80 else work + address - 0xc000
        return save[offset:offset + size]

    def byte(address):
        return read_at(address)[0]

    def signed(address):
        return int.from_bytes(read_at(address, 2), "little", signed=True)

    def hex_bytes(address, size):
        return [f"{value:02x}" for value in read_at(address, size)]

    cell = [2 * byte(0xff96) + (signed(0xffae) + byte(0xcd01) - 8) / 16,
            2 * byte(0xff97) + (signed(0xffb0) + byte(0xcd00) - 16) / 16]
    bank, mode, dialogue = byte(0xd08f), byte(0xd0fa), byte(0xffbc)
    script, banner = byte(0xffd6), byte(0xffc1)
    return dict(frame=frame, map="-".join(hex_bytes(0xff9a, 2)), entry=byte(0xff9c),
                cell=cell, story=byte(0xffba), bank=bank, mode=mode, dialogue=dialogue,
                facing=byte(0xcd03), script=script, banner=banner,
                settled=bank in (3, 4, 5) and not (mode or dialogue or script or banner)
                and all(value.is_integer() for value in cell),
                DAA=hex_bytes(0xdaa0, 4), D2AC=hex_bytes(0xd2ac, 2), D284=hex_bytes(0xd284, 2),
                party=[hex_bytes(addr, 1)[0] for addr in (0xd200, 0xd216, 0xd22c)],
                hp=[int.from_bytes(read_at(addr, 2), "little") for addr in (0xd202, 0xd218, 0xd22e)])


def in_row4(row):
    return row["map"] == "00-2a" and 4 <= row["cell"][1] < 5


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
    assert any(in_row4(row) for row in observations[:clips[0]["endFrame"]])
    return clips


def perf_routes(old, actions, ends, observations, records, pinned):
    inherited = [{**route, "controls": ["m10"]} for route in old["perf"]]
    assert len(inherited) == 21
    prior = read(M10_PERF)
    assert prior["samples"] == 252 and not prior["nativeMismatches"]
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
        perf.append(dict(id=f"region6-{map_id}", target=map_id,
                         source=relative(EVIDENCE / (name + ".bin")), sourceFrame=frame,
                         nextAction=index, releasedFramesBeforeNextAction=suffix, coldFirstTarget=first_target,
                         actions=window, controls=["m10"], allowRow4=True))
    assert len({route["id"] for route in perf}) == len(perf) == 27
    assert all(hold > 0 and wait >= 0 for route in perf for _, hold, wait in route["actions"])
    pinned.update(ROOT / route["source"] for route in perf)
    return perf


def main():
    provenance_path = INTEGRATION / "provenance.json"
    provenance = read(provenance_path)
    official = dict(name="official-region6", source=relative(START), sourceSHA256=START_SHA,
                    actions=relative(ACTIONS), result=relative(EVIDENCE / "result.json"),
                    frames=relative(EVIDENCE / "frames.jsonl"), indexBase=1,
                    contacts={map_id: n - 1 for map_id, n in CONTACTS.items()}, endpoint=ENDPOINT)
    old = read(M10_PLAN)
    region5 = {key: value for key, value in old["official"].items() if key != "contacts"}
    region4 = old["region4Regression"]
    pinned = {M10_PLAN, M10_FREEZE, M10_PERF, M10_HANDOVER, START.with_suffix(".json")}

    actions, ends, observations, evidence = validate_replay(official, 717, 63131, 42, pinned)
    assert (evidence["totalActions"], evidence["totalFrames"]) == (717, 63131)
    assert sha(START) == sha(M10_HANDOVER) == evidence["sourceSHA256"] == START_SHA
    assert ENDPOINT == {key: evidence["end"][key] for key in ENDPOINT}
    assert region6_endpoint(EVIDENCE / "end.bin", evidence["end"]["frame"]) == ENDPOINT
    official["row4Frames"] = sum(in_row4(row) for row in observations)
    assert official["row4Frames"] > 0
    for map_id, n in CONTACTS.items():
        row = observations[ends[n] - 1]
        assert row["map"] == map_id and row["settled"], (map_id, n)

    r5_actions, _, _, r5_evidence = validate_replay(region5, 1669, 55206, 52, pinned)
    r4_actions, _, _, r4_evidence = validate_replay(region4, 262, 14572, 262, pinned)
    assert r4_evidence["end"]["stateSHA256"] == r5_evidence["sourceSHA256"]
    assert endpoint_flags(ROOT / region5["result"].replace("result.json", "end.bin"),
                          r5_evidence["end"]) == region5["endpoint"]
    for key in ("map", "story", "ticks", "mode", "bank", "dialogue", "player", "camera", "scroll"):
        assert evidence["initial"][key] == r5_evidence["end"][key], key

    qa_path = ROOT / old["oldQA"]
    history = read(qa_path)
    pinned.add(qa_path)
    pinned.update(ROOT / route["source"] for route in history)
    qa_totals = dict(routes=len(history) + 3,
                     actions=len(actions) + len(r5_actions) + len(r4_actions) +
                     sum(len(route["actions"]) for route in history),
                     frames=frame_count(actions) + frame_count(r5_actions) + frame_count(r4_actions) +
                     sum(frame_count(route["actions"]) for route in history))
    assert qa_totals == dict(routes=36, actions=3744, frames=217044)
    assert len({official["name"], region5["name"], region4["name"],
                *(route["name"] for route in history)}) == qa_totals["routes"]
    perf = perf_routes(old, actions, ends, observations, evidence["records"], pinned)
    clips = preview_clips(ends, observations)

    runtime = {}
    m10_hashes = read(M10_FREEZE)
    for base, key in ((M10, "m10RuntimeSHA256"), (WORK, "m11RuntimeSHA256")):
        root = base / "runtime"
        expected = provenance[key]
        assert set(expected) == {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        for name, digest in expected.items():
            file = root / name
            assert sha(file) == digest, file
            if base == M10:
                assert m10_hashes[relative(file)] == digest, file
            runtime[relative(file)] = digest
    for file in pinned:
        if relative(file) in m10_hashes:
            assert sha(file) == m10_hashes[relative(file)], file
    new_maps = [row["id"] for row in provenance["newMaps"]]
    assert set(new_maps) == set(APPROACHES)
    assert set(CONTACTS) == set(new_maps) | {row["id"] for row in provenance["reusedMaps"]}
    unplated_maps = sorted({row["map"] for row in observations} - CONTACTS.keys())
    pinned.update(ROOT / row[key] for row in provenance["newMaps"]
                  for key in ("source", "originalCLIMetadata"))
    pinned.update(ROOT / row["source"] for row in provenance["reusedMaps"])
    scope_path = WORK / "region6-scope.json"
    pinned.update(ROOT / row["nativePNG"] for row in read(scope_path)["maps"])
    pinned.update([scope_path, provenance_path, WORK / "art/batch-manifest.json",
                   WORK / "outer-runs/m11-region6-watch-resume.sh"])
    pinned.update(WORK / "scripts" / name for name in (
        "prepare-outer.py", "prepare-art.py", "integrate.py", "outer-common.cjs",
        "coverage-attribution.cjs", "region6-qa.cjs", "region6-perf.cjs",
        "region6-perf-summary.py", "region6-preview.cjs", "region6-contact.py", "run-region6-outer.sh"))
    publish("outer-plan.json", dict(official=official, region5Regression=region5,
                                   region4Regression=region4, newMaps=new_maps,
                                   unplatedOfficialMaps=unplated_maps, oldQA=relative(qa_path),
                                   qaTotals=qa_totals, perf=perf, savedM10=relative(M10_PERF), clips=clips))
    pinned.add(INTEGRATION / "outer-plan.json")
    publish("outer-freeze.json", {**runtime, **{relative(p): sha(p) for p in sorted(pinned)}})
    print("Verified 717 official actions, 63131 frames, 42 saved checkpoints and the story-22 endpoint.")
    print(f"Frozen {len(runtime)} runtime files and {len(pinned)} inputs for 36 QA routes and 27 perf routes.")


if __name__ == "__main__":
    main()
