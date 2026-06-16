"""
Hitbox: caja de colisión AABB (Axis-Aligned Bounding Box) en 2D.
Parte del dominio puro del juego (sin dependencias de Pygame).

Convención de coordenadas (estilo Pygame):
    - El origen (0, 0) está en la esquina superior izquierda.
    - X crece hacia la derecha, Y crece hacia abajo.
    - 'position' representa la esquina superior izquierda de la caja.
"""
from src.domain.vector import Vector2


class Hitbox:
    def __init__(self, position: Vector2, width: float, height: float):
        self.position = position
        self.width = width
        self.height = height

    @property
    def left(self) -> float:
        return self.position.x

    @property
    def right(self) -> float:
        return self.position.x + self.width

    @property
    def top(self) -> float:
        return self.position.y

    @property
    def bottom(self) -> float:
        return self.position.y + self.height

    def move_to(self, new_position: Vector2) -> None:
        """Reubica la hitbox en una nueva posición (esquina superior izquierda)."""
        self.position = new_position

    def collides_with(self, other: "Hitbox") -> bool:
        """
        Detección de colisión AABB.
        Dos cajas colisionan si se superponen en ambos ejes.
        El contacto exacto en el borde NO cuenta como colisión.
        """
        if self.right <= other.left or other.right <= self.left:
            return False
        if self.bottom <= other.top or other.bottom <= self.top:
            return False
        return True

    def __repr__(self) -> str:
        return (
            f"Hitbox(pos=({self.position.x}, {self.position.y}), "
            f"w={self.width}, h={self.height})"
        )