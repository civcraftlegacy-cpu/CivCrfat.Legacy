# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

# 🎯 RESUMEN DE CAMBIOS - SISTEMA DE INVESTIGACIONES

## ✅ Cambios en `logica_ciudad.py`:

### 1. **Redefinición de `datos_investigacion`** (Líneas ~40-98)
   - Ahora incluye 6 investigaciones: 3 de Nivel 2 y 3 de Nivel 3
   - Cada investigación tiene:
     - `nivel`: 2 o 3
     - `titulo`: Nombre descriptivo
     - `coste_dinero`: Costo en dinero
     - `pob_req`: Población requerida
     - `edificios_desbloquea`: Lista de edificios que desbloquea
     - `color`: Color para la UI

### 2. **Nuevo método `completar_investigacion()`** (Líneas ~101-127)
   - Marca una investigación como completada
   - Desbloquea automáticamente los edificios asociados
   - Genera noticia de éxito
   - Verifica si se debe subir de nivel

### 3. **Nuevo método `_verificar_subida_nivel()`** (Líneas ~129-154)
   - Verifica si todas las investigaciones del nivel actual están completas
   - Si nivel 2 está completo → sube a nivel 2
   - Si nivel 3 está completo → sube a nivel 3

### 4. **Nuevo método `obtener_investigaciones_disponibles()`** (Líneas ~156-174)
   - Devuelve investigaciones disponibles según el nivel actual
   - Nivel 1 → ve nivel 2
   - Nivel 2+ → ve nivel 3

### 5. **Actualización en `cargar_partida()`** (Líneas ~667-668)
   - Ahora carga `nivel_tecnologico`
   - Ahora carga `investigaciones_completadas`

### 6. **Actualización en `guardar_partida()`** (Líneas ~540-541)
   - Ahora guarda `nivel_tecnologico`
   - Ahora guarda `investigaciones_completadas`

### 7. **Actualización en `guardar_partida_con_nombre()`** (Líneas ~611-612)
   - Ahora guarda `nivel_tecnologico`
   - Ahora guarda `investigaciones_completadas`


## ✅ Cambios en `main.py`:

### 1. **Sincronización de investigaciones** (Línea ~104)
   - Al iniciar, `self.investigaciones_completadas` se sincroniza con `logica.investigaciones_completadas`

### 2. **Actualización de `finalizar_investigacion()`** (Líneas ~1237-1254)
   - Ahora llama a `logica.completar_investigacion()` que desbloquea edificios realmente
   - La noticia se crea en `logica_ciudad`, no en `main.py`

### 3. **Actualización de `procesar_investigacion()`** (Líneas ~1348-1381)
   - Ahora obtiene datos desde `self.logica.datos_investigacion`
   - Manejo de error si investigación no existe

### 4. **Eliminación de `datos_investigacion` local**
   - Ya no hay duplicado de datos en `main.py`
   - Todo se centraliza en `logica_ciudad.py`

### 5. **Actualización de `dibujar_menu_investigacion()`** (Líneas ~1257-1328)
   - Genera dinámicamente los nodos según investigaciones disponibles
   - Muestra nivel 2 cuando estás en nivel 1
   - Muestra nivel 3 cuando estás en nivel 2
   - Actualiza colores según estado (completado, en curso, disponible)

### 6. **Actualización de `dibujar_popup_confirmacion_investigacion()`** (Líneas ~1054-1120)
   - Obtiene datos desde `self.logica.datos_investigacion`
   - Muestra edificios desbloqueados dinámicamente

### 7. **Actualización de manejo de clics** (Líneas ~1545-1548)
   - Usa `self.logica.datos_investigacion` en lugar de `self.datos_investigacion`


## 🎮 FLUJO DE JUEGO FINAL:

1. **Nivel 1 (Inicial)**
   - Investigaciones disponibles: Comida Nivel 2, Agua Nivel 2, Energía Nivel 2
   
2. **Pagando una investigación**
   - Se cobra el dinero
   - Inicia un contador de tiempo (300 frames = ~5-10 segundos)
   - Se muestra barra de progreso

3. **Completada la investigación**
   - Se desbloquean automáticamente los edificios
   - Se marcan como completadas
   - Se guarda en la partida

4. **Completadas todas Nivel 2**
   - La ciudad sube a NIVEL 2
   - Se desbloquean investigaciones NIVEL 3
   - Nivel 3 sustituye a Nivel 2 (mismo espacio, mayor costo)

5. **Completadas todas Nivel 3**
   - La ciudad sube a NIVEL 3 (máximo tecnológico)


## 📊 ESTRUCTURA DE DATOS:

### datos_investigacion
```python
{
    "comida_2": {
        "nivel": 2,
        "titulo": "Comida Nivel 2",
        "coste_dinero": 2500,
        "pob_req": 200,
        "edificios_desbloquea": [...],
        "color": (R, G, B)
    },
    ...
}
```

### Guardado en JSON
```json
{
    "nombre": "Partida",
    "dinero": 100000,
    "año": 5,
    "nivel_tecnologico": 2,
    "investigaciones_completadas": ["comida_2", "agua_2", "energia_2"],
    ...
}
```
