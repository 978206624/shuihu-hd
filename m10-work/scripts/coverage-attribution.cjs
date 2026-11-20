// Same-plate attribution from the M8 outer QA protocol.
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

function addCoverage(totals,u){
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

module.exports={exclusion,addCoverage};
