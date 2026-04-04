# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

#!/usr/bin/env python3
"""Script de prueba para verificar el sistema de investigaciones"""

import sys
sys.path.insert(0, '.')

from configuracion import *
from logica_ciudad import LogicaCiudad
from entidades import Ciudadano

class MockJuego:
    """Mock del objeto Juego para pruebas"""
    def __init__(self):
        self.ruta_partida = "test_partida.json"
        self.mapa_datos = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]

# Crear logica de prueba
juego_mock = MockJuego()
logica = LogicaCiudad(juego_mock, "Test Partida")

print("=" * 60)
print("TEST: SISTEMA DE INVESTIGACIONES")
print("=" * 60)

# Test 1: Verificar datos_investigacion
print("\n1. Verificar que datos_investigacion existe...")
print(f"   Total de investigaciones: {len(logica.datos_investigacion)}")
for inv_id, datos in logica.datos_investigacion.items():
    print(f"   - {inv_id}: {datos['titulo']} (Nivel {datos['nivel']})")

# Test 2: Verificar obtener_investigaciones_disponibles
print("\n2. Obtener investigaciones disponibles (Nivel 1)...")
disponibles = logica.obtener_investigaciones_disponibles()
print(f"   Total disponibles: {len(disponibles)}")
for inv_id, datos in disponibles.items():
    print(f"   - {inv_id}: {datos['titulo']}")

# Test 3: Completar una investigación
print("\n3. Completar investigación 'comida_2'...")
exito, msg = logica.completar_investigacion("comida_2")
print(f"   Resultado: {msg}")
print(f"   Edificios desbloqueados: {logica.edificios_desbloqueados}")

# Test 4: Verificar que se marcó como completada
print("\n4. Verificar estado de investigaciones...")
print(f"   Investigaciones completadas: {logica.investigaciones_completadas}")

# Test 5: Verificar que NO se puede completar de nuevo
print("\n5. Intentar completar 'comida_2' de nuevo...")
exito, msg = logica.completar_investigacion("comida_2")
print(f"   Resultado: {msg}")

# Test 6: Completar todas nivel 2 y verificar subida
print("\n6. Completar todas investigaciones nivel 2...")
logica.completar_investigacion("agua_2")
logica.completar_investigacion("energia_2")
print(f"   Nivel de ciudad actual: {logica.nivel_tecnologico}")
print(f"   ÉXITO: La ciudad subió a nivel {logica.nivel_tecnologico}")

# Test 7: Verificar que nivel 3 está disponible
print("\n7. Verificar investigaciones disponibles (Nivel 2)...")
disponibles = logica.obtener_investigaciones_disponibles()
print(f"   Total disponibles: {len(disponibles)}")
for inv_id, datos in disponibles.items():
    print(f"   - {inv_id}: {datos['titulo']}")

print("\n" + "=" * 60)
print("TESTS COMPLETADOS EXITOSAMENTE")
print("=" * 60)
