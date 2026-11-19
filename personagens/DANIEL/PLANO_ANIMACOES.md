# DANIEL — Plano de animações (Etapa 1 de 6)

**Ordem obrigatória:** DANIEL → HELENA → JOSY → MARKYS → MILENA → GPT-6.

## Identidade visual
Referência oficial: `/DANIEL.png`. Preservar cabelo cacheado escuro, camisa azul aberta sobre camiseta branca, calça cargo bege, tênis pretos e mochila preta. Não usar sprites de outro personagem.

## Produção por etapas
1. **Base visual:** manter proporções, roupa, cores e transparência em todos os quadros.
2. **Movimentação:** `idle`, `walk`, `run`, `jump`, `fall`, `crouch`.
3. **Combate:** `guard`, `crouchGuard`, `punchFront`, `punchBack`, `kickFront`, `kickBack`, `hurt`, `knockdown`, `getup`.
4. **Magias:** `magic1` (hipercorrida), `magic2` (onda sonora), `magic3` (chute veloz), `special` (sequência super-rápida).
5. **Integração:** salvar PNGs em `sprites/` e registrar cada spritesheet no `config.json`.
6. **Validação:** testar orientação, velocidade, colisões, controle de teclado/gamepad e transição entre estados.

## Padrão técnico
Spritesheet PNG transparente, quadros em uma linha horizontal, dimensões idênticas por quadro. Exemplo de configuração:

```json
"walk": {
  "file": "walk.png",
  "frames": 8,
  "fps": 12,
  "frameWidth": 128,
  "frameHeight": 192,
  "loop": true
}
```

**Status:** plano criado. Os sprites ainda precisam ser desenhados e exportados. Não marcar uma animação como concluída antes de existir um arquivo válido e ser testado no jogo.
