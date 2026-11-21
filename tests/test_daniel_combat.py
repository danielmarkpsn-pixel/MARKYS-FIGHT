#!/usr/bin/env python3
"""Verificações estáticas do motor de combate e da direção de arte do Daniel."""
from pathlib import Path
import json
import re

root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text(encoding='utf-8')
cfg=json.loads((root/'personagens/DANIEL/config.json').read_text(encoding='utf-8'))
assert 'function finishRound()' in html
assert 'f.combo=null;f.attack=null;f.attackTime=0' in html, 'Combo precisa ser cancelado ao fim do round'
assert "while(combo.next<=0&&combo.remaining>0&&state==='playing')" in html, 'Combos devem respeitar dt e estado da partida'
assert "if(state==='playing')control(e,dt)" in html, 'Não executar CPU após o fim da partida'
assert "f.magicAnim===4?'special'" in html, 'O especial deve selecionar a animação special'
assert "if(!daniel){" in html, 'PNG de referência não pode ser deformado'
# A coleção oficial atual não possui GIFs de queda (fall/knockdown).
# Validar movimentos disponíveis, sem exigir sprites que o usuário excluiu.
required={'idle','walk','run','jump','crouch','guard','crouchGuard',
          'punchFront','punchBack','kickFront','kickBack','hurt','getup',
          'magic1','magic2','magic3','special'}
assert required.issubset(cfg['animations']), 'Faltam animações oficiais do Daniel'
assert not ({'fall','knockdown'} & cfg['animations'].keys()), 'Não referenciar GIFs antigos excluídos'
assert all(v is None or (isinstance(v,dict) and v.get('file')==name+'.png') for name,v in cfg['animations'].items()), 'Configuração deve referenciar sprites próprios'
assert (root/'DANIEL.png').exists(), 'Preservar a referência original'
assert (root/'personagens/DANIEL/DIRECAO_DE_ARTE.md').exists()
print('OK: invariantes do combate e da arte do Daniel')
