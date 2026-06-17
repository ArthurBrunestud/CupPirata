"""
Tests unitarios para GameLoop (application).
TDD - Ciclo 9a: movimiento del jugador y generacion de su disparo.
La integracion con Boss, colisiones y puntaje se agrega en el ciclo 9b.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.game_state import GameState
from src.application.game_loop import GameLoop


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_game_loop(player_hp=3, boss_hp=300):
    player = Player(
        position=Vector2(400, 500), width=40, height=30, hp=player_hp, speed=200,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )
    boss = Boss(
        position=Vector2(300, 50), width=160, height=120, hp=boss_hp, max_hp=300,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
    )
    game_state = GameState()
    return GameLoop(player=player, boss=boss, game_state=game_state)


class TestGameLoopMovimientoJugador:
    def test_tick_mueve_al_jugador_segun_direccion(self):
        loop = make_game_loop()
        x_inicial = loop.player.position.x
        loop.tick(dt=1.0, move_direction=Vector2(1, 0), is_shooting=False)
        assert loop.player.position.x > x_inicial

    def test_tick_sin_direccion_no_mueve_al_jugador(self):
        loop = make_game_loop()
        x_inicial = loop.player.position.x
        y_inicial = loop.player.position.y
        loop.tick(dt=1.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.position.x == x_inicial
        assert loop.player.position.y == y_inicial


class TestGameLoopDisparoJugador:
    def test_disparar_agrega_un_proyectil_a_la_lista(self):
        loop = make_game_loop()
        assert len(loop.player_projectiles) == 0
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        assert len(loop.player_projectiles) == 1

    def test_no_disparar_no_agrega_proyectiles(self):
        loop = make_game_loop()
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.player_projectiles) == 0

    def test_proyectiles_del_jugador_avanzan_cada_tick(self):
        loop = make_game_loop()
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        y_tras_disparo = loop.player_projectiles[0].position.y
        loop.tick(dt=1.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player_projectiles[0].position.y < y_tras_disparo

    def test_proyectiles_fuera_de_pantalla_se_eliminan(self):
        loop = make_game_loop()
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        assert len(loop.player_projectiles) == 1
        # avanza mucho tiempo: el proyectil sale de pantalla por arriba
        loop.tick(dt=10.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.player_projectiles) == 0

    def test_cooldown_de_disparo_respeta_al_player(self):
        loop = make_game_loop()
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        # el segundo intento de disparo es muy pronto, no debe sumar otro
        assert len(loop.player_projectiles) == 1

class TestGameLoopAtaquesJefe:
    def test_tick_actualiza_al_jefe_y_puede_generar_proyectiles(self):
        loop = make_game_loop()
        # 4 ticks de 0.5s simulan el paso real del tiempo (total 2.0s, igual al cooldown)
        for _ in range(4):
            loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.enemy_projectiles) == 5

    def test_proyectiles_del_jefe_avanzan_cada_tick(self):
        loop = make_game_loop()
        for _ in range(4):
            loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        y_inicial = loop.enemy_projectiles[0].position.y
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.enemy_projectiles[0].position.y != y_inicial

    def test_proyectiles_del_jefe_fuera_de_pantalla_se_eliminan(self):
        loop = make_game_loop()
        for _ in range(4):
            loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.enemy_projectiles) == 5

class TestGameLoopColisiones:
    def test_proyectil_del_jugador_que_impacta_quita_hp_al_jefe(self):
        loop = make_game_loop(boss_hp=300)
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        proyectil = loop.player_projectiles[0]
        proyectil.position = Vector2(loop.boss.position.x + 10, loop.boss.position.y + 10)
        proyectil.hitbox.move_to(proyectil.position)

        loop.tick(dt=0.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.boss.hp < 300

    def test_impacto_al_jefe_suma_puntaje_igual_al_dano(self):
        loop = make_game_loop(boss_hp=300)
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        proyectil = loop.player_projectiles[0]
        proyectil.position = Vector2(loop.boss.position.x + 10, loop.boss.position.y + 10)
        proyectil.hitbox.move_to(proyectil.position)

        dano_esperado = proyectil.damage
        loop.tick(dt=0.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.game_state.score == dano_esperado

    def test_proyectil_del_jefe_que_impacta_quita_vida_al_jugador(self):
        loop = make_game_loop(player_hp=3)
        for _ in range(4):
            loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        proyectil_enemigo = loop.enemy_projectiles[0]
        proyectil_enemigo.position = Vector2(loop.player.position.x, loop.player.position.y)
        proyectil_enemigo.hitbox.move_to(proyectil_enemigo.position)

        loop.tick(dt=0.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp < 3


class TestGameLoopFinDePartida:
    def test_jefe_derrotado_resulta_en_victoria(self):
        loop = make_game_loop(boss_hp=1)
        loop.tick(dt=0.016, move_direction=Vector2(0, 0), is_shooting=True)
        proyectil = loop.player_projectiles[0]
        proyectil.position = Vector2(loop.boss.position.x + 10, loop.boss.position.y + 10)
        proyectil.hitbox.move_to(proyectil.position)

        loop.tick(dt=0.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.game_state.is_game_over() is True

    def test_jugador_derrotado_resulta_en_derrota(self):
        loop = make_game_loop(player_hp=1)
        for _ in range(4):
            loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        proyectil_enemigo = loop.enemy_projectiles[0]
        proyectil_enemigo.position = Vector2(loop.player.position.x, loop.player.position.y)
        proyectil_enemigo.hitbox.move_to(proyectil_enemigo.position)

        loop.tick(dt=0.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.game_state.status.value == "lost"

    def test_partida_terminada_no_sigue_moviendo_al_jugador(self):
        loop = make_game_loop(player_hp=1)
        for _ in range(4):
            loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        proyectil_enemigo = loop.enemy_projectiles[0]
        proyectil_enemigo.position = Vector2(loop.player.position.x, loop.player.position.y)
        proyectil_enemigo.hitbox.move_to(proyectil_enemigo.position)
        loop.tick(dt=0.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.game_state.is_game_over() is True

        x_antes = loop.player.position.x
        loop.tick(dt=1.0, move_direction=Vector2(1, 0), is_shooting=False)
        assert loop.player.position.x == x_antes
class TestGameLoopContactoConJefe:
    def test_tocar_al_jefe_quita_vida_al_jugador(self):
        loop = make_game_loop(player_hp=10)
        loop.boss._tiempo_hasta_nueva_direccion = 999.0  # evita que el jefe se mueva en este test
        loop.player.position = Vector2(loop.boss.position.x, loop.boss.position.y)
        loop.player.hitbox.move_to(loop.player.position)

        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp == 8

    def test_no_tocar_al_jefe_no_quita_vida(self):
        loop = make_game_loop(player_hp=10)
        loop.boss._tiempo_hasta_nueva_direccion = 999.0
        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp == 10

    def test_contacto_continuo_sigue_danando_en_ticks_sucesivos(self):
        loop = make_game_loop(player_hp=10)
        loop.boss._tiempo_hasta_nueva_direccion = 999.0
        loop.player.position = Vector2(loop.boss.position.x, loop.boss.position.y)
        loop.player.hitbox.move_to(loop.player.position)

        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp == 8

        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp == 6

class TestGameLoopMiniBosses:
    def test_no_aparecen_mini_bosses_en_fase_1_o_2(self):
        loop = make_game_loop(boss_hp=300)
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.mini_bosses == []

    def test_aparecen_dos_mini_bosses_al_llegar_a_fase_3(self):
        loop = make_game_loop(boss_hp=300)
        loop.boss.take_damage(250)  # deja al jefe en fase 3
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.mini_bosses) == 2

    def test_mini_bosses_aparecen_en_lados_opuestos(self):
        loop = make_game_loop(boss_hp=300)
        loop.boss.take_damage(250)
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)
        posiciones_x = sorted(m.position.x for m in loop.mini_bosses)
        assert posiciones_x[0] < SCREEN_WIDTH / 2
        assert posiciones_x[1] > SCREEN_WIDTH / 2

    def test_mini_bosses_no_vuelven_a_crearse_en_ticks_siguientes(self):
        loop = make_game_loop(boss_hp=300)
        loop.boss.take_damage(250)
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.mini_bosses) == 2

    def test_no_aparecen_mini_bosses_si_max_phase_limita_a_fase_2(self):
        """Caso clave: en modo Casual (max_phase=2), el jefe nunca llega
        a fase 3, asi que los mini-jefes nunca deben aparecer, sin
        importar cuanto HP pierda."""
        player = Player(
            position=Vector2(400, 500), width=40, height=30, hp=3, speed=200,
            screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
        )
        boss = Boss(
            position=Vector2(300, 50), width=160, height=120, hp=300, max_hp=300,
            screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, max_phase=2,
        )
        game_state = GameState()
        loop = GameLoop(player=player, boss=boss, game_state=game_state)

        loop.boss.take_damage(280)  # en modo normal seria fase 3 (HP=20, ~7%)
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)

        assert loop.boss.phase == 2  # confirma el tope de fase
        assert loop.mini_bosses == []  # y por lo tanto, sin mini-jefes

    def test_mini_bosses_generan_proyectiles_propios(self):
        loop = make_game_loop(boss_hp=300)
        loop.boss.take_damage(250)
        loop.tick(dt=2.0, move_direction=Vector2(0, 0), is_shooting=False)
        assert len(loop.enemy_projectiles) >= 6

    def test_mini_bosses_son_invulnerables_a_proyectiles_del_jugador(self):
        loop = make_game_loop(boss_hp=300)
        loop.boss.take_damage(250)
        loop.tick(dt=0.1, move_direction=Vector2(0, 0), is_shooting=False)

        mini = loop.mini_bosses[0]
        mini.take_damage(9999)
        assert mini.is_alive() is True

class TestGameLoopParpadeoJugador:
    def test_jugador_es_visible_por_defecto(self):
        loop = make_game_loop()
        assert loop.is_player_visible() is True

    def test_perder_hp_activa_el_parpadeo(self):
        loop = make_game_loop(player_hp=10)
        loop.boss._tiempo_hasta_nueva_direccion = 999.0
        loop.player.position = Vector2(loop.boss.position.x, loop.boss.position.y)
        loop.player.hitbox.move_to(loop.player.position)

        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp == 8  # confirma que si perdio hp
        assert loop._player_flash_timer > 0.0

    def test_sin_perder_hp_no_hay_parpadeo(self):
        loop = make_game_loop(player_hp=10)
        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop._player_flash_timer == 0.0

    def test_parpadeo_alterna_visibilidad_cada_0_1s(self):
        loop = make_game_loop(player_hp=10)
        loop._player_flash_timer = 1.0  # simulamos que recien empezo a parpadear

        loop._actualizar_parpadeo_jugador(dt=0.05)
        primera_visibilidad = loop.is_player_visible()

        loop._actualizar_parpadeo_jugador(dt=0.1)
        segunda_visibilidad = loop.is_player_visible()

        assert primera_visibilidad != segunda_visibilidad

    def test_parpadeo_termina_tras_1_segundo_y_vuelve_a_ser_visible(self):
        loop = make_game_loop(player_hp=10)
        loop._player_flash_timer = 1.0

        loop._actualizar_parpadeo_jugador(dt=1.0)

        assert loop._player_flash_timer == 0.0
        assert loop.is_player_visible() is True

    def test_parpadeo_no_se_reinicia_indefinidamente_si_no_hay_nuevo_golpe(self):
        loop = make_game_loop(player_hp=10)
        loop.boss._tiempo_hasta_nueva_direccion = 999.0
        loop.player.position = Vector2(loop.boss.position.x, loop.boss.position.y)
        loop.player.hitbox.move_to(loop.player.position)

        loop.tick(dt=0.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop.player.hp == 8
        timer_tras_primer_golpe = loop._player_flash_timer
        assert timer_tras_primer_golpe > 0.0

        # alejamos al jugador para que no siga recibiendo contacto
        loop.player.position = Vector2(0, 0)
        loop.player.hitbox.move_to(loop.player.position)

        # avanzamos el tiempo suficiente para que el parpadeo termine solo
        loop.tick(dt=1.5, move_direction=Vector2(0, 0), is_shooting=False)
        assert loop._player_flash_timer == 0.0