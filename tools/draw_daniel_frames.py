#!/usr/bin/env python3
"""Renderiza desenhos vetoriais ORIGINAIS de cada pose do Daniel em spritesheets PNG.
Não recorta, deforma ou reutiliza pixels de DANIEL.png. É uma base 2D ilustrada,
sujeita à aprovação artística. Requer cairosvg e Pillow.
"""
from __future__ import annotations
import io, json, math
from pathlib import Path
import cairosvg
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'personagens/DANIEL/sprites'
CONFIG=ROOT/'personagens/DANIEL/config.json'
W,H=192,256
STATES={
 'idle':(8,8,True),'walk':(8,12,True),'run':(8,16,True),
 'jump':(5,12,False),'fall':(3,10,False),'crouch':(3,10,False),
 'guard':(4,10,True),'crouchGuard':(3,10,True),
 'punchFront':(6,18,False),'punchBack':(7,17,False),
 'kickFront':(7,17,False),'kickBack':(8,16,False),
 'hurt':(4,12,False),'knockdown':(6,12,False),
 'getup':(6,12,False),'magic1':(8,18,False),
 'magic2':(8,16,False),'magic3':(8,18,False),
 'special':(12,20,False)}
INK='#142036';BLUE='#1768c9';LIGHT='#4c9ff2';SKIN='#e8a56f'
def path(d,fill,stroke=INK,width=3):
 return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'
def circle(x,y,r,fill,stroke=INK,width=2):
 return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def limb(a,b,c,outer,inner,thick=15):
 x1,y1=a;x2,y2=b;x3,y3=c
 return (f'<path d="M{x1:.1f} {y1:.1f} Q{x2:.1f} {y2:.1f} {x3:.1f} {y3:.1f}" fill="none" stroke="{INK}" stroke-width="{thick+5}" stroke-linecap="round"/>'
         f'<path d="M{x1:.1f} {y1:.1f} Q{x2:.1f} {y2:.1f} {x3:.1f} {y3:.1f}" fill="none" stroke="{outer}" stroke-width="{thick}" stroke-linecap="round"/>'
         f'<path d="M{x1+2:.1f} {y1-2:.1f} Q{x2+2:.1f} {y2-2:.1f} {x3+2:.1f} {y3-2:.1f}" fill="none" stroke="{inner}" stroke-width="3" stroke-linecap="round" opacity=".7"/>')
def position(state,t):
 cyc=math.sin(t*math.tau)
 bounce=abs(cyc)
 crouch=state in ('crouch','crouchGuard')
 running=state in ('run','magic1')
 walking=state=='walk'
 jump=state in ('jump','fall')
 attack=state.startswith(('punch','kick')) or state in ('magic3','special')
 power=max(0,math.sin(math.pi*t))
 cx=96;cy=141
 if crouch:cy=171
 if running:cy=139-6*bounce;cx+=9
 if walking:cy=141-3*bounce
 if jump:cy=116-20*math.sin(t*math.pi)
 if state=='hurt':cx-=13*power;cy+=4*power
 if state in ('knockdown','getup'):
  p=t if state=='knockdown' else 1-t
  cy+=49*p;cx-=22*p
 if state in ('guard','crouchGuard'):cx-=3
 left_hip=(cx-12,cy+28);right_hip=(cx+13,cy+28)
 left_foot=(cx-19,239);right_foot=(cx+19,239)
 left_knee=(cx-18,cy+65);right_knee=(cx+17,cy+65)
 if walking or running:
  a=(29 if running else 16)*cyc
  left_foot=(cx-17+a,239-abs(a)*(.5 if running else .2))
  right_foot=(cx+17-a,239-abs(a)*(.5 if running else .2))
  left_knee=(cx-18+a*.55,cy+65-abs(a)*.25)
  right_knee=(cx+18-a*.55,cy+65-abs(a)*.25)
 if crouch:
  left_knee=(cx-29,cy+43);right_knee=(cx+33,cy+44)
  left_foot=(cx-40,239);right_foot=(cx+45,239)
 if jump:
  left_knee=(cx-31,cy+48);right_knee=(cx+27,cy+48)
  left_foot=(cx-45,cy+77);right_foot=(cx+36,cy+79)
 if state in ('kickFront','kickBack','magic3'):
  right_knee=(cx+28+29*power,cy+42-31*power)
  right_foot=(cx+25+85*power,cy+73-76*power)
 if state in ('knockdown','getup'):
  p=t if state=='knockdown' else 1-t
  left_knee=(left_knee[0]-36*p,left_knee[1]+12*p)
  left_foot=(left_foot[0]-45*p,239)
  right_knee=(right_knee[0]+25*p,right_knee[1]+18*p)
  right_foot=(right_foot[0]+44*p,239)
 left_sh=(cx-22,cy-33);right_sh=(cx+22,cy-33)
 left_el=(cx-37,cy-1);right_el=(cx+39,cy-1)
 left_hand=(cx-39,cy+31);right_hand=(cx+42,cy+29)
 if walking or running:
  a=(23 if running else 12)*cyc
  left_el=(cx-37,cy-5-a*.5);right_el=(cx+37,cy-5+a*.5)
  left_hand=(cx-37,cy+23-a);right_hand=(cx+37,cy+23+a)
 if state in ('guard','crouchGuard'):
  left_el=(cx-29,cy-18);left_hand=(cx-9,cy-40)
  right_el=(cx+29,cy-19);right_hand=(cx+10,cy-45)
 if state.startswith('punch') or state=='magic2' or state=='special':
  amp=power if state!='special' else abs(math.sin(t*math.tau*2))
  right_el=(cx+33+30*amp,cy-24-8*amp)
  right_hand=(cx+37+84*amp,cy-24-15*amp)
  left_hand=(cx-13,cy-26)
 if state=='hurt':
  left_hand=(cx-62,cy-39);right_hand=(cx+52,cy-43)
 if jump:
  left_hand=(cx-46,cy-54);right_hand=(cx+43,cy-54)
 return locals()
