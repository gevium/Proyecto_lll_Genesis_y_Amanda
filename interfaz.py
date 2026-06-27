import tkinter as tk
from tkinter import filedialog, messagebox
from arbol import ArbolDecision
from manejador_archivo import ManejadorArchivo

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
FUENTEboton     = ("Segoe UI", 12, "bold")
FUENTE_NORMAL    = ("Segoe UI", 11)
FUENTE_PEQUENA   = ("Segoe UI", 9)

#Clase para manejar la inicializacion del juego
#(manejo de pantallas, mensajes de resultado, formulario de aprendizaje)
class InterfazJuego:

    #constructor
    def __init__(self, root: tk.Tk):
        self.root = root
        self.arbol = ArbolDecision() #se crea un arbol
        self.manejador = ManejadorArchivo() #se crea un gestor de archivos
        self.archivo_actual: str | None = None

        self.configurar_ventana()
        self.mostrar_pantalla_inicio()


    #Permite configurar la funcionalidad y apariencia de la ventana
    def configurar_ventana(self):
        self.root.title("Adivina en qué estoy pensando")
        self.root.geometry("700x600")
        self.root.configure(bg=COLOR_FONDO)
        self.root.resizable(True, True)


    #Elimina todos los widgets del frame principal
    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    #funcion para crear el frame principal
    def crear_frame_central(self):
        frame = tk.Frame(self.root, bg=COLOR_FONDO)
        frame.pack(expand=True, fill="both", padx=40, pady=30)
        return frame

    #E: Parent, texto, funcion del boton, color y ancho
    #S: boton
    def boton(self, parent, texto, comando, color=COLOR_ACENTO, ancho=22):
        btn = tk.Button(
            parent, text=texto, command=comando,
            bg=color, fg="white", font=FUENTEboton,
            relief="flat", bd=0, padx=16, pady=10,
            cursor="hand2", width=ancho,
            activebackground=color, activeforeground="white"
        )
        return btn

    #E: parent, texto, fuente, color y largo
    #Permite crear labels con diferentes textos
    def etiqueta(self, parent, texto, fuente=FUENTE_NORMAL, color=COLOR_TEXTO, wraplength=580):
        return tk.Label(
            parent, text=texto, font=fuente,
            bg=COLOR_FONDO, fg=color,
            wraplength=wraplength, justify="center"
        )

    #Funcion (Separador para mayor orden visual)
    def separador(self, parent):
        tk.Frame(parent, bg=COLOR_ACENTO, height=2).pack(fill="x", pady=12)
    
    #Funcion que permite guardar manualmente el arbol en curso
    def guardar_manual(self):
        ruta = filedialog.asksaveasfilename(title="Guardar árbol", defaultextension=".json", filetypes=[("Archivos JSON", "*.json")])
        
        if not ruta: #si no establece la ruta para el archivo
            return
        exito, error = self.manejador.guardar(self.arbol, ruta)
        if exito:
            self.archivo_actual = ruta
            messagebox.showinfo("Guardado", f"Árbol guardado en:\n{ruta}")
        else:
            messagebox.showerror("Error al guardar", error)

    """
    ###########################
    1. PANTALLA DE INICIO
    ###########################
    """

    #Funcion que crea el primer frame de pantalla
    def mostrar_pantalla_inicio(self):
        self.limpiar_pantalla()
        frame = self.crear_frame_central()

        #TITULARES
        self.etiqueta(frame, "Adivina en qué estoy pensando...",
                       fuente=FUENTE_TITULO, color=COLOR_ACENTO).pack()
        self.etiqueta(frame, "Piensa en una comida o fruta e intentaré adivinarla",
                       fuente=FUENTE_SUBTITULO, color=COLOR_TEXTO_SUB).pack(pady=(6, 2))

        self.separador(frame)

        #INSTRUCCIONES
        instrucciones = (
            "Reglas:\n"
            " • Piensa en algo\n"
            " • Responde 'Sí' o 'No' a las preguntas\n"
            " • Si no adivino, me enseñas y aprendo para siempre"
        )

        #Label para mostrar la informacion
        tk.Label(frame, text=instrucciones, font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TEXTO, justify="left", padx=20, pady=12,
                 relief="flat", bd=0).pack(fill="x", pady=(0, 16))

        #Creacion de botones
        self.boton(frame, "Jugar con árbol predeterminado", self.iniciar_partida, COLOR_ACENTO).pack(pady=4)
        self.boton(frame, "Cargar árbol desde archivo", self.cargar_archivo, COLOR_ACENTO2).pack(pady=4)
        self.boton(frame, "Guardar árbol actual", self.guardar_manual, COLOR_ACENTO2).pack(pady=4)
        self.boton(frame, "Salir", self.root.quit, "#8B3A3A").pack(pady=4)
        
    """
    ###########################
    2. PANTALLA DE JUEGO (pregunta actual / adivinanza)
    ###########################
    """

    #Reinicia el recorrido del arbol y muestra el primer paso
    def iniciar_partida(self):
        self.arbol.reiniciar_partida()
        self.mostrar_paso_actual()

    #Decide si el nodo actual es pregunta u hoja, y dibuja la pantalla correspondiente
    def mostrar_paso_actual(self):
        self.limpiar_pantalla()
        frame = self.crear_frame_central()

        if self.arbol.es_hoja_actual():
            self.mostrar_pantalla_adivinanza(frame)    #Llega a una respuesta
        else:
            self.mostrar_pantalla_pregunta(frame)      #Todavia hay pregunta

    #E: frame donde dibujar
    #Muestra la pregunta actual del nodo y los botones Si/No
    def mostrar_pantalla_pregunta(self, frame):
        pregunta = self.arbol.obtener_pregunta_actual()

        self.etiqueta(frame, pregunta, fuente=FUENTE_PREGUNTA, color=COLOR_TEXTO).pack(pady=(0, 24))

        framebotones = tk.Frame(frame, bg=COLOR_FONDO)
        framebotones.pack(pady=10)

        self.boton(framebotones, "Sí", lambda: self.responder(True), COLOR_SI, ancho=12).pack(side="left", padx=10)
        self.boton(framebotones, "No", lambda: self.responder(False), COLOR_NO, ancho=12).pack(side="left", padx=10)

    #E: booleano (True = Si, False = No)
    #Avanza el recorrido del arbol segun la respuesta y redibuja la pantalla
    def responder(self, respuesta_si):
        self.arbol.responder(respuesta_si)
        self.mostrar_paso_actual()

    #E: frame donde dibujar
    #Muestra la respuesta final que adivina la app y pregunta si acertó
    def mostrar_pantalla_adivinanza(self, frame):
        respuesta = self.arbol.obtener_pregunta_actual()

        self.etiqueta(frame, f"¿Estabas pensando en {respuesta}?",
                       fuente=FUENTE_PREGUNTA, color=COLOR_ACENTO).pack(pady=(0, 24))

        framebotones = tk.Frame(frame, bg=COLOR_FONDO)
        framebotones.pack(pady=10)

        #Si acierta enseña pantalla de victoria, si falla enseña formulario de aprendizaje
        self.boton(framebotones, "Acertaste", self.mostrar_pantalla_victoria, COLOR_SI, ancho=16).pack(side="left", padx=10)
        self.boton(framebotones, "Fallaste", self.mostrar_pantalla_aprendizaje, COLOR_NO, ancho=16).pack(side="left", padx=10)

    """
    ###########################
    3. PANTALLA DE VICTORIA (RF-07)
    ###########################
    """
    #Muestra el mensaje de victoria y permite jugar de nuevo o salir
    def mostrar_pantalla_victoria(self):
        self.limpiar_pantalla()
        frame = self.crear_frame_central()

        self.etiqueta(frame, "¡Adiviné!", fuente=FUENTE_TITULO, color=COLOR_EXITO).pack(pady=(0, 16))

        #Permite reiniciar la partida desde la raiz
        self.boton(frame, "Jugar otra vez", self.iniciar_partida, COLOR_ACENTO).pack(pady=6)
        self.boton(frame, "Volver al menú", self.mostrar_pantalla_inicio, COLOR_ACENTO2).pack(pady=6)
        self.boton(frame, "Salir", self.root.quit, "#8B3A3A").pack(pady=6)


    """
    ###########################
    4. FORMULARIO DE APRENDIZAJE (RF-08, RF-09, RF-14)
    ###########################
    """
    #Pide la respuesta correcta, una pregunta nueva y si esa pregunta es Si/No para la nueva respuesta
    def mostrar_pantalla_aprendizaje(self):
        self.limpiar_pantalla()
        frame = self.crear_frame_central()

        incorrecta = self.arbol.obtener_pregunta_actual()

        self.etiqueta(frame, f"Pensé en \"{incorrecta}\", pero no era correcto.",
                       fuente=FUENTE_NORMAL, color=COLOR_TEXTO_SUB).pack(pady=(0, 16))

        #Campo: respuesta correcta
        self.etiqueta(frame, "¿En qué estabas pensando?", color=COLOR_TEXTO).pack(anchor="w", padx = 5, fill = "x")
        entrada_respuesta = tk.Entry(frame, font=FUENTE_NORMAL, width=40)
        entrada_respuesta.pack(fill = "x", padx=5, pady=(2, 12))

        #Campo: pregunta nueva que diferencia ambas respuestas
        self.etiqueta(frame, f"Escribe una pregunta que diferencie tu respuesta de \"{incorrecta}\":", color=COLOR_TEXTO).pack(anchor="w", padx = 5, fill = "x")
        entrada_pregunta = tk.Entry(frame, font=FUENTE_NORMAL, width=40)
        entrada_pregunta.pack(fill = "x", padx=5, pady=(2, 12))

        #Campo: la respuesta a esa nueva pregunta para la respuesta correcta (Si o No)
        self.etiqueta(frame, "Para tu respuesta, ¿la contestación a esa pregunta es Sí o No?", color=COLOR_TEXTO).pack(anchor="w", padx = 5, fill = "x")

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
        #Valida los campos y, si todo esta bien, actualiza y guarda el arbol
        def confirmar():
            respuesta_correcta = entrada_respuesta.get().strip()
            nueva_pregunta = entrada_pregunta.get().strip()
            eleccion = valor_si_no.get()

            #Ningun campo puede quedar vacio
            if not respuesta_correcta:
                messagebox.showerror("Falta información", "Debes escribir la respuesta correcta.")
                return
            if not nueva_pregunta:
                messagebox.showerror("Falta información", "Debes escribir una pregunta nueva.")
                return
            if eleccion not in ("si", "no"):
                messagebox.showerror("Falta información", "Debes indicar si la respuesta es Sí o No.")
                return

            #El arbol reemplaza la hoja incorrecta por la nueva pregunta con sus dos ramas
            self.arbol.aprender(respuesta_correcta, nueva_pregunta, eleccion == "si")

            #Guardado automatico obligatorio tras aprender, para conservar el avance
            self.guardar_automatico()

            self.mostrar_pantalla_aprendizaje_exitosa()

        self.boton(frame, "Guardar y continuar", confirmar, COLOR_ACENTO).pack(pady=6)

    #Guarda el arbol en el archivo actual (o en uno por defecto si nunca se cargo ninguno)
    def guardar_automatico(self):
        ruta = self.archivo_actual or "arbol_guardado.json"
        exito, error = self.manejador.guardar(self.arbol, ruta)
        if not exito:
            messagebox.showwarning("No se pudo guardar", error)
        else:
            self.archivo_actual = ruta

    #Confirma que se aprendio y guardo, y permite continuar jugando
    def mostrar_pantalla_aprendizaje_exitosa(self):
        self.limpiar_pantalla()
        frame = self.crear_frame_central()

        self.etiqueta(frame, "¡Gracias! Aprendí algo nuevo.", fuente=FUENTE_PREGUNTA, color=COLOR_EXITO).pack(pady=(0, 8))
        self.etiqueta(frame, f"Guardado en: {self.archivo_actual}", fuente=FUENTE_PEQUENA, color=COLOR_TEXTO_SUB).pack(pady=(0, 16))

        self.boton(frame, "Jugar otra vez", self.iniciar_partida, COLOR_ACENTO).pack(pady=6)
        self.boton(frame, "Volver al menú", self.mostrar_pantalla_inicio, COLOR_ACENTO2).pack(pady=6)
        self.boton(frame, "Salir", self.root.quit, "#8B3A3A").pack(pady=6)

    """
    ###########################
    5. CARGAR ARCHIVO (RF-02)
    ###########################
    """
    
    #Abre un dialogo para elegir un archivo JSON y carga el arbol guardado en el
    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona un árbol guardado",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )

        if not ruta:   #el usuario cerro el dialogo sin elegir nada
            return

        exito, error = self.manejador.cargar(self.arbol, ruta)

        if not exito:
            #Si el archivo no existe, esta vacio o es invalido, se avisa y
            #se sigue con un arbol por defecto, sin cerrar la aplicacion
            messagebox.showerror("Error al cargar", error + "\nSe usará el árbol por defecto.")
            self.arbol = ArbolDecision()
            self.archivo_actual = None
        else:
            self.archivo_actual = ruta
            messagebox.showinfo("Árbol cargado", f"Se cargó correctamente:\n{ruta}")

        self.iniciar_partida()