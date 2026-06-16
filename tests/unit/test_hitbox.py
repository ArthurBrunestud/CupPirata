"""
Tests unitarios para Hitbox (domain).
TDD - Ciclo 2: se escriben antes de implementar Hitbox.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox


class TestHitboxCreacion:
    def test_crea_hitbox_con_posicion_y_tamano(self):
        hb = Hitbox(position=Vector2(10, 20), width=32, height=16)
        assert hb.position.x == 10
        assert hb.position.y == 20
        assert hb.width == 32
        assert hb.height == 16


class TestHitboxBordes:
    def test_borde_izquierdo(self):
        hb = Hitbox(position=Vector2(10, 20), width=32, height=16)
        assert hb.left == 10

    def test_borde_derecho(self):
        hb = Hitbox(position=Vector2(10, 20), width=32, height=16)
        assert hb.right == 42

    def test_borde_superior(self):
        hb = Hitbox(position=Vector2(10, 20), width=32, height=16)
        assert hb.top == 20

    def test_borde_inferior(self):
        hb = Hitbox(position=Vector2(10, 20), width=32, height=16)
        assert hb.bottom == 36


class TestHitboxColision:
    def test_dos_hitboxes_que_se_superponen_colisionan(self):
        a = Hitbox(position=Vector2(0, 0), width=10, height=10)
        b = Hitbox(position=Vector2(5, 5), width=10, height=10)
        assert a.collides_with(b) is True

    def test_dos_hitboxes_separadas_no_colisionan(self):
        a = Hitbox(position=Vector2(0, 0), width=10, height=10)
        b = Hitbox(position=Vector2(100, 100), width=10, height=10)
        assert a.collides_with(b) is False

    def test_hitboxes_que_solo_se_tocan_en_el_borde_no_colisionan(self):
        a = Hitbox(position=Vector2(0, 0), width=10, height=10)
        b = Hitbox(position=Vector2(10, 0), width=10, height=10)
        assert a.collides_with(b) is False

    def test_colision_es_simetrica(self):
        a = Hitbox(position=Vector2(0, 0), width=10, height=10)
        b = Hitbox(position=Vector2(5, 5), width=10, height=10)
        assert a.collides_with(b) == b.collides_with(a)

    def test_hitbox_colisiona_consigo_misma(self):
        a = Hitbox(position=Vector2(0, 0), width=10, height=10)
        assert a.collides_with(a) is True


class TestHitboxMovimiento:
    def test_mover_hitbox_actualiza_posicion(self):
        hb = Hitbox(position=Vector2(0, 0), width=10, height=10)
        hb.move_to(Vector2(50, 60))
        assert hb.position.x == 50
        assert hb.position.y == 60
        assert hb.left == 50
        assert hb.top == 60