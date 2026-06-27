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
COLOR_FONDO       = "#FAF3E0"   # crema cálido 
COLOR_PANEL       = "#E6CCB2"   # beige madera clara
COLOR_ACENTO      = "#BC6C25"   # naranja tierra 
COLOR_ACENTO2     = "#6F4E37"   # café oscuro
COLOR_TEXTO       = "#2F241F"   # marrón muy oscuro 
COLOR_TEXTO_SUB   = "#6B5B4F"   # marrón grisáceo suave
COLOR_SI          = "#588157"   # verde bosque apagado 
COLOR_NO          = "#A4161A"   # rojo vino/rojizo otoñal
COLOR_EXITO       = "#3A7D44"   # verde profundo más “natural”
COLOR_ADVERTENCIA = "#D97706"   # naranja oscuro tipo calabaza

#Tipografías
FUENTE_TITULO    = ("Georgia", 26, "bold")
FUENTE_SUBTITULO = ("Georgia", 14)
FUENTE_PREGUNTA  = ("Cambria", 16, "bold")
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


    #Permite configurar la funcionalidad y apariencia de la ventana
    def _configurar_ventana(self):
        self.root.title("Adivina en qué estoy pensando")
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

    #Funcion que crea el primer frame de pantalla
    def _mostrar_pantalla_inicio(self):
        self._limpiar_pantalla()
        frame = self._crear_frame_central()

        #TITULARES
        self._etiqueta(frame, "Adivina en qué estoy pensando...",
                       fuente=FUENTE_TITULO, color=COLOR_ACENTO).pack()
        self._etiqueta(frame, "Piensa en una comida o fruta e intentaré adivinarla",
                       fuente=FUENTE_SUBTITULO, color=COLOR_TEXTO_SUB).pack(pady=(6, 2))

        self._separador(frame)

        #INSTRUCCIONES
        instrucciones = (
            "Reglas:\n"
            " • Piensa en algo\n"
            " • Responde Sí o No a mis preguntas\n"
            " • Si no adivino, me enseñas y aprendo para siempre"
        )

        #Label para mostrar la informacion
        tk.Label(frame, text=instrucciones, font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TEXTO, justify="left", padx=20, pady=12,
                 relief="flat", bd=0).pack(fill="x", pady=(0, 16))

        #Creacion de botones
        self._boton(frame, "Jugar con árbol predeterminado",
                    self._iniciar_partida, COLOR_ACENTO).pack(pady=4)
        self._boton(frame, "Cargar árbol desde archivo",
                    self._cargar_archivo, COLOR_ACENTO2).pack(pady=4)
        self._boton(frame, "Salir", self.root.quit, "#8B3A3A").pack(pady=4)

        #Pie de la pagina
        #self._etiqueta(frame, "Taller de Programación III — 2026", fuente=FUENTE_PEQUENA, color=COLOR_TEXTO_SUB).pack(side="bottom")

    """
    ###########################
    2. PANTALLA DE JUEGO (pregunta actual / adivinanza)
    ###########################
    """

    #Reinicia el recorrido del arbol y muestra el primer paso (RF-04, RF-12)
    def _iniciar_partida(self):
        self.arbol.reiniciar_partida()
        self._mostrar_paso_actual()

    #Decide si el nodo actual es pregunta u hoja, y dibuja la pantalla correspondiente
    def _mostrar_paso_actual(self):
        self._limpiar_pantalla()
        frame = self._crear_frame_central()

        if self.arbol.es_hoja_actual():
            self._mostrar_pantalla_adivinanza(frame)   #RF-06: llegamos a una respuesta
        else:
            self._mostrar_pantalla_pregunta(frame)      #RF-04/RF-05: todavia hay pregunta

    #E: frame donde dibujar
    #Muestra la pregunta actual del nodo y los botones Si/No (RF-04, RF-13)
    def _mostrar_pantalla_pregunta(self, frame):
        pregunta = self.arbol.obtener_pregunta_actual()

        self._etiqueta(frame, pregunta, fuente=FUENTE_PREGUNTA, color=COLOR_TEXTO).pack(pady=(0, 24))

        frame_botones = tk.Frame(frame, bg=COLOR_FONDO)
        frame_botones.pack(pady=10)

        self._boton(frame_botones, "Sí", lambda: self._responder(True), COLOR_SI, ancho=12).pack(side="left", padx=10)
        self._boton(frame_botones, "No", lambda: self._responder(False), COLOR_NO, ancho=12).pack(side="left", padx=10)

    #E: booleano (True = Si, False = No)
    #Avanza el recorrido del arbol segun la respuesta y redibuja la pantalla (RF-04)
    def _responder(self, respuesta_si):
        self.arbol.responder(respuesta_si)
        self._mostrar_paso_actual()

    #E: frame donde dibujar
    #Muestra la respuesta final que adivina la app y pregunta si acerto (RF-06)
    def _mostrar_pantalla_adivinanza(self, frame):
        respuesta = self.arbol.obtener_pregunta_actual()

        self._etiqueta(frame, f"¿Estabas pensando en {respuesta}?",
                       fuente=FUENTE_PREGUNTA, color=COLOR_ACENTO).pack(pady=(0, 24))

        frame_botones = tk.Frame(frame, bg=COLOR_FONDO)
        frame_botones.pack(pady=10)

        #RF-07: si acierta -> pantalla de victoria. RF-08: si falla -> formulario de aprendizaje
        self._boton(frame_botones, "Acertaste", self._mostrar_pantalla_victoria, COLOR_SI, ancho=16).pack(side="left", padx=10)
        self._boton(frame_botones, "Fallaste", self._mostrar_pantalla_aprendizaje, COLOR_NO, ancho=16).pack(side="left", padx=10)

    """
    ###########################
    3. PANTALLA DE VICTORIA (RF-07)
    ###########################
    """
    #Muestra el mensaje de victoria y permite jugar de nuevo o salir
    def _mostrar_pantalla_victoria(self):
        self._limpiar_pantalla()
        frame = self._crear_frame_central()

        self._etiqueta(frame, "¡Adiviné!", fuente=FUENTE_TITULO, color=COLOR_EXITO).pack(pady=(0, 16))

        #RF-12: permite reiniciar la partida desde la raiz
        self._boton(frame, "Jugar otra vez", self._iniciar_partida, COLOR_ACENTO).pack(pady=6)
        self._boton(frame, "Salir", self.root.quit, "#8B3A3A").pack(pady=6)


    """
    ###########################
    4. FORMULARIO DE APRENDIZAJE (RF-08, RF-09, RF-14)
    ###########################
    """
    #Pide la respuesta correcta, una pregunta nueva y si esa pregunta es Si/No para la nueva respuesta
    def _mostrar_pantalla_aprendizaje(self):
        self._limpiar_pantalla()
        frame = self._crear_frame_central()

        incorrecta = self.arbol.obtener_pregunta_actual()

        self._etiqueta(frame, f"Pensé en \"{incorrecta}\", pero no era correcto.",
                       fuente=FUENTE_NORMAL, color=COLOR_TEXTO_SUB).pack(pady=(0, 16))

        #Campo: respuesta correcta
        self._etiqueta(frame, "¿En qué estabas pensando?", color=COLOR_TEXTO).pack(anchor="w")
        entrada_respuesta = tk.Entry(frame, font=FUENTE_NORMAL, width=40)
        entrada_respuesta.pack(pady=(2, 12))

        #Campo: pregunta nueva que diferencia ambas respuestas
        self._etiqueta(frame, f"Escribe una pregunta que diferencie tu respuesta de \"{incorrecta}\":",
                       color=COLOR_TEXTO).pack(anchor="w")
        entrada_pregunta = tk.Entry(frame, font=FUENTE_NORMAL, width=40)
        entrada_pregunta.pack(pady=(2, 12))

        #Campo: la respuesta a esa nueva pregunta para la respuesta correcta (Si o No)
        self._etiqueta(frame, "Para tu respuesta, ¿la contestación a esa pregunta es Sí o No?",
                       color=COLOR_TEXTO).pack(anchor="w")

        valor_si_no = tk.StringVar(value="")
        frame_radios = tk.Frame(frame, bg=COLOR_FONDO)
        frame_radios.pack(pady=(2, 16))
        
        tk.Radiobutton(frame_radios, text="Sí", variable=valor_si_no, value="si",
                       bg=COLOR_FONDO, fg=COLOR_TEXTO, selectcolor=COLOR_PANEL,
                       activebackground=COLOR_FONDO, activeforeground=COLOR_TEXTO,
                       font=FUENTE_NORMAL).pack(side="left", padx=10)
        
        tk.Radiobutton(frame_radios, text="No", variable=valor_si_no, value="no",
                       bg=COLOR_FONDO, fg=COLOR_TEXTO, selectcolor=COLOR_PANEL,
                       activebackground=COLOR_FONDO, activeforeground=COLOR_TEXTO,
                       font=FUENTE_NORMAL).pack(side="left", padx=10)

        #E: lee los widgets de arriba
        #Valida los campos (RF-14) y, si todo esta bien, actualiza y guarda el arbol (RF-09, RF-10)
        def confirmar():
            respuesta_correcta = entrada_respuesta.get().strip()
            nueva_pregunta = entrada_pregunta.get().strip()
            eleccion = valor_si_no.get()

            #RF-14: ningun campo puede quedar vacio
            if not respuesta_correcta:
                messagebox.showerror("Falta información", "Debes escribir la respuesta correcta.")
                return
            if not nueva_pregunta:
                messagebox.showerror("Falta información", "Debes escribir una pregunta nueva.")
                return
            if eleccion not in ("si", "no"):
                messagebox.showerror("Falta información", "Debes indicar si la respuesta es Sí o No.")
                return

            #RF-09: el arbol reemplaza la hoja incorrecta por la nueva pregunta con sus dos ramas
            self.arbol.aprender(respuesta_correcta, nueva_pregunta, eleccion == "si")

            #RF-10/RF-11: guardado automatico obligatorio tras aprender, para conservar el avance
            self._guardar_automatico()

            self._mostrar_pantalla_aprendizaje_exitosa()

        self._boton(frame, "Guardar y continuar", confirmar, COLOR_ACENTO).pack(pady=6)

    #Guarda el arbol en el archivo actual (o en uno por defecto si nunca se cargo ninguno)
    def _guardar_automatico(self):
        ruta = self.archivo_actual or "arbol_guardado.json"
        exito, error = self.manejador.guardar(self.arbol, ruta)
        if not exito:
            messagebox.showwarning("No se pudo guardar", error)
        else:
            self.archivo_actual = ruta

    #Confirma que se aprendio y guardo, y permite continuar jugando (RF-12)
    def _mostrar_pantalla_aprendizaje_exitosa(self):
        self._limpiar_pantalla()
        frame = self._crear_frame_central()

        self._etiqueta(frame, "¡Gracias! Aprendí algo nuevo.", fuente=FUENTE_PREGUNTA, color=COLOR_EXITO).pack(pady=(0, 8))
        self._etiqueta(frame, f"Guardado en: {self.archivo_actual}", fuente=FUENTE_PEQUENA, color=COLOR_TEXTO_SUB).pack(pady=(0, 16))

        self._boton(frame, "Jugar otra vez", self._iniciar_partida, COLOR_ACENTO).pack(pady=6)
        self._boton(frame, "Salir", self.root.quit, "#8B3A3A").pack(pady=6)

    """
    ###########################
    5. CARGAR ARCHIVO (RF-02)
    ###########################
    """
    
    #Abre un dialogo para elegir un archivo JSON y carga el arbol guardado en el
    def _cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un árbol guardado",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )

        if not ruta:   #el usuario cerro el dialogo sin elegir nada
            return

        exito, error = self.manejador.cargar(self.arbol, ruta)

        if not exito:
            #RF-02: si el archivo no existe, esta vacio o es invalido, avisamos y
            #seguimos con un arbol por defecto, sin cerrar la aplicacion
            messagebox.showerror("Error al cargar", error + "\nSe usará el árbol por defecto.")
            self.arbol = ArbolDecision()
            self.archivo_actual = None
        else:
            self.archivo_actual = ruta
            messagebox.showinfo("Árbol cargado", f"Se cargó correctamente:\n{ruta}")

        self._iniciar_partida()

"""
#####################################################################
INICIALIZAR
#####################################################################
"""

#TEMPORAL, PARA PROBAR
if __name__ == "__main__":
    raiz = tk.Tk()
    app = InterfazJuego(raiz)
    raiz.mainloop()


