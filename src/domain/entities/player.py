"""
Player: avión del jugador.
Parte del dominio puro del juego (sin dependencias de Pygame).

Responsabilidades:
    - Mantener posición, tamaño, vidas y velocidad.
    - Moverse en 8 direcciones respetando los límites de pantalla.
    - Recibir daño y reportar si sigue vivo.
    - Disparar proyectiles respetando un cooldown entre disparos.
    - Exponer un hitbox que se sincroniza con su posición.

NO responsabilidades:
    - Renderizarse en pantalla.
    - Leer input del teclado (eso vive en infrastructure/).
"""
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox
from src.domain.entities.projectile import Projectile, Owner

# Valores por defecto del disparo del jugador.
DEFAULT_SHOOT_COOLDOWN = 0.25      # segundos entre disparos
DEFAULT_PROJECTILE_WIDTH = 8
DEFAULT_PROJECTILE_HEIGHT = 16
DEFAULT_PROJECTILE_SPEED = 500     # px/seg, hacia arriba
DEFAULT_PROJECTILE_DAMAGE = 1


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
        shoot_cooldown: float = DEFAULT_SHOOT_COOLDOWN,
    ):
        self.position = position
        self.width = width
        self.height = height
        self.hp = hp
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hitbox = Hitbox(position=position, width=width, height=height)

        self.shoot_cooldown = shoot_cooldown
        self._cooldown_restante = 0.0

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
        normalized = direction.normalized()
        desplazamiento = normalized * (self.speed * dt)
        nueva_posicion = self.position + desplazamiento
        self.position = self._recortar_a_pantalla(nueva_posicion)
        self.hitbox.move_to(self.position)

    def _recortar_a_pantalla(self, posicion: Vector2) -> Vector2:
        x = max(0, min(posicion.x, self.screen_width - self.width))
        y = max(0, min(posicion.y, self.screen_height - self.height))
        return Vector2(x, y)

    # -------------------- Disparo --------------------

    def update_cooldown(self, dt: float) -> None:
        """Reduce el temporizador de cooldown. Se llama una vez por frame."""
        self._cooldown_restante = max(0.0, self._cooldown_restante - dt)

    def can_shoot(self) -> bool:
        return self.is_alive() and self._cooldown_restante <= 0.0

    def shoot(self) -> Projectile | None:
        """
        Genera un Projectile que sale desde el centro superior del Player,
        siempre que esté vivo y el cooldown haya terminado.
        Devuelve None si no puede disparar todavía.
        """
        if not self.can_shoot():
            return None

        self._cooldown_restante = self.shoot_cooldown

        spawn_x = self.position.x + self.width / 2 - DEFAULT_PROJECTILE_WIDTH / 2
        spawn_y = self.position.y

        return Projectile(
            position=Vector2(spawn_x, spawn_y),
            velocity=Vector2(0, -DEFAULT_PROJECTILE_SPEED),
            width=DEFAULT_PROJECTILE_WIDTH,
            height=DEFAULT_PROJECTILE_HEIGHT,
            damage=DEFAULT_PROJECTILE_DAMAGE,
            owner=Owner.PLAYER,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
        )