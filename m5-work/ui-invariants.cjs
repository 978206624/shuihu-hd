// Targeted replay invariants: OAM exact everywhere; UI text exact outside approved lifecycle wipes.
const fs=require('fs'),assert=require('assert');
(async()=>{const a=await require('./offline-runtime.cjs').open();const targets=[361,362,4767,7703,11530,18360,18361];let rows=[];
for(let f=0;f<=targets.at(-1);f++){a.input('A',f%120<2);a.step(1,targets.some(t=>f>=t-12&&f<=t));if(!targets.includes(f))continue;
const o=a.r.observation,p=a.r.pixels(),out=a.screen.getContext('2d').getImageData(0,0,640,576).data;let actors=0,changed=0;const tr=a.r.meta.mapResult?.uiTransition;const transitioning=i=>tr&&i%160>=tr.rect.x&&i%160<tr.rect.x+tr.rect.w&&(i/160|0)>=tr.rect.y&&(i/160|0)<tr.rect.y+tr.rect.h;
for(let i=0;i<23040;i++)if(o.actorMask[i]||(o.mask[i]&&!transitioning(i)&&![161,162,163,164].includes(o.tiles[(((i/160|0)+o.scy)&255)>>3<<5|(((i%160+o.scx)&255)>>3)]))){actors++;const x=i%160,y=i/160|0;for(let dy=0;dy<4;dy++)for(let dx=0;dx<4;dx++)for(let c=0;c<3;c++)if(out[((y*4+dy)*640+x*4+dx)*4+c]!==p[i*4+c])changed++;}
assert.equal(changed,0,`native actor/text changed at ${f}`);const audit=a.r.audit();rows.push({frame:f,eligible:audit.eligibleBackgroundPixels,gpt:audit.gptBackgroundPixels,gaps:audit.uncoveredBackgroundPixels,actors,changed,border:audit.dialogueBorderPixels,borderCovered:audit.dialogueBorderCoveredPixels});console.log(rows.at(-1));}
fs.writeFileSync(__dirname+'/ui-invariants.json',JSON.stringify(rows,null,2));})().catch(e=>{console.error(e);process.exitCode=1});
