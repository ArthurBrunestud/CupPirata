"""
Tests unitarios para BeamAttack (domain).
TDD - Ciclo 13: el rayo del jefe ahora tiene una fase de ALERTA (no dana,
se muestra en rojo) antes de pasar a ACTIVO (si dana).

Ciclo de vida temporal:
    [0, warning_duration)              -> warning (alerta, no dana)
    [warning_duration, total_duration) -> active (dañino)
    >= total_duration                  -> terminado
"""
import pytest
from src.domain.vector import Vector2
from src.domain.entities.beam_attack import BeamAttack


def make_beam(x=400, y=0, width=20, height=600, duration=2.0, warning_duration=1.0):
    return BeamAttack(
        position=Vector2(x, y), width=width, height=height,
        duration=duration, warning_duration=warning_duration,
    )


class TestBeamAttackCreacion:
    def test_se_crea_con_posicion_tamano_y_duracion(self):
        beam = make_beam(x=400, y=0, width=20, height=600, duration=2.0)
        assert beam.position.x == 400
        assert beam.position.y == 0
        assert beam.width == 20
        assert beam.height == 600
        assert beam.duration == 2.0

    def test_rayo_tiene_hitbox_acorde_a_su_tamano(self):
        beam = make_beam(x=400, y=0, width=20, height=600)
        assert beam.hitbox.left == 400
        assert beam.hitbox.top == 0
        assert beam.hitbox.width == 20
        assert beam.hitbox.height == 600

    def test_rayo_vertical_es_mas_alto_que_ancho(self):
        beam = make_beam(width=20, height=600)
        assert beam.is_vertical() is True

    def test_rayo_horizontal_es_mas_ancho_que_alto(self):
        beam = BeamAttack(position=Vector2(0, 300), width=800, height=20, duration=2.0, warning_duration=1.0)
        assert beam.is_vertical() is False


class TestBeamAttackFaseAlerta:
    def test_rayo_recien_creado_esta_en_alerta(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        assert beam.is_warning() is True

    def test_rayo_en_alerta_no_esta_activo_aun(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        assert beam.is_active() is False

    def test_rayo_en_alerta_sigue_visible(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        assert beam.is_visible() is True

    def test_alerta_termina_justo_al_cumplir_warning_duration(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=1.0)
        assert beam.is_warning() is False
        assert beam.is_active() is True

    def test_alerta_sigue_antes_de_cumplirse(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=0.9)
        assert beam.is_warning() is True
        assert beam.is_active() is False


class TestBeamAttackFaseActiva:
    def test_rayo_activo_tras_pasar_la_alerta(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=1.5)
        assert beam.is_active() is True
        assert beam.is_warning() is False

    def test_rayo_sigue_visible_mientras_esta_activo(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=1.5)
        assert beam.is_visible() is True


class TestBeamAttackFinDeVida:
    def test_rayo_termina_al_completar_duracion_total(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=2.0)
        assert beam.is_active() is False
        assert beam.is_warning() is False
        assert beam.is_visible() is False

    def test_rayo_termina_si_supera_duracion_total(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=3.0)
        assert beam.is_visible() is False

    def test_rayo_no_termina_si_solo_paso_un_poco_de_tiempo(self):
        beam = make_beam(duration=2.0, warning_duration=1.0)
        beam.update(dt=0.3)
        beam.update(dt=0.3)
        assert beam.is_visible() is True