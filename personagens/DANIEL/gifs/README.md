# GIFs oficiais enviados — DANIEL

Esta pasta já contém **14 arquivos GIF originais** adicionados pelo usuário. O jogo importa seus movimentos com o workflow `Importar GIFs reais do Daniel` na branch `main`, sem recortar o `DANIEL.png`.

## Correspondência para os estados do jogo

| GIF de entrada | Estado do jogo |
| --- | --- |
| DANIEL CAMINHANDO.gif | walk |
| DANIEL CORRENDO.gif | run |
| DANIEL SALTANDO.gif | jump |
| DANIEL SOCO DIRETO.gif | punchFront |
| DANIEL CHUTE ALTO.gif | kickFront |
| DANIEL SOFRENDO DANO.gif | hurt |
| DANIEL DERROTADO.gif | knockdown |
| DANIEL LEVANTANDO.gif | getup |
| DANIEL HIPERCORRIDA.gif | magic1 |
| DANIEL ONDA SONICA.gif | magic2 |
| DANIEL ESPECIAL PARTE 1.gif + PARTE 2.gif + PARTE 3.gif | special (sequência concatenada) |

`DANIEL SALTO MORTAL PRA TRAS.gif` é mapeado para `kickBack` temporariamente, até existir um estado específico de evasão; não é tratado como chute alto. **Estados não mapeados continuam com o sprite existente**, sem criar movimento novo artificial.

## Conversão

O workflow é acionado quando os GIFs ou o importador mudam. Também pode ser executado manualmente em GitHub Actions.

```bash
python -m pip install Pillow
python tools/import_gif_animations.py DANIEL --dry-run
python tools/import_gif_animations.py DANIEL
python tools/validate_daniel_sprites.py
```

As saídas são `personagens/DANIEL/sprites/<estado>.png` e `personagens/DANIEL/config.json`.

**Atenção à qualidade:** a extração preserva o canal alfa quando presente, mas não remove fundos opacos dos GIFs. O resultado deve ser conferido no laboratório `personagens/DANIEL/visualizar.html`. GIFs que sejam apenas uma composição de sprites estática poderão exigir recorte ou correção manual antes de serem usados em partida.
