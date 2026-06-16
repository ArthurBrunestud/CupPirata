"""
Tests unitarios para GameState (domain).
TDD - Ciclo 8: puntaje y condiciones de fin de partida.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.game_state import GameState, GameStatus


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_player(hp=3):
    return Player(
        position=Vector2(400, 300), width=40, height=30, hp=hp, speed=200,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


def make_boss(hp=300, max_hp=300):
    return Boss(
        position=Vector2(300, 50), width=160, height=120, hp=hp, max_hp=max_hp,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )


class TestGameStateCreacion:
    def test_inicia_con_puntaje_cero(self):
        gs = GameState()
        assert gs.score == 0

    def test_inicia_en_estado_playing(self):
        gs = GameState()
        assert gs.status == GameStatus.PLAYING

    def test_is_playing_es_true_al_inicio(self):
        gs = GameState()
        assert gs.is_playing() is True

    def test_is_game_over_es_false_al_inicio(self):
        gs = GameState()
        assert gs.is_game_over() is False


class TestGameStatePuntaje:
    def test_agregar_puntaje_lo_suma_al_total(self):
        gs = GameState()
        gs.add_score(10)
        gs.add_score(25)
        assert gs.score == 35

    def test_agregar_puntaje_negativo_no_resta(self):
        gs = GameState()
        gs.add_score(50)
        gs.add_score(-20)
        assert gs.score == 50


class TestGameStateCondicionesFin:
    def test_jugador_vivo_y_jefe_vivo_sigue_jugando(self):
        gs = GameState()
        p = make_player(hp=3)
        b = make_boss(hp=300)
        gs.check_end_conditions(p, b)
        assert gs.status == GameStatus.PLAYING

    def test_jugador_muerto_resulta_en_derrota(self):
        gs = GameState()
        p = make_player(hp=1)
        p.take_damage(1)
        b = make_boss(hp=300)
        gs.check_end_conditions(p, b)
        assert gs.status == GameStatus.LOST

    def test_jefe_muerto_resulta_en_victoria(self):
        gs = GameState()
        p = make_player(hp=3)
        b = make_boss(hp=10, max_hp=300)
        b.take_damage(10)
        gs.check_end_conditions(p, b)
        assert gs.status == GameStatus.WON

    def test_si_ambos_mueren_a_la_vez_gana_la_derrota(self):
        """Regla de desambiguacion: si jugador y jefe mueren en el mismo
        frame, se prioriza la derrota (el jugador no llego a ganar)."""
        gs = GameState()
        p = make_player(hp=1)
        p.take_damage(1)
        b = make_boss(hp=10, max_hp=300)
        b.take_damage(10)
        gs.check_end_conditions(p, b)
        assert gs.status == GameStatus.LOST

    def test_is_playing_false_tras_victoria(self):
        gs = GameState()
        p = make_player(hp=3)
        b = make_boss(hp=10, max_hp=300)
        b.take_damage(10)
        gs.check_end_conditions(p, b)
        assert gs.is_playing() is False

    def test_is_game_over_true_tras_derrota(self):
        gs = GameState()
        p = make_player(hp=1)
        p.take_damage(1)
        b = make_boss(hp=300)
        gs.check_end_conditions(p, b)
        assert gs.is_game_over() is True

    def test_estado_terminado_no_vuelve_a_playing(self):
        """Trinquete: una vez WON o LOST, no debe regresar a PLAYING
        aunque se vuelva a llamar check_end_conditions con datos validos."""
        gs = GameState()
        p_muerto = make_player(hp=1)
        p_muerto.take_damage(1)
        b_vivo = make_boss(hp=300)
        gs.check_end_conditions(p_muerto, b_vivo)
        assert gs.status == GameStatus.LOST

        p_revivido = make_player(hp=3)  # simula un estado nuevo "sano"
        gs.check_end_conditions(p_revivido, b_vivo)
        assert gs.status == GameStatus.LOST