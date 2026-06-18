"""
Steps para combate.feature.
Los steps 'un jugador con X puntos de vida' y 'un jefe con X puntos de vida'
viven en common_steps.py para evitar duplicacion con fin_de_partida.feature.
"""
from behave import given, when, then
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.entities.projectile import Projectile, Owner
from src.domain.game_state import GameState
from src.domain.rules.collision import resolve_boss_hit, resolve_player_hit, resolve_contact_damage

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def crear_jugador(x=400, y=500, hp=10):
    return Player(
        position=Vector2(x, y), width=30, height=30, hp=hp, speed=200,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def crear_jefe(x=300, y=50, hp=300):
    return Boss(
        position=Vector2(x, y), width=160, height=120, hp=hp, max_hp=300,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def crear_proyectil(x, y, owner, damage=5):
    return Projectile(
        position=Vector2(x, y), velocity=Vector2(0, 0),
        width=10, height=10, damage=damage, owner=owner,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


@given("un proyectil del jugador justo sobre el jefe")
def step_proyectil_sobre_jefe(context):
    centro_x = context.boss.position.x + context.boss.width / 2
    centro_y = context.boss.position.y + context.boss.height / 2
    context.player_projectiles = [crear_proyectil(centro_x, centro_y, Owner.PLAYER)]


@given("un proyectil del jugador lejos del jefe")
def step_proyectil_lejos_jefe(context):
    context.player_projectiles = [crear_proyectil(0, 0, Owner.PLAYER)]


@given("el jugador está tocando físicamente al jefe")
def step_jugador_tocando_jefe(context):
    context.boss = crear_jefe()
    context.player.position = Vector2(context.boss.position.x, context.boss.position.y)
    context.player.hitbox.move_to(context.player.position)


@given("un proyectil del jefe justo sobre el jugador")
def step_proyectil_sobre_jugador(context):
    context.enemy_projectiles = [
        crear_proyectil(context.player.position.x, context.player.position.y, Owner.ENEMY)
    ]


@when("se resuelven las colisiones del frame")
def step_resolver_colisiones(context):
    if hasattr(context, "player_projectiles"):
        hp_antes = context.boss.hp
        resolve_boss_hit(context.boss, context.player_projectiles)
        dano = hp_antes - context.boss.hp
        if dano > 0:
            context.game_state.add_score(dano)
    if hasattr(context, "enemy_projectiles"):
        resolve_player_hit(context.player, context.enemy_projectiles)


@when("pasan {segundos:f} segundos de contacto continuo")
def step_pasan_segundos_contacto(context, segundos):
    resolve_contact_damage(context.player, context.boss, dt=segundos, contact_timer=0.0)


@then("la vida del jefe debe ser menor a {valor:d}")
def step_verificar_vida_jefe_menor(context, valor):
    assert context.boss.hp < valor, f"Se esperaba HP jefe menor a {valor}, fue {context.boss.hp}"


@then("la vida del jefe debe seguir siendo {valor:d}")
def step_verificar_vida_jefe_igual(context, valor):
    assert context.boss.hp == valor, f"Se esperaba HP jefe igual a {valor}, fue {context.boss.hp}"


@then("el puntaje del jugador debe haber aumentado")
def step_verificar_puntaje_aumento(context):
    assert context.game_state.score > 0, "Se esperaba puntaje mayor a 0, sigue en 0"


@then("la vida del jugador debe ser menor a {valor:d}")
def step_verificar_vida_jugador_menor(context, valor):
    assert context.player.hp < valor, f"Se esperaba HP jugador menor a {valor}, fue {context.player.hp}"