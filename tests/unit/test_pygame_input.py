"""
Tests unitarios para la traduccion de input de teclado a comandos del dominio.
TDD - Ciclo 10: read_input no abre ventana, solo traduce un diccionario
de teclas presionadas (simulable) a (Vector2 direccion, bool disparando).
"""
import pytest
import pygame
from src.domain.vector import Vector2
from src.infrastructure.pygame_input import read_input


def teclas(presionadas: list) -> dict:
    """Simula el diccionario que devuelve pygame.key.get_pressed(),
    pero solo como un dict normal indexado por constante de tecla."""
    todas = {
        pygame.K_LEFT: False, pygame.K_RIGHT: False,
        pygame.K_UP: False, pygame.K_DOWN: False,
        pygame.K_a: False, pygame.K_d: False,
        pygame.K_w: False, pygame.K_s: False,
        pygame.K_SPACE: False,
    }
    for tecla in presionadas:
        todas[tecla] = True
    return todas


class TestReadInputMovimiento:
    def test_sin_teclas_direccion_es_cero(self):
        direccion, _ = read_input(teclas([]))
        assert direccion.x == 0
        assert direccion.y == 0

    def test_flecha_derecha_mueve_a_la_derecha(self):
        direccion, _ = read_input(teclas([pygame.K_RIGHT]))
        assert direccion.x == 1
        assert direccion.y == 0

    def test_flecha_izquierda_mueve_a_la_izquierda(self):
        direccion, _ = read_input(teclas([pygame.K_LEFT]))
        assert direccion.x == -1

    def test_flecha_arriba_mueve_hacia_arriba(self):
        direccion, _ = read_input(teclas([pygame.K_UP]))
        assert direccion.y == -1

    def test_flecha_abajo_mueve_hacia_abajo(self):
        direccion, _ = read_input(teclas([pygame.K_DOWN]))
        assert direccion.y == 1

    def test_wasd_funciona_igual_que_flechas(self):
        direccion, _ = read_input(teclas([pygame.K_d]))
        assert direccion.x == 1

    def test_movimiento_diagonal_combina_ejes(self):
        direccion, _ = read_input(teclas([pygame.K_RIGHT, pygame.K_UP]))
        assert direccion.x == 1
        assert direccion.y == -1

    def test_teclas_opuestas_se_cancelan(self):
        direccion, _ = read_input(teclas([pygame.K_LEFT, pygame.K_RIGHT]))
        assert direccion.x == 0


class TestReadInputDisparo:
    def test_sin_espacio_no_dispara(self):
        _, disparando = read_input(teclas([]))
        assert disparando is False

    def test_espacio_presionado_dispara(self):
        _, disparando = read_input(teclas([pygame.K_SPACE]))
        assert disparando is True