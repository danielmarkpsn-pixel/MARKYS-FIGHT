/* MARKYS FIGHT — Gamepad API, padrão de controles tipo Xbox/PlayStation.
   Sem bibliotecas externas; teclado e toque continuam funcionando. */
(()=>{'use strict';
const held=new Set(),previous=new Map(),tap=new Set();
let active=null,connected=false,deadzone=.27;
const map={0:'j',1:'k',2:'1',3:'2',4:'s',5:'3',6:'s',7:'shift',8:'p',9:'start',10:'l',11:'l',12:'w',13:'s',14:'a',15:'d'};
function pressed(p,i){const b=p.buttons[i];return !!b&&(b.pressed||b.value>.55)}
function update(){
  const pads=navigator.getGamepads?navigator.getGamepads():[];
  let p=active!==null?pads[active]:null;
  if(!p||!p.connected){p=Array.from(pads).find(x=>x&&x.connected)||null;active=p?p.index:null}
  connected=!!p;held.clear();tap.clear();
  if(!p){previous.clear();return}
  const current=new Set();
  for(let i=0;i<p.buttons.length;i++)if(pressed(p,i))current.add(i);
  const axis=p.axes[0]||0,vertical=p.axes[1]||0;
  if(axis< -deadzone){held.add('a');if(!previous.has('axis-left'))tap.add('a')}else if(axis>deadzone){held.add('d');if(!previous.has('axis-right'))tap.add('d')}
  if(vertical< -0.6)current.add(12);else if(vertical>.65)held.add('s');
  for(const i of current){const k=map[i];if(!k)continue;
    if(['a','d','s','shift'].includes(k)){held.add(k);if(!previous.has(i))tap.add(k);}
    else if(!previous.has(i))tap.add(k);
  }
  previous.clear();for(const i of current)previous.set(i,true);if(axis< -deadzone)previous.set('axis-left',true);if(axis>deadzone)previous.set('axis-right',true);
}
window.markysPad={
  update,down:k=>held.has(k)||tap.has(k),consume:k=>tap.delete(k),
  just:k=>tap.has(k),connected:()=>connected,
  clear:()=>{held.clear();tap.clear();previous.clear()},
  index:()=>active
};
window.addEventListener('gamepaddisconnected',()=>{active=null;window.markysPad.clear()});
})();