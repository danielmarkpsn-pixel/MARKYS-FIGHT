#!/usr/bin/env python3
"""Valida a configuração de animações do Daniel e os spritesheets instalados.
Arquivos ausentes são permitidos apenas para animações ainda não configuradas.
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'personagens' / 'DANIEL'
STATES = ('idle','walk','run','jump','fall','crouch','guard','crouchGuard',
          'punchFront','punchBack','kickFront','kickBack','hurt','knockdown',
          'getup','magic1','magic2','magic3','special')

def validate():
    cfg = json.loads((DIR/'config.json').read_text(encoding='utf-8'))
    animations = cfg.get('animations', {})
    errors = []
    ready = 0
    for state in STATES:
        item = animations.get(state)
        if item is None:
            continue
        if not isinstance(item,dict):
            errors.append(f'{state}: configuração inválida')
            continue
        filename = item.get('file')
        if filename != state + '.png':
            errors.append(f'{state}: arquivo deve ser {state}.png')
            continue
        try:
            frames = item['frames']
            columns = item.get('columns',frames)
            width = item['frameWidth']
            height = item['frameHeight']
            fps = item['fps']
            if any(type(n) is not int or n<1 for n in (frames,columns,width,height)) or not isinstance(fps,(int,float)) or not 0<fps<=120:
                raise ValueError('parâmetros inválidos')
            data = (DIR/'sprites'/filename).read_bytes()
            if len(data)<24 or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR':
                raise ValueError('PNG inválido')
            image_width,image_height = struct.unpack('>II',data[16:24])
            rows = (frames+columns-1)//columns
            if image_width<columns*width or image_height<rows*height:
                raise ValueError('dimensões insuficientes')
            ready += 1
        except (OSError,KeyError,ValueError,TypeError) as exc:
            errors.append(f'{state}: {exc}')
    for err in errors:
        print('ERRO:',err)
    print(f'DANIEL: {ready}/{len(STATES)} spritesheets configurados e válidos')
    if errors:
        raise SystemExit(1)

if __name__=='__main__':
    validate()
