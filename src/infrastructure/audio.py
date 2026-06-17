"""
AudioManager: maneja la musica de fondo del juego.
Vive en infrastructure porque depende de pygame.mixer.

Comportamiento: al iniciar cada run se elige una de las canciones
disponibles al azar (random puro) y se reproduce en loop infinito
durante toda esa partida.

Si el audio no se puede inicializar o falta un archivo, el juego
continua sin musica (nunca crashea por un audio faltante).
"""
import os
import random
import pygame

SOUNDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "sounds"
)

CANCIONES = ["musica1.mp3", "musica2.mp3", "musica3.mp3"]
VOLUMEN_DEFECTO = 0.5  # 0.0 (silencio) a 1.0 (maximo)


class AudioManager:
    def __init__(self):
        self._disponible = False
        try:
            pygame.mixer.init()
            self._disponible = True
        except pygame.error as e:
            print(f"[AudioManager] AVISO: no se pudo inicializar el audio ({e}). El juego correra sin sonido.")

    def reproducir_cancion_aleatoria(self, random_choice_func=random.choice) -> None:
        """Elige una cancion al azar de las disponibles y la reproduce
        en loop infinito. Pensado para llamarse al iniciar cada run."""
        if not self._disponible:
            return

        cancion = random_choice_func(CANCIONES)
        ruta = os.path.join(SOUNDS_DIR, cancion)

        if not os.path.exists(ruta):
            print(f"[AudioManager] AVISO: no se encontro '{ruta}'. El juego correra sin musica.")
            return

        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(VOLUMEN_DEFECTO)
            pygame.mixer.music.play(loops=-1)  # -1 = loop infinito durante la run
        except pygame.error as e:
            print(f"[AudioManager] AVISO: no se pudo reproducir la musica ({e}).")

    def pausar(self) -> None:
        if self._disponible:
            pygame.mixer.music.pause()

    def reanudar(self) -> None:
        if self._disponible:
            pygame.mixer.music.unpause()

    def detener(self) -> None:
        if self._disponible:
            pygame.mixer.music.stop()