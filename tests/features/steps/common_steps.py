"""
Steps compartidos entre combate.feature y fin_de_partida.feature.
Centralizarlos aqui evita definiciones duplicadas con el mismo texto
Gherkin, lo que causaria comportamiento ambiguo en behave.
"""
from behave import given
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.game_state import GameState

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def crear_jugador_generico(hp):
    return Player(
        position=Vector2(400, 500), width=30, height=30, hp=max(hp, 1), speed=200,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def crear_jefe_generico(hp):
    return Boss(
        position=Vector2(300, 50), width=160, height=120, hp=max(hp, 1), max_hp=300,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def asegurar_game_state(context):
    if not hasattr(context, "game_state"):
        context.game_state = GameState()


@given("un jugador con {hp:d} puntos de vida")
def step_jugador_con_hp_compartido(context, hp):
    context.player = crear_jugador_generico(hp=hp)
    if hp == 0:
        context.player.take_damage(999)
    asegurar_game_state(context)


@given("un jefe con {hp:d} puntos de vida")
def step_jefe_con_hp_compartido(context, hp):
    context.boss = crear_jefe_generico(hp=hp)
    if hp == 0:
        context.boss.take_damage(999)
    asegurar_game_state(context)