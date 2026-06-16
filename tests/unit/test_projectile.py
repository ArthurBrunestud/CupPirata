"""
Tests unitarios para Projectile (domain).
TDD - Ciclo 4: se escriben antes de implementar Projectile.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.projectile import Projectile, Owner


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PROJ_WIDTH = 8
PROJ_HEIGHT = 8


def make_projectile(
    x=400, y=300,
    vx=0, vy=-500,
    damage=1,
    owner=Owner.PLAYER,
):
    return Projectile(
        position=Vector2(x, y),
        velocity=Vector2(vx, vy),
        width=PROJ_WIDTH,
        height=PROJ_HEIGHT,
        damage=damage,
        owner=owner,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
    )


class TestProjectileCreacion:
    def test_se_crea_con_posicion_velocidad_y_dano(self):
        p = make_projectile(x=100, y=200, vx=0, vy=-500, damage=2)
        assert p.position.x == 100
        assert p.position.y == 200
        assert p.velocity.x == 0
        assert p.velocity.y == -500
        assert p.damage == 2

    def test_proyectil_del_jugador_tiene_owner_player(self):
        p = make_projectile(owner=Owner.PLAYER)
        assert p.owner == Owner.PLAYER

    def test_proyectil_del_enemigo_tiene_owner_enemy(self):
        p = make_projectile(owner=Owner.ENEMY)
        assert p.owner == Owner.ENEMY

    def test_proyectil_tiene_hitbox_acorde_a_su_tamano(self):
        p = make_projectile(x=100, y=200)
        assert p.hitbox.left == 100
        assert p.hitbox.top == 200
        assert p.hitbox.width == PROJ_WIDTH
        assert p.hitbox.height == PROJ_HEIGHT


class TestProjectileMovimiento:
    def test_proyectil_avanza_segun_velocidad_y_dt(self):
        p = make_projectile(x=100, y=300, vx=0, vy=-500)
        p.update(dt=1.0)
        assert p.position.y == -200  # 300 + (-500)*1.0

    def test_proyectil_horizontal_avanza_en_x(self):
        p = make_projectile(x=100, y=300, vx=400, vy=0)
        p.update(dt=0.5)
        assert p.position.x == 300  # 100 + 400*0.5
        assert p.position.y == 300

    def test_hitbox_se_mueve_con_el_proyectil(self):
        p = make_projectile(x=100, y=300, vx=0, vy=-200)
        p.update(dt=0.1)
        assert p.hitbox.left == p.position.x
        assert p.hitbox.top == p.position.y

    def test_proyectil_no_se_recorta_a_pantalla(self):
        """A diferencia del Player, el proyectil SÍ puede salir de pantalla."""
        p = make_projectile(x=400, y=10, vx=0, vy=-500)
        p.update(dt=1.0)
        assert p.position.y == -490  # se va más allá del borde superior


class TestProjectileFueraDePantalla:
    def test_dentro_de_pantalla_no_esta_fuera(self):
        p = make_projectile(x=400, y=300)
        assert p.is_off_screen() is False

    def test_arriba_de_pantalla_esta_fuera(self):
        p = make_projectile(x=400, y=-50)
        assert p.is_off_screen() is True

    def test_abajo_de_pantalla_esta_fuera(self):
        p = make_projectile(x=400, y=SCREEN_HEIGHT + 10)
        assert p.is_off_screen() is True

    def test_a_la_izquierda_de_pantalla_esta_fuera(self):
        p = make_projectile(x=-20, y=300)
        assert p.is_off_screen() is True

    def test_a_la_derecha_de_pantalla_esta_fuera(self):
        p = make_projectile(x=SCREEN_WIDTH + 10, y=300)
        assert p.is_off_screen() is True

    def test_en_borde_exacto_aun_visible_no_esta_fuera(self):
        """Si una parte del proyectil aún se ve, no está 'fuera'."""
        p = make_projectile(x=0, y=0)
        assert p.is_off_screen() is False