# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import pygame
import os
import json
from configuracion import ANCHO, ALTO, BASE_DIR, BLANCO, NEGRO, ROJO, VERDE, ORO, GRIS_CLARO, AMARILLO, CIAN

CARPETA_PARTIDAS = os.path.join(BASE_DIR, "usuarios")

class MenuPartidas:
    def __init__(self, pantalla, usuario_nombre):
        self.pantalla = pantalla
        self.usuario_nombre = usuario_nombre
        self.fuente = pygame.font.SysFont("Arial", 26, bold=True)
        self.fuente_m = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_p = pygame.font.SysFont("Arial", 16)
        self.fuente_peq = pygame.font.SysFont("Arial", 14)
        
        self.seleccion = None  # Guardará la partida seleccionada o "nueva"
        self.hecho = False
        
        # Cargar partidas disponibles
        self.partidas = self.cargar_partidas_usuario()
        self.scroll_y = 0
        self.botones_eliminar = []
        self.partida_a_eliminar = None
        self.confirmando_eliminar = False
        
    def cargar_partidas_usuario(self):
        """Carga todas las partidas del usuario desde archivo JSON"""
        ruta_partidas = os.path.join(CARPETA_PARTIDAS, f"partidas_{self.usuario_nombre}.json")
        partidas = []
        
        if os.path.exists(ruta_partidas):
            try:
                with open(ruta_partidas, "r", encoding="utf-8") as f:
                    datos_guardados = json.load(f)
                    
                    # Manejo de compatibilidad: si es un objeto, convertir a lista
                    if isinstance(datos_guardados, dict):
                        datos_lista = [datos_guardados]
                    else:
                        datos_lista = datos_guardados
                    
                    # Filtrar partidas con 0 habitantes
                    for i, datos in enumerate(datos_lista):
                        poblacion = len(datos.get("poblacion", []))
                        if poblacion > 0:  # Solo mostrar si tienen habitantes
                            partidas.append({
                                "nombre": datos.get("nombre", f"Partida Sin Nombre {i}"),
                                "datos": datos,
                                "index": i,
                                "poblacion": poblacion,
                                "dinero": datos.get("dinero", 0),
                                "año": datos.get("año", 0)
                            })
            except Exception as e:
                print(f"Error cargando partidas: {e}")
        
        return partidas

    def eliminar_partida(self, index):
        """Elimina una partida del archivo JSON"""
        ruta_partidas = os.path.join(CARPETA_PARTIDAS, f"partidas_{self.usuario_nombre}.json")
        
        try:
            if os.path.exists(ruta_partidas):
                with open(ruta_partidas, "r", encoding="utf-8") as f:
                    datos_guardados = json.load(f)
                
                # Manejo de compatibilidad: si es un objeto, convertir a lista
                if isinstance(datos_guardados, dict):
                    datos_lista = [datos_guardados]
                else:
                    datos_lista = datos_guardados
                
                # Eliminar la partida especificada
                if 0 <= index < len(datos_lista):
                    datos_lista.pop(index)
                    
                    # Guardar archivo actualizado
                    with open(ruta_partidas, "w", encoding="utf-8") as f:
                        json.dump(datos_lista, f, ensure_ascii=False, indent=4)
                    
                    # Recargar partidas
                    self.partidas = self.cargar_partidas_usuario()
                    return True
        except Exception as e:
            print(f"Error eliminando partida: {e}")
        
        return False
    
    def dibujar(self):
        self.pantalla.fill((25, 25, 25))
        
        # --- TÍTULO ---
        titulo = self.fuente.render("MIS PARTIDAS", True, ORO)
        self.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))
        
        # --- USUARIO ---
        txt_user = self.fuente_p.render(f"Usuario: {self.usuario_nombre}", True, CIAN)
        self.pantalla.blit(txt_user, (50, 100))
        
        # --- ÁREA DE PARTIDAS ---
        area_y = 150
        area_altura = ALTO - 300
        
        # Fondo del área
        pygame.draw.rect(self.pantalla, (40, 40, 40), (50, area_y, ANCHO - 100, area_altura), border_radius=15)
        pygame.draw.rect(self.pantalla, ORO, (50, area_y, ANCHO - 100, area_altura), 2, border_radius=15)
        
        # --- BOTÓN CREAR NUEVA PARTIDA (solo si hay menos de 5 partidas) ---
        puede_crear = len(self.partidas) < 5
        self.btn_nueva = pygame.Rect(70, area_y + 20, ANCHO - 140, 70)
        color_nueva = (0, 150, 0) if puede_crear else (100, 100, 100)
        pygame.draw.rect(self.pantalla, color_nueva, self.btn_nueva, border_radius=12)
        pygame.draw.rect(self.pantalla, VERDE if puede_crear else (150, 150, 150), self.btn_nueva, 3, border_radius=12)
        
        txt_nueva_text = "CREAR NUEVA PARTIDA (máx 5)" if puede_crear else "MÁXIMO 5 PARTIDAS ALCANZADO"
        txt_nueva = self.fuente_m.render(txt_nueva_text, True, BLANCO)
        self.pantalla.blit(txt_nueva, (self.btn_nueva.centerx - txt_nueva.get_width() // 2, self.btn_nueva.centery - txt_nueva.get_height() // 2))
        
        # --- PARTIDAS GUARDADAS ---
        y_partida = area_y + 110
        self.botones_partidas = []
        self.botones_eliminar = []
        
        if len(self.partidas) > 0:
            txt_guardadas = self.fuente_m.render(f"Partidas Guardadas ({len(self.partidas)}/5):", True, AMARILLO)
            self.pantalla.blit(txt_guardadas, (70, y_partida))
            y_partida += 50
            
            for i, partida in enumerate(self.partidas):
                rect_partida = pygame.Rect(70, y_partida + (i * 85), ANCHO - 220, 75)
                self.botones_partidas.append((rect_partida, partida))
                
                # Color alternado
                color_fondo = (50, 50, 50) if i % 2 == 0 else (45, 45, 45)
                pygame.draw.rect(self.pantalla, color_fondo, rect_partida, border_radius=10)
                pygame.draw.rect(self.pantalla, (100, 100, 100), rect_partida, 2, border_radius=10)
                
                # Texto de la partida
                txt_nombre = self.fuente_m.render(partida["nombre"], True, CIAN)
                self.pantalla.blit(txt_nombre, (rect_partida.x + 20, rect_partida.y + 10))
                
                # Datos de la partida
                txt_datos = self.fuente_peq.render(
                    f"Dinero: ${int(partida.get('dinero', 0)):,} | Año: {partida.get('año', 0)} | Población: {partida.get('poblacion', 0)}",
                    True, BLANCO
                )
                self.pantalla.blit(txt_datos, (rect_partida.x + 20, rect_partida.y + 40))
                
                # Botón eliminar
                btn_eliminar = pygame.Rect(rect_partida.right + 10, rect_partida.y + 15, 130, 45)
                self.botones_eliminar.append((btn_eliminar, partida))
                pygame.draw.rect(self.pantalla, (200, 50, 50), btn_eliminar, border_radius=8)
                pygame.draw.rect(self.pantalla, ROJO, btn_eliminar, 2, border_radius=8)
                txt_eliminar = self.fuente_peq.render("ELIMINAR", True, BLANCO)
                self.pantalla.blit(txt_eliminar, (btn_eliminar.centerx - txt_eliminar.get_width() // 2, btn_eliminar.centery - txt_eliminar.get_height() // 2))
        else:
            txt_sin = self.fuente_p.render("Sin partidas guardadas. ¡Crea una nueva!", True, AMARILLO)
            self.pantalla.blit(txt_sin, (70, y_partida))
        
        # --- DIÁLOGO DE CONFIRMACIÓN DE ELIMINACIÓN ---
        if self.confirmando_eliminar:
            self._dibujar_confirmacion_eliminar()
        
        # --- BOTONES INFERIORES ---
        btn_y = ALTO - 100
        
        # Botón Volver
        self.btn_volver = pygame.Rect(50, btn_y, 200, 60)
        pygame.draw.rect(self.pantalla, (150, 0, 0), self.btn_volver, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_volver, 2, border_radius=12)
        txt_volver = self.fuente_m.render("VOLVER", True, BLANCO)
        self.pantalla.blit(txt_volver, (self.btn_volver.centerx - txt_volver.get_width() // 2, self.btn_volver.centery - txt_volver.get_height() // 2))
        
        # Botón Jugar (solo si hay partida guardada)
        if len(self.partidas) > 0:
            self.btn_jugar = pygame.Rect(ANCHO - 250, btn_y, 200, 60)
            pygame.draw.rect(self.pantalla, (0, 150, 0), self.btn_jugar, border_radius=12)
            pygame.draw.rect(self.pantalla, ORO, self.btn_jugar, 2, border_radius=12)
            txt_jugar = self.fuente_m.render("JUGAR ÚLTIMA", True, BLANCO)
            self.pantalla.blit(txt_jugar, (self.btn_jugar.centerx - txt_jugar.get_width() // 2, self.btn_jugar.centery - txt_jugar.get_height() // 2))
        
        pygame.display.flip()
    
    def _dibujar_confirmacion_eliminar(self):
        """Dibuja diálogo de confirmación de eliminación"""
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))
        
        cuadro = pygame.Rect(ANCHO//2 - 250, ALTO//2 - 100, 500, 200)
        pygame.draw.rect(self.pantalla, (40, 40, 40), cuadro, border_radius=15)
        pygame.draw.rect(self.pantalla, ROJO, cuadro, 3, border_radius=15)
        
        # Título
        txt_tit = self.fuente_m.render("¿Eliminar partida?", True, ROJO)
        self.pantalla.blit(txt_tit, (cuadro.centerx - txt_tit.get_width()//2, cuadro.y + 20))
        
        # Nombre de la partida
        texto_partida = self.fuente_p.render(self.partida_a_eliminar["nombre"], True, AMARILLO)
        self.pantalla.blit(texto_partida, (cuadro.centerx - texto_partida.get_width()//2, cuadro.y + 65))
        
        # Botones
        self.btn_confirm_si = pygame.Rect(cuadro.centerx - 120, cuadro.y + 120, 100, 40)
        self.btn_confirm_no = pygame.Rect(cuadro.centerx + 20, cuadro.y + 120, 100, 40)
        
        pygame.draw.rect(self.pantalla, (150, 0, 0), self.btn_confirm_si, border_radius=8)
        pygame.draw.rect(self.pantalla, ROJO, self.btn_confirm_si, 2, border_radius=8)
        txt_si = self.fuente_p.render("SÍ", True, BLANCO)
        self.pantalla.blit(txt_si, (self.btn_confirm_si.centerx - txt_si.get_width()//2, self.btn_confirm_si.centery - txt_si.get_height()//2))
        
        pygame.draw.rect(self.pantalla, (80, 150, 80), self.btn_confirm_no, border_radius=8)
        pygame.draw.rect(self.pantalla, VERDE, self.btn_confirm_no, 2, border_radius=8)
        txt_no = self.fuente_p.render("NO", True, BLANCO)
        self.pantalla.blit(txt_no, (self.btn_confirm_no.centerx - txt_no.get_width()//2, self.btn_confirm_no.centery - txt_no.get_height()//2))
    
    def manejar_eventos(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if ev.type == pygame.MOUSEBUTTONDOWN:
                pos = ev.pos
                
                # Si hay diálogo de confirmación abierto
                if self.confirmando_eliminar:
                    if self.btn_confirm_si.collidepoint(pos):
                        self.eliminar_partida(self.partida_a_eliminar["index"])
                        self.confirmando_eliminar = False
                        self.partida_a_eliminar = None
                        return
                    elif self.btn_confirm_no.collidepoint(pos):
                        self.confirmando_eliminar = False
                        self.partida_a_eliminar = None
                        return
                else:
                    # Botón crear nueva partida (solo si hay menos de 5)
                    if len(self.partidas) < 5 and self.btn_nueva.collidepoint(pos):
                        self.seleccion = "nueva"
                        self.hecho = True
                        return
                    
                    # Botón volver
                    if self.btn_volver.collidepoint(pos):
                        self.seleccion = "volver"
                        self.hecho = True
                        return
                    
                    # Botón jugar última partida
                    if len(self.partidas) > 0 and hasattr(self, 'btn_jugar') and self.btn_jugar.collidepoint(pos):
                        self.seleccion = self.partidas[0]["datos"]  # Retornar el diccionario de datos
                        self.hecho = True
                        return
                    
                    # Botones eliminar
                    for btn_eliminar, partida in self.botones_eliminar:
                        if btn_eliminar.collidepoint(pos):
                            self.partida_a_eliminar = partida
                            self.confirmando_eliminar = True
                            return
                    
                    # Seleccionar una partida para jugar
                    for rect_partida, partida in self.botones_partidas:
                        if rect_partida.collidepoint(pos):
                            self.seleccion = partida["datos"]  # Retornar el diccionario de datos
                            self.hecho = True
                            return
    
    def ejecutar(self):
        """Ejecuta el menú y retorna: "nueva", "volver", o la partida seleccionada"""
        while not self.hecho:
            self.manejar_eventos()
            self.dibujar()
            pygame.time.Clock().tick(60)
        
        return self.seleccion
