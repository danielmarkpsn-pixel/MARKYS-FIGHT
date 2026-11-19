/* Execute: node --test tests/sprites.test.cjs */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function boot(config,dimensions={width:512,height:384}){
 const images=[];
 class MockImage{
  constructor(){this.naturalWidth=0;this.naturalHeight=0;images.push(this)}
  set src(value){this._src=value;this.naturalWidth=dimensions.width;this.naturalHeight=dimensions.height;queueMicrotask(()=>this.onload?.())}
 }
 const context={window:{},Image:MockImage,fetch:async()=>({ok:true,json:async()=>config}),encodeURIComponent,console};
 vm.runInNewContext(fs.readFileSync('sprites.js','utf8'),context,{filename:'sprites.js'});
 return context.window.markysSprites;
}
test('aceita spritesheet com quatro colunas e oito quadros',async()=>{
 const sprites=boot({animations:{walk:{file:'walk.png',frames:8,columns:4,fps:12,frameWidth:128,frameHeight:192}}});
 await sprites.load('DANIEL');
 assert.equal(sprites.status('DANIEL'),'ready');
 const calls=[];const ctx={drawImage:(...args)=>calls.push(args)};
 assert.equal(sprites.draw(ctx,{name:'DANIEL',animClock:5/12},'walk',-55,-165,110,165),true);
 assert.equal(calls[0][1],128);assert.equal(calls[0][2],192);
});
test('mantém fallback quando não há sprites cadastrados',async()=>{
 const sprites=boot({animations:{idle:null}});
 await sprites.load('DANIEL');
 assert.equal(sprites.draw({drawImage(){throw Error('não deveria desenhar')}},{name:'DANIEL',animClock:0},'idle',0,0,100,100),false);
});
test('rejeita caminho inseguro e arquivo inválido',()=>{
 const sprites=boot({animations:{}});
 assert.equal(sprites.normalize({file:'../original.png',frames:1,fps:10,frameWidth:128,frameHeight:192}),null);
 assert.equal(sprites.normalize({file:'walk.svg',frames:1,fps:10,frameWidth:128,frameHeight:192}),null);
});
test('não desenha spritesheet com dimensões insuficientes',async()=>{
 const sprites=boot({animations:{walk:{file:'walk.png',frames:8,columns:4,fps:12,frameWidth:128,frameHeight:192}}},{width:128,height:192});
 await sprites.load('DANIEL');
 assert.equal(sprites.status('DANIEL'),'partial');
 assert.equal(sprites.report('DANIEL').errors.length,1);
});
