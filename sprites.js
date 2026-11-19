/* MARKYS FIGHT: carregador de sprites por personagem, sem substituir a arte original.
   Spritesheets PNG/WebP: quadros de tamanho fixo em grade, da esquerda para direita.
   Exemplo: {file:"walk.png",frames:8,columns:4,fps:12,frameWidth:128,frameHeight:192}
*/
(()=>{'use strict';
const names=['idle','walk','run','jump','fall','crouch','guard','crouchGuard','punchFront','punchBack','kickFront','kickBack','hurt','knockdown','getup','magic1','magic2','magic3','special'];
const characters=new Map();
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
   const response=await fetch('personagens/'+encodeURIComponent(name)+'/config.json');
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
     image.src='personagens/'+encodeURIComponent(name)+'/sprites/'+def.file;
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
 const dw=w*a.scale,dh=h*a.scale;
 ctx.drawImage(a.image,col*a.width,row*a.height,a.width,a.height,x+(w-dw)/2+a.offsetX,y+(h-dh)+a.offsetY,dw,dh);
 return true;
}
function report(name){const e=characters.get(name);return e?{status:e.status,ready:Object.keys(e.animations).filter(k=>e.animations[k].ready),errors:[...e.errors]}:{status:'not-loaded',ready:[],errors:[]}}
window.markysSprites={load,draw,report,status:name=>report(name).status,normalize};
})();
