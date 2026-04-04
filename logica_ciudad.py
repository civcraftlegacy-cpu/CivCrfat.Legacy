# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import pygame
import random
import os
from configuracion import *
from entidades import Ciudadano, Edificio
import json

class LogicaCiudad:
    def __init__(self, juego_referencia, nombre_partida_inicial="Nueva Partida"):
        self.juego = juego_referencia
        self.nombre_partida_actual = nombre_partida_inicial 
        
        # --- 1. DECLARACIÓN DE VARIABLES (EL "ESCUDO") ---
        # Definimos TODO lo que el código pueda preguntar después
        self.game_over = False
        self.dinero = 100000
        self.poblacion = []
        self.edificios = []
        self.noticias = []
        self.año = 0
        self.rango_actual = "Aldea"
        self.años_en_deuda = 0
        self.nivel_tecnologico = 1

        self.recursos = {"comida": 0, "agua": 0, "electricidad": 0}
        self.max_comida = 10000
        self.max_agua = 10000
        self.max_energia = 10000

        self.total_mantenimiento_anual = 0
        self.investigando_id = None
        self.tiempo_investigacion = 0
        self.tiempo_total_req = 300
        self.investigaciones_completadas = []
        self.mostrar_popup_evento = False
        self.evento_actual = None

        # IMPORTANTE: crear esto antes de cualquier lógica que lo use
        self.poblacion_inicial = 100
        self.capacidad_max_poblacion = 100


        # --- 2. LÓGICA DE INICIALIZACIÓN ---
        
        # Primero calculamos los límites reales (esto sobreescribirá los 10000 de arriba)
        self.aplicar_limites_dinamicos() 

        # Ahora sí, agregamos los ciudadanos iniciales   
        for i in range(100):
            self.agregar_ciudadano_nacimiento()

        # Añadimos viviendas iniciales invisibles que no consumen recursos,
        # para que la partida empiece con capacidad para 100 ciudadanos.
        for _ in range(20):
            casa_inicial = Edificio({
                'nombre': 'Casa',
                'costo': 0,
                'mantenimiento': 0,
                'comida': 0,
                'agua': 0,
                'elec': 0,
                'dinero': 0,
                'capacidad': 5,
                'felic': 0,
                'salud': 0,
                'color': VERDE
            }, -1000, -1000)
            self.edificios.append(casa_inicial)

        self.asignar_vivienda_y_empleo()

        cant_personas = len(self.poblacion)
        self.poblacion_inicial = cant_personas
        self.capacidad_max_poblacion = cant_personas


        # Ajustamos los recursos iniciales según la gente que entró
        self.recursos["comida"] = cant_personas * CONSUMO_COMIDA_HAB * 10
        self.recursos["agua"] = cant_personas * CONSUMO_AGUA_HAB * 10
        self.recursos["electricidad"] = cant_personas * CONSUMO_ELEC_HAB * 10 

        self.aplicar_limites_dinamicos()

        # --- 5. INVESTIGACIÓN Y EVENTOS ---
        self.investigando_id = None    
        self.tiempo_investigacion = 0  
        self.tiempo_total_req = 300    
        self.investigaciones_completadas = []
        
        self.mostrar_popup_evento = False
        self.evento_actual = None
        
        self.eventos_posibles = [
            # --- EVENTOS BUENOS ---
            {
                "titulo": "¡AUGE TURÍSTICO!",
                "mensaje": "Un crucero de lujo ha atracado. ¿Invertir en marketing?",
                "opcion_a": "Campaña VIP (Cuesta 10%)",
                "opcion_b": "Dejar que exploren (Gratis)",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.10, 
                "efecto_a": {"dinero_extra": 0.30, "felicidad": 15},
                "efecto_b": {"dinero_extra": 0.05}
            },
            {
                "titulo": "¡INVERSOR ÁNGEL!",
                "mensaje": "Un magnate quiere abrir una sede. Pide beneficios fiscales.",
                "opcion_a": "Aceptar (Felicidad -10)",
                "opcion_b": "Cobrar impuestos normales",
                "tipo": "bueno",
                "efecto_a": {"dinero_extra": 0.40, "felicidad": -10},
                "efecto_b": {"dinero_extra": 0.15}
            },
            {
                "titulo": "¡COSECHA RÉCORD!",
                "mensaje": "El clima ha sido perfecto. Los graneros están llenos.",
                "opcion_a": "Exportar (Ganas 15% Dinero)",
                "opcion_b": "Repartir (Felicidad +30)",
                "tipo": "bueno",
                "efecto_a": {"dinero_extra": 0.15, "comida": -200},
                "efecto_b": {"comida": 800, "felicidad": 30}
            },
            {
                "titulo": "¡DÍA DEL ORGULLO LOCAL!",
                "mensaje": "La gente quiere un festival en la plaza central.",
                "opcion_a": "Financiar (Cuesta 5%)",
                "opcion_b": "Denegar permiso",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.05,
                "efecto_a": {"felicidad": 40},
                "efecto_b": {"felicidad": -15}
            },
            {
                "titulo": "¡HALLAZGO PETROLÍFERO!",
                "mensaje": "Se ha encontrado un pequeño pozo en las afueras.",
                "opcion_a": "Explotar (Dinero +25%)",
                "opcion_b": "Preservar (Felicidad +10)",
                "tipo": "bueno",
                "efecto_a": {"dinero_extra": 0.25, "felicidad": -15},
                "efecto_b": {"felicidad": 10}
            },
            {
                "titulo": "¡BECA TECNOLÓGICA!",
                "mensaje": "Una universidad ofrece mejorar tu red eléctrica gratis.",
                "opcion_a": "Aceptar mejora",
                "opcion_b": "Rechazar (Desconfianza)",
                "tipo": "bueno",
                "efecto_a": {"energia": 300, "felicidad": 5},
                "efecto_b": {"felicidad": -5}
            },
            {
                "titulo": "¡MARATÓN DE SALUD!",
                "mensaje": "La OMS ofrece vacunas subvencionadas.",
                "opcion_a": "Comprar lote (Cuesta 8%)",
                "opcion_b": "Solo las básicas (Gratis)",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.08,
                "efecto_a": {"salud": 50},
                "efecto_b": {"salud": 10}
            },
            {
                "titulo": "¡SISTEMA DE RECICLAJE!",
                "mensaje": "Una nueva ley podría reducir el consumo de recursos.",
                "opcion_a": "Implementar (Cuesta 12%)",
                "opcion_b": "Ignorar",
                "tipo": "bueno",
                "porcentaje_coste_a": 0.12,
                "efecto_a": {"agua": 200, "energia": 200, "felicidad": 10},
                "efecto_b": {}
            },
            # --- EVENTOS MALOS ---
            {
                "titulo": "¡TERREMOTO!",
                "mensaje": "Un sismo ha sacudido la ciudad. Los daños son masivos.",
                "opcion_a": "Plan de Reconstrucción (Cuesta 30%)",
                "opcion_b": "Dejar escombros (Caos total)",
                "tipo": "malo",
                "porcentaje_coste_a": 0.30,
                "efecto_a": {"felicidad": -10},
                "efecto_b": {"felicidad": -50, "salud": -20, "poblacion_extra": -0.10}
            },
            {
                "titulo": "¡PANDEMIA GLOBAL!",
                "mensaje": "Un virus se propaga. Los hospitales no dan abasto.",
                "opcion_a": "Cuarentena Total (Cuesta 20% Dinero)",
                "opcion_b": "Inmunidad de grupo (Mueren ciudadanos)",
                "tipo": "malo",
                "porcentaje_coste_a": 0.20,
                "efecto_a": {"felicidad": -30, "salud": 10},
                "efecto_b": {"salud": -40, "poblacion_extra": -0.20, "felicidad": -10}
            }
        ]

        # --- 5. TIENDA E INVESTIGACIÓN ---
        self.edificios_desbloqueados = [
            "Casa", "Granja", "Planta Agua", "Central Elec.", 
            "Almacen de Comida", "Almacen de Agua", "Almacen de Energia"
        ]

        self.datos_investigacion = {
            "comida_2": {"nivel": 2, "titulo": "Comida Nivel 2", "coste_dinero": 2500, "pob_req": 200, "edificios_desbloquea": ["Granja Ind.", "Silo Gigante"], "color": (100, 255, 100)},
            "agua_2": {"nivel": 2, "titulo": "Agua Nivel 2", "coste_dinero": 3000, "pob_req": 250, "edificios_desbloquea": ["Depuradora"], "color": (100, 100, 255)},
            "energia_2": {"nivel": 2, "titulo": "Energía Nivel 2", "coste_dinero": 4000, "pob_req": 300, "edificios_desbloquea": ["Central Térmica"], "color": (255, 255, 100)},
            "alojamiento_2": {"nivel": 2, "titulo": "Alojamiento Nivel 2", "coste_dinero": 200, "pob_req": 150, "edificios_desbloquea": ["Bloque Pisos"], "color": (255, 200, 100)},
            "comida_3": {"nivel": 3, "titulo": "Comida Nivel 3", "coste_dinero": 5000, "pob_req": 500, "edificios_desbloquea": ["Sintetizador Comida"], "color": (150, 255, 150)},
            "agua_3": {"nivel": 3, "titulo": "Agua Nivel 3", "coste_dinero": 6000, "pob_req": 550, "edificios_desbloquea": ["Extractor Atmosférico"], "color": (150, 150, 255)},
            "energia_3": {"nivel": 3, "titulo": "Energía Nivel 3", "coste_dinero": 8000, "pob_req": 600, "edificios_desbloquea": ["Central Nuclear"], "color": (255, 255, 150)}
        }  

    def limite_negativo_recurso(self, recurso):
        """Retorna el límite negativo dinámico para un recurso dado."""
        limites_max = {
            "comida": self.max_comida,
            "agua": self.max_agua,
            "electricidad": self.max_energia
        }
        maximo = limites_max.get(recurso, 0)
        return -(maximo // 2)

    def completar_investigacion(self, id_investigacion):
        """Marca una investigación como completada y desbloquea sus edificios."""
        if id_investigacion not in self.datos_investigacion:
            return False, "Investigación no válida"
        
        if id_investigacion in self.investigaciones_completadas:
            return False, "Ya está completada"
        
        # Marcar como completada
        self.investigaciones_completadas.append(id_investigacion)
        
        # Desbloquear edificios
        datos_inv = self.datos_investigacion[id_investigacion]
        for edificio in datos_inv.get("edificios_desbloquea", []):
            if edificio not in self.edificios_desbloqueados:
                self.edificios_desbloqueados.append(edificio)
        
        # Noticia
        titulo = datos_inv["titulo"]
        self.noticias.append({
            "txt": f"¡Investigación completada: {titulo}!",
            "tipo": "LOGRO"
        })
        
        # Verificar si completa todas nivel 2 para subir a nivel 3
        self._verificar_subida_nivel()
        
        return True, f"Investigación completada: {titulo}"
    
    def _verificar_subida_nivel(self):
        """Verifica si todas las investigaciones del nivel actual están completas."""
        if self.nivel_tecnologico == 1:
            # Verificar si todas las nivel 2 están completadas
            nivel_2_reqs = ["comida_2", "agua_2", "energia_2", "alojamiento_2"]
            if all(inv_id in self.investigaciones_completadas for inv_id in nivel_2_reqs):
                self.nivel_tecnologico = 2
                self.noticias.append({
                    "txt": "¡Tu ciudad ha avanzado a NIVEL 2!",
                    "tipo": "LOGRO"
                })
        elif self.nivel_tecnologico == 2:
            # Verificar si todas las nivel 3 están completadas
            nivel_3_reqs = ["comida_3", "agua_3", "energia_3"]
            if all(inv_id in self.investigaciones_completadas for inv_id in nivel_3_reqs):
                self.nivel_tecnologico = 3
                self.noticias.append({
                    "txt": "¡Tu ciudad ha avanzado a NIVEL 3! ¡Máximo tecnológico!",
                    "tipo": "LOGRO"
                })
    
    def obtener_investigaciones_disponibles(self):
        """Devuelve investigaciones disponibles según nivel actual."""
        disponibles = {}
        
        # Mostrar nivel 2 si estamos en nivel 1
        # Mostrar nivel 3 si estamos en nivel 2 o superior
        for inv_id, datos in self.datos_investigacion.items():
            # Si ya está completada, no la mostramos
            if inv_id in self.investigaciones_completadas:
                continue
            
            # Si es nivel 2 y estamos en nivel 1+, mostrar
            if datos["nivel"] == 2 and self.nivel_tecnologico >= 1:
                disponibles[inv_id] = datos
            # Si es nivel 3 y estamos en nivel 2+, mostrar
            elif datos["nivel"] == 3 and self.nivel_tecnologico >= 2:
                disponibles[inv_id] = datos
        
        return disponibles
    
    def agregar_ciudadano(self):
        """Añade un ciudadano al pool sin disparar la lógica anual completa."""
        nuevo = Ciudadano()
        self.poblacion.append(nuevo)
        return nuevo

    def agregar_ciudadano_nacimiento(self):
        """Alias para usar al inicio del juego desde __init__."""
        return self.agregar_ciudadano()

    # Nota: esta definición inicial de avanzar_año se eliminó porque existe una segunda versión activa más abajo.

    def actualizar_recursos_globales(self):
        limites_max = {
            "comida": self.max_comida,
            "agua": self.max_agua,
            "electricidad": self.max_energia
        }

        for res in self.recursos:
            # Máximo permitido
            if self.recursos[res] > limites_max[res]:
                self.recursos[res] = limites_max[res]
            # Mínimo permitido: la mitad negativa del límite positivo
            else:
                limite_negativo = -(limites_max[res] // 2)
                if self.recursos[res] < limite_negativo:
                    self.recursos[res] = limite_negativo
                if self.año % 2 == 0:
                    self.noticias.append({"txt": f"¡ESCASEZ CRÍTICA DE {res.upper()}!", "tipo": "CRITICO"})

    def es_posicion_valida(self, x, y, ancho_edf=3, alto_edf=3):
        # 1. Verificar que no se salga del mapa
        if x + ancho_edf > COLUMNAS or y + alto_edf > FILAS:
            return False
        
        # 2. Revisar cada celda del área que ocupará el edificio
        for f in range(y, y + alto_edf):
            for c in range(x, x + ancho_edf):
                # Si la celda no es 0 (Pasto), entonces hay algo (Carretera o HUD)
                if self.juego.mapa_datos[f][c] != 0:
                    return False
                    
        # 3. Verificar si ya hay otro edificio ahí (usando tu lista de edificios)
        for edf in self.edificios:
            # Simplificado: si las coordenadas x,y coinciden o se solapan
            if abs(edf.x - x) < ancho_edf and abs(edf.y - y) < alto_edf:
                return False
                
        return True

    def actualizar_consumos_totales(self):
        # Reiniciamos los totales a 0 para volver a sumar
        self.total_comida_anual = 0
        self.total_agua_anual = 0
        self.total_luz_anual = 0
        self.total_mantenimiento_anual = 0

        # Sumamos lo que gasta cada edificio que hay en la ciudad
        for edf in self.edificios:
            self.total_comida_anual += edf.comida
            self.total_agua_anual += edf.agua
            self.total_luz_anual += edf.elec
            self.total_mantenimiento_anual += edf.mantenimiento

    def asignar_vivienda_y_empleo(self):
        """Asigna vivienda respetando capacidades"""
        for hab in self.poblacion:
            if not hab.tiene_casa:
                # Prioridad: Casas primero
                for e in self.edificios:
                    if e.nombre == "Casa" and e.hay_espacio_vivienda():
                        e.habitantes.append(hab)
                        hab.tiene_casa = True
                        break
                
                # Si no hay Casa, intenta Bloque Pisos
                if not hab.tiene_casa:
                    for e in self.edificios:
                        if e.nombre == "Bloque Pisos" and e.hay_espacio_vivienda():
                            e.habitantes.append(hab)
                            hab.tiene_casa = True
                            break

    def aplicar_efectos_edificios(self):
        """Aplica felicidad y salud de los edificios a los ciudadanos que viven en ellos"""
        for hab in self.poblacion:
            bonus_felicidad = 0
            bonus_salud = 0
            
            for e in self.edificios:
                if hab in e.habitantes:
                    bonus_felicidad += e.felic_impacto 
                    bonus_salud += e.salud_impacto
            
            # Aplicar los bonificadores
            hab.felicidad += bonus_felicidad
            hab.salud += bonus_salud
            
            # Limitar a 100 máximo
            hab.felicidad = min(100, hab.felicidad)
            hab.salud = min(100, hab.salud)

    def actualizar_capacidad_max_poblacion(self):
        """Calcula la capacidad máxima de población basada en viviendas"""
        casas = sum(1 for e in self.edificios if e.nombre == "Casa")
        bloques = sum(1 for e in self.edificios if e.nombre == "Bloque Pisos")
        self.capacidad_max_poblacion = self.poblacion_inicial + (casas * 5) + (bloques * 20)

    def gestionar_inmigracion(self):
        """Gestiona inmigración: Crecimiento acelerado si hay espacio y recursos - RESPETA LÍMITE"""
        pob_actual = len(self.poblacion)
        
        # Permitir crecimiento acelerado: máximo 10% anual si hay espacio y recursos suficientes
        max_nuevos = max(3, int(pob_actual * 0.10))
        
        # Solo permite inmigración si hay espacio en casas/bloques
        if pob_actual < self.capacidad_max_poblacion and self.recursos["comida"] > 500:
            # Calcular cuántos cabemos sin exceder el límite
            espacio_disponible = self.capacidad_max_poblacion - pob_actual
            # Limitar a máximo 15 personas por año para evitar explosión demográfica
            nuevos = min(random.randint(2, min(max_nuevos, 15)), espacio_disponible)  # Nunca excede capacidad
            
            if nuevos > 0:
                for _ in range(nuevos):
                    self.agregar_ciudadano()
                self.noticias.append({"txt": f"Nuevos colonos: +{nuevos}", "tipo": "AVISO"})

    def procesar_noticias(self, lista_notas):
        prioridad = {"CRITICO": 0, "MUERTE": 1, "AVISO": 2}
        lista_notas.sort(key=lambda x: prioridad.get(x["tipo"], 3))
        for n in lista_notas:
            if n not in self.noticias:
                self.noticias.append(n)
        self.noticias = self.noticias[:10]

    def verificar_rango_ciudad(self):
        pob_actual = len(self.poblacion)
        for nivel in reversed(NIVELES_CIUDAD):
            if pob_actual >= nivel["pob_min"]:
                if self.rango_actual != nivel["rango"]:
                    self.rango_actual = nivel["rango"]
                    self.noticias.append({"txt": f"Ciudad nivel: {self.rango_actual}", "tipo": "AVISO"})
                    if hasattr(self.juego, 'reproducir_sonido'):
                        self.juego.reproducir_sonido("nivel")
                break

    def comprar_edificio(self, tipo_data, x, y):
        # --- 1. Definir el tamaño del solar ---
        ancho_solar, alto_solar = 3, 3 

        # --- 2. Verificar límites ---
        if x + ancho_solar > COLUMNAS or y + alto_solar > FILAS:
            return False

        # --- 3. Revisar si hay carretera (tipo != 0) ---
        for f in range(y, y + alto_solar):
            for c in range(x, x + ancho_solar):
                if self.juego.mapa_datos[f][c] != 0:
                    print("Espacio ocupado por carretera")
                    return False

        # --- 4. Revisar si choca con otros edificios ---
        for edf in self.edificios:
            if abs(edf.x - x) < ancho_solar and abs(edf.y - y) < alto_solar:
                print("Espacio ocupado por otro edificio")
                return False

        # --- 5. COMPRA ---
        if self.dinero >= tipo_data[1]:
            data_final = {
                'nombre': tipo_data[0],
                'costo': tipo_data[1],
                'mantenimiento': tipo_data[2],
                'comida': tipo_data[3],
                'agua': tipo_data[4],
                'elec': tipo_data[5],
                'dinero': tipo_data[6],  # ✓ CORRECCIÓN: usar dinero del array
                'capacidad': 20,
                'felic': tipo_data[7],   # ✓ CORRECCIÓN: era tipo_data[6]
                'salud': 0,              # ✓ Por defecto 0
                'color': random.choice([VERDE, AZUL, CIAN])
            }
            
            # Solo UNA VEZ esto:
            nuevo = Edificio(data_final, x, y)
            self.edificios.append(nuevo)
            self.dinero -= tipo_data[1]
            
            # Actualizamos los totales para que el HUD se entere del nuevo consumo
            self.actualizar_consumos_totales()
            # NUEVO FASE 4: Recalcular capacidad por nueva vivienda
            self.actualizar_capacidad_max_poblacion()
            # ✓ ARREGLO 1: Recalcular límites dinámicos después de comprar almacén
            self.aplicar_limites_dinamicos()
            
            return {"exito": True, "razón": "compra_exitosa"}
        else:
            dinero_faltante = tipo_data[1] - self.dinero
            return {"exito": False, "razón": "dinero_insuficiente", "faltante": dinero_faltante, "nombre": tipo_data[0]}
    
    def vender_edificios(self, nombre_edificio, cantidad):
        """Vende edificios del mismo tipo y devuelve el 50% del costo"""
        # Buscar el edificio en EDIFICACIONES
        edificio_data = None
        for ed in EDIFICACIONES:
            if ed[0] == nombre_edificio:
                edificio_data = ed
                break
        
        if not edificio_data:
            return False
        
        costo_original = edificio_data[1]
        precio_venta = costo_original // 2  # 50%
        dinero_total = precio_venta * cantidad
        
        # Eliminar los edificios del mapa (elimina los primeros 'cantidad' que encuentre)
        eliminados = 0
        for _ in range(cantidad):
            for i, edf in enumerate(self.edificios):
                if edf.nombre == nombre_edificio:
                    self.edificios.pop(i)
                    eliminados += 1
                    break
        
        if eliminados > 0:
            self.dinero += dinero_total
            # NUEVO FASE 4: Recalcular capacidad después de venta
            self.actualizar_capacidad_max_poblacion()
            # Recalcular consumos después de eliminar edificios
            self.actualizar_consumos_totales()
            return True
        
        return False
     
    def aplicar_limites_dinamicos(self):
        """Aplica límites: (Población * Consumo * 20) + (Almacenes * 5000)"""
        n_pob = len(self.poblacion)
        
        # 1. Contar almacenes construidos (incluyendo silos y variantes)
        almacenes_comida = sum(1 for e in self.edificios if e.nombre in ["Almacen de Comida", "Silo Gigante"])
        almacenes_agua = sum(1 for e in self.edificios if e.nombre == "Almacen de Agua")
        almacenes_elec = sum(1 for e in self.edificios if e.nombre == "Almacen de Energia")

        # 2. Calcular Máximos (Base de 20 años + Almacenes)
        # ✓ ARREGLO 1: Cambiar de 4000 a 5000 por almacén
        # Comida: (población * 4 * 20) + (N almacenes * 5000)
        self.max_comida = (n_pob * CONSUMO_COMIDA_HAB * 20) + (almacenes_comida * 5000)
        
        # Agua: (población * 5 * 20) + (N almacenes * 5000)
        self.max_agua = (n_pob * CONSUMO_AGUA_HAB * 20) + (almacenes_agua * 5000)
        
        # Energía: (población * 6 * 20) + (N almacenes * 5000)
        self.max_energia = (n_pob * CONSUMO_ELEC_HAB * 20) + (almacenes_elec * 5000)

        # 3. Aplicar el recorte para que no se pase del límite
        limite_neg_comida = -(self.max_comida // 2)
        limite_neg_agua = -(self.max_agua // 2)
        limite_neg_energia = -(self.max_energia // 2)

        self.recursos["comida"] = max(limite_neg_comida, min(self.recursos["comida"], self.max_comida))
        self.recursos["agua"] = max(limite_neg_agua, min(self.recursos["agua"], self.max_agua))
        self.recursos["electricidad"] = max(limite_neg_energia, min(self.recursos["electricidad"], self.max_energia))

    def realizar_intercambio(self, recurso_dar, recurso_recibir, cantidad):
        """Realiza intercambio de recursos con comisión del 10%"""
        if recurso_dar == recurso_recibir:
            return False, "No puedes intercambiar un recurso por sí mismo"
        
        # Mapeo de claves de recursos
        recurso_dar_key = "dinero" if recurso_dar == "dinero" else recurso_dar
        recurso_recibir_key = "dinero" if recurso_recibir == "dinero" else recurso_recibir
        
        # Obtener cantidad actual del recurso a dar
        if recurso_dar == "dinero":
            cantidad_actual = self.dinero
        else:
            cantidad_actual = self.recursos.get(recurso_dar, 0)
        
        # Verificar que hay suficiente
        if cantidad_actual < cantidad:
            return False, f"No tienes suficiente {recurso_dar} (necesitas {cantidad}, tienes {int(cantidad_actual)})"
        
        # Calcular comisión (10%)
        comision = int(cantidad * 0.10)
        cantidad_neta = cantidad - comision
        
        if cantidad_neta <= 0:
            return False, "La cantidad es muy pequeña después de la comisión"
        
        # Realizar el intercambio
        # Restar lo que damos
        if recurso_dar == "dinero":
            self.dinero -= cantidad
        else:
            self.recursos[recurso_dar] -= cantidad
        
        # Sumar lo que recibimos (sin comisión)
        if recurso_recibir == "dinero":
            self.dinero += cantidad_neta
        else:
            self.recursos[recurso_recibir] += cantidad_neta
        
        # Crear noticia
        comision_txt = f" (-{comision} comisión)"
        msg = f"Intercambio: -{cantidad} {recurso_dar} +{cantidad_neta} {recurso_recibir}{comision_txt}"
        
        return True, msg

    def aplicar_efectos_evento(self, efectos, coste_dinero=0):
        # 1. Restar el coste de la opción elegida
        self.dinero -= coste_dinero

        for recurso, valor in efectos.items():
            # Usamos self.recursos porque así lo tienes en avanzar_año
            if recurso in self.recursos:
                self.recursos[recurso] += valor
                
            elif recurso == "felicidad":
                # Como la felicidad es individual, se la aplicamos a todos
                for hab in self.poblacion:
                    hab.felicidad = max(0, min(100, hab.felicidad + valor))
                    
            elif recurso == "habitantes":
                if valor > 0:
                    # Añadir nuevos ciudadanos (tendrías que llamar a tu lógica de crear habitante)
                    for _ in range(valor):
                        self.gestionar_inmigracion(forzar=True) 
                elif valor < 0:
                    # Quitar gente (trágico, pero necesario para el juego)
                    for _ in range(abs(valor)):
                        if self.poblacion:
                            hab_muerto = self.poblacion.pop()
                            # Limpiar sus puestos de trabajo/casa
                            for e in self.edificios:
                                if hab_muerto in e.habitantes: e.habitantes.remove(hab_muerto)
                                if hab_muerto in e.trabajadores: e.trabajadores.remove(hab_muerto)

        # 2. Cerrar el popup después de aplicar
        self.mostrar_popup_evento = False
        self.evento_actual = None
        
        self.noticias.append({"txt": "Se han aplicado las consecuencias del evento", "tipo": "AVISO"})

    def guardar_partida(self):
        """Guarda la partida actual actualizando su nombre registrado"""
        # Usar el nombre de la partida guardado en LogicaCiudad
        nombre_guardado = self.nombre_partida_actual if self.nombre_partida_actual else f"Año {self.año}"
        
        datos_partida = {
            "nombre": nombre_guardado,
            "dinero": self.dinero,
            "año": self.año,
            "recursos": self.recursos,
            "poblacion": [
                {
                    "nombre": c.nombre, 
                    "edad": c.edad, 
                    "salud": c.salud, 
                    "felicidad": c.felicidad,
                    "tiene_casa": c.tiene_casa,
                    "tiene_empleo": c.tiene_empleo,
                    "rango_etario": c.rango_etario
                }
                for c in self.poblacion
            ],
            "edificios": [
                {
                    "id_edificio": e.id_edificio,
                    "nombre": e.nombre, 
                    "x": e.x, 
                    "y": e.y,
                    "capacidad_max_vivienda": e.capacidad_max_vivienda
                }
                for e in self.edificios
            ],
            "capacidad_max_poblacion": self.capacidad_max_poblacion,
            "poblacion_inicial": self.poblacion_inicial,
            "nivel_tecnologico": self.nivel_tecnologico,
            "investigaciones_completadas": self.investigaciones_completadas
        }

        ruta_partidas = self.juego.ruta_partida
        
        try:
            # Cargar partidas existentes
            partidas_guardadas = []
            if os.path.exists(ruta_partidas):
                try:
                    with open(ruta_partidas, "r", encoding="utf-8") as f:
                        datos_guardados = json.load(f)
                        # Si es un array, usarlo; si es un objeto, convertir a array
                        if isinstance(datos_guardados, list):
                            partidas_guardadas = datos_guardados
                        else:
                            partidas_guardadas = [datos_guardados]
                except:
                    partidas_guardadas = []
            
            # Buscar y actualizar partida con nombre actual
            partida_encontrada = False
            for i, p in enumerate(partidas_guardadas):
                if p.get("nombre") == nombre_guardado:
                    partidas_guardadas[i] = datos_partida
                    partida_encontrada = True
                    break
            
            if not partida_encontrada:
                partidas_guardadas.append(datos_partida)
            
            # Guardar todas las partidas como array
            with open(ruta_partidas, "w", encoding="utf-8") as f:
                json.dump(partidas_guardadas, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Error guardando partida: {e}")

    def guardar_partida_con_nombre(self, nombre_partida=""):

        """Guarda la partida con un nombre específico en un sistema de múltiples partidas"""
        datos_partida = {
            "nombre": nombre_partida,
            "dinero": self.dinero,
            "año": self.año,
            "recursos": self.recursos,
            "poblacion": [
                {
                    "nombre": c.nombre, 
                    "edad": c.edad, 
                    "salud": c.salud, 
                    "felicidad": c.felicidad,
                    "tiene_casa": c.tiene_casa,
                    "tiene_empleo": c.tiene_empleo,
                    "rango_etario": c.rango_etario
                }
                for c in self.poblacion
            ],
            "edificios": [
                {
                    "id_edificio": e.id_edificio,
                    "nombre": e.nombre, 
                    "x": e.x, 
                    "y": e.y,
                    "capacidad_max_vivienda": e.capacidad_max_vivienda
                }
                for e in self.edificios
            ],
            "capacidad_max_poblacion": self.capacidad_max_poblacion,
            "poblacion_inicial": self.poblacion_inicial,
            "nivel_tecnologico": self.nivel_tecnologico,
            "investigaciones_completadas": self.investigaciones_completadas
        }

        # Guardar en archivo de partidas
        ruta_partidas = self.juego.ruta_partida
        
        try:
            # Cargar partidas existentes
            partidas_guardadas = []
            if os.path.exists(ruta_partidas):
                with open(ruta_partidas, "r", encoding="utf-8") as f:
                    partidas_guardadas = json.load(f)
            
            # Buscar si ya existe una partida con este nombre  y actualizar o agregar
            partida_encontrada = False
            for i, p in enumerate(partidas_guardadas):
                if p.get("nombre") == nombre_partida:
                    partidas_guardadas[i] = datos_partida
                    partida_encontrada = True
                    break
            
            if not partida_encontrada:
                partidas_guardadas.append(datos_partida)
            
            # Guardar todas las partidas
            with open(ruta_partidas, "w", encoding="utf-8") as f:
                json.dump(partidas_guardadas, f, ensure_ascii=False, indent=4)
            
            # Actualizar nombre de partida actual después de guardar
            self.nombre_partida_actual = nombre_partida
            
        except Exception as e:
            print(f"Error guardando partida con nombre: {e}")

    def cargar_partida(self, partida_dict=None):
        """Carga una partida. Si partida_dict es None, la crea nueva"""
        if partida_dict is None:
            # Nueva partida - ya está inicializada en __init__
            self.aplicar_limites_dinamicos()
            return True
        
        # Cargar partida existente
        try:
            self.dinero = partida_dict.get("dinero", 100000)
            self.año = partida_dict.get("año", 0)
            self.nombre_partida_actual = partida_dict.get("nombre", f"Año {self.año}")  # 🔧 RESTAURAR nombre
            self.recursos = partida_dict.get("recursos", self.recursos)
            self.capacidad_max_poblacion = partida_dict.get("capacidad_max_poblacion", 100)
            self.poblacion_inicial = partida_dict.get("poblacion_inicial", 100)
            
            # 🔧 CARGAR ESTADO DE INVESTIGACIONES Y NIVEL TECNOLÓGICO
            self.nivel_tecnologico = partida_dict.get("nivel_tecnologico", 1)
            self.investigaciones_completadas = partida_dict.get("investigaciones_completadas", [])

            # --- Reconstruir edificios ---
            self.edificios = []
            for d in partida_dict.get("edificios", []):
                tipo = next((e for e in EDIFICACIONES if e[0] == d["nombre"]), None)
                if tipo:
                    data_final = {
                        'nombre': tipo[0], 'costo': tipo[1], 'mantenimiento': tipo[2],
                        'comida': tipo[3], 'agua': tipo[4], 'elec': tipo[5],
                        'dinero': tipo[6], 'capacidad': 20,  # ✓ CORRECCIÓN
                        'felic': tipo[7], 'salud': 0, 'color': VERDE  # ✓ CORRECCIÓN
                    }
                    nuevo = Edificio(data_final, d["x"], d["y"])
                    # 🔧 RESTAURAR UUID y capacidad_max_vivienda
                    nuevo.id_edificio = d.get("id_edificio", nuevo.id_edificio)
                    nuevo.capacidad_max_vivienda = d.get("capacidad_max_vivienda", nuevo.capacidad_max_vivienda)
                    self.edificios.append(nuevo)

            # --- Reconstruir población con TODAS las propiedades ---
            self.poblacion = []
            for c in partida_dict.get("poblacion", []):
                ciudadano = Ciudadano()
                ciudadano.nombre = c["nombre"]
                ciudadano.edad = c["edad"]
                ciudadano.salud = c["salud"]
                ciudadano.felicidad = c["felicidad"]
                # 🔧 RESTAURAR propiedades del ciudadano
                ciudadano.tiene_casa = c.get("tiene_casa", False)
                ciudadano.tiene_empleo = c.get("tiene_empleo", False)
                ciudadano.rango_etario = c.get("rango_etario", "Niño")
                self.poblacion.append(ciudadano)

            # 🔧 RECALCULAR límites después de cargar TODO
            self.aplicar_limites_dinamicos()

            return True

        except Exception as e:
            print(f"Error cargando partida: {e}")
            return False
        
    def avanzar_año(self):
        if len(self.poblacion) <= 0:
            self.game_over = True
        
        self.año += 1
        pob_inicial = len(self.poblacion) 
        self.noticias = []

        self.actualizar_consumos_totales()

        n_pob = len(self.poblacion)

        # 10% de probabilidad anual de que se active un evento aleatorio
        if random.random() < 0.10:
            self.evento_actual = random.choice(self.eventos_posibles)
            self.mostrar_popup_evento = True
            self.noticias.append({
                "txt": f"Evento: {self.evento_actual.get('titulo', 'Evento Desconocido')}",
                "tipo": "EVENTO"
            })
            if hasattr(self.juego, 'reproducir_sonido'):
                self.juego.reproducir_sonido("evento")

        dinero_por_persona = INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100)
        impuestos_totales = n_pob * dinero_por_persona
        
        ingresos_edif = sum(getattr(e, 'produccion_dinero', 0) for e in self.edificios)
        
        balance_anual = (impuestos_totales + ingresos_edif) - self.total_mantenimiento_anual
        self.dinero += balance_anual

        if self.dinero < 0:
            self.años_en_deuda += 1
            self.noticias.append({"txt": f"¡DEUDA! Año {self.años_en_deuda}/3", "tipo": "CRITICO"})
            for hab in self.poblacion: hab.felicidad -= 10
            if self.años_en_deuda >= 3:
                self.game_over = True
                return
        else:
            self.años_en_deuda = 0

        if self.dinero > 50000 and self.recursos["comida"] > 4000:
            for hab in self.poblacion:
                hab.felicidad += 2  # Un pequeño empujón positivo

        # RECURSOS
        self.actualizar_consumos_totales() 
        
        self.recursos["comida"] += self.total_comida_anual
        self.recursos["agua"] += self.total_agua_anual
        self.recursos["electricidad"] += self.total_luz_anual

        self.actualizar_recursos_globales()
        self.aplicar_limites_dinamicos()
        
        # POBLACIÓN
        self.asignar_vivienda_y_empleo()
        self.aplicar_efectos_edificios()
        
        # 🔥 CONSUMO GLOBAL CON LÍMITE
        consumo_comida = len(self.poblacion) * CONSUMO_COMIDA_HAB
        consumo_agua = len(self.poblacion) * CONSUMO_AGUA_HAB
        consumo_electricidad = len(self.poblacion) * CONSUMO_ELEC_HAB

        # Restar consumo global de recursos
        self.recursos["comida"] -= consumo_comida
        self.recursos["agua"] -= consumo_agua
        self.recursos["electricidad"] -= consumo_electricidad
        
        energia_disponible = max(0, self.recursos["electricidad"] + consumo_electricidad)

        # Clampear según el límite dinámico negativo por recurso
        self.recursos["comida"] = max(self.recursos["comida"], -(self.max_comida // 2))
        self.recursos["agua"] = max(self.recursos["agua"], -(self.max_agua // 2))
        self.recursos["electricidad"] = max(self.recursos["electricidad"], -(self.max_energia // 2))
        sin_luz = max(0, len(self.poblacion) - (energia_disponible // CONSUMO_ELEC_HAB))

        noticias_sucias = []
        for hab in self.poblacion[:]:
            # 🔧 CAMBIO: ya NO toca recursos
            notas = hab.actualizar_necesidades(self.recursos)
            noticias_sucias.extend(notas)
            
            if sin_luz > 0:
                hab.felicidad -= 5
                hab.salud -= DANO_SIN_LUZ_SALUD
                sin_luz -= 1

            if self.recursos["comida"] < 0: hab.salud -= 5
            if self.recursos["agua"] < 0: hab.salud -= 5

            hab.salud = max(0, min(100, hab.salud))
            hab.felicidad = max(0, min(100, hab.felicidad))

            if not hab.esta_vivo or hab.salud <= 0 or hab.edad >= EDAD_MAXIMA:
                for e in self.edificios:
                    if hab in e.habitantes: e.habitantes.remove(hab)
                    if hab in e.trabajadores: e.trabajadores.remove(hab)
                if hab in self.poblacion: self.poblacion.remove(hab)

        pob_final = len(self.poblacion)
        muertos = pob_inicial - pob_final
        if muertos > 0:
            self.noticias.append({"txt": f"Han fallecido {muertos} ciudadanos", "tipo": "MUERTE"})

        self.procesar_noticias(noticias_sucias)
        self.gestionar_inmigracion()
        self.verificar_rango_ciudad()
        self.guardar_partida()
