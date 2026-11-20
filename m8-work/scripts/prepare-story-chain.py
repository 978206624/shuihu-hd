"""Freeze successful natural inputs; independent surveys remain explicit."""
from pathlib import Path
import json, hashlib, shutil, datetime
R=Path('/workspace/shawu'); W=R/'m8-work'
sha=lambda b:hashlib.sha256(b).hexdigest()
names=['delivered-tavern-exit','delivered-outer-exit','delivered-field-arrival',
 'delivered-field-south-attempt','field-bridge-attempt','field-bottom-attempt',
 'field-bottom-zigzag-attempt','south-village-arrival','south-village-settled',
 'village-sign-start','village-sign-dialogue','village-sign-b','village-first-npc',
 'village-first-npc-pages','village-decline-duel','survey-00-05',
 'room-05-dialogue-replay','room-05-dialogue-pages','room05-wu-dialogue-start',
 'room05-wu-dialogue-pages','room05-wu-near','room05-wu-mission-pages',
 'room05-left-npc-dialogue','room05-left-npc-pages']
start=W/'play/continuous-letter-chain-v1/latest.bin'; previous=start.read_bytes()
actions=[]; segments=[]
for name in names:
    d=W/'play'/name
    assert (d/'start.bin').read_bytes()==previous, f'Broken boundary {name}'
    aa=json.loads((d/'actions.json').read_text()); end=(d/'latest.bin').read_bytes()
    segments.append(dict(directory=str(d.relative_to(R)),startSHA256=sha(previous),
      endSHA256=sha(end),actionOffset=len(actions),actions=len(aa),
      frames=sum(a[1]+a[2] for a in aa)))
    actions.extend(aa); previous=end
assert json.loads((W/'play/room05-left-npc-pages/result.json').read_text())['end']['story']==12
def immutable(path,value):
    text=json.dumps(value,indent=2,ensure_ascii=False)+'\n'
    if path.exists(): assert path.read_text()==text, str(path)
    else: path.write_text(text)
dest=W/'frozen-starts/story11-letter-delivered.bin'
if not dest.exists(): shutil.copy2(start,dest)
assert dest.read_bytes()==start.read_bytes()
immutable(W/'checkpoints/story11-to12-actions.json',actions)
initial=json.loads((W/'checkpoints/letter-natural-actions.json').read_text())
immutable(W/'checkpoints/story9-to12-actions.json',initial+actions)
immutable(W/'checkpoints/story11-to12-segmented.json',dict(
 source=str(start.relative_to(R)),sourceSHA256=sha(start.read_bytes()),
 frozenSource=str(dest.relative_to(R)),allBoundariesByteIdentical=True,
 segments=segments,actions=len(actions),frames=sum(a[1]+a[2] for a in actions),
 segmentedEndSHA256=sha(previous),endStory=12,
 endpoint='吴用要求众人赴黄泥岗客栈会合、乔装掌柜小二设伏；尚未到黄泥岗客栈。',
 notes=['The 19596-frame / 185-action story9-to11 chain was already verified before reboot and is not repeated by this preparation.',
        'survey-00-05 is the one selected doorway replay incorporated into this chain; the other six surveys remain independent.',
        'Several historical directory names guessed 吴用 or letter delivery before the actual dialogue; identity is taken only from native dialogue.',
        'room05-wu-near / room05-wu-mission-pages actually speak to 戴宗; 吴用 is room05-left-npc-dialogue / pages.',
        'Unsuccessful searches and post-letter 大名府 investigation are excluded.']))
print(json.dumps(dict(actions=len(actions),frames=sum(a[1]+a[2] for a in actions),
 segments=len(segments),startSHA256=sha(start.read_bytes()),endSHA256=sha(previous))))
