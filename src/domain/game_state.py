"""
GameState: estado global de la partida.
Parte del dominio puro del juego (sin dependencias de Pygame).

Responsabilidades:
    - Acumular puntaje.
    - Determinar si la partida sigue, se gano o se perdio, en base
      al estado de Player y Boss.
    - El estado de fin de partida es un trinquete: una vez WON o LOST,
      nunca vuelve a PLAYING.

Regla de desambiguacion: si Player y Boss mueren en el mismo frame,
se prioriza la derrota (el jugador no llego a completar la victoria).
"""
from enum import Enum


class GameStatus(Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


class GameState:
    def __init__(self):
        self.score = 0
        self.status = GameStatus.PLAYING

    # -------------------- Puntaje --------------------

    def add_score(self, points: int) -> None:
        """Suma puntos al total. Ignora valores no positivos."""
        if points <= 0:
            return
        self.score += points

    # -------------------- Estado de la partida --------------------

    def is_playing(self) -> bool:
        return self.status == GameStatus.PLAYING

    def is_game_over(self) -> bool:
        return self.status in (GameStatus.WON, GameStatus.LOST)

    def check_end_conditions(self, player, boss) -> None:
        """
        Evalua si la partida debe terminar, en base al estado actual
        de player y boss. No hace nada si la partida ya termino
        (trinquete: WON/LOST son estados finales).
        """
        if self.is_game_over():
            return

        jugador_muerto = not player.is_alive()
        jefe_muerto = not boss.is_alive()

        if jugador_muerto:
            self.status = GameStatus.LOST
        elif jefe_muerto:
            self.status = GameStatus.WON