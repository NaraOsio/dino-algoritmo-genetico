import pygame
import random
import math

LARGURA = 1000
ALTURA = 500
CHAO_Y = 380
FPS = 60

TAMANHO_POPULACAO = 30
TAXA_MUTACAO = 0.12
ELITISMO = 4

pygame.init()

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dino IA - Algoritmo Genético")

relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("Arial", 22)
fonte_grande = pygame.font.SysFont("Arial", 34, bold=True)


class Cerebro:

    def __init__(self, pesos=None, bias=None):

        self.pesos = pesos[:] if pesos else [
            random.uniform(-1, 1) for _ in range(6)
        ]

        self.bias = random.uniform(-1, 1) if bias is None else bias

    def ativacao(self, x):
        return 1 / (1 + math.exp(-x))

    def decidir(self, sensores):

        soma = self.bias

        for valor, peso in zip(sensores, self.pesos):
            soma += valor * peso

        return self.ativacao(soma) > 0.5

    def cruzar(self, outro):

        novos_pesos = [
            random.choice([a, b])
            for a, b in zip(self.pesos, outro.pesos)
        ]

        novo_bias = random.choice([self.bias, outro.bias])

        return Cerebro(novos_pesos, novo_bias)

    def mutar(self):

        for i in range(len(self.pesos)):

            if random.random() < TAXA_MUTACAO:
                self.pesos[i] += random.uniform(-0.5, 0.5)

        if random.random() < TAXA_MUTACAO:
            self.bias += random.uniform(-0.5, 0.5)


class Obstaculo:

    def __init__(self, velocidade):

        self.largura = random.randint(25, 55)
        self.altura = random.randint(45, 95)

        self.x = LARGURA + random.randint(0, 180)

        self.y = CHAO_Y - self.altura

        self.velocidade = velocidade

    def atualizar(self, velocidade):

        self.velocidade = velocidade
        self.x -= self.velocidade

    def desenhar(self):

        pygame.draw.rect(
            tela,
            (45, 45, 45),
            (self.x, self.y, self.largura, self.altura),
            border_radius=4
        )

    def saiu_da_tela(self):
        return self.x + self.largura < 0


class Dino:

    def __init__(self, cerebro=None):

        self.x = 100

        self.largura = 42
        self.altura = 58

        self.y = CHAO_Y - self.altura

        self.vel_y = 0

        self.vivo = True

        self.pontuacao = 0
        self.aptidao = 0

        self.cerebro = cerebro if cerebro else Cerebro()

    def no_chao(self):
        return self.y >= CHAO_Y - self.altura

    def pular(self):

        if self.no_chao():
            self.vel_y = -15

    def atualizar(self):

        if not self.vivo:
            return

        self.vel_y += 0.8
        self.y += self.vel_y

        if self.y >= CHAO_Y - self.altura:

            self.y = CHAO_Y - self.altura
            self.vel_y = 0

        self.pontuacao += 1
        self.aptidao = self.pontuacao

    def sensores(self, obstaculo, velocidade):

        distancia = max(0, obstaculo.x - self.x) / LARGURA

        altura_obstaculo = obstaculo.altura / 120

        largura_obstaculo = obstaculo.largura / 80

        velocidade_norm = velocidade / 20

        altura_dino = (CHAO_Y - self.y) / 200

        esta_no_chao = 1 if self.no_chao() else 0

        return [
            distancia,
            altura_obstaculo,
            largura_obstaculo,
            velocidade_norm,
            altura_dino,
            esta_no_chao
        ]

    def pensar(self, obstaculo, velocidade):

        if self.vivo and self.cerebro.decidir(
                self.sensores(obstaculo, velocidade)):

            self.pular()

    def colidiu(self, obstaculo):

        rect_dino = pygame.Rect(
            self.x,
            self.y,
            self.largura,
            self.altura
        )

        rect_obstaculo = pygame.Rect(
            obstaculo.x,
            obstaculo.y,
            obstaculo.largura,
            obstaculo.altura
        )

        return rect_dino.colliderect(rect_obstaculo)

    def desenhar(self, destaque=False):

        if not self.vivo:
            return

        cor = (25, 160, 80) if destaque else (80, 170, 255)

        # Corpo
        pygame.draw.rect(
            tela,
            cor,
            (self.x, self.y + 15, self.largura, self.altura - 15),
            border_radius=8
        )

        # Cabeça
        pygame.draw.rect(
            tela,
            cor,
            (self.x + 25, self.y, 35, 28),
            border_radius=8
        )

        # Olho
        pygame.draw.circle(
            tela,
            (0, 0, 0),
            (self.x + 50, self.y + 9),
            3
        )

        # Pernas
        pygame.draw.rect(
            tela,
            cor,
            (self.x + 7, self.y + self.altura - 5, 10, 18)
        )

        pygame.draw.rect(
            tela,
            cor,
            (self.x + 27, self.y + self.altura - 5, 10, 18)
        )


