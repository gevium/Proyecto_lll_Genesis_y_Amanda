import json
import os
from arbol import ArbolDecision

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


"""
#####################################################################
GESTOR DE ARCHIVOS
#####################################################################
"""
#Clase para gestionar los archivos
class ManejadorArchivo:

    #funcion para guardar los arboles en formato JSON
    def guardar(self, arbol: ArbolDecision, ruta: str):
        try:
            datos = arbol.a_diccionario()
            if datos is None: #Si no se encuentran datos en el arbol
                return False, "El árbol está vacío, no hay nada que guardar."


            with open(ruta, "w", encoding="utf-8") as archivo:
                #dumb: permite convertir automáticamente los tipos de datos de Python en su forma equivalente en Json
                #ensure_ascii permite asegurar que el archivo solo contenga caracteres ascii
                json.dump(datos, archivo, ensure_ascii=False, indent=2)

            return True, ""

        #Excepción 1:
        except PermissionError:
            return False, f"Sin permiso para escribir en '{ruta}'."
        
        #Excepción 2:
        except OSError as e:
            return False, f"Error al guardar el archivo: {e}"

    #Funcion para cargar archivos desde un archivo Json
    def cargar(self, arbol: ArbolDecision, ruta: str):

        #Verificar que el archivo exista
        if not os.path.exists(ruta):
            return False, f"El archivo '{ruta}' no existe."

        #Verificar que no esté vacío
        if os.path.getsize(ruta) == 0:
            return False, "El archivo está vacío."

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            #Validar que tenga la estructura mínima
            if not self._validar_estructura(datos):
                return False, "El archivo tiene un formato incorrecto o está dañado."

            arbol.desde_diccionario(datos)
            return True, ""

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except KeyError as e:
            return False, f"El archivo está incompleto, falta la clave: {e}"
        except OSError as e:
            return False, f"No se pudo leer el archivo: {e}"

    #E: datos cargados del JSON
    #S: booleano
    #Valida que el contenido del archivo tenga la estructura correcta
    def _validar_estructura(self, datos):
        if isinstance(datos, str):
            return len(datos.strip()) > 0      #hoja valida si no esta vacia
        if not isinstance(datos, list):
            return False                        #debe ser string o lista
        if len(datos) != 3:
            return False                        #toda lista debe tener raiz, hi, hd
        if not isinstance(datos[0], str) or not datos[0].strip():
            return False                        #la raiz debe ser string no vacio
        return (self._validar_estructura(datos[1]) and    #validar rama Si
                self._validar_estructura(datos[2]))        #validar rama No


"""
#####################################################################
INTERFAZ GRÁFICA 
#####################################################################
"""
#Paleta de colores
COLOR_FONDO      = "#1E1E2E"
COLOR_PANEL      = "#2A2A3E"
COLOR_ACENTO     = "#F97316"   # naranja vibrante
COLOR_ACENTO2    = "#6366F1"   # índigo
COLOR_TEXTO      = "#E2E8F0"
COLOR_TEXTO_SUB  = "#94A3B8"
COLOR_SI         = "#22C55E"   # verde
COLOR_NO         = "#EF4444"   # rojo
COLOR_EXITO      = "#10B981"
COLOR_ADVERTENCIA= "#F59E0B"

#Tipografías
FUENTE_TITULO    = ("Segoe UI", 26, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 14)
FUENTE_PREGUNTA  = ("Segoe UI", 16, "bold")
FUENTE_BOTON     = ("Segoe UI", 12, "bold")
FUENTE_NORMAL    = ("Segoe UI", 11)
FUENTE_PEQUENA   = ("Segoe UI", 9)

