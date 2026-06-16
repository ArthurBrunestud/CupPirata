"""
Tests unitarios para BeamAttack (domain).
TDD - Ciclo 6b-1: el rayo del jefe, como zona de peligro temporal.
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.beam_attack import BeamAttack


def make_beam_vertical(x=400, y=0, width=20, height=600, duration=1.5):
    return BeamAttack(
        position=Vector2(x, y),
        width=width,
        height=height,
        duration=duration,
    )


class TestBeamAttackCreacion:
    def test_se_crea_con_posicion_tamano_y_duracion(self):
        beam = make_beam_vertical(x=400, y=0, width=20, height=600, duration=1.5)
        assert beam.position.x == 400
        assert beam.position.y == 0
        assert beam.width == 20
        assert beam.height == 600
        assert beam.duration == 1.5

    def test_rayo_tiene_hitbox_acorde_a_su_tamano(self):
        beam = make_beam_vertical(x=400, y=0, width=20, height=600)
        assert beam.hitbox.left == 400
        assert beam.hitbox.top == 0
        assert beam.hitbox.width == 20
        assert beam.hitbox.height == 600

    def test_rayo_esta_activo_al_crearse(self):
        beam = make_beam_vertical()
        assert beam.is_active() is True

    def test_rayo_vertical_es_mas_alto_que_ancho(self):
        beam = make_beam_vertical(width=20, height=600)
        assert beam.is_vertical() is True

    def test_rayo_horizontal_es_mas_ancho_que_alto(self):
        beam = BeamAttack(position=Vector2(0, 300), width=800, height=20, duration=1.0)
        assert beam.is_vertical() is False


class TestBeamAttackTiempo:
    def test_rayo_sigue_activo_antes_de_terminar_duracion(self):
        beam = make_beam_vertical(duration=1.0)
        beam.update(dt=0.5)
        assert beam.is_active() is True

    def test_rayo_se_desactiva_al_completar_duracion(self):
        beam = make_beam_vertical(duration=1.0)
        beam.update(dt=1.0)
        assert beam.is_active() is False

    def test_rayo_se_desactiva_si_supera_duracion(self):
        beam = make_beam_vertical(duration=1.0)
        beam.update(dt=1.5)
        assert beam.is_active() is False

    def test_rayo_no_se_desactiva_si_solo_paso_un_poco_de_tiempo(self):
        beam = make_beam_vertical(duration=2.0)
        beam.update(dt=0.3)
        beam.update(dt=0.3)
        assert beam.is_active() is True