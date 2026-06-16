"""
Tests unitarios para MiniBoss (domain).
TDD - Ciclo 15b: mini-jefe invulnerable que aparece cuando el Boss
principal baja de cierto HP. Se mueve verticalmente al azar y dispara
un abanico de 3 balas siempre apuntando al centro horizontal de pantalla.
"""
import pytest
import math
from src.domain.vector import Vector2
from src.domain.entities.mini_boss import MiniBoss
from src.domain.entities.projectile import Owner


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MINI_BOSS_WIDTH = 60
MINI_BOSS_HEIGHT = 60


def make_mini_boss(x=20, y=300, shoot_cooldown=2.0):
    return MiniBoss(
        position=Vector2(x, y), width=MINI_BOSS_WIDTH, height=MINI_BOSS_HEIGHT,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
        shoot_cooldown=shoot_cooldown,
    )


class TestMiniBossCreacion:
    def test_se_crea_con_posicion_y_tamano(self):
        m = make_mini_boss(x=20, y=300)
        assert m.position.x == 20
        assert m.position.y == 300
        assert m.width == MINI_BOSS_WIDTH
        assert m.height == MINI_BOSS_HEIGHT

    def test_tiene_hitbox_acorde_a_su_tamano(self):
        m = make_mini_boss(x=20, y=300)
        assert m.hitbox.left == 20
        assert m.hitbox.top == 300


class TestMiniBossInvulnerabilidad:
    def test_siempre_esta_vivo(self):
        m = make_mini_boss()
        assert m.is_alive() is True

    def test_take_damage_no_hace_nada(self):
        m = make_mini_boss()
        m.take_damage(9999)
        assert m.is_alive() is True


class TestMiniBossMovimientoVertical:
    def test_se_mueve_segun_direccion_elegida(self):
        m = make_mini_boss(y=300)

        def direccion_fija(opciones):
            return 1

        def intervalo_fijo(minimo, maximo):
            return 10.0

        m.update(dt=0.1, choose_direction_func=direccion_fija, choose_interval_func=intervalo_fijo)
        assert m.position.y > 300

    def test_no_se_mueve_si_direccion_elegida_es_cero(self):
        m = make_mini_boss(y=300)

        def direccion_fija(opciones):
            return 0

        def intervalo_fijo(minimo, maximo):
            return 10.0

        m.update(dt=0.1, choose_direction_func=direccion_fija, choose_interval_func=intervalo_fijo)
        assert m.position.y == 300

    def test_no_sale_de_pantalla_por_arriba(self):
        m = make_mini_boss(y=5)

        def direccion_fija(opciones):
            return -1

        def intervalo_fijo(minimo, maximo):
            return 10.0

        m.update(dt=5.0, choose_direction_func=direccion_fija, choose_interval_func=intervalo_fijo)
        assert m.position.y == 0

    def test_no_sale_de_pantalla_por_abajo(self):
        m = make_mini_boss(y=SCREEN_HEIGHT - MINI_BOSS_HEIGHT - 5)

        def direccion_fija(opciones):
            return 1

        def intervalo_fijo(minimo, maximo):
            return 10.0

        m.update(dt=5.0, choose_direction_func=direccion_fija, choose_interval_func=intervalo_fijo)
        assert m.position.y == SCREEN_HEIGHT - MINI_BOSS_HEIGHT

    def test_se_mueve_en_x_es_decir_no_cambia_nunca(self):
        m = make_mini_boss(x=20, y=300)

        def direccion_fija(opciones):
            return 1

        def intervalo_fijo(minimo, maximo):
            return 10.0

        m.update(dt=1.0, choose_direction_func=direccion_fija, choose_interval_func=intervalo_fijo)
        assert m.position.x == 20


class TestMiniBossDisparo:
    def test_dispara_abanico_de_3_al_cumplir_cooldown(self):
        m = make_mini_boss(shoot_cooldown=2.0)
        proyectiles = m.update(dt=2.0)
        assert len(proyectiles) == 3

    def test_no_dispara_antes_de_cumplir_cooldown(self):
        m = make_mini_boss(shoot_cooldown=2.0)
        proyectiles = m.update(dt=1.0)
        assert proyectiles == []

    def test_proyectiles_pertenecen_al_enemigo(self):
        m = make_mini_boss(shoot_cooldown=2.0)
        proyectiles = m.update(dt=2.0)
        for p in proyectiles:
            assert p.owner == Owner.ENEMY

    def test_abanico_apunta_hacia_el_centro_de_pantalla_desde_la_izquierda(self):
        """Un MiniBoss a la izquierda debe disparar predominantemente
        hacia la derecha (centro de pantalla esta a su derecha)."""
        m = make_mini_boss(x=20, y=300, shoot_cooldown=2.0)
        proyectiles = m.update(dt=2.0)
        for p in proyectiles:
            assert p.velocity.x > 0

    def test_abanico_apunta_hacia_el_centro_de_pantalla_desde_la_derecha(self):
        """Un MiniBoss a la derecha debe disparar predominantemente
        hacia la izquierda (centro de pantalla esta a su izquierda)."""
        m = make_mini_boss(x=SCREEN_WIDTH - 80, y=300, shoot_cooldown=2.0)
        proyectiles = m.update(dt=2.0)
        for p in proyectiles:
            assert p.velocity.x < 0

    def test_cooldown_se_reinicia_tras_disparar(self):
        m = make_mini_boss(shoot_cooldown=2.0)
        m.update(dt=2.0)
        proyectiles_inmediatos = m.update(dt=0.1)
        assert proyectiles_inmediatos == []