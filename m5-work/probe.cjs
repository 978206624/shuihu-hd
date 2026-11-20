const fs=require('fs');
(async()=>{const a=await require('./offline-runtime.cjs').open();
const targets=[359,360,361,362,363,2061,4767,5300,5380,5411,5440,5476,5486,7703,11530,11630,11631,11632,11633,18027,18360,18361,18370,18703,19722,22000];
for(let f=0;f<=targets.at(-1);f++){
 a.input('A',f%120<2);a.step(1,targets.some(t=>f>=t-8&&f<=t));
 if(targets.includes(f)){const o=a.r.observation;fs.writeFileSync(__dirname+'/probe_'+f+'.json',JSON.stringify({o,p:Array.from(a.r.pixels()),audit:a.r.audit()}));fs.writeFileSync(__dirname+'/probe_'+f+'.png',a.screen.toBuffer('image/png'));console.log(f,a.r.audit().scene,a.r.audit().uncoveredBackgroundPixels);}
}
})().catch(e=>{console.error(e);process.exitCode=1});
