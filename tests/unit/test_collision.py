"""
Tests unitarios para las reglas de colision (domain/rules).
TDD - Ciclo 7: resolucion de impactos entre proyectiles y entidades.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.entities.projectile import Projectile, Owner
from src.domain.rules.collision import resolve_player_hit, resolve_boss_hit


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_player(x=400, y=300, hp=3):
    return Player(
        position=Vector2(x, y), width=40, height=30, hp=hp, speed=200,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def make_boss(x=300, y=50, hp=300, max_hp=300):
    return Boss(
        position=Vector2(x, y), width=160, height=120, hp=hp, max_hp=max_hp,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def make_projectile(x, y, owner, damage=1, vx=0, vy=0):
    return Projectile(
        position=Vector2(x, y), velocity=Vector2(vx, vy),
        width=8, height=8, damage=damage, owner=owner,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


class TestResolvePlayerHit:
    def test_proyectil_enemigo_que_impacta_quita_vida_al_jugador(self):
        p = make_player(x=400, y=300, hp=3)
        proyectil = make_projectile(x=400, y=300, owner=Owner.ENEMY, damage=1)
        resolve_player_hit(p, [proyectil])
        assert p.hp == 2

    def test_proyectil_que_impacta_desaparece_de_la_lista(self):
        p = make_player(x=400, y=300, hp=3)
        proyectil = make_projectile(x=400, y=300, owner=Owner.ENEMY)
        sobrevivientes = resolve_player_hit(p, [proyectil])
        assert sobrevivientes == []

    def test_proyectil_que_no_impacta_sobrevive_y_no_hace_dano(self):
        p = make_player(x=400, y=300, hp=3)
        proyectil_lejano = make_projectile(x=0, y=0, owner=Owner.ENEMY)
        sobrevivientes = resolve_player_hit(p, [proyectil_lejano])
        assert p.hp == 3
        assert sobrevivientes == [proyectil_lejano]

    def test_proyectiles_del_jugador_no_danan_al_jugador(self):
        """Un proyectil con owner=PLAYER nunca debe dañar al propio Player."""
        p = make_player(x=400, y=300, hp=3)
        proyectil_propio = make_projectile(x=400, y=300, owner=Owner.PLAYER)
        sobrevivientes = resolve_player_hit(p, [proyectil_propio])
        assert p.hp == 3
        assert sobrevivientes == [proyectil_propio]

    def test_multiples_proyectiles_se_resuelven_correctamente(self):
        p = make_player(x=400, y=300, hp=3)
        impacta = make_projectile(x=400, y=300, owner=Owner.ENEMY)
        no_impacta = make_projectile(x=0, y=0, owner=Owner.ENEMY)
        sobrevivientes = resolve_player_hit(p, [impacta, no_impacta])
        assert p.hp == 2
        assert sobrevivientes == [no_impacta]

    def test_jugador_muerto_no_recibe_mas_dano(self):
        p = make_player(x=400, y=300, hp=1)
        primer_golpe = make_projectile(x=400, y=300, owner=Owner.ENEMY)
        resolve_player_hit(p, [primer_golpe])
        assert p.hp == 0

        segundo_golpe = make_projectile(x=400, y=300, owner=Owner.ENEMY)
        resolve_player_hit(p, [segundo_golpe])
        assert p.hp == 0  # take_damage ya clampa en 0, no es un requisito nuevo


class TestResolveBossHit:
    def test_proyectil_del_jugador_que_impacta_quita_hp_al_jefe(self):
        b = make_boss(x=300, y=50, hp=300, max_hp=300)
        # el jefe ocupa x:[300,460] y:[50,170]; disparamos dentro de ese rango
        proyectil = make_projectile(x=350, y=100, owner=Owner.PLAYER, damage=10)
        resolve_boss_hit(b, [proyectil])
        assert b.hp == 290

    def test_proyectil_que_impacta_al_jefe_desaparece(self):
        b = make_boss(x=300, y=50, hp=300, max_hp=300)
        proyectil = make_projectile(x=350, y=100, owner=Owner.PLAYER)
        sobrevivientes = resolve_boss_hit(b, [proyectil])
        assert sobrevivientes == []

    def test_proyectiles_del_enemigo_no_danan_al_jefe(self):
        """El jefe no se autodaña con sus propios proyectiles."""
        b = make_boss(x=300, y=50, hp=300, max_hp=300)
        proyectil_propio = make_projectile(x=350, y=100, owner=Owner.ENEMY)
        sobrevivientes = resolve_boss_hit(b, [proyectil_propio])
        assert b.hp == 300
        assert sobrevivientes == [proyectil_propio]

    def test_proyectil_lejano_no_impacta_al_jefe(self):
        b = make_boss(x=300, y=50, hp=300, max_hp=300)
        proyectil_lejano = make_projectile(x=0, y=500, owner=Owner.PLAYER)
        sobrevivientes = resolve_boss_hit(b, [proyectil_lejano])
        assert b.hp == 300
        assert sobrevivientes == [proyectil_lejano]