#Clase para manejar la inicializacion del juego
#(manejo de pantallas, mensajes de resultado, formulario de aprendizaje...)
class InterfazJuego:

    #constructor
    def __init__(self, root: tk.Tk):
        self.root = root
        self.arbol = ArbolDecision() #se crea un arbol
        self.manejador = ManejadorArchivo() #se crea un gestor de archivos
        self.archivo_actual: str | None = None

        self._configurar_ventana()
        self._mostrar_pantalla_inicio()

    #E: N/A
    #S: N/A
    #Permite configurar la funcionalidad y apariencia de la ventana
    def _configurar_ventana(self):
        self.root.title("🍕 Adivina en qué estoy pensando")
        self.root.geometry("700x520")
        self.root.minsize(600, 460)
        self.root.configure(bg=COLOR_FONDO)
        self.root.resizable(True, True)

        self.root.geometry("700x520")

    #Elimina todos los widgets del frame principal
    def _limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    #funcion para crear el frame principal
    def _crear_frame_central(self):
        frame = tk.Frame(self.root, bg=COLOR_FONDO)
        frame.pack(expand=True, fill="both", padx=40, pady=30)
        return frame

    #E: Parent, texto, funcion del boton, color y ancho
    #S: boton
    def _boton(self, parent, texto, comando, color=COLOR_ACENTO, ancho=22):
        btn = tk.Button(
            parent, text=texto, command=comando,
            bg=color, fg="white", font=FUENTE_BOTON,
            relief="flat", bd=0, padx=16, pady=10,
            cursor="hand2", width=ancho,
            activebackground=color, activeforeground="white"
        )
        return btn

    #E: parent, texto, fuente, color y largo
    #S: N/A
    #Permite crear labels con diferentes textos
    def _etiqueta(self, parent, texto, fuente=FUENTE_NORMAL, color=COLOR_TEXTO, wraplength=580):
        return tk.Label(
            parent, text=texto, font=fuente,
            bg=COLOR_FONDO, fg=color,
            wraplength=wraplength, justify="center"
        )

    #Funcion (Separador para mayor orden visual)
    def _separador(self, parent):
        tk.Frame(parent, bg=COLOR_ACENTO, height=2).pack(fill="x", pady=12)

    """
    ###########################
    1. PANTALLA DE INICIO
    ###########################
    """
    #E: N/A
    #S: N/A
    #Funcion que crea el primer frame de pantalla
    def _mostrar_pantalla_inicio(self):
        self._limpiar_pantalla()
        frame = self._crear_frame_central()

        #TITULARES
        self._etiqueta(frame, "🍕 🍎 🌮", fuente=("Segoe UI", 32)).pack(pady=(0, 6))
        self._etiqueta(frame, "Adivina en qué estoy pensando...",
                       fuente=FUENTE_TITULO, color=COLOR_ACENTO).pack()
        self._etiqueta(frame, "¡Piensa en una comida o fruta e intentaré adivinarla!",
                       fuente=FUENTE_SUBTITULO, color=COLOR_TEXTO_SUB).pack(pady=(6, 2))

        self._separador(frame)

        #INSTRUCCIONES
        instrucciones = (
            "Reglas:\n"
            " • Piensa en una comida, fruta o ingrediente.\n"
            " • Responde solo Sí o No a mis preguntas.\n"
            " • Si no adivino, ¡me enseñas y aprendo para siempre!"
        )

        #Label para mostrar la informacion
        tk.Label(frame, text=instrucciones, font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TEXTO, justify="left", padx=20, pady=12,
                 relief="flat", bd=0).pack(fill="x", pady=(0, 16))

        #Creacion de botones
        self._boton(frame, "Jugar con árbol por defecto",
                    self._iniciar_partida, COLOR_ACENTO).pack(pady=4)
        self._boton(frame, "Cargar árbol desde archivo",
                    self._cargar_archivo, COLOR_ACENTO2).pack(pady=4)
        self._boton(frame, "Salir", self.root.quit, "#64748B").pack(pady=4)

        #Pie de la pagina
        self._etiqueta(frame, "Taller de Programación III — 2026", fuente=FUENTE_PEQUENA, color=COLOR_TEXTO_SUB).pack(side="bottom")

    """
    ###########################
    Cargar el archivo
    ###########################
    """




"""
#####################################################################
INICIALIZAR
#####################################################################
"""



