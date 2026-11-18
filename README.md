# MARKYS FIGHT

Jogo de luta 2D para navegador, com cinco personagens originais: Daniel, Helena, Josy, Markys e Milena.

## Executar

Abra `index.html` no navegador. As imagens `DANIEL.png`, `HELENA.png`, `JOSY.png`, `MARKYS.png` e `MILENA.png` devem permanecer na mesma pasta do HTML.

## Controles

- A / D: movimentar
- Shift + A / D: correr
- W: pular
- S: defender
- J: soco
- K: chute
- 1 / 2 / 3: poderes individuais
- L: especial (requer energia)
- P: pausar

## Estado real do desenvolvimento

- **Implementado:** seleção dos cinco personagens, combate contra CPU, vida, energia, golpes, poderes, projéteis, rodadas e animações procedurais de imagem inteira.
- **Pendente:** spritesheets autênticos e animações articuladas (braços, pernas e poses completas), testes visuais e balanceamento de todos os poderes.
- **Importante:** os cinco PNGs originais são as referências definitivas. Não substituir por personagens genéricos.

## Organização

O desenvolvimento é feito diretamente na branch `main`, conforme solicitado. Os arquivos originais de personagens devem ser preservados.


## Gamepad (Xbox / PlayStation)

- A / ✕: soco frontal
- X / □: chute frontal
- Y / △: soco traseiro
- B / ○: chute traseiro
- RT / R2: defesa
- Analógico esquerdo ou direcional: movimentação, salto e agachamento (a movimentação agachada ainda requer ajuste visual)
- Start / Options: pausa

### Combinações de magias (relativas à direção do personagem)

1. ↓ ↘ → + A / ✕
2. ↓ ↙ ← + X / □
3. → ↓ ↘ + Y / △
4. ↓ ↘ → ↓ ↘ → + B / ○

As sequências têm janela de entrada de 1,25 segundo. Todos os personagens compartilham as mesmas combinações nesta etapa; futuramente podem receber perfis próprios.

**Limitação:** reconhecimento implementado no código, ainda sem homologação em controle físico. Golpes frontais e traseiros usam as animações básicas existentes; animações distintas ainda estão pendentes.
