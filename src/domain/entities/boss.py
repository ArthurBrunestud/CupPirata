"""
Boss: jefe del nivel aereo. Unico oponente del juego (sin enemigos menores).
Parte del dominio puro del juego (sin dependencias de Pygame).

Reglas de fase (HP):
    - Fase 1: HP > 66% de max_hp
    - Fase 2: HP <= 66% y > 33% de max_hp
    - Fase 3: HP <= 33% de max_hp

Reglas de ataque por fase:
    - Fase 1: abanico de 5 proyectiles cada 2.0s. 1 rayo vertical cada 6.0s.
    - Fase 2: abanico de 8 proyectiles cada 1.5s. 2-3 rayos verticales cada 3.0s.
    - Fase 3: abanico de 8 proyectiles cada 1.0s. 2-3 rayos vertical/horizontal
      (orientacion al azar por rayo) cada 2.0s.

Reglas de movimiento por fase:
    - Fase 1: velocidad 80 px/s. Fase 2: 130 px/s. Fase 3: 220 px/s.
    - Cada 2.0-3.0s (aleatorio) elige nueva direccion: -1, 0 o 1.

Toda aleatoriedad se resuelve via funciones inyectables (valores por
defecto usan random real; en tests se sustituyen por funciones fijas).
"""
import math
import random

from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox
from src.domain.entities.projectile import Projectile, Owner
from src.domain.entities.beam_attack import BeamAttack

PROJECTILE_SPEED = 250
PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 10
PROJECTILE_DAMAGE = 1
FAN_SPREAD_DEGREES = 50

DIRECTION_CHOICES = [-1, 0, 1]
DIRECTION_INTERVAL_MIN = 2.0
DIRECTION_INTERVAL_MAX = 3.0

BEAM_WARNING_DURATION = 1.0
BEAM_ACTIVE_DURATION = 1.0
BEAM_THICKNESS = 20
ORIENTATION_CHOICES = ["vertical", "horizontal"]

PHASE_CONFIG = {
    1: {
        "bullet_count": 5, "shoot_cooldown": 2.0,
        "beam_cooldown": 6.0, "beam_count_range": (1, 1),
        "beam_orientation": "vertical",
        "move_speed": 80,
    },
    2: {
        "bullet_count": 8, "shoot_cooldown": 1.5,
        "beam_cooldown": 3.0, "beam_count_range": (2, 3),
        "beam_orientation": "vertical",
        "move_speed": 130,
    },
    3: {
        "bullet_count": 8, "shoot_cooldown": 1.0,
        "beam_cooldown": 2.0, "beam_count_range": (2, 3),
        "beam_orientation": "random",
        "move_speed": 220,
    },
}


