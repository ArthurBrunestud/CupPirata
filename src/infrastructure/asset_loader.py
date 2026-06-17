"""
AssetLoader: carga y cachea las imagenes (sprites y fondos) del juego.
Vive en infrastructure porque depende directamente de Pygame.

Si una imagen no se encuentra, se informa con un mensaje claro en consola
y se usa un placeholder de color solido en su lugar, para que el juego
nunca crashee solo por un asset faltante durante el desarrollo.
"""
import os
import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")


class AssetLoader:
    def __init__(self):
        self._cache = {}

    def load_sprite(self, filename: str, size: tuple = None) -> pygame.Surface:
        return self._load(os.path.join(SPRITES_DIR, filename), size, forzar_opaco=False)

    def load_background(self, filename: str, size: tuple = None) -> pygame.Surface:
        return self._load(os.path.join(BACKGROUNDS_DIR, filename), size, forzar_opaco=True)

    def _load(self, path: str, size: tuple, forzar_opaco: bool = False) -> pygame.Surface:
        cache_key = (path, size, forzar_opaco)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not os.path.exists(path):
            print(f"[AssetLoader] AVISO: no se encontro '{path}', usando placeholder.")
            superficie = self._crear_placeholder(size or (64, 64))
        else:
            if forzar_opaco:
                # convert() en vez de convert_alpha(): descarta cualquier
                # transparencia, evitando que bordes alpha del PNG dejen
                # ver negro detras (un fondo de escenario nunca necesita
                # transparencia, asi que esto es seguro).
                superficie = pygame.image.load(path).convert()
            else:
                superficie = pygame.image.load(path).convert_alpha()

            if size is not None:
                superficie = pygame.transform.scale(superficie, size)

        self._cache[cache_key] = superficie
        return superficie

    def _crear_placeholder(self, size: tuple) -> pygame.Surface:
        superficie = pygame.Surface(size)
        superficie.fill((255, 0, 255))  # magenta brillante, facil de notar
        return superficie