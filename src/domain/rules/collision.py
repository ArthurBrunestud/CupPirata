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