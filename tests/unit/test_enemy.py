"""
Tests unitarios para Enemy (domain).
TDD - Ciclo 15a: clase base compartida por Boss y MiniBoss.
Contiene solo lo genuinamente comun: posicion, tamano, hitbox,
y un metodo generico para recortar una coordenada a los bordes de pantalla.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.enemy import Enemy


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_enemy(x=100, y=100, width=50, height=50):
    return Enemy(
        position=Vector2(x, y), width=width, height=height,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


class TestEnemyCreacion:
    def test_se_crea_con_posicion_y_tamano(self):
        e = make_enemy(x=100, y=200, width=50, height=60)
        assert e.position.x == 100
        assert e.position.y == 200
        assert e.width == 50
        assert e.height == 60

    def test_tiene_hitbox_acorde_a_su_tamano(self):
        e = make_enemy(x=100, y=200, width=50, height=60)
        assert e.hitbox.left == 100
        assert e.hitbox.top == 200
        assert e.hitbox.width == 50
        assert e.hitbox.height == 60


class TestEnemyMovimientoGenerico:
    def test_mover_a_actualiza_posicion_y_hitbox(self):
        e = make_enemy(x=100, y=100)
        e.move_to(Vector2(300, 400))
        assert e.position.x == 300
        assert e.position.y == 400
        assert e.hitbox.left == 300
        assert e.hitbox.top == 400

    def test_recortar_x_a_pantalla_dentro_del_rango_no_cambia(self):
        e = make_enemy(width=50, height=50)
        resultado = e.clamp_x(400)
        assert resultado == 400

    def test_recortar_x_a_pantalla_por_la_izquierda(self):
        e = make_enemy(width=50, height=50)
        resultado = e.clamp_x(-20)
        assert resultado == 0

    def test_recortar_x_a_pantalla_por_la_derecha(self):
        e = make_enemy(width=50, height=50)
        resultado = e.clamp_x(SCREEN_WIDTH + 100)
        assert resultado == SCREEN_WIDTH - 50

    def test_recortar_y_a_pantalla_por_arriba(self):
        e = make_enemy(width=50, height=50)
        resultado = e.clamp_y(-30)
        assert resultado == 0

    def test_recortar_y_a_pantalla_por_abajo(self):
        e = make_enemy(width=50, height=50)
        resultado = e.clamp_y(SCREEN_HEIGHT + 100)
        assert resultado == SCREEN_HEIGHT - 50