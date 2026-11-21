#!/usr/bin/env python3
"""Cria GIFs transparentes para os 7 estados sem GIF do Daniel.

Desenho vetorial quadro a quadro, sem extrair partes de DANIEL.png.
Preserva os 14 GIFs enviados pelo usuário. São rascunhos de animação
para avaliação artística, não substitutos da arte original.
"""
from __future__ import annotations
import io
import importlib.util
from pathlib import Path
import cairosvg
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DRAW=ROOT/'tools/draw_daniel_frames.py'
spec=importlib.util.spec_from_file_location('daniel_draw',DRAW)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
OUT=ROOT/'personagens/DANIEL/gifs'
MISSING={
    'idle':('idle.gif',10,100),
    'fall':('fall.gif',8,110),
    'crouch':('crouch.gif',6,130),
    'guard':('guard.gif',8,100),
    'crouchGuard':('crouchGuard.gif',8,110),
    'punchBack':('punchBack.gif',8,85),
    'magic3':('magic3.gif',10,85),
}
def create():
    OUT.mkdir(parents=True,exist_ok=True)
    for state,(filename,count,delay) in MISSING.items():
        dest=OUT/filename
        if dest.exists():
            print('PRESERVADO:',dest.name)
            continue
        frames=[]
        for i in range(count):
            t=i/count if state in ('idle','guard','crouchGuard') else i/(count-1)
            svg=module.draw(state,t).encode('utf-8')
            png=cairosvg.svg2png(bytestring=svg)
            frame=Image.open(io.BytesIO(png)).convert('RGBA')
            # GIF usa transparência de 1 bit. Paleta indexada e índice
            # reservado para transparência, sem fundo opaco.
            alpha=frame.getchannel('A')
            rgb=Image.new('RGB',frame.size,(255,0,255))
            rgb.paste(frame,mask=alpha)
            pal=rgb.quantize(colors=254,method=Image.Quantize.MEDIANCUT)
            palette=pal.getpalette()
            palette[255*3:255*3+3]=[255,0,255]
            pal.putpalette(palette)
            transparent=alpha.point(lambda a:255 if a<96 else 0)
            pal.paste(255,mask=transparent)
            pal.info['transparency']=255
            frames.append(pal)
        frames[0].save(dest,save_all=True,append_images=frames[1:],
                       duration=delay,loop=0,disposal=2,transparency=255,
                       optimize=False)
        with Image.open(dest) as check:
            if check.n_frames<2:
                raise RuntimeError(f'GIF não animado: {dest}')
            if check.info.get('transparency') is None:
                raise RuntimeError(f'GIF sem transparência: {dest}')
        print('CRIADO:',dest.name,len(frames),'quadros')
if __name__=='__main__':
    create()
