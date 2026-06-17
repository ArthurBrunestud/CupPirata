"""
Renderer: dibuja el estado del juego usando rectangulos de colores
(version provisional, sin sprites). Reemplazable mas adelante por PNGs
sin tocar GameLoop ni el dominio.

Colores (placeholder):
    - Player: celeste
    - Boss: rojo oscuro
    - MiniBoss: morado
    - Proyectiles del jugador: amarillo
    - Proyectiles del jefe: magenta
    - Rayo en alerta: rojo / Rayo activo: blanco
    - HUD: blanco sobre fondo oscuro
"""
import pygame

COLOR_FONDO = (20, 20, 40)
COLOR_PLAYER = (80, 200, 255)
COLOR_BOSS = (180, 30, 30)
COLOR_MINI_BOSS = (140, 60, 160)
COLOR_PROYECTIL_JUGADOR = (255, 230, 80)
COLOR_PROYECTIL_ENEMIGO = (255, 80, 200)
COLOR_RAYO_ALERTA = (200, 30, 30)
COLOR_RAYO_ACTIVO = (255, 255, 255)
COLOR_HUD_TEXTO = (255, 255, 255)


class Renderer:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Arial", 20)

    def draw(self, surface, game_loop) -> None:
        surface.fill(COLOR_FONDO)

        if game_loop.is_player_visible():
            self._draw_entity(surface, game_loop.player, COLOR_PLAYER)

        self._draw_entity(surface, game_loop.boss, COLOR_BOSS)

        for mini in game_loop.mini_bosses:
            self._draw_entity(surface, mini, COLOR_MINI_BOSS)

        for proyectil in game_loop.player_projectiles:
            self._draw_entity(surface, proyectil, COLOR_PROYECTIL_JUGADOR)
        for proyectil in game_loop.enemy_projectiles:
            self._draw_entity(surface, proyectil, COLOR_PROYECTIL_ENEMIGO)
        for beam in game_loop.beams:
            color = COLOR_RAYO_ALERTA if beam.is_warning() else COLOR_RAYO_ACTIVO
            self._draw_entity(surface, beam, color)

        self._draw_hud(surface, game_loop)

    def _draw_entity(self, surface, entidad, color) -> None:
        rect = pygame.Rect(
            entidad.hitbox.left,
            entidad.hitbox.top,
            entidad.hitbox.width,
            entidad.hitbox.height,
        )
        pygame.draw.rect(surface, color, rect)

    def _draw_hud(self, surface, game_loop) -> None:
        textos = [
            f"HP Jugador: {game_loop.player.hp}",
            f"HP Jefe: {game_loop.boss.hp}/{game_loop.boss.max_hp}  Fase: {game_loop.boss.phase}",
            f"Puntaje: {game_loop.game_state.score}",
        ]
        for i, texto in enumerate(textos):
            render = self.font.render(texto, True, COLOR_HUD_TEXTO)
            surface.blit(render, (10, 10 + i * 25))

        if game_loop.game_state.is_game_over():
            mensaje = "VICTORIA" if game_loop.game_state.status.value == "won" else "DERROTA"
            render = self.font.render(mensaje, True, COLOR_HUD_TEXTO)
            rect = render.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(render, rect)