"""
Steps para fases_jefe.feature.
"""
from behave import given, when, then
from src.domain.vector import Vector2
from src.domain.entities.boss import Boss

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def crear_jefe(hp_maximo, max_phase=3):
    return Boss(
        position=Vector2(300, 50), width=160, height=120,
        hp=hp_maximo, max_hp=hp_maximo,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
        max_phase=max_phase,
    )


@given("un jefe recién creado con {hp:d} de vida máxima")
def step_crear_jefe_basico(context, hp):
    context.boss = crear_jefe(hp_maximo=hp)


@given("un jefe en modo Casual con {hp:d} de vida máxima")
def step_crear_jefe_casual(context, hp):
    context.boss = crear_jefe(hp_maximo=hp, max_phase=2)


@given("un jefe en modo Profesional con {hp:d} de vida máxima")
def step_crear_jefe_profesional(context, hp):
    context.boss = crear_jefe(hp_maximo=hp, max_phase=3)


@when("el jefe recibe {dano:d} puntos de daño")
def step_jefe_recibe_dano(context, dano):
    context.boss.take_damage(dano)


@then("el jefe debe estar en la fase {fase:d}")
def step_verificar_fase(context, fase):
    assert context.boss.phase == fase, (
        f"Se esperaba fase {fase}, pero el jefe está en fase {context.boss.phase}"
    )


@then("el jefe no debe avanzar más allá de la fase {fase_maxima:d}")
def step_verificar_tope_fase(context, fase_maxima):
    assert context.boss.phase <= fase_maxima, (
        f"El jefe avanzó a fase {context.boss.phase}, superando el tope de {fase_maxima}"
    )