class Populacao:

    def __init__(self):

        self.geracao = 1

        self.dinos = [
            Dino()
            for _ in range(TAMANHO_POPULACAO)
        ]

        self.melhor_pontuacao = 0

    def vivos(self):

        return [d for d in self.dinos if d.vivo]

    def todos_mortos(self):

        return len(self.vivos()) == 0

    def nova_geracao(self):

        self.dinos.sort(
            key=lambda d: d.aptidao,
            reverse=True
        )

        if self.dinos[0].aptidao > self.melhor_pontuacao:
            self.melhor_pontuacao = self.dinos[0].aptidao

        melhores = self.dinos[:ELITISMO]

        nova_lista = []

        # Mantém os melhores
        for melhor in melhores:

            cerebro = Cerebro(
                melhor.cerebro.pesos,
                melhor.cerebro.bias
            )

            nova_lista.append(Dino(cerebro))

        # Cria filhos
        while len(nova_lista) < TAMANHO_POPULACAO:

            pai = random.choice(melhores)
            mae = random.choice(melhores)

            filho = pai.cerebro.cruzar(mae.cerebro)

            filho.mutar()

            nova_lista.append(Dino(filho))

        self.dinos = nova_lista

        self.geracao += 1


class Jogo:

    def __init__(self):

        self.populacao = Populacao()

        self.velocidade = 7

        self.pontuacao = 0

        self.obstaculos = [
            Obstaculo(self.velocidade)
        ]

    def reiniciar_mapa(self):

        self.velocidade = 7

        self.pontuacao = 0

        self.obstaculos = [
            Obstaculo(self.velocidade)
        ]

    def proximo_obstaculo(self):

        frente = [
            o for o in self.obstaculos
            if o.x + o.largura > 100
        ]

        return min(frente, key=lambda o: o.x)

    def atualizar(self):

        self.pontuacao += 1

        self.velocidade = 7 + self.pontuacao / 1200

        if len(self.obstaculos) == 0 or self.obstaculos[-1].x < 650:

            self.obstaculos.append(
                Obstaculo(self.velocidade)
            )

        for obstaculo in self.obstaculos:
            obstaculo.atualizar(self.velocidade)

        self.obstaculos = [
            o for o in self.obstaculos
            if not o.saiu_da_tela()
        ]

        alvo = self.proximo_obstaculo()

        for dino in self.populacao.dinos:

            if dino.vivo:

                dino.pensar(alvo, self.velocidade)

                dino.atualizar()

                for obstaculo in self.obstaculos:

                    if dino.colidiu(obstaculo):
                        dino.vivo = False
                        break

        if self.populacao.todos_mortos():

            self.populacao.nova_geracao()

            self.reiniciar_mapa()

    def desenhar_sensores(self):

        vivos = self.populacao.vivos()

        if not vivos:
            return

        dino = vivos[0]

        obstaculo = self.proximo_obstaculo()

        pygame.draw.line(
            tela,
            (255, 80, 80),
            (dino.x + dino.largura, dino.y + 10),
            (obstaculo.x, obstaculo.y),
            2
        )

        texto = fonte.render(
            "Sensor: distância até o obstáculo",
            True,
            (200, 50, 50)
        )

        tela.blit(texto, (20, 170))

    def desenhar_interface(self):

        info = [

            f"Geração: {self.populacao.geracao}",

            f"Vivos: {len(self.populacao.vivos())}/{TAMANHO_POPULACAO}",

            f"Pontuação: {self.pontuacao}",

            f"Melhor: {self.populacao.melhor_pontuacao}",

            f"Velocidade: {self.velocidade:.1f}",
        ]

        y = 15

        for linha in info:

            texto = fonte.render(
                linha,
                True,
                (30, 30, 30)
            )

            tela.blit(texto, (20, y))

            y += 32

        titulo = fonte_grande.render(
            "Dino IA - Algoritmo Genético",
            True,
            (35, 35, 35)
        )

        tela.blit(titulo, (LARGURA - 430, 18))

    def desenhar(self):

        tela.fill((245, 245, 245))

        pygame.draw.rect(
            tela,
            (235, 245, 255),
            (0, 0, LARGURA, CHAO_Y)
        )

        pygame.draw.line(
            tela,
            (80, 80, 80),
            (0, CHAO_Y),
            (LARGURA, CHAO_Y),
            4
        )

        for obstaculo in self.obstaculos:
            obstaculo.desenhar()

        vivos = self.populacao.vivos()

        melhor_vivo = vivos[0] if vivos else None

        for dino in self.populacao.dinos:

            dino.desenhar(
                destaque=(dino == melhor_vivo)
            )

        self.desenhar_sensores()

        self.desenhar_interface()


def main():

    jogo = Jogo()

    executando = True

    pausado = False

    while executando:

        relogio.tick(FPS)

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                executando = False

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:
                    executando = False

                if evento.key == pygame.K_SPACE:
                    pausado = not pausado

        if not pausado:
            jogo.atualizar()

        jogo.desenhar()

        if pausado:

            aviso = fonte_grande.render(
                "PAUSADO - aperte ESPAÇO",
                True,
                (180, 0, 0)
            )

            tela.blit(aviso, (330, 220))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()