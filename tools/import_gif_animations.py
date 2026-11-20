#!/usr/bin/env python3
"""Converte GIFs animados autorais em spritesheets PNG para MARKYS FIGHT.
Uso: python tools/import_gif_animations.py DANIEL --fps 12
Entrada: personagens/DANIEL/gifs/<estado>.gif
Saída: personagens/DANIEL/sprites/<estado>.png e config.json
Requer Pillow. Não utiliza nem deforma DANIEL.png.
"""
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageSequence

ROOT=Path(__file__).resolve().parents[1]
STATES=('idle','walk','run','jump','fall','crouch','guard','crouchGuard','punchFront',
'punchBack','kickFront','kickBack','hurt','knockdown','getup','magic1','magic2','magic3','special')
MAX_FRAMES=240
def import_gifs(name, fps, width, height, columns):
    if name not in ('DANIEL','HELENA','JOSY','MARKYS','MILENA','GPT-6'):
        raise ValueError('Personagem desconhecido')
    folder=ROOT/'personagens'/name
    source=folder/'gifs'
    target=folder/'sprites'
    cfg_path=folder/'config.json'
    cfg=json.loads(cfg_path.read_text(encoding='utf-8'))
    updates={}
    for state in STATES:
        path=source/(state+'.gif')
        if not path.exists():
            continue
        with Image.open(path) as gif:
            if getattr(gif,'n_frames',1)<2:
                raise ValueError(f'{path.name}: GIF precisa ter pelo menos 2 quadros')
            count=min(gif.n_frames,MAX_FRAMES)
            col=min(columns,count)
            sheet=Image.new('RGBA',(width*col,height*math.ceil(count/col)))
            for i in range(count):
                gif.seek(i)
                frame=gif.convert('RGBA')
                # GIF pode conter transparência, mas também pode trazer fundo opaco.
                # Nunca remover fundos automaticamente: evitar apagar detalhes do personagem.
                frame.thumbnail((width,height),Image.Resampling.LANCZOS)
                tile=Image.new('RGBA',(width,height))
                tile.alpha_composite(frame,((width-frame.width)//2,height-frame.height))
                sheet.alpha_composite(tile,((i%col)*width,(i//col)*height))
            target.mkdir(parents=True,exist_ok=True)
            sheet.save(target/(state+'.png'),optimize=True)
            updates[state]={'file':state+'.png','frames':count,'columns':col,
              'fps':fps,'frameWidth':width,'frameHeight':height,
              'loop':state in ('idle','walk','run','guard','crouchGuard')}
            print(f'{name}: {state} — {count} quadros')
    if not updates:
        raise SystemExit(f'Nenhum GIF encontrado em {source}')
    cfg.setdefault('animations',{}).update(updates)
    cfg_path.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(updates)} animações convertidas e configuradas')
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('character')
    p.add_argument('--fps',type=float,default=12)
    p.add_argument('--width',type=int,default=192)
    p.add_argument('--height',type=int,default=256)
    p.add_argument('--columns',type=int,default=4)
    args=p.parse_args()
    if not 1<=args.fps<=120 or not 1<=args.width<=2048 or not 1<=args.height<=2048 or not 1<=args.columns<=16:
        p.error('Parâmetros fora do limite')
    import_gifs(args.character,args.fps,args.width,args.height,args.columns)
