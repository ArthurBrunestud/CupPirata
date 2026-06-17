"""
MiniBoss: mini-jefe invulnerable que aparece a los costados de la pantalla
cuando el Boss principal baja de cierto HP (logica de aparicion vive en
GameLoop, no aqui).

Hereda de Enemy: reutiliza posicion, hitbox y utilidades de recorte
a pantalla (clamp_y, en este caso, porque el MiniBoss solo se mueve
verticalmente).

Comportamiento:
    - Movimiento vertical aleatorio: cada 2.0-3.0s (igual que el patron
      que usa Boss horizontalmente) elige una nueva direccion -1/0/1.
    - Dispara un abanico de 3 balas con cooldown propio fijo, siempre
      apuntando hacia el centro horizontal de la pantalla (no hacia
      abajo, a diferencia del abanico del Boss principal).
    - Invulnerable: is_alive() siempre True, take_damage() no hace nada.
"""
import math
import random

from src.domain.vector import Vector2
from src.domain.entities.enemy import Enemy
from src.domain.entities.projectile import Projectile, Owner

DIRECTION_CHOICES = [-1, 0, 1]
DIRECTION_INTERVAL_MIN = 2.0
DIRECTION_INTERVAL_MAX = 3.0
MOVE_SPEED = 60

PROJECTILE_SPEED = 300
PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 10
PROJECTILE_DAMAGE = 1
FAN_SPREAD_DEGREES = 30


class MiniBoss(Enemy):
    def __init__(
        self,
        position: Vector2,
        width: float,
        height: float,
        screen_width: int,
        screen_height: int,
        shoot_cooldown: float,
    ):
        super().__init__(
            position=position, width=width, height=height,
            screen_width=screen_width, screen_height=screen_height,
        )
        self.shoot_cooldown = shoot_cooldown
        self._shoot_cooldown_restante = shoot_cooldown

        self._direccion_actual = 0
        self._tiempo_hasta_nueva_direccion = 0.0

    # -------------------- Invulnerabilidad --------------------

    def is_alive(self) -> bool:
        return True

    def take_damage(self, amount: int) -> None:
        """El MiniBoss es invulnerable: ignora cualquier intento de dano."""
        pass

    # -------------------- Update principal --------------------

    def update(
        self,
        dt: float,
        choose_direction_func=random.choice,
        choose_interval_func=random.uniform,
    ) -> list:
        self._actualizar_movimiento(dt, choose_direction_func, choose_interval_func)

        self._shoot_cooldown_restante = max(0.0, self._shoot_cooldown_restante - dt)

        if self._shoot_cooldown_restante <= 0.0:
            proyectiles = self._disparar_hacia_centro()
            self._shoot_cooldown_restante = self.shoot_cooldown
            return proyectiles

        return []

    # -------------------- Movimiento vertical --------------------

    def _actualizar_movimiento(self, dt, choose_direction_func, choose_interval_func) -> None:
        self._tiempo_hasta_nueva_direccion -= dt
        if self._tiempo_hasta_nueva_direccion <= 0.0:
            self._direccion_actual = choose_direction_func(DIRECTION_CHOICES)
            self._tiempo_hasta_nueva_direccion = choose_interval_func(
                DIRECTION_INTERVAL_MIN, DIRECTION_INTERVAL_MAX
            )

        if self._direccion_actual == 0:
            return

        nueva_y = self.position.y + self._direccion_actual * MOVE_SPEED * dt
        nueva_y = self.clamp_y(nueva_y)
        self.move_to(Vector2(self.position.x, nueva_y))

    # -------------------- Disparo --------------------

    def _centro_propio(self) -> Vector2:
        return Vector2(
            self.position.x + self.width / 2,
            self.position.y + self.height / 2,
        )

    def _angulo_hacia_centro_pantalla(self) -> float:
        """Calcula el angulo (en grados) desde el centro del MiniBoss
        hacia el centro horizontal de la pantalla (eje Y igual, solo
        importa la direccion horizontal: izquierda o derecha)."""
        centro_propio = self._centro_propio()
        centro_pantalla_x = self.screen_width / 2

        dx = centro_pantalla_x - centro_propio.x
        # apunta horizontalmente: 0 grados = derecha, 180 = izquierda
        return 0.0 if dx >= 0 else 180.0

    def _disparar_hacia_centro(self) -> list:
        centro_propio = self._centro_propio()
        angulo_base = self._angulo_hacia_centro_pantalla()

        inicio = angulo_base - FAN_SPREAD_DEGREES / 2
        paso = FAN_SPREAD_DEGREES / 2  # 3 balas: inicio, centro, fin
        angulos = [inicio + i * paso for i in range(3)]

        proyectiles = []
        for angulo_grados in angulos:
            radianes = math.radians(angulo_grados)
            vx = math.cos(radianes) * PROJECTILE_SPEED
            vy = math.sin(radianes) * PROJECTILE_SPEED

            proyectiles.append(
                Projectile(
                    position=Vector2(
                        centro_propio.x - PROJECTILE_WIDTH / 2,
                        centro_propio.y - PROJECTILE_HEIGHT / 2,
                    ),
                    velocity=Vector2(vx, vy),
                    width=PROJECTILE_WIDTH,
                    height=PROJECTILE_HEIGHT,
                    damage=PROJECTILE_DAMAGE,
                    owner=Owner.ENEMY,
                    screen_width=self.screen_width,
                    screen_height=self.screen_height,
                )
            )
        return proyectiles