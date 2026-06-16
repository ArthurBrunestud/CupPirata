"""
Reglas de colision: funciones puras que resuelven impactos entre
proyectiles y entidades (Player, Boss).

Diseño: funciones puras en vez de metodos en las entidades, para que
ninguna entidad necesite conocer a la otra (Player no importa Boss,
y viceversa). Esta capa es la unica que conecta ambos mundos.
"""
from src.domain.entities.projectile import Projectile, Owner


def resolve_player_hit(player, projectiles: list[Projectile]) -> list[Projectile]:
    """
    Revisa la lista de proyectiles contra el Player.
    Aplica daño por cada proyectil ENEMY que colisione con su hitbox.
    Los proyectiles PLAYER se ignoran (no se autodañan).
    Devuelve la lista de proyectiles que NO impactaron (sobrevivientes).
    """
    sobrevivientes = []
    for proyectil in projectiles:
        es_amenaza = proyectil.owner == Owner.ENEMY
        impacta = es_amenaza and player.hitbox.collides_with(proyectil.hitbox)

        if impacta:
            player.take_damage(proyectil.damage)
        else:
            sobrevivientes.append(proyectil)

    return sobrevivientes


def resolve_boss_hit(boss, projectiles: list[Projectile]) -> list[Projectile]:
    """
    Revisa la lista de proyectiles contra el Boss.
    Aplica daño por cada proyectil PLAYER que colisione con su hitbox.
    Los proyectiles ENEMY se ignoran (el jefe no se autodaña).
    Devuelve la lista de proyectiles que NO impactaron (sobrevivientes).
    """
    sobrevivientes = []
    for proyectil in projectiles:
        es_amenaza = proyectil.owner == Owner.PLAYER
        impacta = es_amenaza and boss.hitbox.collides_with(proyectil.hitbox)

        if impacta:
            boss.take_damage(proyectil.damage)
        else:
            sobrevivientes.append(proyectil)

    return sobrevivientes

CONTACT_DAMAGE_INTERVAL = 0.5
CONTACT_DAMAGE_AMOUNT = 2


def resolve_contact_damage(player, boss, dt: float, contact_timer: float) -> float:
    """
    Aplica dano por contacto fisico entre Player y Boss.

    Mientras las hitboxes de player y boss se superpongan, acumula dt
    en contact_timer. Cada vez que el timer alcanza CONTACT_DAMAGE_INTERVAL
    (0.5s), aplica CONTACT_DAMAGE_AMOUNT (2) de dano al jugador y reinicia
    el timer a 0. El dano es fijo, no depende de la fase del jefe.

    Si no hay colision, el timer se reinicia a 0 (el contacto debe ser
    continuo para acumular danio; separarse y volver a tocar empieza de cero).

    Devuelve el nuevo valor de contact_timer, que quien llama debe
    conservar y pasar de vuelta en el siguiente frame.
    """
    hay_contacto = player.hitbox.collides_with(boss.hitbox)

    if not hay_contacto:
        return 0.0

    nuevo_timer = contact_timer + dt

    if nuevo_timer >= CONTACT_DAMAGE_INTERVAL:
        player.take_damage(CONTACT_DAMAGE_AMOUNT)
        return 0.0

    return nuevo_timer