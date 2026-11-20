const {chromium}=require('playwright');
const fs=require('fs'),assert=require('assert/strict'),crypto=require('crypto'),{spawn}=require('child_process');
const R='/workspace/shawu/m4-work',root=R+'/extracted-final/shuihu-hd-m4',base='http://127.0.0.1:18765';
const hash=x=>crypto.createHash('sha256').update(Buffer.from(x)).digest('hex');
(async()=>{
 const server=spawn('python3',['-m','http.server','18765','--bind','127.0.0.1','--directory',root],{stdio:['ignore','pipe','pipe']});
 let browser;try{
  await new Promise((resolve,reject)=>{let txt='';server.stderr.on('data',x=>{txt+=x;if(txt.includes('Address already in use'))reject(Error('Package test port occupied'));});let tries=0;const timer=setInterval(async()=>{try{if((await fetch(base+'/index.html')).ok){clearInterval(timer);resolve();}}catch{}if(++tries>100){clearInterval(timer);reject(Error('Local server did not start'));}},50);});
  browser=await chromium.launch({args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1180,height:1000}}),errors=[],outbound=[],failed=[],requested=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));
  await page.route('**/*',route=>{const url=route.request().url();requested.push(url);if(url.startsWith(base+'/')||url.startsWith('data:')||url.startsWith('blob:'))route.continue();else{outbound.push(url);route.abort();}});
  page.on('response',r=>{if(r.status()>=400&& !r.url().endsWith('/favicon.ico'))errors.push(r.status()+': '+r.url());});
  await page.goto(base);await page.waitForFunction(()=>window.shuihu?.ready,{timeout:60000});
  const boot=await page.evaluate(()=>shuihu.meta());assert.ok(boot);
  await page.evaluate(()=>{shuihu.setHD(true);shuihu.step(3300);shuihu.input('start',true);shuihu.step(2);shuihu.input('start',false);shuihu.step(120)});
  assert.equal((await page.evaluate(()=>shuihu.audit())).scene,'title');
  await page.locator('#screen').screenshot({path:R+'/package-offline-title.png'});
  await page.evaluate(()=>{for(let f=0;f<360;f++){shuihu.input('A',f%120<2);shuihu.step(1)}shuihu.input('A',false)});
  const actualHash=hash(await page.evaluate(()=>shuihu.state())),baseline=JSON.parse(fs.readFileSync('/workspace/shawu/m3-work/original-state-hashes.json'));assert.equal(actualHash,baseline[2]);
  const audit=await page.evaluate(()=>shuihu.audit());assert.ok(audit.gptBackgroundPixels>0);assert.equal(audit.scene,'interior');
  await page.locator('#screen').screenshot({path:R+'/package-offline-interior.png'});
  assert.deepEqual(errors,[]);assert.deepEqual(outbound,[]);assert.deepEqual(failed,[]);
  const report={pass:true,environment:'Linux headless Chromium; not real Windows execution',source:'clean extraction of shuihu-hd-m4-windows.zip',network:'all non-localhost requests blocked; no external requests attempted',requests:requested.length,originalStateAtFrame360Matches:true,loadedScene:audit.scene,gptBackgroundPixels:audit.gptBackgroundPixels,errors,outbound,failed};
  fs.writeFileSync(R+'/package-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{if(browser)await browser.close();server.kill();}
})().catch(e=>{console.error(e);process.exit(1)});
