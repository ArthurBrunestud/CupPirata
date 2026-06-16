"""
GameLoop: orquesta un frame completo de logica del juego.
Capa de aplicacion: usa el dominio (Player, Boss, GameState, etc.)
pero NO depende de Pygame.

Ciclo 9a (este archivo): movimiento del jugador y su disparo.
Ciclo 9b (siguiente): ataques del jefe, colisiones, puntaje y fin de partida.
"""
from src.domain.vector import Vector2
from src.domain.entities.player import Player
from src.domain.entities.boss import Boss
from src.domain.game_state import GameState


class GameLoop:
    def __init__(self, player: Player, boss: Boss, game_state: GameState):
        self.player = player
        self.boss = boss
        self.game_state = game_state

        self.player_projectiles = []
        self.enemy_projectiles = []
        self.beams = []

    def tick(self, dt: float, move_direction: Vector2, is_shooting: bool) -> None:
        """
        Avanza un frame de logica:
            1. Mueve al jugador segun la direccion recibida.
            2. Actualiza el cooldown de disparo del jugador.
            3. Si is_shooting y puede disparar, genera un nuevo proyectil.
            4. Actualiza la posicion de todos los proyectiles del jugador.
            5. Elimina los proyectiles del jugador que salieron de pantalla.
        """
        self._mover_jugador(dt, move_direction)
        self._procesar_disparo_jugador(dt, is_shooting)
        self._actualizar_proyectiles_jugador(dt)

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

    def _actualizar_proyectiles_jugador(self, dt: float) -> None:
        for proyectil in self.player_projectiles:
            proyectil.update(dt)
        self.player_projectiles = [
            p for p in self.player_projectiles if not p.is_off_screen()
        ]