// Byte arithmetic/cache ownership test; no browser raster/performance claim.
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
function url(n){return 'data:text/javascript;base64,'+Buffer.from(fs.readFileSync(path.join(root,n),'utf8').replace(/from '(\.\/[^']+)'/g,(_,p)=>`from '${url(p.slice(2))}'`)).toString('base64');}
class Data{constructor(w,h){this.width=w;this.height=h;this.data=new Uint8ClampedArray(w*h*4);}}
let reads=0;
class Canvas{getContext(){return this.ctx??={drawImage:im=>this.data=im.data.slice(),getImageData:()=>{reads++;const d=new Data(this.width,this.height);d.data.set(this.data);return d;},putImageData:d=>this.data=d.data.slice()};}}
global.ImageData=Data;global.document={createElement:()=>new Canvas()};
(async()=>{const {MapRenderer}=await import(url('map-renderer.js')),r=new MapRenderer();const image={width:256,height:1,data:new Uint8ClampedArray(1024)};for(let i=0;i<256;i++)image.data.set([i,255-i,(i*17)%256,i],i*4);r.dialogue=image;r.maps=[];await r.warmup(()=>{});assert.equal(reads,1);assert.equal(r.uiCache,undefined);
 const base=[248,248,248,248,144,144,120,0,0,0,0,0],saved=[];
 for(let k=0;k<65;k++){const palettes=new Array(128).fill(255);for(let i=96;i<112;i++)palettes[i]=(k*31+i*17)%256;if(k===64)for(let i=0;i<4;i++)for(let ch=0;ch<3;ch++)palettes[96+i*4+ch]=base[i*3+ch];const expected=image.data.slice();for(let ch=0;ch<3;ch++){let sx=0,sy=0,sxx=0,sxy=0;for(let i=0;i<4;i++){const x=base[i*3+ch],y=palettes[96+i*4+ch];sx+=x;sy+=y;sxx+=x*x;sxy+=x*y;}const den=4*sxx-sx*sx,a=den?(4*sxy-sx*sy)/den:1,b=(sy-a*sx)/4;if(Math.abs(a-1)<.0001&&Math.abs(b)<.0001)continue;for(let i=ch;i<expected.length;i+=4)expected[i]=Math.max(0,Math.min(255,a*expected[i]+b));}
 const c=r.dialogueImage({palettes});assert.deepEqual(c.data,expected);assert.equal(r.dialogueImage({palettes}),c);saved.push([c,expected]);assert.ok(r.uiCache.size<=8);}
 for(const [c,expected]of saved)assert.deepEqual(c.data,expected,'evicted/cached canvas retains pixels');assert.deepEqual(r.dialoguePixels.data,image.data);assert.equal(reads,1);
 console.log(JSON.stringify({pass:true,palettes:65,sourceBytes:1024,readbacks:reads,retainedCanvasChecks:65,cacheLimit:8}));
})().catch(e=>{console.error(e);process.exitCode=1;});
