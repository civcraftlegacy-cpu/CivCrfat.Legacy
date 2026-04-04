# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

#!/usr/bin/env python3
"""Test de guardado y cargado de investigaciones"""

import sys
import json
import os
sys.path.insert(0, '.')

from configuracion import *
from logica_ciudad import LogicaCiudad

class MockJuego:
    def __init__(self):
        self.ruta_partida = "test_investigaciones_save.json"
        self.mapa_datos = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]

# Test 1: Crear partida, hacer investigaciones y guardar
print("=" * 60)
print("TEST: GUARDAR Y CARGAR INVESTIGACIONES")
print("=" * 60)

print("\n1. Crear y modificar partida original...")
juego1 = MockJuego()
logica1 = LogicaCiudad(juego1, "Test Save Partida")

# Hacer algunas investigaciones
logica1.completar_investigacion("comida_2")
logica1.completar_investigacion("agua_2")
logica1.completar_investigacion("energia_2")

print(f"   Nivel actual: {logica1.nivel_tecnologico}")
print(f"   Investigaciones completadas: {logica1.investigaciones_completadas}")

# Guardar dato manualmente para simular guardado
datos_a_guardar = {
    "nombre": "Test Save Partida",
    "dinero": logica1.dinero,
    "año": logica1.año,
    "recursos": logica1.recursos,
    "poblacion": [],
    "edificios": [],
    "capacidad_max_poblacion": logica1.capacidad_max_poblacion,
    "poblacion_inicial": logica1.poblacion_inicial,
    "nivel_tecnologico": logica1.nivel_tecnologico,
    "investigaciones_completadas": logica1.investigaciones_completadas
}

# Guardar a archivo
with open(juego1.ruta_partida, 'w', encoding='utf-8') as f:
    json.dump([datos_a_guardar], f, ensure_ascii=False, indent=2)

print("   ✓ Datos guardados a archivo")

# Test 2: Cargar partida y verificar
print("\n2. Cargar partida desde archivo...")
juego2 = MockJuego()
juego2.ruta_partida = juego1.ruta_partida  # Mismo archivo
logica2 = LogicaCiudad(juego2, "Test Load")

# Cargar datos del archivo
with open(juego2.ruta_partida, 'r', encoding='utf-8') as f:
    datos_guardados = json.load(f)

logica2.cargar_partida(datos_guardados[0])

print(f"   Nivel cargado: {logica2.nivel_tecnologico}")
print(f"   Investigaciones cargadas: {logica2.investigaciones_completadas}")

# Test 3: Verificar consistencia
print("\n3. Verificar que los datos se cargaron correctamente...")
assert logica2.nivel_tecnologico == logica1.nivel_tecnologico, "Nivel no coincide"
assert logica2.investigaciones_completadas == logica1.investigaciones_completadas, "Investigaciones no coinciden"
print("   ✓ Todos los datos coinciden")

# Test 4: Verificar que se pueden completar nuevas investigaciones
print("\n4. Completar nivel 3 en la partida cargada...")
logica2.completar_investigacion("comida_3")
logica2.completar_investigacion("agua_3")
logica2.completar_investigacion("energia_3")
print(f"   Nivel final: {logica2.nivel_tecnologico}")
assert logica2.nivel_tecnologico == 3, "La ciudad no subió a nivel 3"
print("   ✓ La ciudad subió correctamente a nivel 3")

# Limpiar archivo de test
if os.path.exists(juego1.ruta_partida):
    os.remove(juego1.ruta_partida)

print("\n" + "=" * 60)
print("✓ TODOS LOS TESTS DE GUARDADO/CARGADO PASARON")
print("=" * 60)
