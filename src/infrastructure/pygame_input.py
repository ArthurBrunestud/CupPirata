"""
pygame_input: traduce el estado del teclado (segun pygame) a comandos
del dominio: una direccion de movimiento (Vector2) y un booleano de disparo.

Esta es la UNICA pieza de infrastructure que GameLoop necesita para
recibir input, manteniendo al dominio y a la aplicacion sin conocer
absolutamente nada sobre pygame.

Controles:
    - Flechas o WASD: movimiento en 8 direcciones.
    - SPACE: disparar.
"""
import pygame
from src.domain.vector import Vector2


def read_input(keys_pressed) -> tuple:
    """
    keys_pressed: el resultado de pygame.key.get_pressed() (o un dict
    equivalente indexado por constante de tecla, util para testear).

    Devuelve: (direccion: Vector2, disparando: bool)
    """
    x = 0
    y = 0

    if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
        x -= 1
    if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
        x += 1
    if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
        y -= 1
    if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
        y += 1

    direccion = Vector2(x, y)
    disparando = bool(keys_pressed[pygame.K_SPACE])

    return direccion, disparando