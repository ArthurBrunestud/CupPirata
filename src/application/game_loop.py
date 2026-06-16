"""
GameLoop: orquesta un frame completo de logica del juego.
Capa de aplicacion: usa el dominio (Player, Boss, MiniBoss, GameState, etc.)
pero NO depende de Pygame.

Responsabilidades por frame (tick):
    1. Si la partida ya termino (WON/LOST), no hace nada mas.
    2. Mueve al jugador segun la direccion recibida.
    3. Procesa el disparo del jugador (respeta su cooldown).
    4. Actualiza al jefe: genera sus ataques (proyectiles y rayos) y se mueve.
    5. Si el HP del jefe baja a 50 o menos, hace aparecer 2 MiniBoss
       (uno a cada lado de la pantalla), una sola vez.
    6. Actualiza los MiniBoss existentes: se mueven y generan sus proyectiles.
    7. Actualiza posiciones de todos los proyectiles (jugador y enemigo) y rayos.
    8. Resuelve colisiones jugador<->proyectiles enemigos y jefe<->proyectiles
       del jugador. Cada punto de dano al jefe suma 1 punto de puntaje.
    9. Resuelve dano por contacto fisico directo entre jugador y jefe.
    10. Detecta si el jugador perdio HP en este frame (comparando con el HP
        del frame anterior) y, si fue asi, activa un parpadeo visual de 1s.
    11. Elimina proyectiles fuera de pantalla y rayos que terminaron su vida.
    12. Evalua condiciones de fin de partida.
"""
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.entities.mini_boss import MiniBoss
from src.domain.game_state import GameState
from src.domain.rules.collision import (
    resolve_player_hit,
    resolve_boss_hit,
    resolve_contact_damage,
)

MINI_BOSS_HP_TRIGGER = 50
MINI_BOSS_WIDTH = 80
MINI_BOSS_HEIGHT = 80
MINI_BOSS_SHOOT_COOLDOWN = 2.0
MINI_BOSS_MARGIN = 20

PLAYER_FLASH_DURATION = 1.0
PLAYER_FLASH_INTERVAL = 0.1


