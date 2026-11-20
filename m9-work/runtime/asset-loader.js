// Decoding and raster preparation finish before the game can run. No core steps.
const images=new Map();
let report=()=>{},complete=0,total=0;
export function setAssetProgress(fn){report=fn;}
export function loadImage(src){
 if(images.has(src))return images.get(src);
 total++;report(complete,total,src);
 const task=(async()=>{const im=new Image();im.decoding='async';
 await new Promise((resolve,reject)=>{im.onload=resolve;im.onerror=()=>reject(Error('图像载入失败：'+src));im.src=src;});
 if(im.decode)await im.decode();complete++;report(complete,total,src);return im;
 })();images.set(src,task);return task;
}
export const yieldStartup=()=>new Promise(resolve=>setTimeout(resolve,0));
// Default canvas resampling matches M5's authored HD rasterization exactly.
export function rasterize(image,w,h){const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;const g=canvas.getContext('2d');g.drawImage(image,0,0,w,h);return {canvas,pixels:g.getImageData(0,0,w,h)};}
// Uint8ClampedArray implements the same ties-to-even conversion as ImageData.
export function colorTables(fit){return fit.map(([a,b])=>{const t=new Uint8ClampedArray(256);for(let i=0;i<256;i++)t[i]=Math.max(0,Math.min(255,a*i+b));return t;});}
export function recolor(source,target,tables){const [r,g,b]=tables;for(let i=0;i<target.length;i+=4){target[i]=r[source[i]];target[i+1]=g[source[i+1]];target[i+2]=b[source[i+2]];target[i+3]=source[i+3];}}
