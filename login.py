# Copyright (c) 2026 [Cayetano Tielas Fernández]. Todos los derechos reservados.

import pygame
import os
import json
from configuracion import ANCHO, ALTO, BASE_DIR, BLANCO, NEGRO, ROJO, VERDE, ORO, GRIS_CLARO

AMARILLO = (255, 255, 0)

CARPETA_USUARIOS = os.path.join(BASE_DIR, "usuarios")
os.makedirs(CARPETA_USUARIOS, exist_ok=True)

class LoginScreen:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("Arial", 26, bold=True)
        self.fuente_peq = pygame.font.SysFont("Arial", 18)
        self.error = ""
        self.usuario = ""
        self.password = ""
        self.re_password = ""
        self.modo = "usuario"  # o "password"
        self.hecho = False
        self.usuario_valido = None
        self.seccion = "login"
        self.rect_link = pygame.Rect(0, 0, 0, 0)
        self.rect_re_pass = ""
        
    def dibujar(self):
        self.pantalla.fill((25, 25, 25))

        # --- 1. CUADRO MUCHO MÁS PEQUEÑO Y AJUSTADO ---
        cuadro_ancho = 500
        # Bajamos a 310 en registro y 260 en login para que no sobre nada de aire
        cuadro_alto = 310 if self.seccion == "registro" else 260 
        cuadro_x = ANCHO//2 - cuadro_ancho//2
        cuadro_y = ALTO//2 - cuadro_alto//2

        cuadro = pygame.Rect(cuadro_x, cuadro_y, cuadro_ancho, cuadro_alto)
        pygame.draw.rect(self.pantalla, (35, 35, 35), cuadro, border_radius=18)
        pygame.draw.rect(self.pantalla, ORO, cuadro, 3, border_radius=18)

        # --- TÍTULO ---
        titulo = self.fuente.render("INICIO DE SESIÓN" if self.seccion == "login" else "REGISTRO", True, ORO)
        self.pantalla.blit(titulo, (cuadro.centerx - titulo.get_width()//2, cuadro.y + 15))

        # --- INPUTS (Separación de solo 40px entre ellos para que estén pegados) ---
        self.rect_user = pygame.Rect(cuadro.x + 180, cuadro.y + 70, 230, 30)
        self.rect_pass = pygame.Rect(cuadro.x + 180, cuadro.y + 110, 230, 30)
        
        # 1. USUARIO
        self.pantalla.blit(self.fuente_peq.render("Usuario:", True, BLANCO), (cuadro.x + 40, cuadro.y + 75))
        pygame.draw.rect(self.pantalla, GRIS_CLARO, self.rect_user, border_radius=8)
        if self.modo == "usuario": pygame.draw.rect(self.pantalla, AMARILLO, self.rect_user, 2, border_radius=8)
        self.pantalla.blit(self.fuente_peq.render(self.usuario, True, NEGRO), (self.rect_user.x + 8, self.rect_user.y + 6))

        # 2. CONTRASEÑA
        self.pantalla.blit(self.fuente_peq.render("Contraseña:", True, BLANCO), (cuadro.x + 40, cuadro.y + 115))
        pygame.draw.rect(self.pantalla, GRIS_CLARO, self.rect_pass, border_radius=8)
        if self.modo == "password": pygame.draw.rect(self.pantalla, AMARILLO, self.rect_pass, 2, border_radius=8)
        self.pantalla.blit(self.fuente_peq.render(self.password, True, NEGRO), (self.rect_pass.x + 8, self.rect_pass.y + 6))

        # 3. REPETIR CONT: (Pegado a la anterior)
        if self.seccion == "registro":
            self.rect_re_pass = pygame.Rect(cuadro.x + 180, cuadro.y + 150, 230, 30)
            self.pantalla.blit(self.fuente_peq.render("Repetir Cont:", True, BLANCO), (cuadro.x + 40, cuadro.y + 155))
            pygame.draw.rect(self.pantalla, GRIS_CLARO, self.rect_re_pass, border_radius=8)
            if self.modo == "re_password": pygame.draw.rect(self.pantalla, AMARILLO, self.rect_re_pass, 2, border_radius=8)
            self.pantalla.blit(self.fuente_peq.render(self.re_password, True, NEGRO), (self.rect_re_pass.x + 8, self.rect_re_pass.y + 6))

        # --- BOTÓN REGISTRAR/ENTRAR (Justo debajo) ---
        y_btn = cuadro.y + 200 if self.seccion == "registro" else cuadro.y + 160
        self.btn_entrar = pygame.Rect(cuadro.centerx - 90, y_btn, 180, 40) # Botón un poco más fino (40px)
        
        color_btn = VERDE if len(self.usuario) > 0 and len(self.password) >= 4 else (80, 80, 80)
        pygame.draw.rect(self.pantalla, color_btn, self.btn_entrar, border_radius=10)
        
        txt_btn = self.fuente.render("ENTRAR" if self.seccion == "login" else "REGISTRAR", True, BLANCO)
        self.pantalla.blit(txt_btn, (self.btn_entrar.centerx - txt_btn.get_width()//2, self.btn_entrar.centery - txt_btn.get_height()//2))

        # --- ENLACE AZUL (Pegado al borde inferior del cuadro) ---
        texto_link = "¿No tienes cuenta? Registrate" if self.seccion == "login" else "¿Ya tienes cuenta? Logueate"
        self.render_link = self.fuente_peq.render(texto_link, True, (0, 255, 255))
        # Ajustado a -18 para que quede a ras del borde
        self.rect_link = self.render_link.get_rect(center=(cuadro.centerx, cuadro.bottom - 18))
        self.pantalla.blit(self.render_link, self.rect_link)

        # --- ERROR (Flotando sobre el botón) ---
        if self.error:
            t_err = self.fuente_peq.render(self.error, True, ROJO)
            self.pantalla.blit(t_err, (cuadro.centerx - t_err.get_width()//2, y_btn - 20))

        pygame.display.flip()

    def manejar_eventos(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()

            # --- TODO lo que use ev.pos DEBE ir aquí dentro ---
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if self.rect_user.collidepoint(ev.pos):
                    self.modo = "usuario"
                elif self.rect_pass.collidepoint(ev.pos):
                    self.modo = "password"
                # Añadimos la detección del tercer campo si es registro
                elif self.seccion == "registro" and hasattr(self, 'rect_re_pass') and self.rect_re_pass.collidepoint(ev.pos):
                    self.modo = "re_password"
                # MOVER ESTO AQUÍ ADENTRO (Estaba fuera y por eso fallaba)
                elif self.rect_link.collidepoint(ev.pos):
                    self.seccion = "registro" if self.seccion == "login" else "login"
                    self.error = "" 
                    self.modo = "usuario"
                elif hasattr(self, 'btn_entrar') and self.btn_entrar.collidepoint(ev.pos):
                    self.intentar_login()
                    if self.hecho: 
                        return     

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if self.modo == "usuario":
                        self.modo = "password"
                    elif self.modo == "password" and self.seccion == "registro":
                        self.modo = "re_password"
                    else:
                        self.intentar_login()
                        if self.hecho:
                            return

                # 2. BACKSPACE: Ahora permite borrar en los 3 campos
                elif ev.key == pygame.K_BACKSPACE:
                    if self.modo == "usuario" and len(self.usuario) > 0:
                        self.usuario = self.usuario[:-1]
                    elif self.modo == "password" and len(self.password) > 0:
                        self.password = self.password[:-1]
                    elif self.modo == "re_password" and len(self.re_password) > 0:
                        self.re_password = self.re_password[:-1]

                # 3. TAB: Salta entre los 3 campos en orden
                elif ev.key == pygame.K_TAB:
                    if self.modo == "usuario":
                        self.modo = "password"
                    elif self.modo == "password" and self.seccion == "registro":
                        self.modo = "re_password"
                    else:
                        self.modo = "usuario"

                # 4. ESCRIBIR: Guarda el texto según el campo activo
                else:
                    if self.modo == "usuario" and len(self.usuario) < 15:
                        # Usamos isprintable para evitar caracteres raros
                        if ev.unicode.isprintable(): self.usuario += ev.unicode
                    elif self.modo == "password" and len(self.password) < 12:
                        if ev.unicode.isprintable(): self.password += ev.unicode
                    elif self.modo == "re_password" and len(self.re_password) < 12:
                        if ev.unicode.isprintable(): self.re_password += ev.unicode

    def intentar_login(self):
        # 1. Validación de contraseñas iguales (Solo en Registro)
        if self.seccion == "registro":
            if self.password != self.re_password:
                self.error = "Las contraseñas no coinciden"
                return
        
        # 2. Validación de largo
        if len(self.password) < 4 or len(self.password) > 12:
            self.error = "Contraseña de 4 a 12 caracteres"
            return

        ruta_user = os.path.join(CARPETA_USUARIOS, f"{self.usuario}.json")

        # --- AQUÍ VIENE EL CAMBIO IMPORTANTE ---

        if self.seccion == "login":
            # LÓGICA DE LOGIN: El usuario DEBE existir
            if os.path.exists(ruta_user):
                with open(ruta_user, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                if datos.get("password") == self.password:
                    self.hecho = True
                    self.usuario_valido = self.usuario
                else:
                    self.error = "Contraseña incorrecta"
            else:
                self.error = "El usuario no existe"

        else: 
            # --- LÓGICA DE REGISTRO ---
            if os.path.exists(ruta_user):
                self.error = "Este usuario ya está en uso"
            else:
                datos = {"password": self.password}
                with open(ruta_user, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4)
                
                # EL CAMBIO ESTÁ AQUÍ:
                self.usuario_valido = self.usuario
                self.hecho = True # <--- Esto hace que entre DIRECTO tras crear la cuenta
                self.error = ""

    def ejecutar(self):
        while not self.hecho:
            self.manejar_eventos()
            self.dibujar()
        return self.usuario_valido
