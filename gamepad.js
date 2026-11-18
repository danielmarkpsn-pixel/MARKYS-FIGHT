/* MARKYS FIGHT — controles padrão Gamepad API (Xbox / PlayStation).
 * Sequências de magia relativas à direção do lutador, com buffer de 1,2 s.
 * Futuramente: perfis individuais de comandos por personagem.
 */
(()=>{'use strict';
const held=new Set(),tap=new Set(),previous=new Set(),history=[];
const buttonMap={0:'j',1:'i',2:'k',3:'u',4:'throw',5:'interact',6:'stance',7:'s',8:'select',9:'start',10:'l',11:'l'};
const moves=[
 {id:4,seq:[2,3,6,2,3,6],button:1},
 {id:1,seq:[2,3,6],button:0},
 {id:2,seq:[2,1,4],button:2},
 {id:3,seq:[6,2,3],button:3}
];
let active=null,connected=false,lastDir=5;
const DEAD=.32, WINDOW=1250;
function pressed(p,i){const b=p.buttons[i];return !!b&&(b.pressed||b.value>.55)}
function direction(p){
 let x=p.axes[0]||0,y=p.axes[1]||0;
 const left=pressed(p,14),right=pressed(p,15),up=pressed(p,12),down=pressed(p,13);
 if(left||right)x=left?-1:1;
 if(up||down)y=up?-1:1;
 x=Math.abs(x)<DEAD?0:Math.sign(x);y=Math.abs(y)<DEAD?0:Math.sign(y);
 return (y+1)*3+(x+1)+1; // teclado numérico: 1=↙ 2=↓ 3=↘ 4=← 5=neutro 6=→ 7=↖ 8=↑ 9=↗
}
function relative(dir,face){if(face>=0)return dir;const row=Math.floor((dir-1)/3),col=(dir-1)%3;return row*3+(2-col)+1}
function update(){
 const pads=typeof navigator.getGamepads==='function'?navigator.getGamepads():[];
 let p=active!==null?pads[active]:null;
 if(!p||!p.connected){p=Array.from(pads).find(x=>x&&x.connected)||null;active=p?p.index:null;previous.clear();history.length=0;lastDir=5}
 connected=!!p;held.clear();tap.clear();if(!p)return;
 const current=new Set();for(let i=0;i<p.buttons.length;i++)if(pressed(p,i))current.add(i);
 const dir=direction(p),now=performance.now();
 if(dir!==lastDir){if(dir!==5)history.push({dir,t:now});lastDir=dir}
 while(history.length&&now-history[0].t>WINDOW)history.shift();
 if([1,4,7].includes(dir))held.add('a');
 if([3,6,9].includes(dir))held.add('d');
 if([7,8,9].includes(dir))held.add('w');
 if([1,2,3].includes(dir))held.add('c');
 for(const i of current){
   const key=buttonMap[i];if(!key)continue;
   if(i===7)held.add('s');
   else if(!previous.has(i))tap.add(key);
 }
 previous.clear();for(const i of current)previous.add(i);
}
function consumeMove(face){
 const now=performance.now();
 for(const move of moves){
  const key=buttonMap[move.button];if(!tap.has(key))continue;
  const dirs=history.filter(x=>now-x.t<=WINDOW).map(x=>relative(x.dir,face));
  let j=move.seq.length-1,matched=[];
  for(let i=dirs.length-1;i>=0&&j>=0;i--)if(dirs[i]===move.seq[j]){matched.push(i);j--}
  if(j<0){
   tap.delete(key);
   const first=Math.min(...matched);history.splice(0,first+1);
   return move.id;
  }
 }
 return null;
}
window.markysPad={
 update,down:key=>held.has(key)||tap.has(key),just:key=>tap.has(key),
 consume:key=>tap.delete(key),consumeMove,
 connected:()=>connected,index:()=>active,
 clear:()=>{held.clear();tap.clear();previous.clear();history.length=0;lastDir=5},
 direction:()=>lastDir
};
window.addEventListener('gamepaddisconnected',()=>{active=null;window.markysPad.clear()});
})();