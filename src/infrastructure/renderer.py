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
    - HUD: barras de vida + texto sobre fondo oscuro
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

COLOR_VIDA_LLENA = (80, 220, 100)
COLOR_VIDA_VACIA = (60, 60, 70)
COLOR_HP_JEFE_LLENO = (220, 50, 50)
COLOR_HP_JEFE_VACIO = (60, 60, 70)
COLOR_BARRA_BORDE = (255, 255, 255)


class Renderer:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_pequena = pygame.font.SysFont("Arial", 16)

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

    # -------------------- HUD --------------------

    def _draw_hud(self, surface, game_loop) -> None:
        self._draw_vida_jugador(surface, game_loop)
        self._draw_barra_jefe(surface, game_loop)
        self._draw_puntaje(surface, game_loop)

        if game_loop.game_state.is_game_over():
            self._draw_mensaje_fin(surface, game_loop)

    def _draw_vida_jugador(self, surface, game_loop) -> None:
        """Dibuja la vida del jugador como segmentos (uno por punto de HP).
        Ideal para HP bajo (3-5), donde una barra continua se ve poco clara."""
        margen_x = 20
        margen_y = 20
        segmento_ancho = 30
        segmento_alto = 18
        espacio = 6

        hp_maximo_referencia = max(game_loop.player.hp, 3)  # evita romper si hp baja de 3

        etiqueta = self.font_pequena.render("VIDA", True, COLOR_HUD_TEXTO)
        surface.blit(etiqueta, (margen_x, margen_y))

        y_segmentos = margen_y + 20
        for i in range(hp_maximo_referencia):
            x = margen_x + i * (segmento_ancho + espacio)
            rect = pygame.Rect(x, y_segmentos, segmento_ancho, segmento_alto)
            color = COLOR_VIDA_LLENA if i < game_loop.player.hp else COLOR_VIDA_VACIA
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, COLOR_BARRA_BORDE, rect, width=2)

    def _draw_barra_jefe(self, surface, game_loop) -> None:
        """Barra de HP del jefe, centrada arriba, con la fase indicada al lado."""
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