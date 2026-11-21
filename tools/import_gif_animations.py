#!/usr/bin/env python3
"""Importador oficial dos GIFs enviados pelo usuário para MARKYS FIGHT.

Descobre nomes em português/inglês, cria spritesheets PNG RGBA e atualiza
somente os estados que possuem GIFs válidos. Não altera DANIEL.png.
O GIF de origem pode ser uma spritesheet animada ou uma sequência de poses.
"""
import argparse
import json
import math
import re
import unicodedata
from pathlib import Path
from PIL import Image, ImageSequence

ROOT=Path(__file__).resolve().parents[1]
STATES=('idle','walk','run','jump','fall','crouch','guard','crouchGuard','punchFront',
        'punchBack','kickFront','kickBack','hurt','knockdown','getup','magic1',
        'magic2','magic3','special')
# Correspondência EXATA dos 14 GIFs originais existentes na main.
DANIEL_NAMES={
    'idle':'Daniel em posição de combate, animação de respiração-1.gif',
    'crouch':'Animação de Crouch do Daniel-2.gif',
    'guard':'Animação de guarda defensiva pixel art-3.gif',
    'crouchGuard':'Daniel em Guarda_ Animação Pixel Art-4.gif',
    'punchBack':'Sequência Animada de Soco do Daniel-5.gif',
    'magic3':'Daniel Liberta o Golpe de Energia-6.gif',
    'walk':'DANIEL CAMINHANDO.gif',
    'run':'DANIEL CORRENDO.gif',
    'jump':'DANIEL SALTANDO.gif',
    'fall':'DANIEL CAINDO.gif',
    'punchFront':'DANIEL SOCO DIRETO.gif',
    'kickFront':'DANIEL CHUTE ALTO.gif',
    'hurt':'DANIEL SOFRENDO DANO.gif',
    'knockdown':'DANIEL DERROTADO.gif',
    'getup':'DANIEL LEVANTANDO.gif',
    'magic1':'DANIEL HIPERCORRIDA.gif',
    'magic2':'DANIEL ONDA SONICA.gif',
    'special':'DANIEL ESPECIAL PARTE 1.gif',
}
SPECIAL_PARTS=(
    'DANIEL ESPECIAL PARTE 1.gif',
    'DANIEL ESPECIAL PARTE 2.gif',
    'DANIEL ESPECIAL PARTE 3.gif',
)
OPTIONAL_DANIEL={
    'fall':'DANIEL CAINDO.gif',
    'kickBack':'DANIEL SALTO MORTAL PRA TRAS.gif',
}
LOOP={'idle','walk','run','guard','crouchGuard'}
MAX_FRAMES=240
# Priorizar a pose individual, sem importar por acidente colagens inteiras:
# alguns GIFs gerados por IA são uma ÚNICA imagem em grade 4x2 ou 4x3.
def grid_dimensions(w,h):
    ratio=w/h
    if 1.75<=ratio<=2.35: return 4,2
    if 1.15<=ratio<=1.55: return 4,3
    if .68<=ratio<=.90: return 2,4
    return 1,1

def normalized(text):
    text=unicodedata.normalize('NFKD',text)
    return re.sub(r'[^A-Z0-9]+',' ',''.join(c for c in text if not unicodedata.combining(c)).upper()).strip()

def find_gif(folder,filename):
    wanted=normalized(Path(filename).stem)
    for path in sorted(folder.glob('*')):
        if path.suffix.lower()=='.gif' and normalized(path.stem)==wanted:
            return path
    return None

