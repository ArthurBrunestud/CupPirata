"""
Steps para fin_de_partida.feature.
Los steps 'un jugador con X puntos de vida' y 'un jefe con X puntos de vida'
viven en common_steps.py para evitar duplicacion con combate.feature.
"""
from behave import given, when, then
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.game_state import GameState

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def crear_jugador(hp):
    return Player(
        position=Vector2(400, 500), width=30, height=30, hp=max(hp, 1), speed=200,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def crear_jefe(hp):
    return Boss(
        position=Vector2(300, 50), width=160, height=120, hp=max(hp, 1), max_hp=300,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def _asegurar_game_state(context):
    if not hasattr(context, "game_state"):
        context.game_state = GameState()


@given("un jugador vivo y un jefe vivo")
def step_ambos_vivos(context):
    context.player = crear_jugador(hp=3)
    context.boss = crear_jefe(hp=300)
    _asegurar_game_state(context)


@given("un jefe vivo")
def step_jefe_vivo(context):
    context.boss = crear_jefe(hp=300)


@given("un jugador vivo")
def step_jugador_vivo(context):
    context.player = crear_jugador(hp=3)
    _asegurar_game_state(context)


@when("se evalúan las condiciones de fin de partida")
def step_evaluar_fin_partida(context):
    context.game_state.check_end_conditions(context.player, context.boss)


@when("el jugador recupera la vida y se vuelven a evaluar las condiciones")
def step_jugador_recupera_y_revalua(context):
    context.player = crear_jugador(hp=3)
    context.game_state.check_end_conditions(context.player, context.boss)


@then('el estado de la partida debe ser "{estado_esperado}"')
def step_verificar_estado(context, estado_esperado):
    mapa_estados = {
        "jugando": "playing",
        "derrota": "lost",
        "victoria": "won",
    }
    valor_esperado = mapa_estados[estado_esperado]
    assert context.game_state.status.value == valor_esperado, (
        f"Se esperaba '{estado_esperado}' ({valor_esperado}), "
        f"pero fue '{context.game_state.status.value}'"
    )