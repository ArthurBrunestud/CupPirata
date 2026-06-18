# language: es

Característica: Combate contra el jefe
  Como jugador
  Quiero disparar al jefe y recibir retroalimentación clara
  Para poder derrotarlo y ganar puntos en el proceso

  Escenario: Un disparo del jugador impacta al jefe y reduce su vida
    Dado un jefe con 300 puntos de vida
    Y un proyectil del jugador justo sobre el jefe
    Cuando se resuelven las colisiones del frame
    Entonces la vida del jefe debe ser menor a 300
    Y el puntaje del jugador debe haber aumentado

  Escenario: Un disparo que no toca al jefe no le hace daño
    Dado un jefe con 300 puntos de vida
    Y un proyectil del jugador lejos del jefe
    Cuando se resuelven las colisiones del frame
    Entonces la vida del jefe debe seguir siendo 300

  Escenario: El contacto físico con el jefe daña al jugador
    Dado un jugador con 10 puntos de vida
    Y el jugador está tocando físicamente al jefe
    Cuando pasan 0.5 segundos de contacto continuo
    Entonces la vida del jugador debe ser menor a 10

  Escenario: Un proyectil del jefe impacta y daña al jugador
    Dado un jugador con 10 puntos de vida
    Y un proyectil del jefe justo sobre el jugador
    Cuando se resuelven las colisiones del frame
    Entonces la vida del jugador debe ser menor a 10