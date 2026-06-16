"""
Tests unitarios para Vector2 (domain).
TDD - Ciclo 1: estos tests se escriben ANTES de implementar Vector2.
"""
import pytest
from src.domain.vector import Vector2


class TestVector2Creacion:
    def test_crea_vector_con_x_y_y(self):
        v = Vector2(3, 4)
        assert v.x == 3
        assert v.y == 4

    def test_vector_por_defecto_es_origen(self):
        v = Vector2()
        assert v.x == 0
        assert v.y == 0


class TestVector2Operaciones:
    def test_suma_de_dos_vectores(self):
        a = Vector2(1, 2)
        b = Vector2(3, 4)
        resultado = a + b
        assert resultado.x == 4
        assert resultado.y == 6

    def test_resta_de_dos_vectores(self):
        a = Vector2(5, 7)
        b = Vector2(2, 3)
        resultado = a - b
        assert resultado.x == 3
        assert resultado.y == 4

    def test_multiplicacion_por_escalar(self):
        v = Vector2(2, 3)
        resultado = v * 2
        assert resultado.x == 4
        assert resultado.y == 6

    def test_magnitud_de_vector_3_4_es_5(self):
        v = Vector2(3, 4)
        assert v.magnitude() == 5

    def test_vector_normalizado_tiene_magnitud_1(self):
        v = Vector2(3, 4)
        normalizado = v.normalized()
        assert round(normalizado.magnitude(), 5) == 1.0

    def test_normalizar_vector_cero_no_lanza_error(self):
        v = Vector2(0, 0)
        normalizado = v.normalized()
        assert normalizado.x == 0
        assert normalizado.y == 0


class TestVector2Igualdad:
    def test_dos_vectores_iguales_son_iguales(self):
        a = Vector2(1, 1)
        b = Vector2(1, 1)
        assert a == b

    def test_dos_vectores_distintos_no_son_iguales(self):
        a = Vector2(1, 1)
        b = Vector2(2, 2)
        assert a != b
