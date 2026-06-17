"""
Renderer: dibuja el estado del juego usando sprites PNG.
El jefe y el fondo cambian de imagen segun la fase actual del jefe.
"""
import pygame
from src.infrastructure.asset_loader import AssetLoader

COLOR_FONDO_RESPALDO = (20, 20, 40)
COLOR_PROYECTIL_JUGADOR = (255, 230, 80)
COLOR_PROYECTIL_ENEMIGO = (255, 80, 200)
COLOR_RAYO_ALERTA = (200, 30, 30)
COLOR_RAYO_ACTIVO = (255, 255, 255)
COLOR_MINI_BOSS = (140, 60, 160)
COLOR_HUD_TEXTO = (255, 255, 255)
COLOR_HP_JEFE_LLENO = (220, 50, 50)
COLOR_HP_JEFE_VACIO = (60, 60, 70)
COLOR_BARRA_BORDE = (255, 255, 255)

HEART_SIZE = (28, 28)


class Renderer:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_pequena = pygame.font.SysFont("Arial", 16)

        self.assets = AssetLoader()

        self.heart_sprite = self.assets.load_sprite("heart.png", size=HEART_SIZE)
        self.heart_empty_sprite = self._crear_corazon_vacio()

        self.player_sprite = None  # se carga al primer draw, ya con tamaño real
        self.boss_sprites = {}     # se carga perezosamente por fase
        self.background_sprites = {}

    def draw(self, surface, game_loop) -> None:
        self._draw_background(surface, game_loop.boss.phase)

        if game_loop.is_player_visible():
            self._draw_player(surface, game_loop.player)

        self._draw_boss(surface, game_loop.boss)

        for mini in game_loop.mini_bosses:
            self._draw_rect_entity(surface, mini, COLOR_MINI_BOSS)

        for proyectil in game_loop.player_projectiles:
            self._draw_rect_entity(surface, proyectil, COLOR_PROYECTIL_JUGADOR)
        for proyectil in game_loop.enemy_projectiles:
            self._draw_rect_entity(surface, proyectil, COLOR_PROYECTIL_ENEMIGO)
        for beam in game_loop.beams:
            color = COLOR_RAYO_ALERTA if beam.is_warning() else COLOR_RAYO_ACTIVO
            self._draw_rect_entity(surface, beam, color)

        self._draw_hud(surface, game_loop)

    # -------------------- Fondo dinamico por fase --------------------

    def _draw_background(self, surface, phase: int) -> None:
        if phase not in self.background_sprites:
            filename = f"fondo_fase{phase}.png"
            self.background_sprites[phase] = self.assets.load_background(
                filename, size=(self.screen_width, self.screen_height)
            )
        surface.blit(self.background_sprites[phase], (0, 0))

    # -------------------- Player --------------------

    def _draw_player(self, surface, player) -> None:
        if self.player_sprite is None:
            size = (int(player.width), int(player.height))
            self.player_sprite = self.assets.load_sprite("player.png", size=size)
        surface.blit(self.player_sprite, (player.hitbox.left, player.hitbox.top))

    # -------------------- Boss dinamico por fase --------------------

    def _draw_boss(self, surface, boss) -> None:
        if boss.phase not in self.boss_sprites:
            filename = f"boss_fase{boss.phase}.png"
            size = (int(boss.width), int(boss.height))
            self.boss_sprites[boss.phase] = self.assets.load_sprite(filename, size=size)
        surface.blit(self.boss_sprites[boss.phase], (boss.hitbox.left, boss.hitbox.top))

    # -------------------- Entidades genericas (rectangulos, sin sprite aun) --------------------

    def _draw_rect_entity(self, surface, entidad, color) -> None:
        rect = pygame.Rect(
            entidad.hitbox.left, entidad.hitbox.top,
            entidad.hitbox.width, entidad.hitbox.height,
        )
        pygame.draw.rect(surface, color, rect)

    # -------------------- HUD --------------------

    def _draw_hud(self, surface, game_loop) -> None:
        self._draw_vida_jugador(surface, game_loop)
        self._draw_barra_jefe(surface, game_loop)
        self._draw_puntaje(surface, game_loop)

        if game_loop.game_state.is_game_over():
            self._draw_mensaje_fin(surface, game_loop)

    def _crear_corazon_vacio(self) -> pygame.Surface:
        """Version 'apagada' del corazon: mismo sprite pero oscurecido,
        para representar vida perdida sin necesitar un segundo archivo PNG."""
        vacio = self.heart_sprite.copy()
        oscurecedor = pygame.Surface(HEART_SIZE, pygame.SRCALPHA)
        oscurecedor.fill((0, 0, 0, 160))
        vacio.blit(oscurecedor, (0, 0))
        return vacio

    def _draw_vida_jugador(self, surface, game_loop) -> None:
        margen_x = 20
        margen_y = 20
        espacio = 6

        hp_maximo_referencia = max(game_loop.player.hp, 3)

        etiqueta = self.font_pequena.render("VIDA", True, COLOR_HUD_TEXTO)
        surface.blit(etiqueta, (margen_x, margen_y))

        y_corazones = margen_y + 20
        for i in range(hp_maximo_referencia):
            x = margen_x + i * (HEART_SIZE[0] + espacio)
            sprite = self.heart_sprite if i < game_loop.player.hp else self.heart_empty_sprite
            surface.blit(sprite, (x, y_corazones))

    def _draw_barra_jefe(self, surface, game_loop) -> None:
        boss = game_loop.boss
        ancho_barra = 400
        alto_barra = 24
        x = self.screen_width // 2 - ancho_barra // 2
        y = 20

        porcentaje = max(0.0, boss.hp / boss.max_hp) if boss.max_hp > 0 else 0.0
        ancho_lleno = int(ancho_barra * porcentaje)

        fondo_rect = pygame.Rect(x, y, ancho_barra, alto_barra)
        pygame.draw.rect(surface, COLOR_HP_JEFE_VACIO, fondo_rect)

        if ancho_lleno > 0:
            lleno_rect = pygame.Rect(x, y, ancho_lleno, alto_barra)
            pygame.draw.rect(surface, COLOR_HP_JEFE_LLENO, lleno_rect)

        pygame.draw.rect(surface, COLOR_BARRA_BORDE, fondo_rect, width=2)

        etiqueta = self.font_pequena.render(
            f"JEFE - Fase {boss.phase}", True, COLOR_HUD_TEXTO
        )
        etiqueta_rect = etiqueta.get_rect(center=(self.screen_width // 2, y - 12))
        surface.blit(etiqueta, etiqueta_rect)

    def _draw_puntaje(self, surface, game_loop) -> None:
        texto = self.font.render(
            f"Puntaje: {game_loop.game_state.score}", True, COLOR_HUD_TEXTO
        )
        rect = texto.get_rect(topright=(self.screen_width - 20, 20))
        surface.blit(texto, rect)

    def _draw_mensaje_fin(self, surface, game_loop) -> None:
        mensaje = "VICTORIA" if game_loop.game_state.status.value == "won" else "DERROTA"
        render = self.font.render(mensaje, True, COLOR_HUD_TEXTO)
        rect = render.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(render, rect)