class GameLoop:
    def __init__(self, player: Player, boss: Boss, game_state: GameState):
        self.player = player
        self.boss = boss
        self.game_state = game_state

        self.player_projectiles = []
        self.enemy_projectiles = []
        self.beams = []
        self.mini_bosses = []
        self._contact_timer = 0.0

        self._player_flash_timer = 0.0
        self._player_visible = True
        self._hp_anterior = player.hp

    def tick(self, dt: float, move_direction: Vector2, is_shooting: bool) -> None:
        if self.game_state.is_game_over():
            return

        self._mover_jugador(dt, move_direction)
        self._procesar_disparo_jugador(dt, is_shooting)
        self._actualizar_jefe(dt)
        self._verificar_aparicion_mini_bosses()
        self._actualizar_mini_bosses(dt)
        self._actualizar_proyectiles(dt)
        self._actualizar_rayos(dt)
        self._resolver_colisiones()
        self._resolver_contacto_con_jefe(dt)
        self._actualizar_parpadeo_jugador(dt)
        self.game_state.check_end_conditions(self.player, self.boss)

    # -------------------- Pasos internos --------------------

    def _mover_jugador(self, dt: float, move_direction: Vector2) -> None:
        if move_direction.x == 0 and move_direction.y == 0:
            return
        self.player.move(direction=move_direction, dt=dt)

    def _procesar_disparo_jugador(self, dt: float, is_shooting: bool) -> None:
        self.player.update_cooldown(dt)
        if is_shooting:
            proyectil = self.player.shoot()
            if proyectil is not None:
                self.player_projectiles.append(proyectil)

    def _actualizar_jefe(self, dt: float) -> None:
        resultado = self.boss.update(dt)
        self.enemy_projectiles.extend(resultado["projectiles"])
        self.beams.extend(resultado["beams"])

    def _verificar_aparicion_mini_bosses(self) -> None:
        if self.mini_bosses:
            return
        if self.boss.hp > MINI_BOSS_HP_TRIGGER:
            return

        screen_width = self.boss.screen_width
        screen_height = self.boss.screen_height
        y_inicial = screen_height / 2 - MINI_BOSS_HEIGHT / 2

        mini_izquierdo = MiniBoss(
            position=Vector2(MINI_BOSS_MARGIN, y_inicial),
            width=MINI_BOSS_WIDTH, height=MINI_BOSS_HEIGHT,
            screen_width=screen_width, screen_height=screen_height,
            shoot_cooldown=MINI_BOSS_SHOOT_COOLDOWN,
        )
        mini_derecho = MiniBoss(
            position=Vector2(screen_width - MINI_BOSS_WIDTH - MINI_BOSS_MARGIN, y_inicial),
            width=MINI_BOSS_WIDTH, height=MINI_BOSS_HEIGHT,
            screen_width=screen_width, screen_height=screen_height,
            shoot_cooldown=MINI_BOSS_SHOOT_COOLDOWN,
        )

        self.mini_bosses = [mini_izquierdo, mini_derecho]

    def _actualizar_mini_bosses(self, dt: float) -> None:
        for mini in self.mini_bosses:
            proyectiles = mini.update(dt)
            self.enemy_projectiles.extend(proyectiles)

    def _actualizar_proyectiles(self, dt: float) -> None:
        for proyectil in self.player_projectiles:
            proyectil.update(dt)
        for proyectil in self.enemy_projectiles:
            proyectil.update(dt)

        self.player_projectiles = [
            p for p in self.player_projectiles if not p.is_off_screen()
        ]
        self.enemy_projectiles = [
            p for p in self.enemy_projectiles if not p.is_off_screen()
        ]

    def _actualizar_rayos(self, dt: float) -> None:
        for beam in self.beams:
            beam.update(dt)
        self.beams = [b for b in self.beams if b.is_visible()]

    def _resolver_colisiones(self) -> None:
        hp_jefe_antes = self.boss.hp
        self.player_projectiles = resolve_boss_hit(self.boss, self.player_projectiles)
        dano_infligido = hp_jefe_antes - self.boss.hp
        if dano_infligido > 0:
            self.game_state.add_score(dano_infligido)

        self.enemy_projectiles = resolve_player_hit(self.player, self.enemy_projectiles)

    def _resolver_contacto_con_jefe(self, dt: float) -> None:
        self._contact_timer = resolve_contact_damage(
            self.player, self.boss, dt, self._contact_timer
        )

    # -------------------- Parpadeo visual del jugador --------------------

    def _actualizar_parpadeo_jugador(self, dt: float) -> None:
        """
        Detecta si el jugador perdio HP en este frame (comparando con el
        HP registrado al final del frame anterior) y, si fue asi, activa
        un parpadeo visual de PLAYER_FLASH_DURATION segundos.

        Mientras el parpadeo este activo, alterna self._player_visible
        cada PLAYER_FLASH_INTERVAL segundos. El Renderer consulta
        is_player_visible() para decidir si dibuja al jugador o no.
        """
        if self.player.hp < self._hp_anterior:
            self._player_flash_timer = PLAYER_FLASH_DURATION
        self._hp_anterior = self.player.hp

        if self._player_flash_timer <= 0.0:
            self._player_flash_timer = 0.0
            self._player_visible = True
            return

        tiempo_transcurrido_total = PLAYER_FLASH_DURATION - self._player_flash_timer
        ciclo_actual = int(tiempo_transcurrido_total / PLAYER_FLASH_INTERVAL)

        self._player_flash_timer = max(0.0, self._player_flash_timer - dt)

        nuevo_tiempo_transcurrido = PLAYER_FLASH_DURATION - self._player_flash_timer
        nuevo_ciclo = int(nuevo_tiempo_transcurrido / PLAYER_FLASH_INTERVAL)

        if nuevo_ciclo != ciclo_actual:
            self._player_visible = not self._player_visible

        if self._player_flash_timer == 0.0:
            self._player_visible = True

    def is_player_visible(self) -> bool:
        return self._player_visible