"""
Boss: jefe del nivel aereo. Unico oponente del juego (sin enemigos menores).
Parte del dominio puro del juego (sin dependencias de Pygame).

Ciclo 6a (este archivo): HP, fases y estado de vida.
Ciclo 6b (siguiente): generacion de ataques (proyectiles y rayo).

Reglas de fase:
    - Fase 1: HP > 66% de max_hp
    - Fase 2: HP <= 66% y > 33% de max_hp
    - Fase 3: HP <= 33% de max_hp (incluye HP == 0)
    - La fase es un trinquete: una vez avanzada, nunca retrocede,
      incluso si el HP subiera por algun motivo externo.
"""
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox


class Boss:
    def __init__(
        self,
        position: Vector2,
        width: float,
        height: float,
        hp: int,
        max_hp: int,
        screen_width: int,
        screen_height: int,
    ):
        self.position = position
        self.width = width
        self.height = height
        self.hp = hp
        self.max_hp = max_hp
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hitbox = Hitbox(position=position, width=width, height=height)

        self.phase = 1
        self._actualizar_fase()

    # -------------------- Estado de vida --------------------

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        """Aplica daño. Ignora cantidades no positivas (no cura)."""
        if amount <= 0:
            return
        self.hp = max(0, self.hp - amount)
        self._actualizar_fase()

    # -------------------- Fases --------------------

    def _porcentaje_hp(self) -> float:
        if self.max_hp == 0:
            return 0.0
        return self.hp / self.max_hp

    def _fase_segun_hp(self) -> int:
        porcentaje = self._porcentaje_hp()
        if porcentaje <= 0.33:
            return 3
        if porcentaje <= 0.66:
            return 2
        return 1

    def _actualizar_fase(self) -> None:
        """
        Avanza self.phase si el HP actual indica una fase mayor.
        Es un trinquete: nunca permite retroceder de fase.
        """
        fase_calculada = self._fase_segun_hp()
        if fase_calculada > self.phase:
            self.phase = fase_calculada