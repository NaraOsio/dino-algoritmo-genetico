# Dino com Algoritmo Genético

Projeto inspirado no jogo do dinossauro.

## Como executar

```bash
pip install -r requirements.txt
python main.py
```

## Como funciona

Cada dinossauro possui um cérebro com pesos numéricos. Ele recebe sensores:

- distância até o obstáculo
- altura do obstáculo
- largura do obstáculo
- velocidade do jogo
- altura atual do dinossauro
- se está no chão

Quando todos morrem, o algoritmo genético seleciona os melhores, cruza os pesos, aplica mutação e cria uma nova geração.
