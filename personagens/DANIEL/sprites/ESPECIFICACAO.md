# DANIEL — especificação de exportação de sprites

**Arte oficial:** `/DANIEL.png`. Preservar o rosto, cabelo cacheado escuro, camisa azul sobre camiseta branca, calça cargo bege, tênis pretos e mochila preta.

## Quadros planejados

| Estado | Quadros | FPS | Loop |
|---|---:|---:|---|
| idle | 8 | 8 | sim |
| walk | 8 | 12 | sim |
| run | 8 | 16 | sim |
| jump | 5 | 12 | não |
| fall | 3 | 10 | não |
| crouch | 3 | 10 | não |
| guard | 4 | 10 | sim |
| crouchGuard | 3 | 10 | sim |
| punchFront | 6 | 18 | não |
| punchBack | 7 | 17 | não |
| kickFront | 7 | 17 | não |
| kickBack | 8 | 16 | não |
| hurt | 4 | 12 | não |
| knockdown | 6 | 12 | não |
| getup | 6 | 12 | não |
| magic1 | 8 | 18 | não |
| magic2 | 8 | 16 | não |
| magic3 | 8 | 18 | não |
| special | 12 | 20 | não |

**Exportação:** PNG com transparência real, cada quadro com dimensões idênticas, personagem alinhado ao solo. Grade horizontal ou múltiplas linhas. Recomenda-se 128 × 192 px por quadro, 4 colunas por spritesheet, e nenhuma legenda, fundo ou moldura.

O carregador aceita `file`, `frames`, `columns`, `fps`, `frameWidth`, `frameHeight`, `loop`, `scale`, `offsetX` e `offsetY`. Não basta uma prancha ilustrativa com quadros de tamanhos variados: cada animação deve ser exportada como spritesheet jogável.

## Exemplo para inserir em ../config.json

```json
"walk": {
  "file": "walk.png",
  "frames": 8,
  "columns": 4,
  "fps": 12,
  "frameWidth": 128,
  "frameHeight": 192,
  "loop": true
}
```

**Estado atual:** especificações e carregador disponíveis. Os arquivos de quadros articulados não foram produzidos. Os efeitos vetoriais de poderes e impacto estão em `../assets/`.
