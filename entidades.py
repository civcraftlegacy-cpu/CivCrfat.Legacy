# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import random
import uuid
from configuracion import *

class Ciudadano:
    def __init__(self):
        self.nombre = f"{random.choice(NOMBRES_BASE)} {random.choice(APELLIDOS_BASE)}"
        self.profesion = random.choice(PROFESIONES_BASE)
        self.edad = random.randint(18, 50)
        self.salud = 100
        self.felicidad = 80
        self.esta_vivo = True
        self.tiene_casa = False

        self.rango_etario = "Adulto"


    def definir_rango(self):
        if self.edad < 18:
            self.rango_etario = "Niño"
        elif self.edad < 65:
            self.rango_etario = "Adulto"
        else:
            self.rango_etario = "Anciano"

    def actualizar_necesidades(self, recursos):
        noticias_del_turno = []
        self.definir_rango()

        # 🔧 NOTA: Consumo de comida y agua se hace GLOBALMENTE en logica_ciudad.avanzar_año()
        # No repetir aquí para evitar DOBLE CONSUMO
        
        # Solo checkeamos si hay SUFICIENTES recursos (la resta ya se hizo globalmente)
        if recursos['comida'] < 0:
            self.salud -= DANO_HAMBRE
            noticias_del_turno.append({"txt": f"Hambre: {self.nombre}", "tipo": "CRITICO"})
        
        if recursos['agua'] < 0:
            self.salud -= DANO_SED
            
        if not self.tiene_casa:
            self.felicidad -= DANO_SIN_TECHO_FELIC
            self.salud -= 1

        self.edad += 1
        
        if self.edad > EDAD_MAXIMA or self.salud <= 0:
            self.esta_vivo = False
            noticias_del_turno.append({"txt": f"Fallecimiento: {self.nombre}", "tipo": "MUERTE"})
        
        return noticias_del_turno

class Edificio:
    def __init__(self, tipo_data, pos_x, pos_y):
        self.id_edificio = str(uuid.uuid4())  # NUEVO: ID único para cada edificio
        self.nombre = tipo_data['nombre']
        self.costo = tipo_data['costo']
        self.mantenimiento = tipo_data['mantenimiento']
        self.comida = tipo_data['comida']
        self.agua = tipo_data['agua']
        self.elec = tipo_data['elec']
        self.produccion_dinero = tipo_data['dinero']
        self.capacidad_max = tipo_data['capacidad']
        
        # NUEVO FASE 4: Capacidad específica para vivienda
        self.capacidad_max_vivienda = 0
        if self.nombre == "Casa":
            self.capacidad_max_vivienda = 5
        elif self.nombre == "Bloque Pisos":
            self.capacidad_max_vivienda = 20
        
        self.salud_impacto = tipo_data['salud']
        self.felic_impacto = tipo_data['felic']
        self.color = tipo_data['color']
        self.x = pos_x
        self.y = pos_y
        self.habitantes = []
        self.trabajadores = []
        self.es_residencial = self.capacidad_max_vivienda > 0

    def hay_espacio_vivienda(self):
        return len(self.habitantes) < self.capacidad_max_vivienda

    def hay_puesto_trabajo(self):
        if self.es_residencial or self.nombre == "Parque":
            return False
        return len(self.trabajadores) < 15

    def actualizar_impacto_global(self, ciudad_stats):
        ciudad_stats['salud_total'] += self.salud_impacto
        ciudad_stats['felicidad_total'] += self.felic_impacto
        ciudad_stats['dinero'] += self.produccion_dinero
        ciudad_stats['dinero'] -= self.mantenimiento