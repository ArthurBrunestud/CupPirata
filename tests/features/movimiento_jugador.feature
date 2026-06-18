# language: es

Característica: Movimiento del jugador
  Como jugador
  Quiero mover mi avión libremente por la pantalla
  Para poder esquivar los ataques del jefe

  Escenario: El jugador se mueve hacia la derecha
    Dado un jugador en la posición (400, 500)
    Cuando el jugador se mueve hacia la derecha durante 1 segundo
    Entonces la posición X del jugador debe ser mayor que 400

  Escenario: El jugador no puede salir de la pantalla por la derecha
    Dado un jugador cerca del borde derecho de la pantalla
    Cuando el jugador intenta moverse hacia la derecha durante 5 segundos
    Entonces el jugador debe quedar exactamente en el borde derecho de la pantalla

  Escenario: El jugador no puede salir de la pantalla por la izquierda
    Dado un jugador cerca del borde izquierdo de la pantalla
    Cuando el jugador intenta moverse hacia la izquierda durante 5 segundos
    Entonces el jugador debe quedar exactamente en el borde izquierdo de la pantalla

  Escenario: El movimiento diagonal no es más rápido que el movimiento recto
    Dado un jugador en el centro de la pantalla
    Cuando el jugador se mueve en diagonal durante 1 segundo
    Entonces la distancia recorrida debe ser igual a la velocidad del jugador