class Boss:
    def __init__(self, position, width, height, hp, max_hp, screen_width, screen_height, max_phase=3):
        self.position = position
        self.width = width
        self.height = height
        self.hp = hp
        self.max_hp = max_hp
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_phase = max_phase
        self.hitbox = Hitbox(position=position, width=width, height=height)

        self.phase = 1
        self._shoot_cooldown_restante = PHASE_CONFIG[self.phase]["shoot_cooldown"]
        self._beam_cooldown_restante = PHASE_CONFIG[self.phase]["beam_cooldown"]
        self._actualizar_fase()
        self._direccion_actual = 0
        self._tiempo_hasta_nueva_direccion = 0.0
    # -------------------- Estado de vida --------------------

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
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
        fase_calculada = min(self._fase_segun_hp(), self.max_phase)
        if fase_calculada > self.phase:
            self.phase = fase_calculada
            self._shoot_cooldown_restante = PHASE_CONFIG[self.phase]["shoot_cooldown"]
            self._beam_cooldown_restante = PHASE_CONFIG[self.phase]["beam_cooldown"]

    # -------------------- Update principal --------------------

    def update(
        self,
        dt: float,
        random_x_func=random.uniform,
        choose_direction_func=random.choice,
        choose_interval_func=random.uniform,
        choose_beam_count_func=random.randint,
        choose_orientation_func=random.choice,
    ) -> dict:
        """
        Devuelve: {"projectiles": list[Projectile], "beams": list[BeamAttack]}
        """
        config = PHASE_CONFIG[self.phase]

        self._actualizar_movimiento(dt, config, choose_direction_func, choose_interval_func)

        self._shoot_cooldown_restante = max(0.0, self._shoot_cooldown_restante - dt)
        self._beam_cooldown_restante = max(0.0, self._beam_cooldown_restante - dt)

        proyectiles = []
        if self._shoot_cooldown_restante <= 0.0:
            proyectiles = self._disparar_abanico(config["bullet_count"])
            self._shoot_cooldown_restante = config["shoot_cooldown"]

        rayos = []
        if self._beam_cooldown_restante <= 0.0:
            rayos = self._generar_rayos(
                config, random_x_func, choose_beam_count_func, choose_orientation_func
            )
            self._beam_cooldown_restante = config["beam_cooldown"]

        return {"projectiles": proyectiles, "beams": rayos}

    # -------------------- Movimiento --------------------

    def _actualizar_movimiento(self, dt, config, choose_direction_func, choose_interval_func) -> None:
        self._tiempo_hasta_nueva_direccion -= dt
        if self._tiempo_hasta_nueva_direccion <= 0.0:
            self._direccion_actual = choose_direction_func(DIRECTION_CHOICES)
            self._tiempo_hasta_nueva_direccion = choose_interval_func(
                DIRECTION_INTERVAL_MIN, DIRECTION_INTERVAL_MAX
            )

        if self._direccion_actual == 0:
            return

        velocidad = config["move_speed"]
        nueva_x = self.position.x + self._direccion_actual * velocidad * dt
        nueva_x = max(0, min(nueva_x, self.screen_width - self.width))

        self.position = Vector2(nueva_x, self.position.y)
        self.hitbox.move_to(self.position)

    # -------------------- Ataque: proyectiles --------------------

    def _centro(self) -> Vector2:
        return Vector2(self.position.x + self.width / 2, self.position.y + self.height)

    def _disparar_abanico(self, cantidad: int) -> list:
        centro = self._centro()
        proyectiles = []

        if cantidad == 1:
            angulos = [90.0]
        else:
            inicio = 90 - FAN_SPREAD_DEGREES / 2
            paso = FAN_SPREAD_DEGREES / (cantidad - 1)
            angulos = [inicio + i * paso for i in range(cantidad)]

        for angulo_grados in angulos:
            radianes = math.radians(angulo_grados)
            vx = math.cos(radianes) * PROJECTILE_SPEED
            vy = math.sin(radianes) * PROJECTILE_SPEED

            proyectiles.append(
                Projectile(
                    position=Vector2(centro.x - PROJECTILE_WIDTH / 2, centro.y),
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

    # -------------------- Ataque: rayos --------------------

    def _generar_rayos(self, config, random_x_func, choose_beam_count_func, choose_orientation_func) -> list:
        minimo, maximo = config["beam_count_range"]
        cantidad = choose_beam_count_func(minimo, maximo)

        rayos = []
        posiciones_usadas = []

        for _ in range(cantidad):
            orientacion = self._elegir_orientacion(config["beam_orientation"], choose_orientation_func)
            rayo = self._crear_un_rayo(orientacion, random_x_func, posiciones_usadas)
            rayos.append(rayo)

        return rayos

    def _elegir_orientacion(self, modo: str, choose_orientation_func) -> str:
        if modo == "random":
            return choose_orientation_func(ORIENTATION_CHOICES)
        return modo

    def _crear_un_rayo(self, orientacion: str, random_x_func, posiciones_usadas: list) -> BeamAttack:
        duration = BEAM_WARNING_DURATION + BEAM_ACTIVE_DURATION

        if orientacion == "vertical":
            x = random_x_func(0, self.screen_width - BEAM_THICKNESS)
            posiciones_usadas.append(x)
            return BeamAttack(
                position=Vector2(x, 0),
                width=BEAM_THICKNESS,
                height=self.screen_height,
                duration=duration,
                warning_duration=BEAM_WARNING_DURATION,
            )
        else:  # horizontal
            y = random_x_func(0, self.screen_height - BEAM_THICKNESS)
            posiciones_usadas.append(y)
            return BeamAttack(
                position=Vector2(0, y),
                width=self.screen_width,
                height=BEAM_THICKNESS,
                duration=duration,
                warning_duration=BEAM_WARNING_DURATION,
            )