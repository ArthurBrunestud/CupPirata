"""
Player: avión del jugador.
Parte del dominio puro del juego (sin dependencias de Pygame).

Responsabilidades:
    - Mantener posición, tamaño, vidas y velocidad.
    - Moverse en 8 direcciones respetando los límites de pantalla.
    - Recibir daño y reportar si sigue vivo.
    - Exponer un hitbox que se sincroniza con su posición.

NO responsabilidades (van en otras rebanadas):
    - Disparar proyectiles.
    - Renderizarse en pantalla.
    - Leer input del teclado.
"""
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox


class Player:
    def __init__(
        self,
        position: Vector2,
        width: float,
        height: float,
        hp: int,
        speed: float,
        screen_width: int,
        screen_height: int,
    ):
        self.position = position
        self.width = width
        self.height = height
        self.hp = hp
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hitbox = Hitbox(position=position, width=width, height=height)

    # -------------------- Estado de vida --------------------

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        """Aplica daño. Ignora cantidades no positivas (no cura)."""
        if amount <= 0:
            return
        self.hp = max(0, self.hp - amount)

    # -------------------- Movimiento --------------------

    def move(self, direction: Vector2, dt: float) -> None:
        """
        Mueve al jugador en la dirección indicada durante dt segundos.

        - 'direction' es un vector indicativo (no necesita estar normalizado);
          se normaliza internamente para que el movimiento diagonal NO sea
          más rápido que el horizontal o vertical.
        - El movimiento queda recortado a los bordes de la pantalla.
        """
        normalized = direction.normalized()
        desplazamiento = normalized * (self.speed * dt)
        nueva_posicion = self.position + desplazamiento
        self.position = self._recortar_a_pantalla(nueva_posicion)
        self.hitbox.move_to(self.position)

    def _recortar_a_pantalla(self, posicion: Vector2) -> Vector2:
        """Mantiene al jugador dentro de [0, screen_width - width] en X
        y [0, screen_height - height] en Y."""
        x = max(0, min(posicion.x, self.screen_width - self.width))
        y = max(0, min(posicion.y, self.screen_height - self.height))
        return Vector2(x, y)