def extract_frames(path,split_grid=True):
    frames=[];duration_ms=[]
    with Image.open(path) as gif:
        count=gif.n_frames
        if count<1: raise ValueError('GIF sem quadros')
        # GIFs de um quadro podem conter uma spritesheet inteira.
        # GIFs de vários quadros são tratados como imagens temporais.
        for idx in range(min(count,MAX_FRAMES)):
            gif.seek(idx)
            im=gif.convert('RGBA')
            duration=max(20,int(gif.info.get('duration',100) or 100))
            if count==1 and split_grid:
                cols,rows=grid_dimensions(*im.size)
                if cols*rows>1:
                    fw=im.width//cols;fh=im.height//rows
                    for k in range(cols*rows):
                        frames.append(im.crop(((k%cols)*fw,(k//cols)*fh,
                                             (k%cols+1)*fw,(k//cols+1)*fh)))
                        duration_ms.append(100)
                    break
            frames.append(im)
            duration_ms.append(duration)
    return frames,duration_ms

def export(name, fps=None, width=192, height=256, columns=4, dry_run=False):
    if name not in ('DANIEL','HELENA','JOSY','MARKYS','MILENA','GPT-6'):
        raise ValueError('Personagem desconhecido')
    folder=ROOT/'personagens'/name
    gifs=folder/'gifs'
    dest=folder/'sprites'
    config_path=folder/'config.json'
    config=json.loads(config_path.read_text(encoding='utf-8'))
    prepared=[]
    for state in STATES:
        filename=(DANIEL_NAMES.get(state,state+'.gif') if name=='DANIEL' else state+'.gif')
        path=find_gif(gifs,filename) if filename else None
        if not path and name=='DANIEL' and state in OPTIONAL_DANIEL:
            path=find_gif(gifs,OPTIONAL_DANIEL[state])
        if not path: continue
        sources=[path]
        if name=='DANIEL' and state=='special':
            sources=[p for filename in SPECIAL_PARTS if (p:=find_gif(gifs,filename))]
        frames=[];durations=[]
        for src in sources:
            f,d=extract_frames(src)
            frames.extend(f);durations.extend(d)
        frames=frames[:MAX_FRAMES];durations=durations[:MAX_FRAMES]
        if not frames: raise ValueError(f'{state}: nenhum quadro')
        rate=fps if fps is not None else 1000/(sum(durations)/len(durations))
        rate=min(120,max(1,round(rate,2)))
        col=min(columns,len(frames))
        sprite=Image.new('RGBA',(width*col,height*math.ceil(len(frames)/col)))
        for i,frame in enumerate(frames):
            # Preservar proporções e origem; posicionamento dos pés na borda inferior.
            frame=frame.copy()
            frame.thumbnail((width,height),Image.Resampling.LANCZOS)
            tile=Image.new('RGBA',(width,height))
            tile.alpha_composite(frame,((width-frame.width)//2,height-frame.height))
            sprite.alpha_composite(tile,((i%col)*width,(i//col)*height))
        prepared.append((state,path.name,sprite,{
            'file':state+'.png','frames':len(frames),'columns':col,
            'fps':rate,'frameWidth':width,'frameHeight':height,
            'loop':state in LOOP
        }))
    if not prepared: raise SystemExit(f'Nenhum GIF reconhecido em {gifs}')
    for state,source,sprite,definition in prepared:
        print(f'{state}: {source} -> {definition["frames"]} frames, {definition["fps"]} FPS')
        if not dry_run:
            dest.mkdir(parents=True,exist_ok=True)
            sprite.save(dest/(state+'.png'),optimize=True)
            config.setdefault('animations',{})[state]=definition
    if not dry_run:
        config['notes']='Animações de GIFs fornecidos pelo usuário; imagens em DANIEL.png mantidas somente como referência.'
        config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(prepared)} movimentos importados' if not dry_run else f'{len(prepared)} movimentos encontrados (simulação)')

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('character',nargs='?',default='DANIEL')
    ap.add_argument('--fps',type=float,default=None)
    ap.add_argument('--width',type=int,default=192)
    ap.add_argument('--height',type=int,default=256)
    ap.add_argument('--columns',type=int,default=4)
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    if (args.fps is not None and not 1<=args.fps<=120) or not 1<=args.width<=2048 or not 1<=args.height<=2048 or not 1<=args.columns<=16:
        ap.error('Parâmetros fora do limite')
    export(args.character,args.fps,args.width,args.height,args.columns,args.dry_run)
