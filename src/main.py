"""
Punto de entrada del juego. Conecta dominio, aplicacion e infraestructura.
Corre en pantalla completa, adaptandose a la resolucion del monitor.

Controles:
    - En el menu de dificultad: 1 = Casual, 2 = Profesional
    - Flechas / WASD: mover
    - SPACE: disparar
    - P: pausar / despausar
    - R: volver al menu de dificultad (solo cuando la partida termino)
    - ESC: salir del juego
"""
import pygame

from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.game_state import GameState
from src.application.game_loop import GameLoop
from src.infrastructure.pygame_input import read_input
from src.infrastructure.renderer import Renderer

FPS = 60

PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_SPEED = 400

BOSS_WIDTH = 160
BOSS_HEIGHT = 120
BOSS_HP = 300

ESTADO_MENU = "menu"
ESTADO_JUGANDO = "jugando"


def crear_partida(screen_width: int, screen_height: int, max_phase: int) -> GameLoop:
    player_x = screen_width / 2 - PLAYER_WIDTH / 2
    player_y = screen_height - 100

    boss_x = screen_width / 2 - BOSS_WIDTH / 2
    boss_y = 50

    player = Player(
        position=Vector2(player_x, player_y),
        width=PLAYER_WIDTH, height=PLAYER_HEIGHT, hp=3, speed=PLAYER_SPEED,
        screen_width=screen_width, screen_height=screen_height,
    )
    boss = Boss(
        position=Vector2(boss_x, boss_y),
        width=BOSS_WIDTH, height=BOSS_HEIGHT, hp=BOSS_HP, max_hp=BOSS_HP,
        screen_width=screen_width, screen_height=screen_height,
        max_phase=max_phase,
    )
    game_state = GameState()
    return GameLoop(player=player, boss=boss, game_state=game_state)


def dibujar_menu_dificultad(surface, font, screen_width, screen_height):
    surface.fill((20, 20, 40))

    titulo = font.render("Selecciona la dificultad", True, (255, 255, 255))
    rect_titulo = titulo.get_rect(center=(screen_width // 2, screen_height // 2 - 60))
    surface.blit(titulo, rect_titulo)

    opcion1 = font.render("1 - Casual (el jefe llega hasta su segunda fase)", True, (200, 230, 255))
    rect1 = opcion1.get_rect(center=(screen_width // 2, screen_height // 2))
    surface.blit(opcion1, rect1)

    opcion2 = font.render("2 - Profesional (jefe completo, 3 fases)", True, (255, 200, 200))
    rect2 = opcion2.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
    surface.blit(opcion2, rect2)


def dibujar_pausa(surface, font, screen_width, screen_height):
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    texto = font.render("PAUSA", True, (255, 255, 255))
    rect = texto.get_rect(center=(screen_width // 2, screen_height // 2))
    surface.blit(texto, rect)


def dibujar_mensaje_reinicio(surface, font, screen_width, screen_height):
    texto = font.render("Presiona R para volver al menu", True, (255, 255, 255))
    rect = texto.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
    surface.blit(texto, rect)


def main():
    pygame.init()

    info_pantalla = pygame.display.Info()
    screen_width = info_pantalla.current_w
    screen_height = info_pantalla.current_h

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Cuphead Shmup - Prototipo TDD")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28)

    renderer = Renderer(screen_width, screen_height)

    estado = ESTADO_MENU
    game_loop = None
    pausado = False

    corriendo = True
    while corriendo:
        dt = clock.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False

                if estado == ESTADO_MENU:
                    if evento.key == pygame.K_1:
                        game_loop = crear_partida(screen_width, screen_height, max_phase=2)
                        estado = ESTADO_JUGANDO
                        pausado = False
                    elif evento.key == pygame.K_2:
                        game_loop = crear_partida(screen_width, screen_height, max_phase=3)
                        estado = ESTADO_JUGANDO
                        pausado = False

                elif estado == ESTADO_JUGANDO:
                    if evento.key == pygame.K_p and not game_loop.game_state.is_game_over():
                        pausado = not pausado

                    if evento.key == pygame.K_r and game_loop.game_state.is_game_over():
                        estado = ESTADO_MENU
                        game_loop = None
                        pausado = False

        if estado == ESTADO_MENU:
            dibujar_menu_dificultad(screen, font, screen_width, screen_height)

        elif estado == ESTADO_JUGANDO:
            keys = pygame.key.get_pressed()
            direccion, disparando = read_input(keys)

            if not pausado:
                game_loop.tick(dt=dt, move_direction=direccion, is_shooting=disparando)

            renderer.draw(screen, game_loop)

            if pausado:
                dibujar_pausa(screen, font, screen_width, screen_height)

            if game_loop.game_state.is_game_over():
                dibujar_mensaje_reinicio(screen, font, screen_width, screen_height)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()