def draw(state,t):
 p=position(state,t);g=lambda key:p[key]
 cx,cy=g('cx'),g('cy')
 # Cada quadro é desenhado de novo em camadas de traços e preenchimentos.
 # Nenhum membro é extraído de uma imagem estática.
 pieces=[]
 pieces.append(limb(g('left_hip'),g('left_knee'),g('left_foot'),'#c48a43','#efc16c',19))
 pieces.append(limb(g('right_hip'),g('right_knee'),g('right_foot'),'#c48a43','#efc16c',19))
 for key in ('left_foot','right_foot'):
  x,y=g(key);pieces.append(path(f'M{x-13:.1f} {y-5:.1f} q14 -7 27 1 l7 6 q-3 6 -14 6 h-24 z','#182d4f',INK,3))
  pieces.append(path(f'M{x-11:.1f} {y:.1f} q12 -3 21 0','none','#e8f3ff',2))
 # Mochila, torso e sobrecamisa azul com camiseta branca.
 pieces.append(path(f'M{cx-28} {cy-38} Q{cx-42} {cy-19} {cx-30} {cy+33} L{cx+29} {cy+33} Q{cx+41} {cy-15} {cx+27} {cy-39}Z','#28394e'))
 pieces.append(path(f'M{cx-25} {cy-40} Q{cx} {cy-47} {cx+25} {cy-40} L{cx+26} {cy+27} Q{cx} {cy+36} {cx-26} {cy+27}Z',BLUE))
 pieces.append(path(f'M{cx-10} {cy-36} L{cx+9} {cy-36} L{cx+13} {cy+28} L{cx-12} {cy+28}Z','#f0f2f2'))
 pieces.append(path(f'M{cx-26} {cy-38} L{cx-11} {cy-35} L{cx-4} {cy+22} L{cx-25} {cy+26}Z',LIGHT))
 pieces.append(path(f'M{cx+26} {cy-38} L{cx+10} {cy-35} L{cx+4} {cy+22} L{cx+25} {cy+26}Z',BLUE))
 pieces.append(limb(g('left_sh'),g('left_el'),g('left_hand'),BLUE,LIGHT,13))
 pieces.append(limb(g('right_sh'),g('right_el'),g('right_hand'),BLUE,LIGHT,13))
 for key in ('left_hand','right_hand'):
  x,y=g(key);pieces.append(circle(x,y,8,SKIN))
 # Cabeça com cachos, expressão e rosto ilustrados a cada pose.
 head_y=cy-62
 pieces.append(path(f'M{cx-17} {head_y-18} Q{cx-25} {head_y+4} {cx-15} {head_y+18} Q{cx} {head_y+28} {cx+17} {head_y+17} Q{cx+27} {head_y-6} {cx+15} {head_y-20}Z',SKIN))
 for dx,dy,rad in [(-19,-20,9),(-11,-30,10),(0,-33,10),(12,-29,10),(21,-20,9),(-23,-9,8),(-8,-19,9),(8,-20,9),(23,-10,7)]:
  pieces.append(circle(cx+dx,head_y+dy,rad,'#241a1b','#130e13',1.5))
 for dx in (-9,9):
  pieces.append(path(f'M{cx+dx-4} {head_y+2} q4 -4 8 0','none','#3b241b',2))
  pieces.append(circle(cx+dx,head_y+7,2.3,'#17171b','#17171b',1))
 pieces.append(path(f'M{cx-5} {head_y+17} q5 4 10 0','none','#87492e',2))
 if state.startswith(('punch','kick')) or state=='special':
  pieces.append(path(f'M{cx-5} {head_y+17} q5 7 10 0','none','#6c2d25',2))
 return ('<svg xmlns="http://www.w3.org/2000/svg" width="192" height="256" viewBox="0 0 192 256">'
         +''.join(pieces)+'</svg>')
def main():
 DEST.mkdir(parents=True,exist_ok=True)
 cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
 for state,(frames,fps,loop) in STATES.items():
  columns=min(frames,4)
  rows=math.ceil(frames/columns)
  sheet=Image.new('RGBA',(W*columns,H*rows))
  for i in range(frames):
   svg=draw(state,i/frames if loop else i/max(1,frames-1))
   image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
   sheet.alpha_composite(image,((i%columns)*W,(i//columns)*H))
  sheet.save(DEST/(state+'.png'),optimize=True)
  cfg['animations'][state]={'file':state+'.png','frames':frames,'columns':columns,
   'fps':fps,'frameWidth':W,'frameHeight':H,'loop':loop}
 cfg['notes']='Spritesheets vetoriais experimentais, cada pose desenhada em SVG sem recorte de DANIEL.png. Exigem revisão artística e testes em partida.'
 CONFIG.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'{len(STATES)} animações exportadas.')
if __name__=='__main__':main()
