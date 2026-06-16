"""
BeamAttack: rayo del jefe, representado como una zona de peligro rectangular
delgada y temporal.

Ciclo de vida temporal (en base al tiempo transcurrido desde su creacion):
    [0, warning_duration)              -> WARNING: visible (rojo), NO dana.
    [warning_duration, duration)       -> ACTIVE: visible, SI dana.
    >= duration                        -> terminado, ya no visible.

Convencion de orientacion:
    - height > width  -> rayo vertical (cortina de arriba a abajo)
    - width > height  -> rayo horizontal (barrera de lado a lado)
    - El Boss decide la orientacion y posicion al crear el BeamAttack;
      esta clase solo administra su hitbox y su ciclo de vida temporal.

Parte del dominio puro del juego (sin dependencias de Pygame).
"""
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox


class BeamAttack:
    def __init__(
        self,
        position: Vector2,
        width: float,
        height: float,
        duration: float,
        warning_duration: float,
    ):
        self.position = position
        self.width = width
        self.height = height
        self.duration = duration
        self.warning_duration = warning_duration
        self.hitbox = Hitbox(position=position, width=width, height=height)

        self._tiempo_transcurrido = 0.0

    def is_vertical(self) -> bool:
        return self.height > self.width

    def is_warning(self) -> bool:
        """True mientras el rayo solo esta avisando (no dana todavia)."""
        return self._tiempo_transcurrido < self.warning_duration

    def is_active(self) -> bool:
        """True cuando el rayo ya puede dañar (paso la fase de alerta
        pero no ha terminado su duracion total)."""
        return self.warning_duration <= self._tiempo_transcurrido < self.duration

    def is_visible(self) -> bool:
        """True durante todo el ciclo de vida (alerta + activo)."""
        return self._tiempo_transcurrido < self.duration

    def update(self, dt: float) -> None:
        self._tiempo_transcurrido += dt