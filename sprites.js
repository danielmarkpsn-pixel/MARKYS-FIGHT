/* MARKYS FIGHT — carregamento opcional de spritesheets por personagem.
   Formato de config.json -> animations:
   "walk": {"file":"walk.png","frames":8,"fps":12,"frameWidth":128,"frameHeight":192}
   "punchFront": {"file":"punch.png","frames":6,"fps":15,"frameWidth":128,"frameHeight":192,"loop":false}
   Frames em linha horizontal. Sem arquivo válido, o jogo preserva o retrato original.
*/
(()=>{'use strict';
const characters=new Map(),supported=['idle','walk','run','jump','fall','crouch','guard','crouchGuard','punchFront','punchBack','kickFront','kickBack','hurt','knockdown','getup','magic1','magic2','magic3','special'];
function safePath(file){return typeof file==='string'&&/^[a-z0-9_./-]+\.(png|webp|gif)$/i.test(file)&&!file.includes('..')&&!file.startsWith('/')}
async function load(name){
 if(characters.has(name))return characters.get(name);
 const result={animations:{},status:'loading'};characters.set(name,result);
 try{
  const response=await fetch('personagens/'+encodeURIComponent(name)+'/config.json');
  if(!response.ok)throw Error('Configuração não encontrada');
  const config=await response.json();
  for(const state of supported){
   const def=config.animations?.[state];
   if(!def||!safePath(def.file))continue;
   const frames=Number(def.frames),fps=Number(def.fps),width=Number(def.frameWidth),height=Number(def.frameHeight);
   if(!Number.isInteger(frames)||frames<1||frames>240||!Number.isFinite(fps)||fps<=0||fps>120||!Number.isInteger(width)||width<1||!Number.isInteger(height)||height<1)continue;
   const img=new Image();img.src='personagens/'+encodeURIComponent(name)+'/sprites/'+def.file;
   result.animations[state]={img,frames,fps,width,height,loop:def.loop!==false};
  }
  result.status='ready';
 }catch(e){result.status='fallback'}
 return result;
}
function draw(ctx,f,state,x,y,w,h){
 const entry=characters.get(f.name)?.animations[state];
 if(!entry||!entry.img.complete||!entry.img.naturalWidth)return false;
 const {img,frames,fps,width,height,loop}=entry;
 if(img.naturalWidth<frames*width||img.naturalHeight<height)return false;
 const frame=loop?Math.floor(f.animClock*fps)%frames:Math.min(frames-1,Math.floor(f.animClock*fps));
 ctx.drawImage(img,frame*width,0,width,height,x,y,w,h);
 return true;
}
window.markysSprites={load,draw,status:name=>characters.get(name)?.status||'not-loaded'};
})();
