"""
Enemy: clase base para entidades enemigas con posicion, tamano y hitbox.
Parte del dominio puro del juego (sin dependencias de Pygame).

Contiene SOLO lo genuinamente compartido entre Boss y MiniBoss:
posicion, dimensiones, hitbox sincronizado, y utilidades genericas
para recortar una coordenada a los bordes de pantalla (clamp_x, clamp_y).

NO incluye HP/take_damage/is_alive aqui a proposito: Boss los necesita
con su propio sistema de fases, MiniBoss es invulnerable y no los usa.
Cada subclase decide que mecanismo de vida (si alguno) implementar.
"""
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox


class Enemy:
    def __init__(
        self,
        position: Vector2,
        width: float,
        height: float,
        screen_width: int,
        screen_height: int,
    ):
        self.position = position
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hitbox = Hitbox(position=position, width=width, height=height)

    def move_to(self, new_position: Vector2) -> None:
        """Reubica la entidad y sincroniza su hitbox."""
        self.position = new_position
        self.hitbox.move_to(new_position)

    def clamp_x(self, x: float) -> float:
        """Recorta una coordenada X al rango visible de pantalla,
        considerando el ancho de la entidad."""
        return max(0, min(x, self.screen_width - self.width))

    def clamp_y(self, y: float) -> float:
        """Recorta una coordenada Y al rango visible de pantalla,
        considerando el alto de la entidad."""
        return max(0, min(y, self.screen_height - self.height))