const {fs,path,W,output,sha}=require('./common.cjs');
const assert=require('node:assert/strict'),{gunzipSync}=require('node:zlib');
const legacyGap='legacy map renderer: uncertified native background';
const unknownGap='native background: audit reason unavailable';

function gapReason(frame,tile){
  if(typeof tile.reason==='string'&&tile.reason.trim())return tile.reason;
  return !frame.mapResult?.mapId&&Array.isArray(tile.screenBounds)?legacyGap:unknownGap;
}

function exclusion(frame){
  return frame.mode!==0||[0x2b,0x2c,0x2d].includes(frame.bank)
    ?'mode='+frame.mode+'/bank='+frame.bank.toString(16):null;
}

function addRegion3Coverage(totals,u){
  const world=totals[u.map]??={frames:0,eligible:0,covered:0,gap:0,nativeGap:0,otherHD:0,reasons:{}};
  const samePlate=u.sourcePixels[u.map]||0,otherHD=u.coverage.covered-samePlate;
  const attributed=Object.values(u.sourcePixels).reduce((a,b)=>a+b,0);
  if(otherHD<0||(u.mapResult?.mapId&&attributed!==u.coverage.covered))throw Error('Invalid plate attribution '+u.map);
  world.frames++;world.eligible+=u.coverage.eligible;world.covered+=samePlate;
  world.gap+=u.coverage.eligible-samePlate;world.nativeGap+=u.coverage.gap;world.otherHD+=otherHD;
  const add=(reason,pixels)=>world.reasons[reason]=(world.reasons[reason]||0)+pixels;
  let remainder=u.coverage.gap;
  for(const tile of u.mapResult?.uncoveredTiles||[]){
    add(gapReason(u,tile),tile.pixels);
    remainder-=tile.pixels;
  }
  if(remainder>0)add(u.mapResult?.mapId?'native gap outside region audit':'no certified region source: '+u.scene,remainder);
  if(otherHD>0)add('other verified HD source: '+(u.mapResult?.mapId?'map/history':'other scene '+u.scene),otherHD);
}

// Recount from finished QA dumps and write a separate attribution report.
function derive(){
  const out=output(),qaDir=path.join(out,'qa');
  const reportBytes=fs.readFileSync(path.join(qaDir,'report.json'));
  const report=JSON.parse(reportBytes);
  assert(fs.existsSync(path.join(out,'qa.done'))&&report.pass&&!report.errors.length,'Completed QA required');
  const routes=JSON.parse(fs.readFileSync(W+'/inputs/qa-routes.json'));
  const maps=new Set(JSON.parse(fs.readFileSync(W+'/inputs/route-disclosures.json')).newMapIDs);
  const region3Coverage={},region3Excluded={},reclassifiedUndefined={};
  let actions=0,frames=0;
  assert.equal(routes.length,report.routes.length);
  for(const [routeIndex,route] of routes.entries()){
    const previous=report.routes[routeIndex];
    assert.equal(previous.name,route.name);
    assert.equal(previous.actions,route.actions.length);
    let routeFrames=0;
    for(const [i,input] of route.actions.entries()){
      const file=path.join(qaDir,route.name+'-'+String(i).padStart(4,'0')+'.json.gz');
      const dump=JSON.parse(gunzipSync(fs.readFileSync(file)));
      assert.deepEqual(dump.input,input,file);
      const rows=dump.candidate.rows;
      assert.equal(rows.length,input[1]+input[2],file);
      actions++;routeFrames+=rows.length;
      for(const u of rows){
        if(!maps.has(u.map))continue;
        const excluded=exclusion(u);
        if(excluded){
          const counts=region3Excluded[u.map]??={};
          counts[excluded]=(counts[excluded]||0)+1;
          continue;
        }
        addRegion3Coverage(region3Coverage,u);
        const unlabelled=(u.mapResult?.uncoveredTiles||[]).filter(tile=>tile.reason===undefined);
        if(unlabelled.length){
          const row=reclassifiedUndefined[u.map]??={frames:0,pixels:0,byRoute:{}};
          const pixels=unlabelled.reduce((n,tile)=>n+tile.pixels,0);
          row.frames++;row.pixels+=pixels;
          row.byRoute[route.name]=(row.byRoute[route.name]||0)+pixels;
        }
      }
    }
    assert.equal(routeFrames,previous.frames,route.name);
    frames+=routeFrames;
  }
  assert.equal(actions,report.actions);
  assert.equal(frames,report.frames);
  assert.deepEqual(region3Excluded,report.region3Excluded);
  assert.deepEqual(Object.keys(region3Coverage).sort(),Object.keys(report.region3Coverage).sort());
  for(const [id,{reasons,...counts}] of Object.entries(region3Coverage)){
    const {reasons:oldReasons,...oldCounts}=report.region3Coverage[id];
    assert.deepEqual(counts,oldCounts,id);
    const {undefined:unlabelled=0,...oldNamed}=oldReasons;
    const {[legacyGap]:legacy=0,[unknownGap]:unknown=0,...newNamed}=reasons;
    assert.deepEqual(newNamed,oldNamed,id);
    assert.equal(unlabelled,legacy+unknown,id);
    assert.equal(unlabelled,reclassifiedUndefined[id]?.pixels??0,id);
    assert.equal(Object.values(reasons).reduce((a,b)=>a+b,0),counts.gap,id);
  }
  const derived={qaReportSHA256:sha(reportBytes),actions,frames,region3Coverage,reclassifiedUndefined};
  fs.writeFileSync(path.join(out,'qa-coverage-attribution.json'),JSON.stringify(derived,null,2)+'\n',{flag:'wx'});
  console.log('Reclassified saved QA coverage',actions,'actions',frames,'frames',reclassifiedUndefined);
}

module.exports={gapReason,exclusion,addRegion3Coverage};
if(require.main===module)derive();
