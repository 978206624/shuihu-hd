// File-only harness: identical frozen WASM/ROM, no server or network.
const fs=require('fs'),path=require('path'),vm=require('vm');
const canvas=require('/opt/sand/sand-host/node_modules/@napi-rs/canvas');
exports.open=async function(root='/workspace/shawu/web'){
 global.document={createElement:kind=>{if(kind!=='canvas')throw Error(kind);return canvas.createCanvas(300,150);}};
 global.Image=class extends canvas.Image {set src(v){super.src=fs.readFileSync(path.join(root,v));}get src(){return super.src;}};
 global.ImageData=canvas.ImageData;
 global.fetch=async name=>{const b=fs.readFileSync(path.join(root,name));return {ok:true,json:async()=>JSON.parse(b),arrayBuffer:async()=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)};};
 vm.runInThisContext(fs.readFileSync(path.join(root,'vendor/binjgb.js'),'utf8'));
 const wasm=new WebAssembly.Module(fs.readFileSync(path.join(root,'vendor/binjgb.wasm')));
 const m=await Binjgb({instantiateWasm:(imports,done)=>{done(new WebAssembly.Instance(wasm,imports),wasm);return {};}});
 const rom=fs.readFileSync(path.join(root,'assets/game.gbc')),rp=m._malloc(rom.length);m.HEAPU8.set(rom,rp);
 const e=m._emulator_new_simple(rp,rom.length,48000,2048,0),joy=m._joypad_new();m._emulator_set_default_joypad_callback(e,joy);
 const {Renderer}=await import('file://'+root+'/renderer.js');
 const screen=canvas.createCanvas(640,576),r=await Renderer.create(screen,m,e);
 const input=(k,on)=>m['_set_joyp_'+k](e,+on);
 const step=(n=1,draw=true)=>{for(let i=0;i<n;i++){const target=m._emulator_get_ticks_f64(e)+70224;let guard=0;while(true){const event=m._emulator_run_until_f64(e,target);if(event&4)break;if(++guard>100)throw Error('core unresponsive');}}if(draw)r.draw(true);};
 const file=kind=>{const f=m[kind==='state'?'_state_file_data_new':'_ext_ram_file_data_new'](e);try{m[kind==='state'?'_emulator_write_state':'_emulator_write_ext_ram'](e,f);const p=m._get_file_data_ptr(f),n=m._get_file_data_size(f);return m.HEAPU8.slice(p,p+n);}finally{m._file_data_delete(f);m._free(f);}};
 step(1);step(3300);input('start',true);step(2);input('start',false);step(120);
 return {m,e,r,screen,input,step,file};
};
