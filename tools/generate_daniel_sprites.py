#!/usr/bin/env python3
"""Gera spritesheets articulados experimentais do DANIEL.png original.
Requer Pillow. Preserva o arquivo original e grava 19 animações PNG RGBA.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'DANIEL.png'
DEST=ROOT/'personagens'/'DANIEL'/'sprites'
CONFIG=ROOT/'personagens'/'DANIEL'/'config.json'
FRAME=(160,224)
BASE=(140,204)
STATES={
 'idle':(8,8,True),'walk':(8,12,True),'run':(8,16,True),
 'jump':(5,12,False),'fall':(3,10,False),'crouch':(3,10,False),
 'guard':(4,10,True),'crouchGuard':(3,10,True),
 'punchFront':(6,18,False),'punchBack':(7,17,False),
 'kickFront':(7,17,False),'kickBack':(8,16,False),
 'hurt':(4,12,False),'knockdown':(6,12,False),
 'getup':(6,12,False),'magic1':(8,18,False),
 'magic2':(8,16,False),'magic3':(8,18,False),
 'special':(12,20,False)
}
# Máscaras e pontos de articulação normalizados ao retrato original.
POLYGONS={
 'left_leg':[(.33,.50),(.51,.50),(.52,.67),(.47,.88),(.46,1),(.22,1),(.24,.84),(.28,.67)],
 'right_leg':[(.49,.50),(.68,.50),(.72,.67),(.78,.86),(.79,1),(.53,1),(.52,.86),(.48,.68)],
 'left_arm':[(.34,.26),(.43,.34),(.38,.44),(.32,.57),(.18,.60),(.13,.51),(.20,.37)],
 'right_arm':[(.64,.26),(.73,.34),(.84,.46),(.86,.57),(.70,.61),(.65,.51),(.61,.40)],
 'head':[(.31,0),(.69,0),(.72,.13),(.66,.27),(.59,.31),(.39,.31),(.31,.25),(.27,.13)],
 'torso':[(.37,.27),(.63,.27),(.71,.36),(.67,.54),(.53,.57),(.43,.57),(.31,.53),(.29,.37)]
}
PIVOTS={'left_leg':(.41,.53),'right_leg':(.59,.53),'left_arm':(.35,.32),'right_arm':(.65,.32),'head':(.5,.27),'torso':(.5,.48)}
def part(source,name):
 w,h=source.size
 mask=Image.new('L',(w,h))
 d=ImageDraw.Draw(mask)
 d.polygon([(round(x*w),round(y*h)) for x,y in POLYGONS[name]],fill=255)
 layer=source.copy()
 layer.putalpha(Image.composite(source.getchannel('A'),Image.new('L',(w,h)),mask))
 return layer
def rotated(layer,angle,pivot):
 w,h=layer.size
 return layer.rotate(angle,resample=Image.Resampling.BICUBIC,center=(pivot[0]*w,pivot[1]*h),expand=False)
def pose(state,t):
 cycle=math.sin(t*math.tau)
 swing=math.sin(t*math.tau)
 vals={k:0 for k in POLYGONS}
 shift=0; rise=0; crouch=1.0
 if state=='idle':
  vals['head']=1.5*cycle;rise=round(2*math.sin(t*math.tau))
 elif state in ('walk','run'):
  factor=1 if state=='walk' else 1.6
  vals.update(left_leg=22*swing*factor,right_leg=-22*swing*factor,
   left_arm=-17*swing*factor,right_arm=17*swing*factor,torso=-3*swing)
  rise=round(abs(swing)*(3 if state=='walk' else 6));shift=round(2*swing)
 elif state in ('jump','fall'):
  vals.update(left_leg=-20,right_leg=26,left_arm=32,right_arm=-30,torso=6)
  rise=round((12 if state=='jump' else 5)*math.sin(t*math.pi))
 elif state in ('crouch','crouchGuard'):
  crouch=.78;vals.update(left_leg=-25,right_leg=25,torso=5,left_arm=-20,right_arm=25)
 elif state=='guard':
  vals.update(left_arm=-42,right_arm=55,torso=-5)
 elif state.startswith('punch'):
  power=math.sin(t*math.pi)
  vals.update(right_arm=-105*power if state=='punchFront' else -145*power,
   left_arm=-20*power,torso=-11*power,head=6*power)
  shift=round(8*power)
 elif state.startswith('kick') or state=='magic3':
  power=math.sin(t*math.pi)
  vals.update(right_leg=-72*power if state=='kickFront' else -110*power,
   left_leg=12*power,left_arm=28*power,right_arm=-30*power,torso=12*power)
  shift=round(6*power)
 elif state=='hurt':
  vals.update(torso=12*math.sin(t*math.pi),head=-12*math.sin(t*math.pi),
   left_arm=-30,right_arm=30)
 elif state in ('knockdown','getup'):
  progress=t if state=='knockdown' else 1-t
  vals.update(torso=-75*progress,head=-15*progress,
   left_leg=-50*progress,right_leg=40*progress,left_arm=-35*progress)
  crouch=1-.32*progress
 elif state=='magic1':
  vals.update(left_leg=30*swing,right_leg=-30*swing,left_arm=-25*swing,right_arm=25*swing,torso=-10)
  shift=round(7*swing)
 elif state=='magic2':
  vals.update(right_arm=-95*math.sin(t*math.pi),left_arm=-40,torso=-6)
 elif state=='special':
  vals.update(right_arm=-60*math.sin(t*math.tau*2),left_arm=55*math.sin(t*math.tau*2),
   left_leg=20*swing,right_leg=-20*swing,torso=-8*swing)
 return vals,shift,rise,crouch
def render(layers,state,t):
 angles,shift,rise,crouch=pose(state,t)
 w,h=BASE
 image=Image.new('RGBA',BASE)
 # Pintura em camadas, preservando as cores, rosto e roupas do DANIEL.png.
 for name in ('left_leg','right_leg','torso','left_arm','right_arm','head'):
  image.alpha_composite(rotated(layers[name],angles[name],PIVOTS[name]))
 if crouch!=1:
  image=image.resize((w,max(1,round(h*crouch))),Image.Resampling.LANCZOS)
 result=Image.new('RGBA',FRAME)
 x=(FRAME[0]-image.width)//2+shift
 y=FRAME[1]-image.height-rise-5
 result.alpha_composite(image,(x,y))
 return result
def main():
 if not SOURCE.exists():raise SystemExit('Arquivo DANIEL.png não encontrado')
 original=Image.open(SOURCE).convert('RGBA')
 bbox=original.getchannel('A').getbbox()
 if not bbox:raise SystemExit('DANIEL.png está vazio')
 original=original.crop(bbox)
 original.thumbnail(BASE,Image.Resampling.LANCZOS)
 base=Image.new('RGBA',BASE)
 base.alpha_composite(original,((BASE[0]-original.width)//2,BASE[1]-original.height))
 layers={name:part(base,name) for name in POLYGONS}
 DEST.mkdir(parents=True,exist_ok=True)
 cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
 for state,(count,fps,loop) in STATES.items():
  columns=min(4,count)
  rows=math.ceil(count/columns)
  sheet=Image.new('RGBA',(FRAME[0]*columns,FRAME[1]*rows))
  for i in range(count):
   frame=render(layers,state,i/count if loop else i/max(1,count-1))
   sheet.alpha_composite(frame,((i%columns)*FRAME[0],(i//columns)*FRAME[1]))
  sheet.save(DEST/(state+'.png'),optimize=True)
  cfg['animations'][state]={'file':state+'.png','frames':count,'columns':columns,
   'fps':fps,'frameWidth':FRAME[0],'frameHeight':FRAME[1],'loop':loop}
 cfg['notes']='19 spritesheets experimentais gerados a partir de DANIEL.png com rig 2D. Revisão artística e testes em partida necessários.'
 CONFIG.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Gerados',len(STATES),'spritesheets em',DEST)
if __name__=='__main__':main()
