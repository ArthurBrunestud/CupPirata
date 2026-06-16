"""
Tests unitarios para Player (domain).
TDD - Ciclo 3: se escriben antes de implementar Player.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.player import Player


# Constantes de prueba (pantalla típica del juego)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 30


def make_player(x=400, y=300, hp=3, speed=200):
    return Player(
        position=Vector2(x, y),
        width=PLAYER_WIDTH,
        height=PLAYER_HEIGHT,
        hp=hp,
        speed=speed,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
    )


class TestPlayerCreacion:
    def test_player_se_crea_con_posicion_y_vidas(self):
        p = make_player(x=100, y=200, hp=3)
        assert p.position.x == 100
        assert p.position.y == 200
        assert p.hp == 3

    def test_player_esta_vivo_al_crearse(self):
        p = make_player(hp=3)
        assert p.is_alive() is True

    def test_player_tiene_hitbox_acorde_a_su_tamano(self):
        p = make_player(x=100, y=200)
        assert p.hitbox.left == 100
        assert p.hitbox.top == 200
        assert p.hitbox.width == PLAYER_WIDTH
        assert p.hitbox.height == PLAYER_HEIGHT


class TestPlayerMovimiento:
    def test_mover_a_la_derecha_aumenta_x(self):
        p = make_player(x=400, y=300, speed=200)
        p.move(direction=Vector2(1, 0), dt=1.0)
        assert p.position.x == 600  # 400 + 200*1

    def test_mover_a_la_izquierda_disminuye_x(self):
        p = make_player(x=400, y=300, speed=200)
        p.move(direction=Vector2(-1, 0), dt=0.5)
        assert p.position.x == 300  # 400 - 200*0.5

    def test_mover_arriba_disminuye_y(self):
        p = make_player(x=400, y=300, speed=100)
        p.move(direction=Vector2(0, -1), dt=1.0)
        assert p.position.y == 200

    def test_mover_abajo_aumenta_y(self):
        p = make_player(x=400, y=300, speed=100)
        p.move(direction=Vector2(0, 1), dt=1.0)
        assert p.position.y == 400

    def test_movimiento_diagonal_se_normaliza(self):
        """Moverse en diagonal NO debe ser más rápido que en línea recta."""
        p = make_player(x=400, y=300, speed=100)
        p.move(direction=Vector2(1, 1), dt=1.0)
        # distancia recorrida debe ser 100 (no sqrt(2)*100)
        dx = p.position.x - 400
        dy = p.position.y - 300
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        assert round(distancia, 5) == 100

    def test_hitbox_se_mueve_con_el_player(self):
        p = make_player(x=400, y=300)
        p.move(direction=Vector2(1, 0), dt=0.1)
        assert p.hitbox.left == p.position.x
        assert p.hitbox.top == p.position.y


class TestPlayerLimitesPantalla:
    def test_player_no_sale_por_la_izquierda(self):
        p = make_player(x=10, y=300, speed=1000)
        p.move(direction=Vector2(-1, 0), dt=1.0)
        assert p.position.x == 0

    def test_player_no_sale_por_la_derecha(self):
        p = make_player(x=700, y=300, speed=1000)
        p.move(direction=Vector2(1, 0), dt=1.0)
        assert p.position.x == SCREEN_WIDTH - PLAYER_WIDTH

    def test_player_no_sale_por_arriba(self):
        p = make_player(x=400, y=10, speed=1000)
        p.move(direction=Vector2(0, -1), dt=1.0)
        assert p.position.y == 0

    def test_player_no_sale_por_abajo(self):
        p = make_player(x=400, y=500, speed=1000)
        p.move(direction=Vector2(0, 1), dt=1.0)
        assert p.position.y == SCREEN_HEIGHT - PLAYER_HEIGHT


class TestPlayerVida:
    def test_recibir_dano_reduce_hp(self):
        p = make_player(hp=3)
        p.take_damage(1)
        assert p.hp == 2

    def test_recibir_dano_mayor_a_hp_lo_deja_en_cero(self):
        p = make_player(hp=2)
        p.take_damage(5)
        assert p.hp == 0

    def test_player_muerto_no_esta_vivo(self):
        p = make_player(hp=1)
        p.take_damage(1)
        assert p.is_alive() is False

    def test_recibir_dano_negativo_no_cura(self):
        """Daño negativo se ignora (no es una cura)."""
        p = make_player(hp=2)
        p.take_damage(-5)
        assert p.hp == 2