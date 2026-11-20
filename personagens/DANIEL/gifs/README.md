# GIFs de animação — Daniel

Coloque os GIFs exportados do Ludo.ai nesta pasta com os nomes dos estados do jogo:

`idle.gif`, `walk.gif`, `run.gif`, `jump.gif`, `fall.gif`, `crouch.gif`, `guard.gif`, `crouchGuard.gif`, `punchFront.gif`, `punchBack.gif`, `kickFront.gif`, `kickBack.gif`, `hurt.gif`, `knockdown.gif`, `getup.gif`, `magic1.gif`, `magic2.gif`, `magic3.gif`, `special.gif`.

**Requisitos:** personagem completo em cada quadro, fundo transparente, perspectiva lateral, consistência de roupas/rosto e pés alinhados. O arquivo `DANIEL.png` é apenas referência artística.

Depois de enviar os GIFs, execute na raiz do repositório:

```bash
python -m pip install Pillow
python tools/import_gif_animations.py DANIEL --fps 12
python tools/validate_daniel_sprites.py
```

O importador gera PNGs em `personagens/DANIEL/sprites/` e atualiza `config.json`. GIFs com fundo opaco precisam de correção na origem. O importador não remove fundos automaticamente. O FPS informado é uniforme: para movimentos com duração irregular, ajuste o GIF antes da importação.

**Atenção:** o vídeo enviado demonstra a ferramenta Ludo.ai, mas não fornece os arquivos GIF individuais do Daniel. A conversão só poderá ocorrer depois de os GIFs serem adicionados.
