/* MARKYS FIGHT: carregador de sprites por personagem, sem substituir a arte original.
   Spritesheets PNG/WebP: quadros de tamanho fixo em grade, da esquerda para direita.
   Exemplo: {file:"walk.png",frames:8,columns:4,fps:12,frameWidth:128,frameHeight:192}
*/
(()=>{'use strict';
const names=['idle','walk','run','jump','fall','crouch','guard','crouchGuard','punchFront','punchBack','kickFront','kickBack','hurt','knockdown','getup','magic1','magic2','magic3','special'];
const characters=new Map();
const ASSET_VERSION='20261120-sprites-cenarios-1';
function safeFile(file){return typeof file==='string'&&/^[a-z0-9_-]+\.(png|webp)$/i.test(file)}
function normalize(def){
 if(!def||!safeFile(def.file))return null;
 const frames=Number(def.frames),columns=Number(def.columns??frames),fps=Number(def.fps),width=Number(def.frameWidth),height=Number(def.frameHeight);
 if(![frames,columns,width,height].every(Number.isInteger)||frames<1||frames>240||columns<1||columns>240||width<1||width>2048||height<1||height>2048||!Number.isFinite(fps)||fps<=0||fps>120)return null;
 return {file:def.file,frames,columns,fps,width,height,loop:def.loop!==false,offsetX:Number.isFinite(def.offsetX)?def.offsetX:0,offsetY:Number.isFinite(def.offsetY)?def.offsetY:0,scale:Number.isFinite(def.scale)&&def.scale>0&&def.scale<=3?def.scale:1};
}
async function load(name){
 if(characters.has(name))return characters.get(name).promise;
 const entry={status:'loading',animations:{},errors:[],promise:null};
 characters.set(name,entry);
 entry.promise=(async()=>{
  try{
   const response=await fetch('personagens/'+encodeURIComponent(name)+'/config.json?v='+ASSET_VERSION,{cache:'no-store'});
   if(!response.ok)throw Error('HTTP '+response.status);
   const config=await response.json();
   const jobs=[];
   for(const state of names){
    const raw=config.animations?.[state];if(raw==null)continue;
    const def=normalize(raw);
    if(!def){entry.errors.push(state+': configuração inválida');continue}
    const image=new Image();
    const animation={...def,image,ready:false};
    entry.animations[state]=animation;
    jobs.push(new Promise(resolve=>{
     image.onload=()=>{
      const rows=Math.ceil(def.frames/def.columns);
      if(image.naturalWidth<def.columns*def.width||image.naturalHeight<rows*def.height)entry.errors.push(state+': dimensões incompatíveis');
      else animation.ready=true;
      resolve();
     };
     image.onerror=()=>{entry.errors.push(state+': arquivo não carregado');resolve()};
     image.src='personagens/'+encodeURIComponent(name)+'/sprites/'+def.file+'?v='+ASSET_VERSION;
    }));
   }
   await Promise.all(jobs);
   entry.status=entry.errors.length?'partial':'ready';
  }catch(err){entry.status='fallback';entry.errors.push(String(err.message||err))}
  return entry;
 })();
 return entry.promise;
}
function draw(ctx,f,state,x,y,w,h){
 const a=characters.get(f.name)?.animations[state];if(!a?.ready)return false;
 const elapsed=Math.max(0,Number(f.animClock)||0);
 const index=a.loop?Math.floor(elapsed*a.fps)%a.frames:Math.min(a.frames-1,Math.floor(elapsed*a.fps));
 const col=index%a.columns,row=Math.floor(index/a.columns);
 // Ancorar os pés na base da caixa de colisão: margens vazias do PNG
 // não podem deixar o lutador flutuando no meio da arena.
 const sx=col*a.width,sy=row*a.height;
 if(!a.bounds)a.bounds={};
 let bounds=a.bounds[index];
 if(!bounds){
  const off=document.createElement('canvas');off.width=a.width;off.height=a.height;
  const oc=off.getContext('2d',{willReadFrequently:true});
  oc.drawImage(a.image,sx,sy,a.width,a.height,0,0,a.width,a.height);
  const pixels=oc.getImageData(0,0,a.width,a.height).data;
  let left=a.width,right=-1,top=a.height,bottom=-1;
  for(let py=0;py<a.height;py++)for(let px=0;px<a.width;px++){
   if(pixels[(py*a.width+px)*4+3]<24)continue;
   if(px<left)left=px;if(px>right)right=px;
   if(py<top)top=py;if(py>bottom)bottom=py;
  }
  bounds=right>=left?{x:left,y:top,w:right-left+1,h:bottom-top+1}:{x:0,y:0,w:a.width,h:a.height};
  a.bounds[index]=bounds;
 }
 const dh=h*a.scale,dw=Math.min(w*a.scale,dh*bounds.w/bounds.h);
 ctx.drawImage(a.image,sx+bounds.x,sy+bounds.y,bounds.w,bounds.h,x+(w-dw)/2+a.offsetX,y+h-dh+a.offsetY,dw,dh);
 return true;
}
function report(name){const e=characters.get(name);return e?{status:e.status,ready:Object.keys(e.animations).filter(k=>e.animations[k].ready),errors:[...e.errors]}:{status:'not-loaded',ready:[],errors:[]}}
window.markysSprites={load,draw,report,status:name=>report(name).status,normalize,version:ASSET_VERSION};
})();
