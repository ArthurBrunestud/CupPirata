"""
Tests unitarios para Boss (domain).
TDD - Ciclo 6a: HP, fases y estado de vida del jefe.
Los ataques (proyectiles y rayo) se agregan en el ciclo 6b.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.boss import Boss
from src.domain.entities.projectile import Owner

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOSS_WIDTH = 160
BOSS_HEIGHT = 120


def make_boss(x=300, y=50, hp=300, max_hp=300):
    return Boss(
        position=Vector2(x, y),
        width=BOSS_WIDTH,
        height=BOSS_HEIGHT,
        hp=hp,
        max_hp=max_hp,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
    )


class TestBossCreacion:
    def test_se_crea_con_posicion_y_hp(self):
        b = make_boss(x=300, y=50, hp=300, max_hp=300)
        assert b.position.x == 300
        assert b.position.y == 50
        assert b.hp == 300
        assert b.max_hp == 300

    def test_jefe_esta_vivo_al_crearse(self):
        b = make_boss(hp=300)
        assert b.is_alive() is True

    def test_jefe_tiene_hitbox_acorde_a_su_tamano(self):
        b = make_boss(x=300, y=50)
        assert b.hitbox.left == 300
        assert b.hitbox.top == 50
        assert b.hitbox.width == BOSS_WIDTH
        assert b.hitbox.height == BOSS_HEIGHT

    def test_jefe_inicia_en_fase_1(self):
        b = make_boss(hp=300, max_hp=300)
        assert b.phase == 1


class TestBossVida:
    def test_recibir_dano_reduce_hp(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(50)
        assert b.hp == 250

    def test_recibir_dano_mayor_a_hp_lo_deja_en_cero(self):
        b = make_boss(hp=20, max_hp=300)
        b.take_damage(50)
        assert b.hp == 0

    def test_jefe_muerto_no_esta_vivo(self):
        b = make_boss(hp=10, max_hp=300)
        b.take_damage(10)
        assert b.is_alive() is False

    def test_recibir_dano_negativo_no_cura(self):
        b = make_boss(hp=200, max_hp=300)
        b.take_damage(-50)
        assert b.hp == 200


class TestBossFases:
    def test_arriba_de_66_porciento_sigue_en_fase_1(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(99)  # queda en 201/300 = 67%
        assert b.phase == 1

    def test_a_66_porciento_o_menos_pasa_a_fase_2(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(102)  # queda en 198/300 = 66%
        assert b.phase == 2

    def test_a_33_porciento_o_menos_pasa_a_fase_3(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(201)  # queda en 99/300 = 33%
        assert b.phase == 3

    def test_jefe_muerto_se_queda_en_fase_3(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(300)  # queda en 0
        assert b.phase == 3

    def test_fase_no_retrocede_aunque_hp_suba_artificialmente(self):
        """La fase es un trinquete: una vez avanzada, no debe retroceder."""
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(250)  # pasa a fase 3
        assert b.phase == 3
        b.hp = 300  # manipulación directa simulando un bug externo
        b._actualizar_fase()
        assert b.phase == 3




class TestBossAtaqueProyectiles:
    def test_fase_1_no_dispara_antes_de_su_cooldown(self):
        b = make_boss(hp=300, max_hp=300)  # fase 1
        resultado = b.update(dt=1.0)  # cooldown fase 1 es 2.0s
        assert resultado["projectiles"] == []

    def test_fase_1_dispara_3_proyectiles_al_cumplir_cooldown(self):
        b = make_boss(hp=300, max_hp=300)
        resultado = b.update(dt=2.0)
        assert len(resultado["projectiles"]) == 3

    def test_proyectiles_disparados_pertenecen_al_enemigo(self):
        b = make_boss(hp=300, max_hp=300)
        resultado = b.update(dt=2.0)
        for p in resultado["projectiles"]:
            assert p.owner == Owner.ENEMY

    def test_fase_2_dispara_5_proyectiles(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(150)  # fase 2 (50% HP)
        resultado = b.update(dt=1.5)  # cooldown fase 2
        assert len(resultado["projectiles"]) == 5

    def test_fase_3_dispara_7_proyectiles(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(250)  # fase 3 (~17% HP)
        resultado = b.update(dt=1.0)  # cooldown fase 3
        assert len(resultado["projectiles"]) == 7

    def test_proyectiles_salen_desde_el_centro_del_jefe(self):
        b = make_boss(x=300, y=50, hp=300, max_hp=300)
        resultado = b.update(dt=2.0)
        centro_x = 300 + BOSS_WIDTH / 2
        centro_y = 50 + BOSS_HEIGHT
        for p in resultado["projectiles"]:
            assert abs(p.position.x - centro_x) < BOSS_WIDTH  # margen razonable
            assert p.position.y == centro_y


class TestBossAtaqueRayo:
    def test_fase_1_nunca_genera_rayo(self):
        b = make_boss(hp=300, max_hp=300)
        resultado = b.update(dt=10.0)  # tiempo de sobra
        assert resultado["beam"] is None

    def test_fase_2_genera_rayo_al_cumplir_su_cooldown(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(150)  # fase 2
        resultado = b.update(dt=4.0)  # cooldown de rayo en fase 2
        assert resultado["beam"] is not None

    def test_rayo_generado_es_instancia_de_beam_attack(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(150)
        resultado = b.update(dt=4.0)
        from src.domain.entities.beam_attack import BeamAttack
        assert isinstance(resultado["beam"], BeamAttack)

    def test_fase_3_genera_rayo_con_su_propio_cooldown(self):
        b = make_boss(hp=300, max_hp=300)
        b.take_damage(250)  # fase 3
        resultado = b.update(dt=3.0)  # cooldown de rayo en fase 3
        assert resultado["beam"] is not None