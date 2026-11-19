#!/usr/bin/env python3
"""Instala o pacote de sprites do Daniel sem alterar os PNGs originais.
Uso: python tools/install_daniel_sprites.py DANIEL_sprites_prototipo.zip
"""
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATES = ('idle','walk','run','jump','fall','crouch','guard','crouchGuard',
          'punchFront','punchBack','kickFront','kickBack','hurt','knockdown',
          'getup','magic1','magic2','magic3','special')
SPRITES = ROOT / 'personagens' / 'DANIEL' / 'sprites'
CONFIG = ROOT / 'personagens' / 'DANIEL' / 'config.json'
MAX_FILE = 12_000_000

def png_dimensions(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR' or len(data) < 24:
        raise ValueError('PNG inválido')
    return struct.unpack('>II', data[16:24])

def install(package):
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read('animations.json'))
        prepared = {}
        for state in STATES:
            if state not in manifest:
                raise ValueError(f'Animação ausente: {state}')
            entry = manifest[state]
            filename = state + '.png'
            if entry.get('file') != filename:
                raise ValueError(f'Nome inesperado em {state}')
            frames = entry.get('frames')
            columns = entry.get('columns', frames)
            fw = entry.get('frameWidth')
            fh = entry.get('frameHeight')
            fps = entry.get('fps')
            if not all(type(n) is int and n > 0 for n in (frames,columns,fw,fh)) or not isinstance(fps,(int,float)) or not 0 < fps <= 120 or frames > 240 or columns > 240:
                raise ValueError(f'Metadados inválidos em {state}')
            data = archive.read('sprites/' + filename)
            if len(data) > MAX_FILE:
                raise ValueError(f'Arquivo muito grande: {filename}')
            width,height = png_dimensions(data)
            if width < columns * fw or height < ((frames+columns-1)//columns)*fh:
                raise ValueError(f'Quadros fora dos limites: {filename}')
            prepared[state] = (data, {k:entry[k] for k in ('file','frames','columns','fps','frameWidth','frameHeight','loop') if k in entry})
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    SPRITES.mkdir(parents=True, exist_ok=True)
    for state,(data,_) in prepared.items():
        (SPRITES/(state+'.png')).write_bytes(data)
    config.setdefault('animations',{}).update({state:meta for state,(_,meta) in prepared.items()})
    CONFIG.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(prepared)} animações instaladas em {SPRITES.relative_to(ROOT)}')
    print('Revise visualmente antes de publicar: o pacote é experimental.')

if __name__ == '__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Uso: python tools/install_daniel_sprites.py arquivo.zip')
    install(Path(sys.argv[1]))
