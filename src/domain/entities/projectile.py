"""
Projectile: proyectil disparado por el jugador o por un enemigo.
Parte del dominio puro del juego (sin dependencias de Pygame).

Responsabilidades:
    - Avanzar cada frame según su velocidad.
    - Saber quién lo disparó (para no auto-dañarse).
    - Saber cuándo está fuera de pantalla (para que el juego lo descarte).
    - Mantener un hitbox sincronizado.

NO responsabilidades:
    - Decidir si colisiona con otra entidad (eso va en rules/collision).
    - Renderizarse.
"""
from enum import Enum

from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox


class Owner(Enum):
    """Indica quién disparó el proyectil."""
    PLAYER = "player"
    ENEMY = "enemy"


class Projectile:
    def __init__(
        self,
        position: Vector2,
        velocity: Vector2,
        width: float,
        height: float,
        damage: int,
        owner: Owner,
        screen_width: int,
        screen_height: int,
    ):
        self.position = position
        self.velocity = velocity
        self.width = width
        self.height = height
        self.damage = damage
        self.owner = owner
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hitbox = Hitbox(position=position, width=width, height=height)

    def update(self, dt: float) -> None:
        """Avanza el proyectil según su velocidad y el tiempo transcurrido."""
        desplazamiento = self.velocity * dt
        self.position = self.position + desplazamiento
        self.hitbox.move_to(self.position)

    def is_off_screen(self) -> bool:
        """
        True si el proyectil ya no es visible en la pantalla.
        Se considera 'fuera' cuando su hitbox queda completamente fuera
        del rectángulo de pantalla; tocar el borde aún cuenta como visible.
        """
        if self.hitbox.right <= 0:
            return True
        if self.hitbox.left >= self.screen_width:
            return True
        if self.hitbox.bottom <= 0:
            return True
        if self.hitbox.top >= self.screen_height:
            return True
        return False

    def __repr__(self) -> str:
        return (
            f"Projectile(pos=({self.position.x}, {self.position.y}), "
            f"vel=({self.velocity.x}, {self.velocity.y}), "
            f"owner={self.owner.value})"
        )