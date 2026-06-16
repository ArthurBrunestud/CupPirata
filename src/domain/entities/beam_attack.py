"""
BeamAttack: rayo del jefe, representado como una zona de peligro rectangular
delgada y temporal (camino mas simple, sin geometria de lineas/angulos reales).

Convencion de orientacion:
    - height > width  -> rayo vertical (cortina de arriba a abajo)
    - width > height  -> rayo horizontal (barrera de lado a lado)
    - El Boss decide la orientacion y posicion al crear el BeamAttack;
      esta clase solo administra su hitbox y su tiempo de vida.

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
    ):
        self.position = position
        self.width = width
        self.height = height
        self.duration = duration
        self.hitbox = Hitbox(position=position, width=width, height=height)

        self._tiempo_transcurrido = 0.0

    def is_vertical(self) -> bool:
        return self.height > self.width

    def is_active(self) -> bool:
        return self._tiempo_transcurrido < self.duration

    def update(self, dt: float) -> None:
        """Avanza el temporizador interno. Cuando supera 'duration',
        el rayo deja de estar activo (is_active() devuelve False)."""
        self._tiempo_transcurrido += dt