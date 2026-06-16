"""
Boss: jefe del nivel aereo. Unico oponente del juego (sin enemigos menores).
Parte del dominio puro del juego (sin dependencias de Pygame).

Responsabilidades:
    - Mantener HP y avanzar de fase segun el HP restante (trinquete, no retrocede).
    - Generar ataques (Projectile en abanico y BeamAttack) segun su fase actual,
      sin necesitar conocer la posicion del jugador.

Reglas de fase (HP):
    - Fase 1: HP > 66% de max_hp
    - Fase 2: HP <= 66% y > 33% de max_hp
    - Fase 3: HP <= 33% de max_hp

Reglas de ataque por fase:
    - Fase 1: abanico de 3 proyectiles cada 2.0s. Sin rayo.
    - Fase 2: abanico de 5 proyectiles cada 1.5s. Rayo cada 4.0s (dura 1.0s).
    - Fase 3: abanico de 7 proyectiles cada 1.0s. Rayo cada 3.0s (dura 1.2s).
"""
from src.domain.vector import Vector2
from src.domain.hitbox import Hitbox
from src.domain.entities.projectile import Projectile, Owner
from src.domain.entities.beam_attack import BeamAttack

PROJECTILE_SPEED = 250
PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 10
PROJECTILE_DAMAGE = 1
FAN_SPREAD_DEGREES = 50  # apertura total del abanico

# (cantidad_proyectiles, cooldown_disparo, cooldown_rayo o None, duracion_rayo)
PHASE_CONFIG = {
    1: {"bullet_count": 3, "shoot_cooldown": 2.0, "beam_cooldown": None, "beam_duration": 0.0},
    2: {"bullet_count": 5, "shoot_cooldown": 1.5, "beam_cooldown": 4.0, "beam_duration": 1.0},
    3: {"bullet_count": 7, "shoot_cooldown": 1.0, "beam_cooldown": 3.0, "beam_duration": 1.2},
}


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
        self._shoot_cooldown_restante = PHASE_CONFIG[self.phase]["shoot_cooldown"]
        self._beam_cooldown_restante = 0.0
        self._actualizar_fase()

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
        fase_calculada = self._fase_segun_hp()
        if fase_calculada > self.phase:
            self.phase = fase_calculada
            self._shoot_cooldown_restante = PHASE_CONFIG[self.phase]["shoot_cooldown"]
            self._beam_cooldown_restante = 0.0

    # -------------------- Ataques --------------------

    def update(self, dt: float) -> dict:
        """
        Avanza los temporizadores de ataque y genera, si corresponde,
        los ataques de este frame.

        Devuelve: {"projectiles": list[Projectile], "beam": BeamAttack | None}
        """
        config = PHASE_CONFIG[self.phase]

        self._shoot_cooldown_restante = max(0.0, self._shoot_cooldown_restante - dt)
        self._beam_cooldown_restante = max(0.0, self._beam_cooldown_restante - dt)

        proyectiles = []
        if self._shoot_cooldown_restante <= 0.0:
            proyectiles = self._disparar_abanico(config["bullet_count"])
            self._shoot_cooldown_restante = config["shoot_cooldown"]

        rayo = None
        if config["beam_cooldown"] is not None and self._beam_cooldown_restante <= 0.0:
            rayo = self._generar_rayo(config["beam_duration"])
            self._beam_cooldown_restante = config["beam_cooldown"]

        return {"projectiles": proyectiles, "beam": rayo}

    def _centro(self) -> Vector2:
        return Vector2(
            self.position.x + self.width / 2,
            self.position.y + self.height,
        )

    def _disparar_abanico(self, cantidad: int) -> list:
        """Genera 'cantidad' proyectiles en abanico hacia abajo,
        sin apuntar al jugador, repartidos en FAN_SPREAD_DEGREES grados."""
        import math

        centro = self._centro()
        proyectiles = []

        if cantidad == 1:
            angulos = [90.0]  # recto hacia abajo
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
                    position=Vector2(
                        centro.x - PROJECTILE_WIDTH / 2,
                        centro.y,
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

    def _generar_rayo(self, duration: float) -> BeamAttack:
        """Genera un rayo vertical delgado en una posicion X pseudo-variable
        (camino mas simple: usa el centro X del jefe como referencia fija
        por ahora; la variacion dinamica de posicion se deja como parametro
        configurable para el Spawner en una rebanada posterior)."""
        centro = self._centro()
        ancho_rayo = 20
        return BeamAttack(
            position=Vector2(centro.x - ancho_rayo / 2, 0),
            width=ancho_rayo,
            height=self.screen_height,
            duration=duration,
        )