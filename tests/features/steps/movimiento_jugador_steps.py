"""
Steps para movimiento_jugador.feature.
"""
from behave import given, when, then
from src.domain.vector import Vector2
from src.domain.entities.player import Player

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_SPEED = 200


def crear_jugador(x, y):
    return Player(
        position=Vector2(x, y), width=PLAYER_WIDTH, height=PLAYER_HEIGHT,
        hp=3, speed=PLAYER_SPEED,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


@given("un jugador en la posición ({x:d}, {y:d})")
def step_jugador_en_posicion(context, x, y):
    context.player = crear_jugador(x, y)


@given("un jugador cerca del borde derecho de la pantalla")
def step_jugador_borde_derecho(context):
    context.player = crear_jugador(SCREEN_WIDTH - PLAYER_WIDTH - 5, 300)


@given("un jugador cerca del borde izquierdo de la pantalla")
def step_jugador_borde_izquierdo(context):
    context.player = crear_jugador(5, 300)


@given("un jugador en el centro de la pantalla")
def step_jugador_centro(context):
    context.player = crear_jugador(
        SCREEN_WIDTH / 2 - PLAYER_WIDTH / 2,
        SCREEN_HEIGHT / 2 - PLAYER_HEIGHT / 2,
    )


@when("el jugador se mueve hacia la derecha durante {segundos:d} segundo")
@when("el jugador se mueve hacia la derecha durante {segundos:d} segundos")
def step_mover_derecha(context, segundos):
    context.player.move(direction=Vector2(1, 0), dt=float(segundos))


@when("el jugador intenta moverse hacia la derecha durante {segundos:d} segundos")
def step_intentar_mover_derecha(context, segundos):
    context.player.move(direction=Vector2(1, 0), dt=float(segundos))


@when("el jugador intenta moverse hacia la izquierda durante {segundos:d} segundos")
def step_intentar_mover_izquierda(context, segundos):
    context.player.move(direction=Vector2(-1, 0), dt=float(segundos))


@when("el jugador se mueve en diagonal durante {segundos:d} segundo")
def step_mover_diagonal(context, segundos):
    context.posicion_inicial = Vector2(context.player.position.x, context.player.position.y)
    context.player.move(direction=Vector2(1, 1), dt=float(segundos))


@then("la posición X del jugador debe ser mayor que {valor:d}")
def step_verificar_posicion_mayor(context, valor):
    assert context.player.position.x > valor, (
        f"Se esperaba posición X mayor a {valor}, pero fue {context.player.position.x}"
    )


@then("el jugador debe quedar exactamente en el borde derecho de la pantalla")
def step_verificar_borde_derecho(context):
    esperado = SCREEN_WIDTH - PLAYER_WIDTH
    assert context.player.position.x == esperado, (
        f"Se esperaba X={esperado}, pero fue {context.player.position.x}"
    )


@then("el jugador debe quedar exactamente en el borde izquierdo de la pantalla")
def step_verificar_borde_izquierdo(context):
    assert context.player.position.x == 0, (
        f"Se esperaba X=0, pero fue {context.player.position.x}"
    )


@then("la distancia recorrida debe ser igual a la velocidad del jugador")
def step_verificar_distancia_diagonal(context):
    dx = context.player.position.x - context.posicion_inicial.x
    dy = context.player.position.y - context.posicion_inicial.y
    distancia = (dx ** 2 + dy ** 2) ** 0.5
    assert round(distancia, 2) == PLAYER_SPEED, (
        f"Se esperaba distancia de {PLAYER_SPEED}, pero fue {distancia}"
    )