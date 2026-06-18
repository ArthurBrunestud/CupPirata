# language: es

Característica: Condiciones de fin de partida
  Como jugador
  Quiero que el juego determine claramente si gané o perdí
  Para saber cuándo termina mi intento y si fui exitoso

  Escenario: La partida continúa si ambos siguen vivos
    Dado un jugador vivo y un jefe vivo
    Cuando se evalúan las condiciones de fin de partida
    Entonces el estado de la partida debe ser "jugando"

  Escenario: El jugador pierde si su vida llega a cero
    Dado un jugador con 0 puntos de vida
    Y un jefe vivo
    Cuando se evalúan las condiciones de fin de partida
    Entonces el estado de la partida debe ser "derrota"

  Escenario: El jugador gana si derrota al jefe
    Dado un jugador vivo
    Y un jefe con 0 puntos de vida
    Cuando se evalúan las condiciones de fin de partida
    Entonces el estado de la partida debe ser "victoria"

  Escenario: Si ambos mueren en el mismo instante, se prioriza la derrota
    Dado un jugador con 0 puntos de vida
    Y un jefe con 0 puntos de vida
    Cuando se evalúan las condiciones de fin de partida
    Entonces el estado de la partida debe ser "derrota"

  Escenario: Una partida que ya terminó no cambia de estado
    Dado un jugador con 0 puntos de vida
    Y un jefe vivo
    Cuando se evalúan las condiciones de fin de partida
    Entonces el estado de la partida debe ser "derrota"
    Cuando el jugador recupera la vida y se vuelven a evaluar las condiciones
    Entonces el estado de la partida debe ser "derrota"