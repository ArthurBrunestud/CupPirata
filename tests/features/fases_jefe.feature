# language: es

Característica: Fases del jefe
  Como jugador
  Quiero que el jefe se vuelva más desafiante a medida que pierde vida
  Para que la pelea tenga una progresión clara de dificultad

  Escenario: El jefe comienza en la primera fase
    Dado un jefe recién creado con 300 de vida máxima
    Entonces el jefe debe estar en la fase 1

  Escenario: El jefe pasa a la segunda fase al perder suficiente vida
    Dado un jefe recién creado con 300 de vida máxima
    Cuando el jefe recibe 150 puntos de daño
    Entonces el jefe debe estar en la fase 2

  Escenario: El jefe pasa a la tercera fase al perder casi toda su vida
    Dado un jefe recién creado con 300 de vida máxima
    Cuando el jefe recibe 250 puntos de daño
    Entonces el jefe debe estar en la fase 3

  Escenario: En dificultad Casual el jefe nunca llega a la tercera fase
    Dado un jefe en modo Casual con 300 de vida máxima
    Cuando el jefe recibe 280 puntos de daño
    Entonces el jefe debe estar en la fase 2
    Y el jefe no debe avanzar más allá de la fase 2

  Escenario: En dificultad Profesional el jefe puede llegar a la tercera fase
    Dado un jefe en modo Profesional con 300 de vida máxima
    Cuando el jefe recibe 280 puntos de daño
    Entonces el jefe debe estar en la fase 3