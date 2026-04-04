# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import pygame
import sys
import random
import os
import json
from configuracion import *
from logica_ciudad import LogicaCiudad
from login import LoginScreen
from menu_partidas import MenuPartidas
import configuracion
pygame.mixer.init()

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(NOMBRE_JUEGO)
        self.reloj = pygame.time.Clock()
        
        # --- VARIABLES DE RESOLUCIÓN ---
        self.ancho = ANCHO
        self.alto = ALTO
        self.fullscreen = False
        self.ancho_anterior = ANCHO
        self.alto_anterior = ALTO
        
        # --- CÁLCULO DE TAMAÑO DE TILE DINÁMICO ---
        self.filas_mapa = FILAS
        self.columnas_mapa = COLUMNAS
        self.tamano_tile = self.calcular_tamano_tile()
        
        # --- CONTROL DE FLUJO ---
        self.debe_reintentar_login = False

        # --- PANTALLA DE LOGIN ---
        self.mostrar_login_y_menu()

        # --- FUENTES Y MAPA BASE ---
        self.fuente_p = pygame.font.SysFont("Arial", 16)
        self.fuente_m = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_g = pygame.font.SysFont("Arial", 30, bold=True)
        self.mapa_datos = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]

        # --- URBANISMO ---
        self.calle_h(12, 0, COLUMNAS)
        self.calle_h(FILAS // 2, 0, COLUMNAS)
        self.calle_h(FILAS - 22, 0, COLUMNAS // 2, ancho=10, con_lineas=False) 
        self.calle_h(FILAS - 22, COLUMNAS // 2, COLUMNAS // 2, ancho=10, con_lineas=False)
        self.calle_v(0, 10, FILAS - 22)
        self.calle_v(0, COLUMNAS // 3, FILAS - 22)
        self.calle_v(FILAS // 2, COLUMNAS // 2 - 2, FILAS // 2 - 18)
        self.calle_v(0, (COLUMNAS // 4) * 3, FILAS // 2)
        self.calle_v(0, COLUMNAS - 12, FILAS // 2)
        self.calle_h(FILAS // 4, (COLUMNAS // 4) * 3, COLUMNAS // 4)

        # --- ROTONDAS ---
        self.dibujar_rotonda(14, 12, radio=7)
        self.dibujar_rotonda(14, COLUMNAS // 3 + 2, radio=7)
        self.dibujar_rotonda(FILAS // 2 + 2, 12, radio=7)
        self.dibujar_rotonda(FILAS // 2 + 2, COLUMNAS // 3 + 2, radio=7)
        self.dibujar_rotonda(FILAS // 2 + 2, COLUMNAS // 2, radio=6)
        self.dibujar_rotonda(14, (COLUMNAS // 4) * 3 + 2, radio=5)
        self.dibujar_rotonda(FILAS // 4 + 2, (COLUMNAS // 4) * 3 + 2, radio=5)
        self.dibujar_rotonda(14, COLUMNAS - 10, radio=5)
        self.dibujar_rotonda(FILAS // 2 + 2, COLUMNAS - 10, radio=5)
        self.dibujar_rotonda(FILAS - 18, COLUMNAS // 2, radio=18)

        # --- SONIDOS y MUSICA ---
        self.volumen_musica = 0.25
        self.volumen_efectos = 0.25
        self.sonidos = {}
        self.rect_slider_musica = pygame.Rect(0, 0, 0, 0)
        self.rect_slider_efectos = pygame.Rect(0, 0, 0, 0)
        self.cargar_sonidos()


        # --- CARGA DE ICONOS ---
        self.iconos = {}
        nombres = ["comida", "agua", "energia", "felicidad", "salud", "dinero", "poblacion", "reloj", "correo"]
        for n in nombres:
            ruta = os.path.join(BASE_DIR, "assets", "imagenes", f"{n}.png")
            if os.path.exists(ruta):
                img = pygame.image.load(ruta).convert_alpha()
                self.iconos[n] = pygame.transform.scale(img, (22, 22))
                self.iconos[f"{n}_g"] = pygame.transform.scale(img, (28, 28))
            else:
                temp = pygame.Surface((28, 28), pygame.SRCALPHA)
                pygame.draw.rect(temp, (200, 0, 0), (0, 0, 28, 28))
                self.iconos[n] = temp
                self.iconos[f"{n}_g"] = temp

        self.img_noticias_btn = pygame.image.load(os.path.join(BASE_DIR, "assets", "imagenes", "noticias.png")).convert_alpha()
        self.img_noticias_btn = pygame.transform.scale(self.img_noticias_btn, (35, 35))

        self.img_inventario_btn = pygame.image.load(os.path.join(BASE_DIR, "assets", "imagenes", "inventario.png")).convert_alpha()
        self.img_inventario_btn = pygame.transform.scale(self.img_inventario_btn, (35, 35))
        
        ruta_x = os.path.join(BASE_DIR, "assets", "imagenes", "cerrar.png")
        self.img_cerrar = pygame.image.load(ruta_x).convert_alpha()
        self.img_cerrar = pygame.transform.scale(self.img_cerrar, (30, 30))

        self.img_mas = pygame.image.load(os.path.join(BASE_DIR, "assets", "imagenes", "mas.png")).convert_alpha()
        self.img_mas = pygame.transform.scale(self.img_mas, (25, 25))
        
        self.img_ajustes = pygame.image.load(os.path.join(BASE_DIR, "assets", "imagenes", "mantenimiento.png")).convert_alpha()
        self.img_ajustes = pygame.transform.scale(self.img_ajustes, (35, 35))

        # Cargar y escalar el icono (suponiendo que los otros miden 30x30 o 40x40)
        self.icon_investigacion = pygame.image.load(os.path.join(BASE_DIR, "assets", "imagenes", "investigacion.png")).convert_alpha()
        self.icon_investigacion = pygame.transform.scale(self.icon_investigacion, (35, 35))

        self.img_investigar_btn = pygame.image.load(os.path.join(BASE_DIR, "assets", "imagenes", "investigacion.png")).convert_alpha()
        self.img_investigar_btn = pygame.transform.scale(self.img_investigar_btn, (35, 35))

        # --- VARIABLES DE ESTADO Y LÓGICA ---
        # Extraer nombre de partida si existe
        nombre_partida = self.partida_actual.get("nombre", f"Año 0") if isinstance(self.partida_actual, dict) else f"Año 0"
        self.logica = LogicaCiudad(self, nombre_partida)
        self.logica.cargar_partida(self.partida_actual)
        
        # 🔧 SINCRONIZAR INVESTIGACIONES COMPLETADAS DESDE LOGICA_CIUDAD
        self.investigaciones_completadas = set(self.logica.investigaciones_completadas)
        
        # Inicializar conteos de edificios
        self.edificios_construidos = {ed[0]: 0 for ed in EDIFICACIONES}
        # Sincronizar con edificios cargados desde la partida
        for edificio in self.logica.edificios:
            if edificio.nombre in self.edificios_construidos:
                self.edificios_construidos[edificio.nombre] += 1
        
        self.mostrando_investigacion = False  # Controla si el menú está abierto
        self.investigacion_seleccionada = None # Almacena el ID (ej: "comida_2") para el popup
        
        self.investigando_id = None            # El ID de la tecnología que se está procesando
        self.tiempo_investigacion = 0           # El contador de frames (el reloj)
        self.tiempo_total_necesario = 300       # 300 frames (aprox 5-10 seg)
        
        # Variable para controlar qué popup está abierto
        self.investigacion_seleccionada = None

        self.investigacion_seleccionada = None # Variable para saber qué ventana abrir

        self.corriendo = True
        self.sin_habitantes_mostrado = False
        self.volver_al_menu = False
        self.nombre_partida_actual = None
        self.input_nombre_partida = ""
        self.campo_nombre_activo = False
        self.menu_compra_abierto = False
        self.noticias_abiertas = False
        self.mostrando_aviso_inv = False
        self.mostrando_inventario = False
        self.dialogo_guardar_abierto = False
        self.menu_ajustes_abierto = False
        self.mostrando_ayuda = False
        self.mostrando_ranking = False
        self.dialogo_dinero_insuficiente = False
        self.dialogo_sin_habitantes = False
        self.dinero_faltante = 0
        self.edificio_intento_compra = None
        self.menu_venta_abierto = False
        self.edificio_a_vender_seleccionado = None
        self.cantidad_a_vender = 1
        self.menu_intercambio_abierto = False
        self.recurso_dar = None  # que vamos a dar
        self.recurso_recibir = None  # que queremos recibir
        self.cantidad_intercambio = 0
        self.input_cantidad_intercambio_activo = False
        self.celdas_ocupadas = []
        self.scroll_y = 0
        self.scroll_inv_y = 0 
        self.cantidad_a_comprar = 1 
        self.confirmacion_pendiente = None
        self.mostrando_investigacion = False 
        self.investigando_id = None
        self.tiempo_investigacion = 0
        self.investigacion_seleccionada = None
        self.investigaciones_completadas = set()
        self.mostrando_detalle_estado = False
        self.detalle_estado_tipo = None
        self.rect_detalle_popup = None
        self.rect_detalle_cerrar = None
        self.rect_hud_info = {}
        # No usar atributos con nombre de método; el control está en self.logica
        self.popup_evento_cerrar = False
        
        # --- TRACKING DE CLASIFICACIÓN ---
        self.rango_anterior = None
        self.mostrando_cambio_rango = False
        self.tiempo_cambio_rango = 0
        self.nuevo_rango = None

        # Llamamos a la actualización de la ubicación de los botones
        self.actualizar_posiciones_ui()
        
        # Guardamos la imagen escalada para usarla después en el dibujo
        if "correo" in self.iconos:
            self.img_correo_btn = pygame.transform.scale(self.iconos["correo"], (35, 35))

    def dibujar_cambio_rango(self):
        """Dibuja un popup visual cuando la ciudad cambia de rango"""
        if not self.mostrando_cambio_rango or not self.nuevo_rango:
            return
        
        # Tiempo de animación: 4 segundos (240 frames a 60 FPS)
        self.tiempo_cambio_rango -= 1
        if self.tiempo_cambio_rango <= 0:
            self.mostrando_cambio_rango = False
            return
        
        # Fondo oscuro
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.pantalla.blit(overlay, (0, 0))
        
        # Cuadro con animación
        tamaño = 150 + int(50 * (1 - self.tiempo_cambio_rango / 240.0))
        cuadro = pygame.Rect(ANCHO // 2 - tamaño // 2, ALTO // 2 - tamaño // 2, tamaño, tamaño)
        
        pygame.draw.rect(self.pantalla, (255, 215, 0), cuadro, border_radius=20)
        pygame.draw.rect(self.pantalla, (255, 255, 0), cuadro, 4, border_radius=20)
        
        # Texto "¡FELICIDADES!"
        txt_felic = self.fuente_g.render("¡FELICIDADES!", True, (255, 215, 0))
        self.pantalla.blit(txt_felic, (ANCHO // 2 - txt_felic.get_width() // 2, ALTO // 2 - 50))
        
        # Nuevo rango
        txt_rango = self.fuente_g.render(f"Ciudad: {self.nuevo_rango}", True, (255, 255, 255))
        self.pantalla.blit(txt_rango, (ANCHO // 2 - txt_rango.get_width() // 2, ALTO // 2 + 20))

    def calle_h(self, fila, col_inicio, celdas, ancho=4, con_lineas=True):
        """Dibuja calle horizontal. con_lineas=False para la Mega Carretera."""
        for c in range(col_inicio, min(col_inicio + celdas, COLUMNAS)):
            for a in range(ancho):
                if 0 <= fila + a < FILAS:
                    # Líneas blancas solo si no es la autopista principal
                    if con_lineas and a == ancho // 2 and (c // 4) % 2 == 0:
                        self.mapa_datos[fila + a][c] = 2
                    else:
                        self.mapa_datos[fila + a][c] = 1

    def calle_v(self, fila_inicio, col, celdas, ancho=4):
        """Dibuja calle vertical."""
        for f in range(fila_inicio, min(fila_inicio + celdas, FILAS)):
            for a in range(ancho):
                if 0 <= col + a < COLUMNAS:
                    if a == ancho // 2 and (f // 4) % 2 == 0:
                        self.mapa_datos[f][col + a] = 2
                    else:
                        self.mapa_datos[f][col + a] = 1

    def dibujar_rotonda(self, f, c, radio=6):
        """Dibuja la rotonda centrada que conecta todas las calles."""
        for i in range(-radio, radio + 1):
            for j in range(-radio, radio + 1):
                dist = (i**2 + j**2)**0.5
                if 0 <= f+i < FILAS and 0 <= c+j < COLUMNAS:
                    if dist <= radio:
                        # Isleta central de pasto (0) y anillo de asfalto (1)
                        self.mapa_datos[f+i][c+j] = 0 if dist < (radio * 0.4) else 1

    def obtener_posicion_aleatoria(self):
        for _ in range(200): # 200 intentos para encontrar hueco
            c = random.randint(0, COLUMNAS - 3)
            f = random.randint(0, FILAS - 3)
            # Usamos la nueva lógica: si el sitio está libre de verdad
            if self.logica.es_posicion_valida(c, f): 
                return (c, f)
        return None

    def dibujar_sub_stats(self, x, balance):
        if balance is None or balance == 0: return 
        
        # 1. Color: Verde si ganas, Rojo si pierdes
        color_bal = (0, 255, 127) if balance > 0 else (255, 30, 30)
        
        # 2. Creamos el texto: 
        # Si es positivo, le ponemos el "+" delante manualmente.
        # Si es negativo, el número ya trae su propio "-"
        if balance > 0:
            texto_pantalla = f"+{int(balance)}"
        else:
            texto_pantalla = f"{int(balance)}" # Aquí ya saldrá el "-" solo
            
        img_texto = self.fuente_p.render(texto_pantalla, True, color_bal)
        
        # 3. Lo dibujamos en la pantalla (ajusta el +35 y 48 si quieres moverlo)
        self.pantalla.blit(img_texto, (x + 35, 48))

    def calcular_detalles_estado(self, tipo):
        poblacion = self.logica.poblacion
        n_pob = len(poblacion)
        edificios = self.logica.edificios

        consumo_electricidad = n_pob * CONSUMO_ELEC_HAB
        energia_disponible = max(0, self.logica.recursos.get('electricidad', 0) + consumo_electricidad)
        sin_luz = max(0, n_pob - (energia_disponible // CONSUMO_ELEC_HAB))
        sin_casa = sum(1 for hab in poblacion if not hab.tiene_casa)
        detalles = []
        total = 0.0

        def promedio(valor):
            return round(valor / n_pob, 1) if n_pob else 0.0

        if tipo == "felicidad":
            positivos = sum(len(e.habitantes) * max(0, getattr(e, 'felic_impacto', 0)) for e in edificios)
            negativos = sum(len(e.habitantes) * min(0, getattr(e, 'felic_impacto', 0)) for e in edificios)

            avg_positivos = promedio(positivos)
            avg_negativos = promedio(negativos)

            if avg_positivos:
                detalles.append(("Edificios: felicidad positiva", avg_positivos))
                total += avg_positivos
            if avg_negativos:
                detalles.append(("Edificios: felicidad negativa", avg_negativos))
                total += avg_negativos

            if self.logica.dinero < 0:
                deuda_penal = -10.0
                detalles.append(("Deuda: -10% de felicidad promedio", deuda_penal))
                total += deuda_penal
            elif self.logica.dinero > 50000 and self.logica.recursos.get('comida', 0) > 4000:
                bonificacion = 2.0
                detalles.append(("Ciudad próspera: +2% de felicidad promedio", bonificacion))
                total += bonificacion

            if sin_casa:
                penal = promedio(-DANO_SIN_TECHO_FELIC * sin_casa)
                detalles.append((f"Sin vivienda: {sin_casa} ciudadanos", penal))
                total += penal

            if sin_luz:
                penal = promedio(-5 * sin_luz)
                detalles.append((f"Sin electricidad útil: {sin_luz} ciudadanos", penal))
                total += penal

            if not detalles:
                detalles.append(("Sin cambios directos de felicidad", 0.0))

        else:
            positivos = sum(len(e.habitantes) * max(0, getattr(e, 'salud_impacto', 0)) for e in edificios)
            negativos = sum(len(e.habitantes) * min(0, getattr(e, 'salud_impacto', 0)) for e in edificios)

            avg_positivos = promedio(positivos)
            avg_negativos = promedio(negativos)

            if avg_positivos:
                detalles.append(("Edificios: salud positiva", avg_positivos))
                total += avg_positivos
            if avg_negativos:
                detalles.append(("Edificios: salud negativa", avg_negativos))
                total += avg_negativos

            if self.logica.recursos.get('comida', 0) < 0:
                hambre_penal = -float(DANO_HAMBRE)
                detalles.append(("Hambre: -salud promedio", hambre_penal))
                total += hambre_penal
            if self.logica.recursos.get('agua', 0) < 0:
                sed_penal = -float(DANO_SED)
                detalles.append(("Sed: -salud promedio", sed_penal))
                total += sed_penal

            if sin_luz:
                luz_salud_penal = promedio(-DANO_SIN_LUZ_SALUD * sin_luz)
                detalles.append((f"Sin electricidad útil: {sin_luz} ciudadanos", luz_salud_penal))
                total += luz_salud_penal

            if sin_casa:
                penal = promedio(-1 * sin_casa)
                detalles.append((f"Sin vivienda: {sin_casa} ciudadanos", penal))
                total += penal

            if not detalles:
                detalles.append(("Sin cambios directos de salud", 0.0))

        return detalles, total

    def dibujar_detalles_estado(self):
        if not self.mostrando_detalle_estado or self.detalle_estado_tipo not in ("felicidad", "salud"):
            return

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.pantalla.blit(overlay, (0, 0))

        detalles, total = self.calcular_detalles_estado(self.detalle_estado_tipo)
        alto_popup = max(280, 120 + len(detalles) * 38)
        ancho_popup = 520
        x = self.ancho // 2 - ancho_popup // 2
        y = self.alto // 2 - alto_popup // 2
        self.rect_detalle_popup = pygame.Rect(x, y, ancho_popup, alto_popup)

        pygame.draw.rect(self.pantalla, GRIS_OSCURO, self.rect_detalle_popup, border_radius=20)
        pygame.draw.rect(self.pantalla, ORO, self.rect_detalle_popup, 3, border_radius=20)

        titulo = "ANÁLISIS DE FELICIDAD" if self.detalle_estado_tipo == "felicidad" else "ANÁLISIS DE SALUD"
        txt_titulo = self.fuente_g.render(titulo, True, BLANCO)
        self.pantalla.blit(txt_titulo, (x + 25, y + 22))

        y_offset = y + 80
        for etiqueta, valor in detalles:
            color = (50, 255, 150) if valor > 0 else (255, 130, 130)
            signo = "+" if valor > 0 else ""
            txt_label = self.fuente_m.render(etiqueta, True, BLANCO)
            txt_valor = self.fuente_m.render(f"{signo}{valor:.1f}%", True, color)
            self.pantalla.blit(txt_label, (x + 35, y_offset))
            self.pantalla.blit(txt_valor, (x + ancho_popup - txt_valor.get_width() - 35, y_offset))
            y_offset += 36

        pygame.draw.line(self.pantalla, (110, 110, 110), (x + 25, y_offset), (x + ancho_popup - 25, y_offset), 2)
        y_offset += 18
        txt_total = self.fuente_m.render(f"Balance anual: {total:+.1f}%", True, (180, 255, 180) if total >= 0 else (255, 120, 120))
        self.pantalla.blit(txt_total, (x + 35, y_offset))

        # Botón cerrar
        self.rect_detalle_cerrar = pygame.Rect(x + ancho_popup - 45, y + 20, 30, 30)
        pygame.draw.rect(self.pantalla, (220, 80, 80), self.rect_detalle_cerrar, border_radius=8)
        txt_x = self.fuente_m.render("X", True, BLANCO)
        self.pantalla.blit(txt_x, (self.rect_detalle_cerrar.centerx - txt_x.get_width()//2, self.rect_detalle_cerrar.centery - txt_x.get_height()//2))

    def _limpiar_partida_sin_habitantes(self):
        """Elimina la partida con 0 habitantes del JSON"""
        try:
            if os.path.exists(self.ruta_partida):
                with open(self.ruta_partida, "r", encoding="utf-8") as f:
                    partidas = json.load(f)
                
                # Filtrar partidas con población > 0
                partidas_validas = [p for p in partidas if len(p.get("poblacion", [])) > 0]
                
                if len(partidas_validas) < len(partidas):
                    with open(self.ruta_partida, "w", encoding="utf-8") as f:
                        json.dump(partidas_validas, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error limpiando partida: {e}")

    def mostrar_menu_partidas_nuevamente(self):
        """Muestra el menú de partidas sin hacer login nuevamente"""
        while True:
            menu = MenuPartidas(self.pantalla, self.usuario_nombre)
            seleccion = menu.ejecutar()
            
            if seleccion == "volver":
                # Volver al login
                self.mostrar_login_y_menu()
                break
            elif seleccion == "nueva":
                # Nueva partida
                self.partida_actual = None
                break
            else:
                # Partida existente seleccionada
                self.partida_actual = seleccion
                break

    def calcular_tamano_tile(self):
        """Calcula el tamaño de los tiles basado en el tamaño actual de la pantalla"""
        # Espacio disponible para el mapa
        ancho_disponible = self.ancho
        alto_disponible = self.alto - MARGEN_HUD_SUP - MARGEN_HUD_INF
        
        # Calcular tamaño máximo que cabe en el ancho
        tamano_por_ancho = ancho_disponible / self.columnas_mapa
        
        # Calcular tamaño máximo que cabe en el alto
        tamano_por_alto = alto_disponible / self.filas_mapa
        
        # Usar el más pequeño para que todo quepa
        tamano = int(min(tamano_por_ancho, tamano_por_alto))
        
        # Asegurar que sea al menos 1 píxel
        return max(1, tamano)

    def mostrar_login_y_menu(self):
        """Maneja el flujo de login y menú de partidas"""
        while True:
            # --- PANTALLA DE LOGIN ---
            login = LoginScreen(self.pantalla)
            usuario_actual = login.ejecutar()
            self.usuario_nombre = usuario_actual  # Guardamos quién juega
            self.ruta_partida = os.path.join(BASE_DIR, "usuarios", f"partidas_{self.usuario_nombre}.json")
            
            # --- MENÚ DE PARTIDAS ---
            menu = MenuPartidas(self.pantalla, usuario_actual)
            seleccion = menu.ejecutar()
            
            # Si selecciona volver, vuelve al login
            if seleccion == "volver":
                continue  # Inicia el loop de nuevo (mostrará login)
            
            # Si selecciona crear nueva partida
            if seleccion == "nueva":
                self.partida_actual = None  # Nueva partida
            else:
                # Si selecciona una partida guardada
                self.partida_actual = seleccion
            
            # Sale del loop de login/menú y continúa con el juego
            break

    def actualizar_posiciones_ui(self):
        """Recalcula las posiciones de todos los elementos UI basado en el tamaño actual"""
        # Recalcular tamaño del tile
        self.tamano_tile = self.calcular_tamano_tile()
        
        # Botones principales
        self.btn_next = pygame.Rect(20, self.alto - 80, 200, 60)
        self.btn_tienda = pygame.Rect(230, self.alto - 80, 150, 60)
        self.btn_intercambio = pygame.Rect(390, self.alto - 80, 150, 60)
        
        # Botones HUD (esquina inferior derecha)
        altura_botones = self.alto - 50
        self.btn_guardar = pygame.Rect(0, 0, 60, 60)
        self.btn_guardar.center = (self.ancho - 230, altura_botones)
        
        self.btn_inventario = pygame.Rect(0, 0, 60, 60)
        self.btn_inventario.center = (self.ancho - 150, altura_botones)
        
        self.btn_noticias = pygame.Rect(0, 0, 60, 60)
        self.btn_noticias.center = (self.ancho - 70, altura_botones)
        
        # Botones de confirmación (centrados)
        self.btn_si = pygame.Rect(self.ancho // 2 - 110, self.alto // 2 + 55, 100, 45)
        self.btn_no = pygame.Rect(self.ancho // 2 + 10, self.alto // 2 + 55, 100, 45)
        
        # Botones multiplicadores
        self.btn_multiplicadores = {}
        cantidades = [1, 2, 3, 5, 10]
        for i, cant in enumerate(cantidades):
            self.btn_multiplicadores[cant] = pygame.Rect(self.ancho // 2 - 125 + (i * 50), self.alto // 2 + 105, 40, 30)

    def dibujar_hud(self):
        # 1. Fondo y básicos
        pygame.draw.rect(self.pantalla, (30, 30, 30), (0, 0, self.ancho, MARGEN_HUD_SUP))
        pob = self.logica.poblacion
        n_pob = len(pob)
        fel = sum(h.felicidad for h in pob)//n_pob if n_pob else 100
        sal = sum(h.salud for h in pob)//n_pob if n_pob else 100
        
        # --- CÁLCULO DE PROYECCIÓN PARA EL SIGUIENTE AÑO ---
        # Esto calcula cuánto va a cambiar el recurso al final del turno
        
        # 1. Energía: Suma lo que producen menos lo que consumen los edificios + habitantes
        prod_elec = sum(getattr(e, 'elec', 0) for e in self.logica.edificios if getattr(e, 'elec', 0) > 0)
        cons_elec = sum(abs(getattr(e, 'elec', 0)) for e in self.logica.edificios if getattr(e, 'elec', 0) < 0)
        cons_elec += (n_pob * CONSUMO_ELEC_HAB)
        bal_elec = prod_elec - cons_elec

        # 2. Comida: Suma producción menos consumo total
        prod_comida = sum(getattr(e, 'comida', 0) for e in self.logica.edificios if getattr(e, 'comida', 0) > 0)
        cons_comida = sum(abs(getattr(e, 'comida', 0)) for e in self.logica.edificios if getattr(e, 'comida', 0) < 0)
        cons_comida += (n_pob * CONSUMO_COMIDA_HAB)
        bal_comida = prod_comida - cons_comida

        # 3. Agua: Suma producción menos consumo total
        prod_agua = sum(getattr(e, 'agua', 0) for e in self.logica.edificios if getattr(e, 'agua', 0) > 0)
        cons_agua = sum(abs(getattr(e, 'agua', 0)) for e in self.logica.edificios if getattr(e, 'agua', 0) < 0)
        cons_agua += (n_pob * CONSUMO_AGUA_HAB)
        bal_agua = prod_agua - cons_agua

        # 4. Dinero: Impuestos + ingresos extra de edificios - mantenimiento
        impuestos_reales = n_pob * (INGRESO_BASE_HAB * (IMPUESTO_INICIAL / 100))
        ingresos_extra = sum(getattr(e, 'produccion_dinero', 0) for e in self.logica.edificios)
        mantenimiento_total = sum(getattr(e, 'mantenimiento', 0) for e in self.logica.edificios)
        bal_dinero = (impuestos_reales + ingresos_extra) - mantenimiento_total

        # --- PREPARAR LISTA DE STATS ---
        # Aquí asignamos los balances calculados arriba a cada icono
        # Limitar visualización de recursos negativos según el límite dinámico
        comida_viz = max(self.logica.limite_negativo_recurso("comida"), int(self.logica.recursos['comida']))
        agua_viz = max(self.logica.limite_negativo_recurso("agua"), int(self.logica.recursos['agua']))
        energia_viz = max(self.logica.limite_negativo_recurso("electricidad"), int(self.logica.recursos['electricidad']))
        
        stats = [
            ("dinero", f"{int(self.logica.dinero)}", ORO, bal_dinero),
            ("poblacion", f"{n_pob}/{self.logica.capacidad_max_poblacion}", BLANCO, None),
            ("comida", f"{comida_viz}", (0, 255, 100), bal_comida),
            ("agua", f"{agua_viz}", CIAN, bal_agua),
            ("energia", f"{energia_viz}", AMARILLO, bal_elec),
            ("felicidad", f"{fel}%", VIOLETA, None),
            ("salud", f"{sal}%", ROJO, None),
            ("reloj", f"Año: {self.logica.año}", BLANCO, None)
        ]

        caps = {

            "comida": getattr(self.logica, "max_comida", 8000),
            "agua": getattr(self.logica, "max_agua", 10000),
            "energia": getattr(self.logica, "max_energia", 12000)
        }


        pygame.draw.rect(self.pantalla, NARANJA, self.btn_next, border_radius=15)
        txt_next = self.fuente_m.render("SIGUIENTE AÑO", True, BLANCO)
        self.pantalla.blit(txt_next, (self.btn_next.centerx - txt_next.get_width()//2, self.btn_next.centery - txt_next.get_height()//2))

        for i, (icon, val, col, balance) in enumerate(stats):
            x = 10 + (i * 148)
            
            # --- EL BLOQUE QUE FALTABA: DIBUJO DE BARRITAS ---
            if icon in caps:
                max_v = caps[icon]
                # Sincronizamos 'energia' con 'electricidad'
                recurso_key = "electricidad" if icon == "energia" else icon
                actual = self.logica.recursos.get(recurso_key, 0)
                
                # Calculamos cuántos bloques iluminar
                bloques_on = min(10, max(0, int((actual / max_v) * 10)))
                
                # Color de la barra
                color_res = (210, 105, 30) if icon=="comida" else (0, 150, 255) if icon=="agua" else (255, 215, 0)
                
                # Dibujamos los 10 mini rectángulos
                for b in range(10):
                    c = color_res if b < bloques_on else (65, 65, 65)
                    pygame.draw.rect(self.pantalla, c, (x + 35 + (b * 8), 10, 6, 5))
            # -------------------------------------------------

            # Icono y Texto
            if f"{icon}_g" in self.iconos:
                self.pantalla.blit(self.iconos[f"{icon}_g"], (x, 25))
            self.pantalla.blit(self.fuente_p.render(val, True, col), (x + 35, 25))

            if icon in ("felicidad", "salud"):
                detalles_estado, total_estado = self.calcular_detalles_estado(icon)
                flecha = "▲" if total_estado >= 0 else "▼"
                color_flecha = (50, 255, 150) if total_estado >= 0 else (255, 80, 80)
                flecha_txt = self.fuente_p.render(flecha, True, color_flecha)
                self.pantalla.blit(flecha_txt, (x + 35 + self.fuente_p.size(val)[0] + 6, 25))
                self.rect_hud_info[icon] = pygame.Rect(x, 10, 145, 50)

            if balance is not None:
                self.dibujar_sub_stats(x, balance)

        # --- BOTÓN SIGUIENTE AÑO ---
        pygame.draw.rect(self.pantalla, NARANJA, self.btn_next, border_radius=15)
        txt_next = self.fuente_m.render("SIGUIENTE AÑO", True, BLANCO)
        self.pantalla.blit(txt_next, (self.btn_next.centerx - txt_next.get_width()//2, self.btn_next.centery - txt_next.get_height()//2))

        # --- BOTÓN TIENDA ---
        pygame.draw.rect(self.pantalla, (0, 180, 0), self.btn_tienda, border_radius=15)
        txt_tie = self.fuente_m.render("TIENDA", True, BLANCO)
        self.pantalla.blit(txt_tie, (self.btn_tienda.centerx - txt_tie.get_width()//2, self.btn_tienda.centery - txt_tie.get_height()//2))

        # --- BOTÓN INTERCAMBIO ---
        pygame.draw.rect(self.pantalla, (100, 100, 200), self.btn_intercambio, border_radius=15)
        txt_int = self.fuente_m.render("INTERCAMBIO", True, BLANCO)
        self.pantalla.blit(txt_int, (self.btn_intercambio.centerx - txt_int.get_width()//2, self.btn_intercambio.centery - txt_int.get_height()//2))

        self.dibujar_botones_circulares()

    def dibujar_aviso_inv(self):
        # Fondo oscuro
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))

        # Cuadro (500x250)
        cuadro = pygame.Rect(self.ancho//2 - 250, self.alto//2 - 125, 500, 250)
        pygame.draw.rect(self.pantalla, (25, 25, 25), cuadro, border_radius=15)
        pygame.draw.rect(self.pantalla, ORO, cuadro, 4, border_radius=15)

        # --- TEXTOS CON FRASE CORTA ---
        # Ahora sí, fuente_g en Rojo porque "NO TIENES EDIFICIOS" es corto
        txt1 = self.fuente_g.render("NO TIENES EDIFICIOS", True, ROJO)
        # Pregunta también en grande
        txt2 = self.fuente_g.render("¿Quieres ir a la tienda?", True, AMARILLO)
        
        # Centrado perfecto
        self.pantalla.blit(txt1, (cuadro.centerx - txt1.get_width()//2, cuadro.y + 45))
        self.pantalla.blit(txt2, (cuadro.centerx - txt2.get_width()//2, cuadro.y + 100))

        # --- BOTONES (Bordes ORO) ---
        self.btn_aviso_si = pygame.Rect(cuadro.centerx - 165, cuadro.y + 170, 145, 60)
        pygame.draw.rect(self.pantalla, (0, 150, 0), self.btn_aviso_si, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_aviso_si, 3, border_radius=12)
        
        txt_si = self.fuente_m.render("SÍ", True, BLANCO)
        self.pantalla.blit(txt_si, (self.btn_aviso_si.centerx - txt_si.get_width()//2, self.btn_aviso_si.centery - txt_si.get_height()//2))

        self.btn_aviso_no = pygame.Rect(cuadro.centerx + 20, cuadro.y + 170, 145, 60)
        pygame.draw.rect(self.pantalla, (150, 0, 0), self.btn_aviso_no, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_aviso_no, 3, border_radius=12)
        
        txt_no = self.fuente_m.render("NO", True, BLANCO)
        self.pantalla.blit(txt_no, (self.btn_aviso_no.centerx - txt_no.get_width()//2, self.btn_aviso_no.centery - txt_no.get_height()//2))

    def dibujar_tienda(self):
        # 1. Fondo oscuro semitransparente
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.pantalla.blit(s, (0, 0))
        
        # 2. El cuadro principal del menú
        cuadro = pygame.Rect(50, 80, 1100, 600)
        pygame.draw.rect(self.pantalla, (40, 40, 40), cuadro, border_radius=20)
        
        # 3. Dibujar Títulos
        titulos = [("Edificio","nombre"), ("Costo","costo"), ("Mant.","mant"), 
                   ("Comida","comida"), ("Agua","agua"), ("Luz","elec"), 
                   ("Felic.","felic"), ("Salud","salud")]
        
        for t, k in titulos:
            texto_tit = self.fuente_m.render(t, True, AMARILLO)
            pos_x = COL_X[k]
            if k == "nombre":
                r_t = texto_tit.get_rect(centerx = pos_x + 60, top = 130)
            else:
                r_t = texto_tit.get_rect(centerx = pos_x + 40, top = 130)
            self.pantalla.blit(texto_tit, r_t)

        # 4. BOTÓN CERRAR
        self.btn_cerrar = pygame.Rect(cuadro.right - 50, cuadro.top + 10, 40, 40)
        self.pantalla.blit(self.img_cerrar, (self.btn_cerrar.x, self.btn_cerrar.y))

        # 5. ÁREA DE SCROLL
        area = pygame.Surface((1050, 480), pygame.SRCALPHA) 
        self.botones_compra = [] 
        
        # Definimos la función de ayuda una sola vez aquí
        def blit_c(val, k, col, y_pos):
            txt = self.fuente_p.render(str(val), True, col)
            area.blit(txt, txt.get_rect(center=(COL_X[k], y_pos + 20)))

        indice_visible = 0

        # ✓ ARREGLO 3: Usar edificios ordenados por tipo de recurso
        edificios_ordenados = configuracion.obtener_edificios_ordenados_por_tipo()
        
        # Mapeo de tipos a iconos
        iconos_tipo = {
            "residencial": "poblacion",
            "comida": "comida",
            "agua": "agua",
            "energia": "energia"
        }
        
        # Nombres de categorías
        nombres_tipo = {
            "residencial": "RESIDENCIAL",
            "comida": "COMIDA",
            "agua": "AGUA",
            "energia": "ENERGÍA"
        }
        
        tipo_actual = None
        separadores_dibujar = []  # Lista de separadores para dibujar después
        
        for ed in edificios_ordenados:
            nombre_edificio = ed[0]

            # --- FILTRO DE INVESTIGACIÓN ---
            if nombre_edificio in self.logica.edificios_desbloqueados:
                # Obtener tipo del edificio
                nuevo_tipo = configuracion.obtener_tipo_edificio(nombre_edificio)
                
                # Si cambió el tipo, guardar separador para dibujar (sin incrementar índice)
                if nuevo_tipo and nuevo_tipo != tipo_actual:
                    y_sep = indice_visible * 55 + self.scroll_y
                    # ✓ SOLO dibujar si será visible en la zona adecuada (no en títulos)
                    if -50 < y_sep < 410:  # Limitado para no sobrepasar títulos
                        separadores_dibujar.append({
                            "tipo": nuevo_tipo,
                            "y": y_sep,
                            "nombre": nombres_tipo.get(nuevo_tipo, "")
                        })
                    
                    tipo_actual = nuevo_tipo
                    # Incrementar índice para dar espaciado entre categorías
                    indice_visible += 1
                
                # Calculamos 'y' basándonos SOLO en los que el jugador puede ver
                y = indice_visible * 55 + self.scroll_y 
                
                # Solo dibujamos si está dentro del área visible del scroll
                if -50 < y < 480:
                    # Imagen del botón (+)
                    centro_btn_x = COL_X["btn"]
                    area.blit(self.img_mas, (centro_btn_x - self.img_mas.get_width()//2, y + 20 - self.img_mas.get_height()//2))
                    
                    # Rect para el click (ajustado a la posición global)
                    rect_click = pygame.Rect(50 + centro_btn_x - 18, 150 + y + 2, 36, 36)
                    self.botones_compra.append((rect_click, ed))

                    # Nombre del edificio
                    area.blit(self.fuente_p.render(nombre_edificio, True, BLANCO), (COL_X["nombre"] - 20, y + 12))
                    
                    # Datos numéricos (usando la función blit_c definida arriba)
                    blit_c(ed[1], "costo", ORO, y)
                    blit_c(ed[2], "mant", (255, 120, 120), y)
                    blit_c(ed[3], "comida", VERDE_BRILLANTE if ed[3] >= 0 else ROJO, y)
                    blit_c(ed[4], "agua", CIAN if ed[4] >= 0 else ROJO, y)
                    blit_c(ed[5], "elec", AMARILLO if ed[5] >= 0 else ROJO, y)
                    blit_c(ed[6], "felic", (150, 255, 150) if ed[6] >= 0 else ROJO, y)
                    blit_c(ed[7], "salud", (100, 255, 200) if ed[7] >= 0 else ROJO, y)

                # Sumamos al contador porque este edificio SI es visible en la lista
                indice_visible += 1

        # 6. Dibujo final del área de scroll sobre la pantalla
        self.pantalla.blit(area, (50, 150))
        
        # ✓ ARREGLO 3: Dibujar separadores DESPUÉS sobre la pantalla principal
        # TÍTULOS DE CATEGORÍAS ELIMINADOS POR SOLICITUD DEL USUARIO
        
        # 7. Barra lateral de scroll para mostrar posición
        # Calcular altura total de contenido y posición del scroll
        altura_scroll = 480
        altura_total_contenido = indice_visible * 55
        
        if altura_total_contenido > altura_scroll:
            # Hay scroll disponible
            barra_scroll_x = 1090
            barra_scroll_y = 150
            barra_scroll_alto = 480
            
            # Fondo gris de la barra
            pygame.draw.rect(self.pantalla, (50, 50, 50), (barra_scroll_x, barra_scroll_y, 10, barra_scroll_alto))
            
            # Calcular posición del thumb (indicador)
            ratio = abs(self.scroll_y) / max(1, altura_total_contenido - altura_scroll)
            thumb_alto = max(20, (altura_scroll / altura_total_contenido) * barra_scroll_alto)
            thumb_y = barra_scroll_y + (ratio * (barra_scroll_alto - thumb_alto))
            
            # Dibujar thumb
            pygame.draw.rect(self.pantalla, (150, 150, 150), (barra_scroll_x, thumb_y, 10, thumb_alto))
            pygame.draw.rect(self.pantalla, (200, 200, 200), (barra_scroll_x, thumb_y, 10, thumb_alto), 1)

    def dibujar_noticias(self):
        if not self.logica.noticias:
            return

        # Espacio fijo en la esquina superior derecha para evitar que aparezca centrado
        cuadro = pygame.Rect(self.ancho - 360, 80, 330, 320)
        pygame.draw.rect(self.pantalla, (20, 20, 20), cuadro, border_radius=12)
        pygame.draw.rect(self.pantalla, GRIS_CLARO, cuadro, 2, border_radius=12)
        self.pantalla.blit(self.fuente_m.render("NOTICIAS DEL AÑO", True, CIAN), (cuadro.x + 20, cuadro.y + 10))

        # Mostrar como máximo 8 noticias recientes
        for i, n in enumerate(self.logica.noticias[-8:]):
            color = ROJO if n.get("tipo") in ["CRITICO", "MUERTE"] else BLANCO
            txt = self.fuente_p.render(f"• {n.get('txt', '')}", True, color)
            self.pantalla.blit(txt, (cuadro.x + 15, cuadro.y + 40 + (i * 30)))

    def dibujar_confirmacion(self):
        # 1. Fondo oscurecido
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))

        # 2. CUADRO PRINCIPAL (Aumentado x1.5 aprox)
        # De 300x230 pasamos a 450x340
        cuadro = pygame.Rect(self.ancho//2 - 225, self.alto//2 - 170, 450, 340)
        pygame.draw.rect(self.pantalla, (40, 40, 40), cuadro, border_radius=20)
        pygame.draw.rect(self.pantalla, ORO, cuadro, 3, border_radius=20)

        # 3. TÍTULO (Más grande y con más aire)
        nombre_edf = self.confirmacion_pendiente[0]
        txt_tit = self.fuente_g.render(f"¿Comprar {nombre_edf}?", True, BLANCO)
        self.pantalla.blit(txt_tit, (cuadro.centerx - txt_tit.get_width()//2, cuadro.y + 20))

        # 4. SUB-CUADRO PARA RECURSOS (Agrandado para que respire el texto)
        rect_recursos = pygame.Rect(cuadro.x + 25, cuadro.y + 70, 200, 190)
        pygame.draw.rect(self.pantalla, (30, 30, 30), rect_recursos, border_radius=15)
        pygame.draw.rect(self.pantalla, (100, 100, 100), rect_recursos, 1, border_radius=15)

        # 5. LISTA DE RECURSOS (Ahora usamos fuente_m por el aumento de tamaño)
        c = self.cantidad_a_comprar
        info_recursos = [
            ("dinero",    f"-{self.confirmacion_pendiente[1] * c}", (255, 100, 100)),
            ("comida",    f"{self.confirmacion_pendiente[3] * c}", (150, 255, 150) if self.confirmacion_pendiente[3] >= 0 else (255, 150, 150)),
            ("agua",      f"{self.confirmacion_pendiente[4] * c}", (150, 150, 255)),
            ("energia",   f"{self.confirmacion_pendiente[5] * c}", (255, 255, 150)),
            ("felicidad", f"{self.confirmacion_pendiente[6] * c}", (180, 255, 180)),
            ("salud",     f"{self.confirmacion_pendiente[7] * c}", (255, 180, 180))
        ]

        for i, (icon_key, texto, color) in enumerate(info_recursos):
            y_pos = rect_recursos.y + 15 + (i * 28) # Espaciado aumentado
            if icon_key in self.iconos:
                ico = pygame.transform.scale(self.iconos[icon_key], (22, 22)) # Iconos más grandes
                self.pantalla.blit(ico, (rect_recursos.x + 15, y_pos))
            txt_r = self.fuente_m.render(texto, True, color) 
            self.pantalla.blit(txt_r, (rect_recursos.x + 45, y_pos))

        # 6. BOTONES SÍ / NO (Más grandes y a la derecha)
        # Ajustamos el tamaño de los Rects de colisión
        self.btn_si.width, self.btn_si.height = 140, 60
        self.btn_no.width, self.btn_no.height = 140, 60
        self.btn_si.topleft = (cuadro.x + 260, cuadro.y + 85)
        self.btn_no.topleft = (cuadro.x + 260, cuadro.y + 175)

        pygame.draw.rect(self.pantalla, (0, 200, 0), self.btn_si, border_radius=15)
        pygame.draw.rect(self.pantalla, (200, 0, 0), self.btn_no, border_radius=15)
        
        # Texto SÍ/NO en fuente Grande (fuente_g)
        txt_s = self.fuente_g.render("SÍ", True, BLANCO)
        txt_n = self.fuente_g.render("NO", True, BLANCO)
        self.pantalla.blit(txt_s, (self.btn_si.centerx - txt_s.get_width()//2, self.btn_si.centery - txt_s.get_height()//2))
        self.pantalla.blit(txt_n, (self.btn_no.centerx - txt_n.get_width()//2, self.btn_no.centery - txt_n.get_height()//2))

        # 7. MULTIPLICADORES (Aumentados y centrados abajo)
        for cant, rect in self.btn_multiplicadores.items():
            rect.width, rect.height = 60, 40 # Más grandes
            rect.y = rect_recursos.bottom + 15
            
            idx = [1, 2, 3, 5, 10].index(cant)
            rect.x = cuadro.x + 65 + (idx * 68)

            color_btn = (0, 200, 0) if self.cantidad_a_comprar == cant else (60, 60, 60)
            pygame.draw.rect(self.pantalla, color_btn, rect, border_radius=8)
            pygame.draw.rect(self.pantalla, BLANCO, rect, 2, border_radius=8)
            
            txt_m = self.fuente_m.render(f"x{cant}", True, BLANCO)
            self.pantalla.blit(txt_m, (rect.centerx - txt_m.get_width()//2, rect.centery - txt_m.get_height()//2))

    def dibujar_inventario(self):
        # 1. Fondo oscuro
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))

        # 2. Panel (Más estrecho para que no sobre espacio, como en la foto 2)
        ancho_panel = 800 
        cuadro = pygame.Rect((self.ancho - ancho_panel) // 2, 80, ancho_panel, self.alto - 200)
        pygame.draw.rect(self.pantalla, (30, 30, 30), cuadro, border_radius=20)
        pygame.draw.rect(self.pantalla, ORO, cuadro, 2, border_radius=20)

        # 3. Título limpio
        txt_inv = self.fuente_g.render("MIS EDIFICIOS", True, AMARILLO)
        self.pantalla.blit(txt_inv, (cuadro.centerx - txt_inv.get_width()//2, cuadro.y + 20))

        # 4. Cabeceras ajustadas (Sin tanto espacio muerto)
        # Reducimos distancias entre x_pos
        headers = ["Edificio", "Cant.", "Mant.", "Comida", "Agua", "Luz", "Felic.", "Salud"]
        # x_relativas dentro del cuadro
        x_rel = [30, 180, 260, 350, 440, 530, 620, 710]
        
        for i, h in enumerate(headers):
            t = self.fuente_p.render(h, True, ORO)
            self.pantalla.blit(t, (cuadro.x + x_rel[i], cuadro.y + 75))

        # 5. Área de Scroll protegida
        area_visible = pygame.Rect(cuadro.x + 10, cuadro.y + 110, cuadro.width - 20, cuadro.height - 130)
        surf_lista = pygame.Surface((area_visible.width, area_visible.height), pygame.SRCALPHA)
        
        # FILTRO: Solo edificios que tengan al menos 1 unidad construida
        edificios_a_mostrar = [ed for ed in EDIFICACIONES if self.edificios_construidos.get(ed[0], 0) > 0]

        for i, ed in enumerate(edificios_a_mostrar):
            y = i * 40 + self.scroll_inv_y 
            
            nombre = ed[0]
            cant = self.edificios_construidos.get(nombre, 0)
            color_f = BLANCO # Ya no hace falta el gris porque solo mostramos los comprados

            # Dibujamos en la superficie 'surf_lista'
            surf_lista.blit(self.fuente_p.render(nombre, True, color_f), (20, y))
            surf_lista.blit(self.fuente_m.render(str(cant), True, CIAN), (x_rel[1]-10, y))
            
            # Datos calculados
            mant = f"-{ed[2] * cant}"
            stats = [ed[3]*cant, ed[4]*cant, ed[5]*cant, ed[6]*cant, ed[7]*cant]

            surf_lista.blit(self.fuente_p.render(mant, True, (255, 100, 100)), (x_rel[2]-10, y))
            
            for j, val in enumerate(stats):
                color_v = VERDE_BRILLANTE if val > 0 else (ROJO if val < 0 else (150, 150, 150))
                txt_v = self.fuente_p.render(f"{val:+}", True, color_v)
                surf_lista.blit(txt_v, (x_rel[j+3]-10, y))

        # Cortamos lo que se salga del área visible
        self.pantalla.blit(surf_lista, (area_visible.x, area_visible.y))

        # 6. Botón Cerrar (X)
        self.btn_cerrar_inv = pygame.Rect(cuadro.right - 50, cuadro.top + 15, 35, 35)
        pygame.draw.circle(self.pantalla, ROJO, self.btn_cerrar_inv.center, 17)
        self.pantalla.blit(self.img_cerrar, (self.btn_cerrar_inv.x + 7, self.btn_cerrar_inv.y + 7))
        
        # 7. Botón Vender
        self.btn_vender_inv = pygame.Rect(cuadro.right - 100, cuadro.bottom - 50, 80, 40)
        pygame.draw.rect(self.pantalla, (150, 100, 50), self.btn_vender_inv, border_radius=5)
        pygame.draw.rect(self.pantalla, ORO, self.btn_vender_inv, 2, border_radius=5)
        txt_vender = self.fuente_p.render("VENDER", True, BLANCO)
        self.pantalla.blit(txt_vender, (self.btn_vender_inv.centerx - txt_vender.get_width()//2, self.btn_vender_inv.centery - txt_vender.get_height()//2))

    def dibujar_dialogo_dinero_insuficiente(self):
        """Dibuja diálogo de dinero insuficiente"""
        # Panel
        panel_ancho = 400
        panel_alto = 200
        panel_x = ANCHO // 2 - panel_ancho // 2
        panel_y = ALTO // 2 - panel_alto // 2
        
        pygame.draw.rect(self.pantalla, (40, 40, 40), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=8)
        pygame.draw.rect(self.pantalla, ROJO, (panel_x, panel_y, panel_ancho, panel_alto), 3, border_radius=8)
        
        # Título
        titulo = self.fuente_g.render("DINERO INSUFICIENTE", True, ROJO)
        self.pantalla.blit(titulo, (panel_x + panel_ancho//2 - titulo.get_width()//2, panel_y + 20))
        
        # Mensaje
        txt_edificio = self.fuente_p.render(f"Edificio: {self.edificio_intento_compra}", True, BLANCO)
        self.pantalla.blit(txt_edificio, (panel_x + 20, panel_y + 60))
        
        txt_falta = self.fuente_p.render(f"Te faltan: ${self.dinero_faltante:,}", True, AMARILLO)
        self.pantalla.blit(txt_falta, (panel_x + 20, panel_y + 90))
        
        # Botón OK
        btn_ok = pygame.Rect(panel_x + panel_ancho//2 - 60, panel_y + 135, 120, 40)
        pygame.draw.rect(self.pantalla, (100, 50, 50), btn_ok, border_radius=5)
        pygame.draw.rect(self.pantalla, ORO, btn_ok, 2, border_radius=5)
        txt_ok = self.fuente_p.render("OK", True, BLANCO)
        self.pantalla.blit(txt_ok, (btn_ok.centerx - txt_ok.get_width()//2, btn_ok.centery - txt_ok.get_height()//2))
        
        self.btn_dinero_ok = btn_ok

    def dibujar_menu_venta(self):
        """Dibuja el menú de venta de edificios con scroll y scrollbar visual"""
        # Panel principal - AMPLIADO
        panel_ancho = 700
        panel_alto = 550
        panel_x = ANCHO // 2 - panel_ancho // 2
        panel_y = ALTO // 2 - panel_alto // 2
        
        pygame.draw.rect(self.pantalla, (30, 30, 30), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=8)
        pygame.draw.rect(self.pantalla, ORO, (panel_x, panel_y, panel_ancho, panel_alto), 3, border_radius=8)
        
        # Título
        titulo = self.fuente_g.render("VENDER EDIFICIOS", True, ORO)
        self.pantalla.blit(titulo, (panel_x + panel_ancho//2 - titulo.get_width()//2, panel_y + 15))
        
        # 🔧 BOTÓN X PARA CERRAR
        btn_cerrar_venta = pygame.Rect(panel_x + panel_ancho - 35, panel_y + 10, 25, 25)
        pygame.draw.rect(self.pantalla, (200, 50, 50), btn_cerrar_venta, border_radius=3)
        txt_x = self.fuente_p.render("X", True, BLANCO)
        self.pantalla.blit(txt_x, (btn_cerrar_venta.centerx - txt_x.get_width()//2, btn_cerrar_venta.centery - txt_x.get_height()//2))
        self.btn_cerrar_venta = btn_cerrar_venta
        
        if self.edificio_a_vender_seleccionado:
            # Mostrar detalles de venta
            ed_data = self.edificio_a_vender_seleccionado
            costo_original = ed_data[1]
            precio_venta = costo_original // 2  # 50%
            
            txt_nombre = self.fuente_p.render(f"Edificio: {ed_data[0]}", True, CIAN)
            self.pantalla.blit(txt_nombre, (panel_x + 20, panel_y + 60))
            
            txt_precio_original = self.fuente_p.render(f"Costo Original: ${costo_original:,}", True, BLANCO)
            self.pantalla.blit(txt_precio_original, (panel_x + 20, panel_y + 90))
            
            txt_precio_venta = self.fuente_p.render(f"Precio Venta (50%): ${precio_venta:,}", True, VERDE_BRILLANTE)
            self.pantalla.blit(txt_precio_venta, (panel_x + 20, panel_y + 120))
            
            # Multiplicadores de cantidad
            txt_cantidad = self.fuente_p.render("¿Cuántos vender?", True, AMARILLO)
            self.pantalla.blit(txt_cantidad, (panel_x + 20, panel_y + 160))
            
            self.btn_multiplicadores_venta = {}
            cantidades = [1, 2, 3, 5, 10]
            x_offset = panel_x + 20
            
            for cant in cantidades:
                btn_rect = pygame.Rect(x_offset, panel_y + 190, 90, 40)
                color_btn = (100, 100, 50) if cant != self.cantidad_a_vender else (150, 150, 0)
                pygame.draw.rect(self.pantalla, color_btn, btn_rect, border_radius=5)
                pygame.draw.rect(self.pantalla, ORO, btn_rect, 1, border_radius=5)
                
                txt_cant = self.fuente_p.render(str(cant), True, BLANCO)
                self.pantalla.blit(txt_cant, (btn_rect.centerx - txt_cant.get_width()//2, btn_rect.centery - txt_cant.get_height()//2))
                
                self.btn_multiplicadores_venta[cant] = btn_rect
                x_offset += 100
            
            # Total a recibir
            total_venta = precio_venta * self.cantidad_a_vender
            txt_total = self.fuente_g.render(f"Total: ${total_venta:,}", True, VERDE)
            self.pantalla.blit(txt_total, (panel_x + panel_ancho//2 - txt_total.get_width()//2, panel_y + 250))
            
            # Botones SÍ y NO
            btn_si = pygame.Rect(panel_x + 100, panel_y + 320, 120, 50)
            btn_no = pygame.Rect(panel_x + 380, panel_y + 320, 120, 50)
            
            pygame.draw.rect(self.pantalla, (50, 150, 50), btn_si, border_radius=5)
            pygame.draw.rect(self.pantalla, ORO, btn_si, 2, border_radius=5)
            txt_si = self.fuente_p.render("VENDER", True, BLANCO)
            self.pantalla.blit(txt_si, (btn_si.centerx - txt_si.get_width()//2, btn_si.centery - txt_si.get_height()//2))
            
            pygame.draw.rect(self.pantalla, (150, 50, 50), btn_no, border_radius=5)
            pygame.draw.rect(self.pantalla, ORO, btn_no, 2, border_radius=5)
            txt_no = self.fuente_p.render("CANCELAR", True, BLANCO)
            self.pantalla.blit(txt_no, (btn_no.centerx - txt_no.get_width()//2, btn_no.centery - txt_no.get_height()//2))
            
            self.btn_venta_si = btn_si
            self.btn_venta_no = btn_no
        else:
            # 🔧 MOSTRAR LISTA CON SCROLL Y SCROLLBAR
            txt_selecciona = self.fuente_p.render("Selecciona edificio a vender:", True, BLANCO)
            self.pantalla.blit(txt_selecciona, (panel_x + 20, panel_y + 60))
            
            # Área scrolleable - AMPLIADA
            scroll_area = pygame.Rect(panel_x + 15, panel_y + 100, panel_ancho - 55, 390)
            pygame.draw.rect(self.pantalla, (20, 20, 20), scroll_area, border_radius=5)
            pygame.draw.rect(self.pantalla, (100, 100, 100), scroll_area, 1, border_radius=5)
            
            self.pantalla.set_clip(scroll_area)
            
            self.botones_venta_lista = []
            edificios_a_mostrar = [ed for ed in EDIFICACIONES if self.edificios_construidos.get(ed[0], 0) > 0]
            
            # Calcular altura total del contenido scrolleable
            altura_contenido = len(edificios_a_mostrar) * 50
            altura_scroll = scroll_area.height
            max_scroll = 0  # Inicializar por defecto
            
            # Limitar el scroll para evitar bugs
            if altura_contenido > altura_scroll:
                max_scroll = altura_contenido - altura_scroll
                self.scroll_inv_y = max(0, min(self.scroll_inv_y, max_scroll))
            else:
                self.scroll_inv_y = 0
            
            y_offset = panel_y + 100 - self.scroll_inv_y
            
            for ed in edificios_a_mostrar:
                cant_disponible = self.edificios_construidos.get(ed[0], 0)
                btn_rect = pygame.Rect(panel_x + 25, y_offset, panel_ancho - 75, 40)
                
                # Solo dibujar si está visible
                if btn_rect.top < scroll_area.bottom and btn_rect.bottom > scroll_area.top:
                    pygame.draw.rect(self.pantalla, (70, 100, 150), btn_rect, border_radius=5)
                    pygame.draw.rect(self.pantalla, ORO, btn_rect, 1, border_radius=5)
                    
                    txt_ed = self.fuente_p.render(f"{ed[0]} ({cant_disponible}x) - ${ed[1]//2:,} c/u", True, BLANCO)
                    self.pantalla.blit(txt_ed, (btn_rect.centerx - txt_ed.get_width()//2, btn_rect.centery - txt_ed.get_height()//2))
                
                self.botones_venta_lista.append((btn_rect, ed))
                y_offset += 50
            
            self.pantalla.set_clip(None)
            
            # 🔧 DIBUJAR SCROLLBAR VISUAL
            if altura_contenido > altura_scroll:
                # Ancho de la scrollbar
                scrollbar_ancho = 15
                scrollbar_x = panel_x + panel_ancho - 30
                scrollbar_y = scroll_area.y
                scrollbar_alto = scroll_area.height
                
                # Rect de la scrollbar
                pygame.draw.rect(self.pantalla, (40, 40, 40), (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_alto), border_radius=3)
                
                # Altura del thumb (indicador)
                thumb_alto = max(20, int((altura_scroll / altura_contenido) * scrollbar_alto))
                thumb_y = scrollbar_y + int((self.scroll_inv_y / max_scroll) * (scrollbar_alto - thumb_alto))
                
                # Dibujar thumb
                pygame.draw.rect(self.pantalla, (150, 150, 150), (scrollbar_x, thumb_y, scrollbar_ancho, thumb_alto), border_radius=3)
                pygame.draw.rect(self.pantalla, ORO, (scrollbar_x, thumb_y, scrollbar_ancho, thumb_alto), 1, border_radius=3)

    def dibujar_menu_intercambio(self):
        """Menú de intercambio de recursos con comisión del 10%"""
        panel_ancho, panel_alto = 700, 520
        panel_x = ANCHO // 2 - panel_ancho // 2
        panel_y = ALTO // 2 - panel_alto // 2
        
        pygame.draw.rect(self.pantalla, (30, 30, 30), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=8)
        pygame.draw.rect(self.pantalla, (100, 100, 200), (panel_x, panel_y, panel_ancho, panel_alto), 3, border_radius=8)
        
        # Botón X para cerrar
        btn_cerrar = pygame.Rect(panel_x + panel_ancho - 35, panel_y + 10, 25, 25)
        pygame.draw.rect(self.pantalla, (200, 50, 50), btn_cerrar, border_radius=3)
        txt_x = self.fuente_p.render("X", True, BLANCO)
        self.pantalla.blit(txt_x, (btn_cerrar.centerx - txt_x.get_width()//2, btn_cerrar.centery - txt_x.get_height()//2))
        self.btn_cerrar_intercambio = btn_cerrar
        
        # Título
        titulo = self.fuente_g.render("INTERCAMBIO DE RECURSOS", True, (100, 200, 255))
        self.pantalla.blit(titulo, (panel_x + panel_ancho//2 - titulo.get_width()//2, panel_y + 15))
        
        # Comisión
        comision_txt = self.fuente_p.render("Comisión: 10%", True, (200, 100, 100))
        self.pantalla.blit(comision_txt, (panel_x + panel_ancho//2 - comision_txt.get_width()//2, panel_y + 50))
        
        # Recursos disponibles (SIN DINERO en DAS)
        recursos_nombres_dar = ["Comida", "Agua", "Energía"]
        recursos_keys_dar = ["comida", "agua", "electricidad"]
        
        recursos_nombres_recibir = ["Dinero", "Comida", "Agua", "Energía"]
        recursos_keys_recibir = ["dinero", "comida", "agua", "electricidad"]
        
        # SECCIÓN IZQUIERDA - QUÉ DAMOS
        txt_dar = self.fuente_m.render("Das:", True, (255, 150, 100))
        self.pantalla.blit(txt_dar, (panel_x + 30, panel_y + 80))
        
        self.botones_recurso_dar = {}
        y_offset = panel_y + 115
        for nombre, key in zip(recursos_nombres_dar, recursos_keys_dar):
            btn_rect = pygame.Rect(panel_x + 30, y_offset, 280, 35)
            color = (100, 150, 100) if key != self.recurso_dar else (150, 200, 150)
            pygame.draw.rect(self.pantalla, color, btn_rect, border_radius=5)
            pygame.draw.rect(self.pantalla, ORO, btn_rect, 1, border_radius=5)
            
            txt = self.fuente_p.render(nombre, True, BLANCO)
            self.pantalla.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))
            self.botones_recurso_dar[key] = btn_rect
            y_offset += 45
        
        # SECCIÓN DERECHA - QUÉ RECIBIMOS
        txt_recibir = self.fuente_m.render("Recibes:", True, (100, 200, 255))
        self.pantalla.blit(txt_recibir, (panel_x + 390, panel_y + 80))
        
        self.botones_recurso_recibir = {}
        y_offset = panel_y + 115
        for nombre, key in zip(recursos_nombres_recibir, recursos_keys_recibir):
            btn_rect = pygame.Rect(panel_x + 390, y_offset, 280, 35)
            color = (100, 150, 100) if key != self.recurso_recibir else (150, 200, 150)
            pygame.draw.rect(self.pantalla, color, btn_rect, border_radius=5)
            pygame.draw.rect(self.pantalla, ORO, btn_rect, 1, border_radius=5)
            
            txt = self.fuente_p.render(nombre, True, BLANCO)
            self.pantalla.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))
            self.botones_recurso_recibir[key] = btn_rect
            y_offset += 45
        
        # CANTIDAD A INTERCAMBIAR - CENTRADA
        txt_cantidad = self.fuente_m.render("Cantidad a dar:", True, BLANCO)
        self.pantalla.blit(txt_cantidad, (panel_x + panel_ancho//2 - txt_cantidad.get_width()//2, panel_y + 290))
        
        # Input box para cantidad (se pone dorada cuando está seleccionada)
        input_rect = pygame.Rect(panel_x + 220, panel_y + 325, 260, 40)
        color_input = ORO if self.input_cantidad_intercambio_activo else (100, 100, 100)
        pygame.draw.rect(self.pantalla, (50, 50, 50), input_rect, border_radius=5)
        pygame.draw.rect(self.pantalla, color_input, input_rect, 2, border_radius=5)
        
        txt_cant = self.fuente_g.render(str(self.cantidad_intercambio) if self.cantidad_intercambio > 0 else "", True, BLANCO)
        self.pantalla.blit(txt_cant, (input_rect.centerx - txt_cant.get_width()//2, input_rect.centery - txt_cant.get_height()//2))
        self.input_cantidad_intercambio = input_rect
        
        # CUADRO DE CANTIDAD A RECIBIR (con comisión)
        if self.recurso_recibir and self.cantidad_intercambio > 0:
            cantidad_final = int(self.cantidad_intercambio * 0.90)  # 10% comisión
            txt_recibira = self.fuente_m.render("Recibirás:", True, (100, 200, 255))
            self.pantalla.blit(txt_recibira, (panel_x + panel_ancho//2 - txt_recibira.get_width()//2, panel_y + 380))
            
            rect_cantidad_final = pygame.Rect(panel_x + 220, panel_y + 415, 260, 40)
            pygame.draw.rect(self.pantalla, (50, 80, 50), rect_cantidad_final, border_radius=5)
            pygame.draw.rect(self.pantalla, (100, 255, 100), rect_cantidad_final, 2, border_radius=5)
            
            txt_final = self.fuente_g.render(f"{cantidad_final} {self.recurso_recibir}", True, (100, 255, 100))
            self.pantalla.blit(txt_final, (rect_cantidad_final.centerx - txt_final.get_width()//2, rect_cantidad_final.centery - txt_final.get_height()//2))
        
        # BOTÓN INTERCAMBIAR
        btn_intercambiar = pygame.Rect(panel_x + 150, panel_y + 470, 400, 50)
        
        if self.recurso_dar and self.recurso_recibir and self.cantidad_intercambio > 0:
            pygame.draw.rect(self.pantalla, (50, 150, 50), btn_intercambiar, border_radius=5)
            txt_btn = self.fuente_m.render("REALIZAR INTERCAMBIO", True, BLANCO)
        else:
            pygame.draw.rect(self.pantalla, (100, 100, 100), btn_intercambiar, border_radius=5)
            txt_btn = self.fuente_m.render("SELECCIONA RECURSOS", True, (150, 150, 150))
        
        pygame.draw.rect(self.pantalla, ORO, btn_intercambiar, 2, border_radius=5)
        self.pantalla.blit(txt_btn, (btn_intercambiar.centerx - txt_btn.get_width()//2, btn_intercambiar.centery - txt_btn.get_height()//2))
        self.btn_realizar_intercambio = btn_intercambiar

    def dibujar_dialogo_guardar(self):
        # 1. Fondo oscurecido
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))

        # 2. CUADRO PRINCIPAL
        cuadro = pygame.Rect(self.ancho//2 - 225, self.alto//2 - 120, 450, 240)
        pygame.draw.rect(self.pantalla, (40, 40, 40), cuadro, border_radius=20)
        pygame.draw.rect(self.pantalla, ORO, cuadro, 3, border_radius=20)

        # 3. TÍTULO
        txt_tit = self.fuente_g.render("¿Guardar la partida?", True, BLANCO)
        self.pantalla.blit(txt_tit, (cuadro.centerx - txt_tit.get_width()//2, cuadro.y + 25))

        # 4. MENSAJE
        txt_msg = self.fuente_m.render(f"Usuario: {self.usuario_nombre}", True, CIAN)
        self.pantalla.blit(txt_msg, (cuadro.centerx - txt_msg.get_width()//2, cuadro.y + 80))

        # 5. BOTONES SÍ / NO
        self.btn_guardar_si = pygame.Rect(cuadro.centerx - 120, cuadro.y + 140, 100, 50)
        self.btn_guardar_no = pygame.Rect(cuadro.centerx + 20, cuadro.y + 140, 100, 50)

        pygame.draw.rect(self.pantalla, (0, 150, 0), self.btn_guardar_si, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_guardar_si, 2, border_radius=12)
        
        txt_si = self.fuente_m.render("SÍ", True, BLANCO)
        self.pantalla.blit(txt_si, (self.btn_guardar_si.centerx - txt_si.get_width()//2, self.btn_guardar_si.centery - txt_si.get_height()//2))

        pygame.draw.rect(self.pantalla, (150, 0, 0), self.btn_guardar_no, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_guardar_no, 2, border_radius=12)
        
        txt_no = self.fuente_m.render("NO", True, BLANCO)
        self.pantalla.blit(txt_no, (self.btn_guardar_no.centerx - txt_no.get_width()//2, self.btn_guardar_no.centery - txt_no.get_height()//2))

    def dibujar_dialogo_guardar_con_nombre(self):
        # 1. Fondo oscurecido
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))

        # 2. CUADRO PRINCIPAL
        cuadro = pygame.Rect(self.ancho//2 - 300, self.alto//2 - 150, 600, 300)
        pygame.draw.rect(self.pantalla, (40, 40, 40), cuadro, border_radius=20)
        pygame.draw.rect(self.pantalla, ORO, cuadro, 3, border_radius=20)

        # 3. TÍTULO
        txt_tit = self.fuente_g.render("Guardar Partida", True, BLANCO)
        self.pantalla.blit(txt_tit, (cuadro.centerx - txt_tit.get_width()//2, cuadro.y + 20))

        # 4. LABEL Y CAMPO DE ENTRADA
        txt_label = self.fuente_m.render("Nombre de la partida:", True, CIAN)
        self.pantalla.blit(txt_label, (cuadro.x + 30, cuadro.y + 70))

        # Campo de entrada
        self.rect_input_nombre = pygame.Rect(cuadro.x + 30, cuadro.y + 110, 540, 40)
        pygame.draw.rect(self.pantalla, (60, 60, 60) if self.campo_nombre_activo else (50, 50, 50), self.rect_input_nombre, border_radius=8)
        pygame.draw.rect(self.pantalla, AMARILLO if self.campo_nombre_activo else (100, 100, 100), self.rect_input_nombre, 2, border_radius=8)
        
        # Texto en el campo
        txt_input = self.fuente_p.render(self.input_nombre_partida if self.input_nombre_partida else f"Año {self.logica.año}", True, BLANCO)
        self.pantalla.blit(txt_input, (self.rect_input_nombre.x + 10, self.rect_input_nombre.centery - txt_input.get_height()//2))

        # Cursor parpadeante
        if self.campo_nombre_activo and (pygame.time.get_ticks() // 500) % 2:
            cursor_x = self.rect_input_nombre.x + 10 + txt_input.get_width()
            pygame.draw.line(self.pantalla, AMARILLO, (cursor_x, self.rect_input_nombre.y + 5), (cursor_x, self.rect_input_nombre.y + 35), 2)

        # 5. BOTONES SÍ / NO
        self.btn_guardar_si = pygame.Rect(cuadro.centerx - 150, cuadro.y + 200, 120, 50)
        self.btn_guardar_no = pygame.Rect(cuadro.centerx + 30, cuadro.y + 200, 120, 50)

        pygame.draw.rect(self.pantalla, (0, 150, 0), self.btn_guardar_si, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_guardar_si, 2, border_radius=12)
        txt_si = self.fuente_m.render("GUARDAR", True, BLANCO)
        self.pantalla.blit(txt_si, (self.btn_guardar_si.centerx - txt_si.get_width()//2, self.btn_guardar_si.centery - txt_si.get_height()//2))

        pygame.draw.rect(self.pantalla, (150, 0, 0), self.btn_guardar_no, border_radius=12)
        pygame.draw.rect(self.pantalla, ORO, self.btn_guardar_no, 2, border_radius=12)
        txt_no = self.fuente_m.render("CANCELAR", True, BLANCO)
        self.pantalla.blit(txt_no, (self.btn_guardar_no.centerx - txt_no.get_width()//2, self.btn_guardar_no.centery - txt_no.get_height()//2))

    def dibujar_botones_circulares(self):
        # --- Botón Investigar ---
        self.btn_investigar = pygame.Rect(ANCHO - 310, ALTO - 80, 60, 60)
        pygame.draw.circle(self.pantalla, (50, 50, 70), self.btn_investigar.center, 30) 
        pygame.draw.circle(self.pantalla, CIAN, self.btn_investigar.center, 30, 2)

        # Esta es la parte que tienes que asegurar que esté así:
        if hasattr(self, 'img_investigar_btn'):
            # Centrado perfecto: Restamos la mitad del ancho/alto de la imagen a las coordenadas del centro del botón
            pos_x = self.btn_investigar.centerx - self.img_investigar_btn.get_width() // 2
            pos_y = self.btn_investigar.centery - self.img_investigar_btn.get_height() // 2
            self.pantalla.blit(self.img_investigar_btn, (pos_x, pos_y))

        # Label
        lbl_inv_lab = self.fuente_p.render("Investigar", True, CIAN)
        self.pantalla.blit(lbl_inv_lab, (self.btn_investigar.centerx - lbl_inv_lab.get_width()//2, self.btn_investigar.bottom + 5))

        # Botón Ajustes (Movido a ANCHO - 230)
        self.btn_ajustes = pygame.Rect(ANCHO - 230, ALTO - 80, 60, 60)
        pygame.draw.circle(self.pantalla, (50, 50, 50), self.btn_ajustes.center, 30)
        pygame.draw.circle(self.pantalla, ORO, self.btn_ajustes.center, 30, 2)
        self.pantalla.blit(self.img_ajustes, (self.btn_ajustes.centerx - 17, self.btn_ajustes.centery - 17))
        lbl_ajustes = self.fuente_p.render("Ajustes", True, ORO)
        self.pantalla.blit(lbl_ajustes, (self.btn_ajustes.centerx - lbl_ajustes.get_width()//2, self.btn_ajustes.bottom + 5))

        # Botón Inventario (ANCHO - 150)
        self.btn_inventario = pygame.Rect(ANCHO - 150, ALTO - 80, 60, 60)
        pygame.draw.circle(self.pantalla, (50, 50, 50), self.btn_inventario.center, 30)
        pygame.draw.circle(self.pantalla, ORO, self.btn_inventario.center, 30, 2)
        self.pantalla.blit(self.img_inventario_btn, (self.btn_inventario.centerx - 17, self.btn_inventario.centery - 17))
        lbl_inv = self.fuente_p.render("Inventario", True, ORO)
        self.pantalla.blit(lbl_inv, (self.btn_inventario.centerx - lbl_inv.get_width()//2, self.btn_inventario.bottom + 5))

        # Botón Noticias (ANCHO - 70)
        self.btn_noticias = pygame.Rect(ANCHO - 70, ALTO - 80, 60, 60)
        pygame.draw.circle(self.pantalla, (50, 50, 50), self.btn_noticias.center, 30)
        pygame.draw.circle(self.pantalla, ORO, self.btn_noticias.center, 30, 2)
        self.pantalla.blit(self.img_noticias_btn, (self.btn_noticias.centerx - 17, self.btn_noticias.centery - 17))
        lbl_not = self.fuente_p.render("Noticias", True, ORO)
        self.pantalla.blit(lbl_not, (self.btn_noticias.centerx - lbl_not.get_width()//2, self.btn_noticias.bottom + 5))

    def dibujar_menu_ajustes(self):
        """Dibuja el menú de ajustes flotante"""
        # Panel principal semi-transparente
        panel_ancho = 300
        panel_alto = 430
        panel_x = ANCHO - panel_ancho - 15
        panel_y = ALTO - panel_alto - 110
        
        # Fondo del panel
        pygame.draw.rect(self.pantalla, (40, 40, 40), (panel_x, panel_y, panel_ancho, panel_alto), border_radius=8)
        pygame.draw.rect(self.pantalla, ORO, (panel_x, panel_y, panel_ancho, panel_alto), 3, border_radius=8)
        
        # Título
        titulo = self.fuente_p.render("AJUSTES", True, ORO)
        self.pantalla.blit(titulo, (panel_x + panel_ancho//2 - titulo.get_width()//2, panel_y + 10))
        
        # Opciones del menú - EXPANDIDAS
        opciones = [
            {"txt": "Guardar Partida", "id": "guardar"},
            {"txt": "Mis Partidas", "id": "partidas"},
            {"txt": "Cómo Jugar", "id": "ayuda"},
            {"txt": "Clasificación", "id": "ranking"},
            {"txt": "Volver al Menú", "id": "menu"},
        ]
        
        self.botones_ajustes = []
        y_offset = panel_y + 50
        
        for i, opcion in enumerate(opciones):
            btn_rect = pygame.Rect(panel_x + 10, y_offset + (i * 48), panel_ancho - 20, 40)
            self.botones_ajustes.append((btn_rect, opcion["id"]))
            
            # Color del botón
            color_btn = (70, 100, 150) if opcion["id"] not in ["menu"] else (150, 50, 50)
            pygame.draw.rect(self.pantalla, color_btn, btn_rect, border_radius=5)
            pygame.draw.rect(self.pantalla, ORO, btn_rect, 1, border_radius=5)
            
            # Texto
            txt = self.fuente_p.render(opcion["txt"], True, BLANCO)
            self.pantalla.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))

        # Slider música
        texto_musica = self.fuente_p.render("Volumen Música", True, BLANCO)
        self.pantalla.blit(texto_musica, (panel_x + 15, panel_y + 295))
        self.rect_slider_musica = pygame.Rect(panel_x + 15, panel_y + 320, panel_ancho - 30, 12)
        pygame.draw.rect(self.pantalla, (80, 80, 80), self.rect_slider_musica, border_radius=6)
        pygame.draw.rect(self.pantalla, ORO, self.rect_slider_musica, 2, border_radius=6)
        handle_x = self.rect_slider_musica.x + int(self.volumen_musica * (self.rect_slider_musica.width - 12))
        handle = pygame.Rect(handle_x, self.rect_slider_musica.y - 4, 16, 20)
        pygame.draw.rect(self.pantalla, (200, 200, 200), handle, border_radius=4)

        # Slider efectos
        texto_efectos = self.fuente_p.render("Volumen Efectos", True, BLANCO)
        self.pantalla.blit(texto_efectos, (panel_x + 15, panel_y + 350))
        self.rect_slider_efectos = pygame.Rect(panel_x + 15, panel_y + 375, panel_ancho - 30, 12)
        pygame.draw.rect(self.pantalla, (80, 80, 80), self.rect_slider_efectos, border_radius=6)
        pygame.draw.rect(self.pantalla, ORO, self.rect_slider_efectos, 2, border_radius=6)
        handle_x = self.rect_slider_efectos.x + int(self.volumen_efectos * (self.rect_slider_efectos.width - 12))
        handle = pygame.Rect(handle_x, self.rect_slider_efectos.y - 4, 16, 20)
        pygame.draw.rect(self.pantalla, (200, 200, 200), handle, border_radius=4)

    def cargar_sonidos(self):
        ruta_sonidos = os.path.join(BASE_DIR, "assets", "sonidos")
        sonido_info = {
            "construir": "construir.mp3",
            "error": "error.mp3",
            "dinero": "dinero.mp3",
            "evento": "evento.mp3",
            "nivel": "nivel.mp3",
            "cerrar": "cerrar.mp3"
        }

        for clave, archivo in sonido_info.items():
            ruta = os.path.join(ruta_sonidos, archivo)
            if os.path.exists(ruta):
                try:
                    self.sonidos[clave] = pygame.mixer.Sound(ruta)
                    self.sonidos[clave].set_volume(self.volumen_efectos)
                except Exception as e:
                    print(f"Aviso: no se pudo cargar {archivo} -> {e}")
                    self.sonidos[clave] = None
            else:
                print(f"Aviso: no se encontró el archivo de sonido {ruta}")
                self.sonidos[clave] = None

        ruta_musica = os.path.join(ruta_sonidos, "juego.mp3")
        if os.path.exists(ruta_musica):
            try:
                pygame.mixer.music.load(ruta_musica)
                pygame.mixer.music.set_volume(self.volumen_musica)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Aviso: no se pudo cargar música de fondo -> {e}")
        else:
            print(f"Aviso: no se encontró la música de fondo {ruta_musica}")

    def reproducir_sonido(self, nombre):
        s = self.sonidos.get(nombre)
        if s:
            try:
                s.set_volume(self.volumen_efectos)
                s.play()
            except:
                pass

    def actualizar_volumen_efectos(self, valor):
        self.volumen_efectos = max(0.0, min(1.0, valor))
        for s in self.sonidos.values():
            if s:
                try:
                    s.set_volume(self.volumen_efectos)
                except:
                    pass

    def dibujar_dialogo_sin_habitantes(self):
        # 1. Fondo oscurecido
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.pantalla.blit(s, (0, 0))

        # 2. CUADRO PRINCIPAL
        cuadro = pygame.Rect(self.ancho//2 - 300, self.alto//2 - 150, 600, 300)
        pygame.draw.rect(self.pantalla, (40, 40, 40), cuadro, border_radius=20)
        pygame.draw.rect(self.pantalla, ROJO, cuadro, 4, border_radius=20)

        # 3. TÍTULO
        txt_tit = self.fuente_g.render("¡GAME OVER!", True, ROJO)
        self.pantalla.blit(txt_tit, (cuadro.centerx - txt_tit.get_width()//2, cuadro.y + 30))

        # 4. MENSAJE
        txt_msg1 = self.fuente_m.render("Te has quedado sin habitantes", True, BLANCO)
        self.pantalla.blit(txt_msg1, (cuadro.centerx - txt_msg1.get_width()//2, cuadro.y + 100))
        
        txt_msg2 = self.fuente_p.render("Tu ciudad no sobrevivió sin ciudadanos", True, AMARILLO)
        self.pantalla.blit(txt_msg2, (cuadro.centerx - txt_msg2.get_width()//2, cuadro.y + 150))

        # 5. BOTÓN VOLVER AL MENÚ
        self.btn_volver_menu_despoblacion = pygame.Rect(cuadro.centerx - 120, cuadro.y + 220, 240, 50)
        pygame.draw.rect(self.pantalla, (150, 50, 50), self.btn_volver_menu_despoblacion, border_radius=12)
        pygame.draw.rect(self.pantalla, ROJO, self.btn_volver_menu_despoblacion, 2, border_radius=12)
        
        txt_btn = self.fuente_m.render("VOLVER AL MENÚ", True, BLANCO)
        self.pantalla.blit(txt_btn, (self.btn_volver_menu_despoblacion.centerx - txt_btn.get_width()//2, 
                                     self.btn_volver_menu_despoblacion.centery - txt_btn.get_height()//2))

    def dibujar_ayuda(self):
        """Dibuja la pantalla de Cómo Jugar"""
        # Panel semitransparente
        panel_rect = pygame.Rect(100, 80, ANCHO - 200, ALTO - 180)
        pygame.draw.rect(self.pantalla, (20, 20, 20), panel_rect, border_radius=8)
        pygame.draw.rect(self.pantalla, ORO, panel_rect, 3, border_radius=8)
        
        # Título
        titulo = self.fuente_g.render("CÓMO JUGAR", True, ORO)
        self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))
        
        # Contenido
        lineas = [
            "OBJETIVO: Construye y expande tu ciudad para que tenga los mejores servicios.",
            "",
            "DINERO: Gana dinero cada año para invertir en nuevas edificaciones.",
            "",
            "RECURSOS: Gestiona comida, agua y electricidad para mantener tu población feliz.",
            "",
            "POBLACIÓN: Aumenta el número de ciudadanos construyendo viviendas y servicios.",
            "",
            "OFICINA DE TURISMO: Atrae más población a tu ciudad de forma más rápida.",
            "",
            "FELICIDAD: La población necesita servicios cercanos. Mayor felicidad = más recursos.",
            "",
            "TIENDA: Compra edificios nuevos. Cada edificio ocupa 3x3 celdas en tu mapa.",
            "",
            "GUARDAR: Usa el botón de Ajustes para guardar tu progreso en cualquier momento.",
        ]
        
        y_start = 150
        for i, linea in enumerate(lineas):
            if linea == "":
                continue
            txt = self.fuente_p.render(linea, True, BLANCO)
            self.pantalla.blit(txt, (120, y_start + (i * 25)))
        
        # Botón volver
        btn_volver = pygame.Rect(ANCHO//2 - 100, ALTO - 130, 200, 40)
        pygame.draw.rect(self.pantalla, (100, 50, 50), btn_volver, border_radius=5)
        pygame.draw.rect(self.pantalla, ORO, btn_volver, 2, border_radius=5)
        txt_volver = self.fuente_p.render("VOLVER", True, BLANCO)
        self.pantalla.blit(txt_volver, (btn_volver.centerx - txt_volver.get_width()//2, btn_volver.centery - txt_volver.get_height()//2))
        
        self.btn_volver_ayuda = btn_volver

    def dibujar_popup_confirmacion_investigacion(self):
        # 1. Configuración de colores y dimensiones
        DORADO = (255, 215, 0)
        NEGRO_FONDO = (15, 15, 15)
        GRIS_BORDE = (60, 60, 60)
        VERDE_BT = (34, 139, 34)
        ROJO_BT = (178, 34, 34)
        
        # Subimos el ancho a 500 para que quepan los nombres largos
        ancho, alto = 500, 320 
        x_pop = (self.ancho - ancho) // 2
        y_pop = (self.alto - alto) // 2
        rect_pop = pygame.Rect(x_pop, y_pop, ancho, alto)
        
        # 2. Dibujar Fondo y Borde Dorado
        pygame.draw.rect(self.pantalla, NEGRO_FONDO, rect_pop, border_radius=15)
        pygame.draw.rect(self.pantalla, DORADO, rect_pop, 3, border_radius=15)
        
        # Obtener datos de la investigación seleccionada desde logica_ciudad
        datos = self.logica.datos_investigacion.get(self.investigacion_seleccionada)
        if not datos:
            return
        
        # 3. Título Dinámico
        titulo_str = f"¿DESBLOQUEAR {datos['titulo'].upper()}?"
        txt_tit = self.fuente_m.render(titulo_str, True, (255, 255, 255))
        self.pantalla.blit(txt_tit, (rect_pop.centerx - txt_tit.get_width()//2, rect_pop.y + 25))
        
        # Línea divisoria
        pygame.draw.line(self.pantalla, GRIS_BORDE, (rect_pop.x + 30, rect_pop.y + 65), (rect_pop.right - 30, rect_pop.y + 65), 1)

        # 4. Información Detallada
        # --- COSTE ---
        txt_coste = self.fuente_p.render(f"• Coste: ${datos['coste_dinero']}", True, (200, 200, 200))
        self.pantalla.blit(txt_coste, (rect_pop.x + 40, rect_pop.y + 85))
        
        # --- REQUISITOS ---
        txt_req = self.fuente_p.render(f"• Requisitos: {datos['pob_req']} Habitantes", True, (200, 200, 200))
        self.pantalla.blit(txt_req, (rect_pop.x + 40, rect_pop.y + 115))
        
        # --- DESBLOQUEOS (Desde datos de logica) ---
        edificios_str = ", ".join(datos.get("edificios_desbloquea", []))
        txt_des = self.fuente_p.render(f"• Desbloqueos: {edificios_str}", True, (0, 255, 255))
        self.pantalla.blit(txt_des, (rect_pop.x + 40, rect_pop.y + 145))

        # 5. BOTONES (Con borde dorado)
        self.btn_inv_si = pygame.Rect(rect_pop.x + 50, rect_pop.y + 220, 160, 50)
        self.btn_inv_no = pygame.Rect(rect_pop.right - 210, rect_pop.y + 220, 160, 50)
        
        # Dibujar Botón CONFIRMAR
        pygame.draw.rect(self.pantalla, VERDE_BT, self.btn_inv_si, border_radius=8)
        pygame.draw.rect(self.pantalla, DORADO, self.btn_inv_si, 2, border_radius=8)
        
        # Dibujar Botón CANCELAR
        pygame.draw.rect(self.pantalla, ROJO_BT, self.btn_inv_no, border_radius=8)
        pygame.draw.rect(self.pantalla, DORADO, self.btn_inv_no, 2, border_radius=8)
        
        # Textos de los botones
        txt_si = self.fuente_p.render("CONFIRMAR", True, (255, 255, 255))
        txt_no = self.fuente_p.render("CANCELAR", True, (255, 255, 255))
        
        self.pantalla.blit(txt_si, (self.btn_inv_si.centerx - txt_si.get_width()//2, self.btn_inv_si.centery - txt_si.get_height()//2))
        self.pantalla.blit(txt_no, (self.btn_inv_no.centerx - txt_no.get_width()//2, self.btn_inv_no.centery - txt_no.get_height()//2))

    def cargar_ranking_global(self):
        """Carga todas las partidas guardadas y las ordena por dinero."""
        # ✓ ARREGLO 2: Quitar filtro por año - mostrar ranking global
        partidas_ranking = []
        carpeta_usuarios = os.path.join(BASE_DIR, "usuarios")
        
        if os.path.exists(carpeta_usuarios):
            for archivo in os.listdir(carpeta_usuarios):
                if archivo.startswith("partidas_") and archivo.endswith(".json"):
                    ruta_completa = os.path.join(carpeta_usuarios, archivo)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            datos = json.load(f)
                            año_partida = datos.get("año", 1)
                            
                            nombre_usuario = archivo.replace("partida_", "").replace(".json", "")
                            partidas_ranking.append({
                                "usuario": nombre_usuario,
                                "dinero": datos.get("dinero", 0),
                                "año": año_partida,
                                "poblacion": len(datos.get("poblacion", [])),
                                "felicidad": sum(p.get("felicidad", 0) for p in datos.get("poblacion", [])) // max(len(datos.get("poblacion", [])), 1),
                                "recursos": datos.get("recursos", {}),
                            })
                    except:
                        pass
        
        # Ordenar por dinero descendente
        partidas_ranking.sort(key=lambda x: x["dinero"], reverse=True)
        return partidas_ranking[:100]  # Top 100

    def dibujar_ranking(self):
        """Dibuja la pantalla de Clasificación Global"""
        # Panel semitransparente
        panel_rect = pygame.Rect(50, 80, ANCHO - 100, ALTO - 180)
        pygame.draw.rect(self.pantalla, (20, 20, 20), panel_rect, border_radius=8)
        pygame.draw.rect(self.pantalla, ORO, panel_rect, 3, border_radius=8)
        
        # ✓ ARREGLO 2: Mostrar ranking global (sin filtro de año)
        titulo = self.fuente_g.render("CLASIFICACIÓN GLOBAL - TOP 100", True, ORO)
        self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))
        
        # Cargar ranking global sin filtro
        ranking = self.cargar_ranking_global()
        
        if not ranking:
            txt_vacio = self.fuente_p.render("No hay partidas guardadas todavía.", True, CIAN)
            self.pantalla.blit(txt_vacio, (ANCHO//2 - txt_vacio.get_width()//2, ALTO//2))
        else:
            # Encabezados
            y_start = 150
            encabezados = ["Pos.", "Usuario", "Dinero", "Años", "Población", "Felicidad"]
            x_positions = [60, 120, 280, 380, 470, 580]
            
            for i, encab in enumerate(encabezados):
                txt = self.fuente_p.render(encab, True, ORO)
                self.pantalla.blit(txt, (x_positions[i], y_start))
            
            # Mostrar ranking (solo los primeros 10 en pantalla)
            for idx, partida in enumerate(ranking[:10]):
                y_pos = y_start + 35 + (idx * 30)
                if y_pos > ALTO - 100:
                    break
                
                color_texto = (255, 215, 0) if idx == 0 else (192, 192, 192) if idx == 1 else (205, 127, 50) if idx == 2 else BLANCO
                
                datos = [
                    str(idx + 1),
                    partida["usuario"],
                    f"${partida['dinero']:,}",
                    str(partida["año"]),
                    str(partida["poblacion"]),
                    f"{partida['felicidad']:.0f}%"
                ]
                
                for i, dato in enumerate(datos):
                    txt = self.fuente_p.render(dato, True, color_texto)
                    self.pantalla.blit(txt, (x_positions[i], y_pos))
        
        # Botón volver
        btn_volver = pygame.Rect(ANCHO//2 - 100, ALTO - 130, 200, 40)
        pygame.draw.rect(self.pantalla, (100, 50, 50), btn_volver, border_radius=5)
        pygame.draw.rect(self.pantalla, ORO, btn_volver, 2, border_radius=5)
        txt_volver = self.fuente_p.render("VOLVER", True, BLANCO)
        self.pantalla.blit(txt_volver, (btn_volver.centerx - txt_volver.get_width()//2, btn_volver.centery - txt_volver.get_height()//2))
        
        self.btn_volver_ranking = btn_volver
    
    def dibujar_popup_evento(self):
        if self.logica.mostrar_popup_evento and self.logica.evento_actual:
            evento = self.logica.evento_actual

            # Fondo oscuro degradado más sutil
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((5, 5, 15, 220))
            self.pantalla.blit(overlay, (0, 0))

            # Cuadro principal elegante
            w, h = 600, 360
            x = (ANCHO - w) // 2
            y = (ALTO - h) // 2
            rect_fondo = pygame.Rect(x, y, w, h)
            pygame.draw.rect(self.pantalla, (15, 20, 45), rect_fondo, border_radius=22)
            pygame.draw.rect(self.pantalla, (230, 210, 80), rect_fondo, 4, border_radius=22)

            # Título y texto centrado
            txt_tit = self.fuente_g.render(evento["titulo"], True, (255, 240, 140))
            self.pantalla.blit(txt_tit, (rect_fondo.centerx - txt_tit.get_width()//2, y + 25))

            # Texto de mensaje en multiline
            lines = []
            words = evento["mensaje"].split(" ")
            curr = ""
            for word in words:
                if self.fuente_p.size(curr + " " + word)[0] > w - 60:
                    lines.append(curr)
                    curr = word
                else:
                    curr = (curr + " " + word).strip()
            if curr:
                lines.append(curr)

            for i, line in enumerate(lines):
                txt_msg = self.fuente_p.render(line, True, (230, 230, 230))
                self.pantalla.blit(txt_msg, (x + 30, y + 100 + i*28))

            # Botones A / B (Ayudar / Ignorar)
            self.rect_opcion_a = pygame.Rect(x + 40, y + 260, 230, 50)
            self.rect_opcion_b = pygame.Rect(x + 330, y + 260, 230, 50)

            # Soft shadow
            sombra = pygame.Surface((w - 20, 70), pygame.SRCALPHA)
            sombra.fill((6, 6, 31, 100))
            self.pantalla.blit(sombra, (x + 10, y + 255))

            pygame.draw.rect(self.pantalla, (50, 165, 80), self.rect_opcion_a, border_radius=16)
            pygame.draw.rect(self.pantalla, (220, 55, 60), self.rect_opcion_b, border_radius=16)
            pygame.draw.rect(self.pantalla, (255, 255, 255), self.rect_opcion_a, 2, border_radius=16)
            pygame.draw.rect(self.pantalla, (255, 255, 255), self.rect_opcion_b, 2, border_radius=16)

            btn_a_text = "AYUDAR"
            btn_b_text = "IGNORAR"

            txt_a = self.fuente_g.render(btn_a_text, True, BLANCO)
            txt_b = self.fuente_g.render(btn_b_text, True, BLANCO)
            self.pantalla.blit(txt_a, (self.rect_opcion_a.centerx - txt_a.get_width() // 2, self.rect_opcion_a.centery - txt_a.get_height() // 2))
            self.pantalla.blit(txt_b, (self.rect_opcion_b.centerx - txt_b.get_width() // 2, self.rect_opcion_b.centery - txt_b.get_height() // 2))

            # Texto adicional (opciones originales)
            txt_detalle_a = self.fuente_p.render(evento.get("opcion_a", ""), True, (210, 255, 210))
            txt_detalle_b = self.fuente_p.render(evento.get("opcion_b", ""), True, (255, 210, 210))
            self.pantalla.blit(txt_detalle_a, (x + 40, y + 320))
            self.pantalla.blit(txt_detalle_b, (x + 330, y + 320))

            # Botón cerrar X
            self.rect_popup_cerrar = pygame.Rect(rect_fondo.right - 34, rect_fondo.top + 10, 24, 24)
            pygame.draw.circle(self.pantalla, (200, 60, 60), self.rect_popup_cerrar.center, 12)
            txt_x = self.fuente_m.render("X", True, (255, 255, 255))
            self.pantalla.blit(txt_x, (self.rect_popup_cerrar.centerx - txt_x.get_width()//2, self.rect_popup_cerrar.centery - txt_x.get_height()//2))

            # Habilitar click de cierre manual: se gestiona en el bucle de eventos

    def finalizar_investigacion(self):
        idtec = self.investigando_id
        
        if idtec is None:
            return

        # ✅ MARCAR COMO COMPLETADA EN LOGICA_CIUDAD (desbloquea edificios)
        exito, mensaje = self.logica.completar_investigacion(idtec)
        
        if exito:
            # ✅ MARCAR COMO COMPLETADA TAMBIÉN AQUÍ
            self.investigaciones_completadas.add(idtec)
            
            # ✅ LA NOTICIA YA SE CREA EN LOGICA_CIUDAD
        else:
            print(f"Error al completar investigación: {mensaje}")

        # ✅ RESET
        self.investigando_id = None
        self.tiempo_investigacion = 0

    def dibujar_menu_investigacion(self):
        # 1. Fondo oscuro
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) 
        self.pantalla.blit(overlay, (0, 0))

        # 2. Configuración de dimensiones
        ancho_m, alto_m = 900, 650
        x_menu = (self.ancho - ancho_m) // 2
        y_menu = (self.alto - alto_m) // 2
        centro_x, centro_y = x_menu + ancho_m // 2, y_menu + alto_m // 2

        # 3. Dibujar marco principal
        rect_fondo = pygame.Rect(x_menu, y_menu, ancho_m, alto_m)
        pygame.draw.rect(self.pantalla, (15, 15, 25), rect_fondo, border_radius=20)
        pygame.draw.rect(self.pantalla, (0, 255, 255), rect_fondo, 2, border_radius=20)

        # 4. Título y Botón Cerrar
        self.pantalla.blit(self.fuente_g.render("LABORATORIO TECNOLÓGICO", True, (0, 255, 255)), (x_menu + 40, y_menu + 30))
        self.btn_cerrar_investigacion = pygame.Rect(x_menu + ancho_m - 50, y_menu + 20, 30, 30)
        self.pantalla.blit(self.img_cerrar, (self.btn_cerrar_investigacion.x, self.btn_cerrar_investigacion.y))

        # 5. CUADRO CENTRAL (Nivel de Ciudad)
        nivel = self.logica.nivel_tecnologico
        rect_centro = pygame.Rect(centro_x - 80, centro_y - 40, 160, 80)
        
        # Generar dinámicamente los nodos según el nivel
        investigaciones_disponibles = self.logica.obtener_investigaciones_disponibles()
        
        # ✓ ARREGLO 2: Mapeo explícito de tipos de investigación a posiciones
        # Este mapeo es independiente del orden del diccionario
        mapa_tipos_posiciones = {
            "comida": ("COMIDA", (-280, -180)),
            "agua": ("AGUA", (120, -180)),
            "energia": ("ENERGÍA", (-280, 100)),
            "alojamiento": ("ALOJAMIENTO", (120, 100))
        }
        
        nodos_data = []
        
        # Para cada tipo de investigación base
        for tipo_base, (nombre_base, offset) in mapa_tipos_posiciones.items():
            # Buscar si existe una investigación disponible de este tipo
            inv_id = None
            inv_datos = None
            
            for clave, datos in investigaciones_disponibles.items():
                if tipo_base in clave:  # comida_2, comida_3, etc.
                    inv_id = clave
                    inv_datos = datos
                    break
            
            if inv_id:
                # Hay investigación disponible para este tipo
                nivel_inv = inv_datos.get("nivel", 2)
                nombre_display = f"{nombre_base} NVL {nivel_inv}"
                nodos_data.append((nombre_display, offset, inv_id, inv_datos))
            else:
                # No hay investigación disponible (ya completada o bloqueada)
                nodos_data.append((nombre_base, offset, "vacio", {}))

        self.botones_investigacion = {}

        # --- DIBUJO DE LÍNEAS ---
        for nombre, pos, id_nodo, inv_datos in nodos_data:
            if id_nodo == "vacio":
                continue
                
            rect_nodo = pygame.Rect(centro_x + pos[0], centro_y + pos[1], 180, 100)
            self.botones_investigacion[id_nodo] = rect_nodo
            
            punto_inicio = rect_centro.center
            punto_final = rect_nodo.center
            punto_codo = (punto_final[0], punto_inicio[1]) 
            pygame.draw.lines(self.pantalla, (0, 200, 200), False, [punto_inicio, punto_codo, punto_final], 3)

        # 6. DIBUJAR LOS CUADROS
        # Cuadro Central
        pygame.draw.rect(self.pantalla, (40, 40, 60), rect_centro, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 215, 0), rect_centro, 3, border_radius=10)
        self.pantalla.blit(self.fuente_p.render("NIVEL CIUDAD", True, (200, 200, 200)), (rect_centro.x + 25, rect_centro.y + 10))
        self.pantalla.blit(self.fuente_g.render(str(nivel), True, (255, 255, 255)), (rect_centro.centerx - 10, rect_centro.y + 35))

        # Cuadros Periféricos (CON BARRA DE PROGRESO)
        for nombre, pos, id_nodo, inv_datos in nodos_data:
            if id_nodo == "vacio":
                continue
                
            rect_nodo = pygame.Rect(centro_x + pos[0], centro_y + pos[1], 180, 100)
            
            # Comprobar estado
            esta_hecho = id_nodo in self.logica.investigaciones_completadas
            siendo_investigado = (self.investigando_id == id_nodo)
            
            # Color del borde dinámico
            color_borde = (255, 215, 0) if esta_hecho else (0, 255, 0) if siendo_investigado else (0, 255, 255)
            
            pygame.draw.rect(self.pantalla, (30, 30, 45), rect_nodo, border_radius=10)
            pygame.draw.rect(self.pantalla, color_borde, rect_nodo, 2, border_radius=10)
            
            if esta_hecho:
                # Caso: YA COMPLETADO
                txt_node = self.fuente_p.render(nombre, True, (100, 100, 100))
                txt_status = self.fuente_p.render("COMPLETADO", True, (255, 215, 0))
                # Centrar horizontalmente
                self.pantalla.blit(txt_node, (rect_nodo.centerx - txt_node.get_width()//2, rect_nodo.y + 20))
                self.pantalla.blit(txt_status, (rect_nodo.centerx - txt_status.get_width()//2, rect_nodo.y + 50))
                
            elif siendo_investigado:
                # Caso: EN PROCESO (Barra de carga)
                txt_status = self.fuente_p.render("INVESTIGANDO...", True, (0, 255, 0))
                self.pantalla.blit(txt_status, (rect_nodo.centerx - txt_status.get_width()//2, rect_nodo.y + 30))
                
                # Dibujar barra
                progreso = self.tiempo_investigacion / 300 # 300 es el tiempo total
                ancho_barra = rect_nodo.width - 40
                pygame.draw.rect(self.pantalla, (50, 50, 50), (rect_nodo.x + 20, rect_nodo.y + 65, ancho_barra, 12), border_radius=5)
                pygame.draw.rect(self.pantalla, (0, 255, 0), (rect_nodo.x + 20, rect_nodo.y + 65, ancho_barra * progreso, 12), border_radius=5)
                
            else:
                # Caso: DISPONIBLE - CENTRADO PARA EVITAR QUE SE SALGA
                txt_node = self.fuente_p.render(nombre, True, (255, 255, 255))
                self.pantalla.blit(txt_node, (rect_nodo.centerx - txt_node.get_width()//2, rect_nodo.y + 40))

        # 7. POPUP DE CONFIRMACIÓN (Si hay uno seleccionado)
        if self.investigacion_seleccionada:
            self.dibujar_popup_confirmacion_investigacion()

    def procesar_investigacion(self, id_nodo):
    
        if id_nodo in self.investigaciones_completadas:
            print("Ya investigado")
            return

        """Ahora esta función solo cobra e INICIA el proceso de tiempo"""
        datos = self.logica.datos_investigacion.get(id_nodo)
        if not datos:
            print(f"Investigación {id_nodo} no encontrada")
            return
            
        coste = datos["coste_dinero"]
        pob_req = datos["pob_req"]
        pob_actual = len(self.logica.poblacion)

        # 1. Comprobar Dinero y Población
        if self.logica.dinero >= coste and pob_actual >= pob_req:
            # COBRAR
            self.logica.dinero -= coste
            
            # INICIAR EL RELOJ
            self.investigando_id = id_nodo
            self.tiempo_investigacion = 0
            
            # Avisar que empezó (en tu sistema de noticias)
            self.logica.noticias.append({
                "txt": f"Iniciando investigación: {datos['titulo']}", 
                "tipo": "AVISO"
            })
            
            # Cerrar el popup de confirmación
            self.investigacion_seleccionada = None
            
        elif pob_actual < pob_req:
            print(f"Faltan habitantes. Requieres {pob_req}")
            # Aquí podrías poner un cartel de "Población insuficiente"
        else:
            self.dialogo_dinero_insuficiente = True
            self.dinero_faltante = coste - self.logica.dinero

    def generar_evento_aleatorio(self):
        # Filtramos eventos que el jugador pueda cumplir (por población, dinero, etc.)
        # Corrección rápida:
        posibles = [e for e in self.pool_eventos if len(self.poblacion) >= e.get("requisito_poblacion", 0)]
        
        if posibles:
            self.evento_actual = random.choice(posibles)
            self.interfaz.mostrar_popup_evento = True # Esto avisa a la clase principal

    def aplicar_efectos_evento(self, efectos):
        # 'efectos' es el diccionario (ej: {"dinero_extra": 0.30, "felicidad": 15})
        for recurso, valor in efectos.items():
            
            # 1. DINERO (Si es porcentaje, calculamos sobre el total actual)
            if recurso == "dinero_extra":
                ganancia = int(self.logica.dinero * valor)
                self.logica.dinero += ganancia
                self.logica.noticias.append({"txt": f"Ganancia extra: +${ganancia}", "tipo": "BUENO"})
            
            # 2. COMIDA (Acceso directo a tu diccionario de recursos o variable)
            elif recurso == "comida":
                self.logica.recursos["comida"] += valor
                
            # 3. FELICIDAD (Como es individual, hay que sumársela a cada habitante)
            elif recurso == "felicidad":
                for hab in self.logica.poblacion:
                    hab.felicidad = max(0, min(100, hab.felicidad + valor))
                    
            # 4. HABITANTES / POBLACIÓN
            elif recurso in ("habitantes", "poblacion_extra"):
                # valor puede ser porcentaje (negativo/positivo) o número entero
                if abs(valor) < 1:
                    cambio = int(len(self.logica.poblacion) * valor)
                else:
                    cambio = int(valor)

                if cambio > 0:
                    nuevos = min(cambio, max(0, self.logica.capacidad_max_poblacion - len(self.logica.poblacion)))
                    for _ in range(nuevos):
                        self.logica.agregar_ciudadano()
                    self.logica.noticias.append({"txt": f"Inmigración de evento: +{nuevos}", "tipo": "AVISO"})

                elif cambio < 0:
                    muertos = min(abs(cambio), len(self.logica.poblacion))
                    for _ in range(muertos):
                        self.logica.poblacion.pop()
                    self.logica.noticias.append({"txt": f"Crisis: -{muertos} habitantes", "tipo": "CRITICO"})

        # IMPORTANTE: Al terminar, cerramos el popup
        self.mostrar_popup_evento = False
        self.evento_actual = None

    def ejecutar(self):
        while self.corriendo:
            self.pantalla.fill(NEGRO)
            
            # --- VERIFICAR CAMBIO DE RANGO ---
            if self.rango_anterior is None:
                self.rango_anterior = self.logica.rango_actual
            
            if self.logica.rango_actual != self.rango_anterior:
                self.rango_anterior = self.logica.rango_actual
                self.nuevo_rango = self.logica.rango_actual
                # NO mostrará popup de rango, solo se registra como noticia
                self.logica.noticias.append({"txt": f"Ciudad nivel: {self.nuevo_rango}", "tipo": "AVISO"})
            
            if hasattr(self, 'investigando_id') and self.investigando_id is not None:
                self.tiempo_investigacion += 1
                
                # Si llega al tiempo (300 frames = 5 seg aprox a 60 FPS)
                if self.tiempo_investigacion >= 300:
                    self.finalizar_investigacion()

            # 🔥 VERIFICAR SI SE QUEDÓ SIN HABITANTES
            if len(self.logica.poblacion) == 0 and not self.sin_habitantes_mostrado:
                self.dialogo_sin_habitantes = True
                self.sin_habitantes_mostrado = True
            
            # Si debe volver al menú
            if self.volver_al_menu:
                # Limpiar la partida con 0 habitantes del JSON (ELIMINARLA, no guardarla)
                self._limpiar_partida_sin_habitantes()
                # Mostrar menú de partidas nuevamente
                self.mostrar_menu_partidas_nuevamente()
                # Recargar LogicaCiudad con la nueva partida seleccionada
                nombre_partida = self.partida_actual.get("nombre", f"Año 0") if isinstance(self.partida_actual, dict) else f"Año 0"
                self.logica = LogicaCiudad(self, nombre_partida)
                self.logica.cargar_partida(self.partida_actual)
                # Reset de variables
                self.sin_habitantes_mostrado = False
                self.volver_al_menu = False
                self.dialogo_sin_habitantes = False
                self.edificios_construidos = {ed[0]: 0 for ed in EDIFICACIONES}
                for edificio in self.logica.edificios:
                    if edificio.nombre in self.edificios_construidos:
                        self.edificios_construidos[edificio.nombre] += 1
                continue
            
            # --- CAPA 1: MAPA Y EDIFICIOS (Fondo) ---
            for f in range(self.filas_mapa):
                for c in range(self.columnas_mapa):
                    tipo = self.mapa_datos[f][c]
                    color = (34, 139, 34) if tipo == 0 else (30, 30, 30) if tipo == 1 else (255, 255, 255)
                    pygame.draw.rect(self.pantalla, color, 
                                   (c * self.tamano_tile, f * self.tamano_tile + MARGEN_HUD_SUP, self.tamano_tile, self.tamano_tile))

            for e in self.logica.edificios:
                rect_edf = (e.x * self.tamano_tile, e.y * self.tamano_tile + MARGEN_HUD_SUP, self.tamano_tile * 3, self.tamano_tile * 3)
                pygame.draw.rect(self.pantalla, e.color, rect_edf, border_radius=3)

            # --- CAPA 2: INTERFAZ BASE ---
            self.dibujar_hud()
            
            # --- CAPA 3: MENÚS (De abajo a arriba en prioridad) ---
            if self.noticias_abiertas: 
                self.dibujar_noticias()

            if self.menu_compra_abierto:
                self.dibujar_tienda()

            if self.mostrando_inventario:
                self.dibujar_inventario()

            if self.mostrando_aviso_inv:
                self.dibujar_aviso_inv()
           
            if self.mostrando_investigacion:
                self.dibujar_menu_investigacion()
            
            if self.dialogo_guardar_abierto:
                self.dibujar_dialogo_guardar_con_nombre()

            if self.menu_ajustes_abierto:
                self.dibujar_menu_ajustes()
            
            if self.mostrando_ayuda:
                self.dibujar_ayuda()
            
            if self.mostrando_ranking:
                self.dibujar_ranking()

            if self.dialogo_dinero_insuficiente:
                self.dibujar_dialogo_dinero_insuficiente()

            if self.dialogo_sin_habitantes:
                self.dibujar_dialogo_sin_habitantes()

            if self.menu_venta_abierto:
                self.dibujar_menu_venta()

            if self.menu_intercambio_abierto:
                self.dibujar_menu_intercambio()

            if self.confirmacion_pendiente:
                self.dibujar_confirmacion()
            
            # --- EVENTO POPUP (DEBE IR SIEMPRE AL FRENTE) ---
            if self.logica.mostrar_popup_evento:
                self.dibujar_popup_evento()

            if self.mostrando_detalle_estado:
                self.dibujar_detalles_estado()
            
            # --- CAMBIO DE RANGO/CLASIFICACIÓN ---
            # (DESACTIVADO a pedido del usuario - solo se muestra en noticias)
            # if self.mostrando_cambio_rango:
            #     self.dibujar_cambio_rango()

            # --- CAPA 4: PROCESAMIENTO DE EVENTOS ---
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.logica.guardar_partida()
                    self.corriendo = False

                # --- EVENTO DE TECLADO ---
                elif ev.type == pygame.KEYDOWN:
                    if self.campo_nombre_activo and self.dialogo_guardar_abierto:
                        if ev.key == pygame.K_BACKSPACE:
                            self.input_nombre_partida = self.input_nombre_partida[:-1]
                        elif ev.key == pygame.K_RETURN:
                            self.logica.guardar_partida_con_nombre(self.input_nombre_partida if self.input_nombre_partida else f"Año {self.logica.año}")
                            self.dialogo_guardar_abierto = False
                            self.campo_nombre_activo = False
                            self.logica.noticias.append({"txt": "¡Partida guardada!", "tipo": "AVISO"})
                        elif len(ev.unicode) > 0 and len(self.input_nombre_partida) < 30:
                            self.input_nombre_partida += ev.unicode
                    elif self.menu_intercambio_abierto:
                        # Input para cantidad de intercambio
                        if ev.key == pygame.K_BACKSPACE:
                            self.cantidad_intercambio = self.cantidad_intercambio // 10
                        elif ev.unicode.isdigit():
                            self.cantidad_intercambio = self.cantidad_intercambio * 10 + int(ev.unicode)
                            self.cantidad_intercambio = min(self.cantidad_intercambio, 999999)  # Límite


                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = ev.pos
                    
                    if self.mostrando_investigacion:
                        # --- CAPA 1: Popup de confirmación (SÍ/NO) ---
                        if self.investigacion_seleccionada:
                            # Botón INVESTIGAR (SÍ)
                            if hasattr(self, 'btn_inv_si') and self.btn_inv_si.collidepoint(pos):
                                # Llamamos a la función que centraliza los requisitos y el inicio del reloj
                                self.procesar_investigacion(self.investigacion_seleccionada)
                                # El popup se cierra dentro de procesar_investigacion (self.investigacion_seleccionada = None)

                            # Botón CANCELAR (NO)
                            elif hasattr(self, 'btn_inv_no') and self.btn_inv_no.collidepoint(pos):
                                self.investigacion_seleccionada = None

                        # --- CAPA 2: Menú general (Nodos de tecnología) ---
                        else:
                            # 1. Cerrar menú con la X
                            if hasattr(self, 'btn_cerrar_investigacion') and self.btn_cerrar_investigacion.collidepoint(pos):
                                self.mostrando_investigacion = False
                            
                            # 2. Click en los nodos para abrir el popup
                            elif hasattr(self, 'botones_investigacion'):
                                for id_nodo, rect in self.botones_investigacion.items():
                                    if rect.collidepoint(pos):
                                        ya_hecha = id_nodo in self.logica.investigaciones_completadas
                                        en_curso = self.investigando_id is not None
                                        
                                        if id_nodo in self.logica.datos_investigacion and not ya_hecha and not en_curso:
                                            self.investigacion_seleccionada = id_nodo
                                        elif en_curso:
                                            print("Ya hay una investigación en curso.")
                                        elif ya_hecha:
                                            print("Tecnología ya adquirida.")
                        
                        continue

                    # 1. Prioridad: Confirmación de compra abierta
                    if self.confirmacion_pendiente:
                        for cant, rect_btn in self.btn_multiplicadores.items():
                            if rect_btn.collidepoint(pos):
                                self.cantidad_a_comprar = cant
                        
                        if self.btn_si.collidepoint(pos):
                            nombre_edf = self.confirmacion_pendiente[0]
                            compras_realizadas = 0
                            
                            for _ in range(self.cantidad_a_comprar):
                                p = self.obtener_posicion_aleatoria()
                                if p:
                                    resultado = self.logica.comprar_edificio(self.confirmacion_pendiente, p[0], p[1])
                                    
                                    # Manejo del nuevo formato de retorno
                                    if isinstance(resultado, dict):
                                        if resultado.get("exito"):
                                            self.celdas_ocupadas.append(p)
                                            if nombre_edf in self.edificios_construidos:
                                                self.edificios_construidos[nombre_edf] += 1
                                            compras_realizadas += 1
                                            self.reproducir_sonido("construir")
                                        elif resultado.get("razón") == "dinero_insuficiente":
                                            # Mostrar diálogo de dinero insuficiente
                                            self.dialogo_dinero_insuficiente = True
                                            self.dinero_faltante = resultado.get("faltante", 0)
                                            self.edificio_intento_compra = resultado.get("nombre", "Desconocido")
                                            self.reproducir_sonido("error")
                                            break
                                    elif resultado:  # Compatibilidad con True/False antiguo
                                        self.celdas_ocupadas.append(p)
                                        if nombre_edf in self.edificios_construidos:
                                            self.edificios_construidos[nombre_edf] += 1
                                        compras_realizadas += 1
                                    else:
                                        break
                            
                            self.confirmacion_pendiente = None
                            self.cantidad_a_comprar = 1
                        elif self.btn_no.collidepoint(pos):
                            self.confirmacion_pendiente = None
                        continue

                    # 2. Inventario abierto
                    if self.mostrando_inventario:
                        if self.btn_cerrar_inv.collidepoint(pos):
                            self.mostrando_inventario = False
                            self.reproducir_sonido("cerrar")
                        elif hasattr(self, 'btn_vender_inv') and self.btn_vender_inv.collidepoint(pos):
                            self.menu_venta_abierto = True
                            self.mostrando_inventario = False
                        if ev.button == 4: self.scroll_inv_y = min(self.scroll_inv_y + 40, 0)
                        if ev.button == 5: self.scroll_inv_y = max(self.scroll_inv_y - 40, -700)
                        continue

                    # 2.3 Menú de venta abierto
                    if self.menu_venta_abierto:
                        # Botón X para cerrar
                        if hasattr(self, 'btn_cerrar_venta') and self.btn_cerrar_venta.collidepoint(pos):
                            self.menu_venta_abierto = False
                            self.edificio_a_vender_seleccionado = None
                            self.cantidad_a_vender = 1
                            continue
                        
                        # Si no hay edificio seleccionado, mostrar lista
                        if not self.edificio_a_vender_seleccionado:
                            if hasattr(self, 'botones_venta_lista'):
                                for btn_rect, ed_data in self.botones_venta_lista:
                                    if btn_rect.collidepoint(pos):
                                        self.edificio_a_vender_seleccionado = ed_data
                                        break
                        else:
                            # Manejar cantidad y venta
                            if hasattr(self, 'btn_multiplicadores_venta'):
                                for cant, rect_btn in self.btn_multiplicadores_venta.items():
                                    if rect_btn.collidepoint(pos):
                                        self.cantidad_a_vender = cant
                            
                            if hasattr(self, 'btn_venta_si') and self.btn_venta_si.collidepoint(pos):
                                # Ejecutar venta
                                resultado = self.logica.vender_edificios(self.edificio_a_vender_seleccionado[0], self.cantidad_a_vender)
                                if resultado:
                                    self.edificios_construidos[self.edificio_a_vender_seleccionado[0]] -= self.cantidad_a_vender
                                    self.logica.noticias.append({"txt": f"Vendiste {self.cantidad_a_vender}x {self.edificio_a_vender_seleccionado[0]}", "tipo": "AVISO"})
                                
                                self.menu_venta_abierto = False
                                self.edificio_a_vender_seleccionado = None
                                self.cantidad_a_vender = 1
                            
                            elif hasattr(self, 'btn_venta_no') and self.btn_venta_no.collidepoint(pos):
                                self.edificio_a_vender_seleccionado = None
                                self.cantidad_a_vender = 1
                        
                        # Scroll para el menú de venta - DINÁMICO Y SIN BUGS
                        if ev.button == 4:  # Rueda arriba
                            self.scroll_inv_y = max(self.scroll_inv_y - 40, 0)
                        if ev.button == 5:  # Rueda abajo
                            # El máximo scroll se calcula dinámicamente en dibujar_menu_venta()
                            self.scroll_inv_y = min(self.scroll_inv_y + 40, 5000)  # Límite alto para seguridad
                        continue

                    # 2.4 Menú de intercambio abierto
                    if self.menu_intercambio_abierto:
                        # Botón X para cerrar
                        if hasattr(self, 'btn_cerrar_intercambio') and self.btn_cerrar_intercambio.collidepoint(pos):
                            self.menu_intercambio_abierto = False
                            self.recurso_dar = None
                            self.recurso_recibir = None
                            self.cantidad_intercambio = 0
                            self.input_cantidad_intercambio_activo = False
                            continue
                        
                        # Input cantidad (se activa/desactiva con click)
                        if hasattr(self, 'input_cantidad_intercambio') and self.input_cantidad_intercambio.collidepoint(pos):
                            self.input_cantidad_intercambio_activo = True
                            continue
                        else:
                            # Si clickeas en otro lado, desactiva el input
                            self.input_cantidad_intercambio_activo = False
                        
                        # Seleccionar recurso a dar
                        if hasattr(self, 'botones_recurso_dar'):
                            for key, btn_rect in self.botones_recurso_dar.items():
                                if btn_rect.collidepoint(pos):
                                    self.recurso_dar = key
                                    break
                        
                        # Seleccionar recurso a recibir
                        if hasattr(self, 'botones_recurso_recibir'):
                            for key, btn_rect in self.botones_recurso_recibir.items():
                                if btn_rect.collidepoint(pos):
                                    self.recurso_recibir = key
                                    break
                        
                        # Botón realizar intercambio
                        if hasattr(self, 'btn_realizar_intercambio') and self.btn_realizar_intercambio.collidepoint(pos):
                            if self.recurso_dar and self.recurso_recibir and self.cantidad_intercambio > 0:
                                exito, msg = self.logica.realizar_intercambio(self.recurso_dar, self.recurso_recibir, self.cantidad_intercambio)
                                if exito:
                                    self.logica.noticias.append({"txt": msg, "tipo": "AVISO"})
                                    self.menu_intercambio_abierto = False
                                    self.recurso_dar = None
                                    self.recurso_recibir = None
                                    self.cantidad_intercambio = 0
                                    self.input_cantidad_intercambio_activo = False
                                else:
                                    self.logica.noticias.append({"txt": msg, "tipo": "CRITICO"})
                        continue

                    # 2.5 Diálogo de dinero insuficiente
                    if self.dialogo_dinero_insuficiente:
                        if hasattr(self, 'btn_dinero_ok') and self.btn_dinero_ok.collidepoint(pos):
                            self.dialogo_dinero_insuficiente = False
                        continue

                    # 2.6 Diálogo de sin habitantes
                    if self.dialogo_sin_habitantes:
                        if hasattr(self, 'btn_volver_menu_despoblacion') and self.btn_volver_menu_despoblacion.collidepoint(pos):
                            self.volver_al_menu = True
                        continue

                    # 3. Aviso de inventario vacío
                    if self.mostrando_aviso_inv:
                        if self.btn_aviso_si.collidepoint(pos):
                            self.mostrando_aviso_inv = False
                            self.menu_compra_abierto = True
                        elif self.btn_aviso_no.collidepoint(pos):
                            self.mostrando_aviso_inv = False
                        continue

                    # 4. Tienda abierta
                    if self.menu_compra_abierto:
                        if self.btn_cerrar.collidepoint(pos):
                            self.menu_compra_abierto = False
                            self.reproducir_sonido("cerrar")
                        elif ev.button == 4: self.scroll_y = min(self.scroll_y + 30, 0)
                        elif ev.button == 5: self.scroll_y -= 30
                        else:
                            for r, data in self.botones_compra:
                                if r.collidepoint(pos):
                                    self.confirmacion_pendiente = data
                        continue

                    # 5. Diálogo de guardado abierto
                    if self.dialogo_guardar_abierto:
                        if self.btn_guardar_si.collidepoint(pos):
                            self.logica.guardar_partida_con_nombre(self.input_nombre_partida if self.input_nombre_partida else f"Año {self.logica.año}")
                            self.dialogo_guardar_abierto = False
                            self.campo_nombre_activo = False
                            # Mostrar noticia de guardado
                            self.logica.noticias.append({"txt": "¡Partida guardada!", "tipo": "AVISO"})
                        elif self.btn_guardar_no.collidepoint(pos):
                            self.dialogo_guardar_abierto = False
                            self.campo_nombre_activo = False
                        elif hasattr(self, 'rect_input_nombre') and self.rect_input_nombre.collidepoint(pos):
                            self.campo_nombre_activo = True
                        continue

                    # 5.5 Menú de ajustes abierto
                    if self.menu_ajustes_abierto:
                        # slider de música
                        if hasattr(self, 'rect_slider_musica') and self.rect_slider_musica.collidepoint(pos):
                            frac = (pos[0] - self.rect_slider_musica.x) / self.rect_slider_musica.width
                            self.volumen_musica = max(0.0, min(1.0, frac))
                            pygame.mixer.music.set_volume(self.volumen_musica)
                            continue

                        # slider de efectos
                        if hasattr(self, 'rect_slider_efectos') and self.rect_slider_efectos.collidepoint(pos):
                            frac = (pos[0] - self.rect_slider_efectos.x) / self.rect_slider_efectos.width
                            self.actualizar_volumen_efectos(max(0.0, min(1.0, frac)))
                            continue

                        manejado = False
                        for btn_rect, opcion_id in self.botones_ajustes:
                            if btn_rect.collidepoint(pos):
                                if opcion_id == "guardar":
                                    self.dialogo_guardar_abierto = True
                                    self.menu_ajustes_abierto = False
                                    self.reproducir_sonido("cerrar")
                                elif opcion_id == "partidas":
                                    menu_partidas = MenuPartidas(self.pantalla, self.usuario_nombre)
                                    resultado = menu_partidas.ejecutar()
                                    
                                    if resultado == "volver":
                                        self.menu_ajustes_abierto = False
                                        self.reproducir_sonido("cerrar")
                                    elif resultado != "nueva":
                                        # Cargar la partida seleccionada
                                        self.partida_actual = resultado
                                        self.logica = LogicaCiudad(self, self.partida_actual.get("nombre", "Nueva Partida"))
                                        self.logica.cargar_partida(self.partida_actual)

                                        
                                        # Sincronizar edificios
                                        for edificio in self.logica.edificios:
                                            if edificio.nombre in self.edificios_construidos:
                                                self.edificios_construidos[edificio.nombre] += 1
                                        
                                        self.menu_ajustes_abierto = False
                                        self.reproducir_sonido("cerrar")
                                elif opcion_id == "ayuda":
                                    self.mostrando_ayuda = True
                                    self.menu_ajustes_abierto = False
                                    self.reproducir_sonido("cerrar")
                                elif opcion_id == "ranking":
                                    self.mostrando_ranking = True
                                    self.menu_ajustes_abierto = False
                                    self.reproducir_sonido("cerrar")
                                elif opcion_id == "menu":
                                    self.logica.guardar_partida()
                                    self.volver_al_menu = True
                                    self.menu_ajustes_abierto = False
                                    self.reproducir_sonido("cerrar")
                                manejado = True
                                break
                        
                        if manejado:
                            continue

                    # 5.6 Pantalla de Ayuda abierta
                    if self.mostrando_ayuda:
                        if hasattr(self, 'btn_volver_ayuda') and self.btn_volver_ayuda.collidepoint(pos):
                            self.mostrando_ayuda = False
                        continue

                    # 5.7 Pantalla de Ranking abierta
                    if self.mostrando_ranking:
                        if hasattr(self, 'btn_volver_ranking') and self.btn_volver_ranking.collidepoint(pos):
                            self.mostrando_ranking = False
                        continue

                    # 6. Prioridad Alta: Eventos Aleatorios (Popup de Si/No)
                    if self.logica.mostrar_popup_evento and self.logica.evento_actual:
                        # Cerrar con la X
                        if hasattr(self, 'rect_popup_cerrar') and self.rect_popup_cerrar.collidepoint(pos):
                            self.logica.mostrar_popup_evento = False
                            self.logica.evento_actual = None
                            self.reproducir_sonido("cerrar")
                            continue

                        # OPCIÓN A (Invertir/Aceptar)
                        if hasattr(self, 'rect_opcion_a') and self.rect_opcion_a.collidepoint(pos):
                            porcentaje = self.logica.evento_actual.get("porcentaje_coste_a", 0)
                            coste_real = int(self.logica.dinero * porcentaje)
                            
                            if self.logica.dinero >= coste_real:
                                efectos = self.logica.evento_actual.get("efecto_a", {})
                                self.logica.aplicar_efectos_evento(efectos, coste_real)
                                self.reproducir_sonido("evento")
                            else:
                                self.logica.noticias.append({"txt": "Dinero insuficiente para esta opción", "tipo": "CRITICO"})
                                self.reproducir_sonido("error")
                            continue # Evita que el click active botones que hay debajo

                        # OPCIÓN B (Ignorar) -> penaliza un poco felicidad
                        elif hasattr(self, 'rect_opcion_b') and self.rect_opcion_b.collidepoint(pos):
                            efectos = self.logica.evento_actual.get("efecto_b", {}).copy()
                            efectos["felicidad"] = efectos.get("felicidad", 0) - 10
                            self.logica.aplicar_efectos_evento(efectos, 0)
                            self.logica.noticias.append({"txt": "Ignoraste el evento y la gente está descontenta", "tipo": "CRITICO"})
                            continue

                    # 6.5. Popup de detalles de estado abierto
                    if self.mostrando_detalle_estado:
                        if hasattr(self, 'rect_detalle_cerrar') and self.rect_detalle_cerrar and self.rect_detalle_cerrar.collidepoint(pos):
                            self.mostrando_detalle_estado = False
                            self.detalle_estado_tipo = None
                        elif hasattr(self, 'rect_detalle_popup') and self.rect_detalle_popup and not self.rect_detalle_popup.collidepoint(pos):
                            self.mostrando_detalle_estado = False
                            self.detalle_estado_tipo = None
                        continue

                    # 7. Botones del HUD Principal (Solo si no hay popups bloqueantes)
                    if self.btn_next.collidepoint(pos):
                        self.logica.avanzar_año()

                    elif self.btn_tienda.collidepoint(pos):
                        self.menu_compra_abierto = not self.menu_compra_abierto
                        self.mostrando_investigacion = False
                        self.mostrando_inventario = False
                        self.menu_intercambio_abierto = False
                        self.noticias_abiertas = False
                        
                    elif self.btn_intercambio.collidepoint(pos):
                        self.menu_intercambio_abierto = not self.menu_intercambio_abierto
                        self.menu_compra_abierto = False
                        self.mostrando_investigacion = False
                        self.mostrando_inventario = False
                        self.noticias_abiertas = False
                        
                    elif self.rect_hud_info.get("felicidad") and self.rect_hud_info["felicidad"].collidepoint(pos):
                        self.mostrando_detalle_estado = True
                        self.detalle_estado_tipo = "felicidad"
                        self.menu_compra_abierto = False
                        self.mostrando_investigacion = False
                        self.mostrando_inventario = False
                        self.menu_intercambio_abierto = False
                        self.noticias_abiertas = False

                    elif self.rect_hud_info.get("salud") and self.rect_hud_info["salud"].collidepoint(pos):
                        self.mostrando_detalle_estado = True
                        self.detalle_estado_tipo = "salud"
                        self.menu_compra_abierto = False
                        self.mostrando_investigacion = False
                        self.mostrando_inventario = False
                        self.menu_intercambio_abierto = False
                        self.noticias_abiertas = False

                    elif hasattr(self, 'btn_investigar') and self.btn_investigar.collidepoint(pos):
                        self.mostrando_investigacion = not self.mostrando_investigacion
                        self.menu_compra_abierto = False
                        self.mostrando_inventario = False
                        self.menu_intercambio_abierto = False
                        self.noticias_abiertas = False

                    elif self.btn_ajustes.collidepoint(pos):
                        self.menu_ajustes_abierto = not self.menu_ajustes_abierto
                        self.reproducir_sonido("cerrar")
                        
                    elif self.btn_inventario.collidepoint(pos):
                        if sum(self.edificios_construidos.values()) > 0:
                            self.mostrando_inventario = not self.mostrando_inventario
                            self.mostrando_investigacion = False 
                            self.menu_compra_abierto = False
                            self.menu_intercambio_abierto = False
                            self.noticias_abiertas = False     
                        else:
                            self.mostrando_aviso_inv = True
                            
                    elif self.btn_noticias.collidepoint(pos):
                        self.noticias_abiertas = not self.noticias_abiertas
                        self.menu_compra_abierto = False
                        self.mostrando_inventario = False
                        self.mostrando_investigacion = False
                        self.menu_intercambio_abierto = False

            # Fin del bucle de eventos
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__": Juego().ejecutar()