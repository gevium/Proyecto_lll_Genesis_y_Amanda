#Contiene la logica del arbol binario de decision
#El arbol se representa con listas: [raiz, hijo_si, hijo_no]
#Los atomos (hojas) son strings directamente, sin lista

class ArbolDecision:

    def __init__(self):
        self.arbol = []         #arbol principal del juego
        self.nodo_actual = []   #nodo en el que se encuentra la partida
        self._crear_arbol_defecto()

    ###################################################################################
    #Funciones base
    ###################################################################################

    #E: cualquier valor
    #S: booleano
    #Retorna True si x es una hoja (string solo, sin hijos)
    def atomo(self, x):
        return not type(x) == list

    #E: arbol
    #S: string con el contenido de la raiz
    #Retorna la raiz del arbol
    def raiz(self, arbol):
        if self.atomo(arbol):
            return arbol        #si es atomo, el nodo ES la raiz
        else:
            return arbol[0]     #si es lista, la raiz es el primer elemento

    #E: arbol
    #S: arbol (rama Sí)
    #Retorna el hijo izquierdo, que corresponde a la respuesta Si
    def hijoizq(self, arbol):
        if self.atomo(arbol):
            return []           #un atomo no tiene hijos
        else:
            return arbol[1]     #segundo elemento es el hijo Si

    #E: arbol
    #S: arbol (rama No)
    #Retorna el hijo derecho, que corresponde a la respuesta No
    def hijoder(self, arbol):
        if self.atomo(arbol):
            return []           #un atomo no tiene hijos
        else:
            return arbol[2]     #tercer elemento es el hijo No

    #E: arbol
    #S: booleano
    #Retorna True si el nodo no tiene hijos (es una respuesta final)
    def hoja(self, nodo):
        if nodo == []:
            return False        #nodo vacio no es hoja
        elif self.atomo(nodo):
            return True         #string solo siempre es hoja
        elif self.hijoizq(nodo) == [] and self.hijoder(nodo) == []:
            return True         #lista sin hijos tambien es hoja
        else:
            return False

    #E: string centro, arbol hi, arbol hd
    #S: arbol construido
    #Construye un nodo con raiz, hijo izquierdo y hijo derecho
    def construir(self, centro, hi, hd):
        if hi == [] and hd == []:
            return centro       #sin hijos es un atomo
        else:
            return [centro, hi, hd]

    ####################################################################################
    # Arbol por defecto
    ####################################################################################

    #E: nada
    #S: nada
    #Crea el arbol inicial basico con comidas y frutas
    def _crear_arbol_defecto(self):
        self.arbol = [
            "¿Es una fruta?",
            ["¿Es cítrica?", "naranja", "mango"],               #rama Si
            ["¿Es comida rápida?", "hamburguesa", "arroz con pollo"]  #rama No
        ]
        self.nodo_actual = self.arbol

    ####################################################################################
    # Control de partida
    ####################################################################################

    #E: nada
    #S: nada
    #Reinicia la partida volviendo al nodo raiz
    def reiniciar_partida(self):
        self.nodo_actual = self.arbol

    #E: nada
    #S: string con la pregunta o respuesta actual
    #Retorna el contenido del nodo actual
    def obtener_pregunta_actual(self):
        return self.raiz(self.nodo_actual)

    #E: nada
    #S: booleano
    #Retorna True si el nodo actual es una hoja (respuesta final)
    def es_hoja_actual(self):
        return self.hoja(self.nodo_actual)

    #E: booleano (True = Si, False = No)
    #S: nada
    #Avanza en el arbol segun la respuesta del usuario
    def responder(self, respuesta_si):
        if respuesta_si:
            self.nodo_actual = self.hijoizq(self.nodo_actual)   #rama Si
        else:
            self.nodo_actual = self.hijoder(self.nodo_actual)   #rama No

    ####################################################################################
    # Aprendizaje
    ####################################################################################

    #E: string respuesta correcta, string nueva pregunta, booleano si la respuesta es Si
    #S: nada
    #Reemplaza la hoja incorrecta por una nueva pregunta con dos hijos
    def aprender(self, respuesta_correcta, nueva_pregunta, nueva_es_si):
        incorrecta = self.raiz(self.nodo_actual)    #guardamos la respuesta incorrecta

        if nueva_es_si:
            nuevo_nodo = [nueva_pregunta, respuesta_correcta, incorrecta]   #correcta va a la izq (Si)
        else:
            nuevo_nodo = [nueva_pregunta, incorrecta, respuesta_correcta]   #correcta va a la der (No)

        self.arbol = self._reemplazar(self.arbol, incorrecta, nuevo_nodo)   #actualizamos el arbol
        self.nodo_actual = self.arbol

    #E: arbol, string objetivo a reemplazar, nodo reemplazo
    #S: arbol actualizado
    #Recorre el arbol recursivamente y reemplaza el nodo objetivo por el reemplazo
    def _reemplazar(self, arbol, objetivo, reemplazo):
        if arbol == []:
            return []                   #arbol vacio, nada que reemplazar
        elif self.atomo(arbol):
            if arbol == objetivo:
                return reemplazo        #encontramos el nodo, lo reemplazamos
            else:
                return arbol            #no es el nodo buscado, lo dejamos igual
        else:
            return [
                self.raiz(arbol),                                               #raiz se mantiene
                self._reemplazar(self.hijoizq(arbol), objetivo, reemplazo),     #buscamos en rama Si
                self._reemplazar(self.hijoder(arbol), objetivo, reemplazo)      #buscamos en rama No
            ]

    #####################################################################################
    # Serializacion (para ManejadorArchivo)
    #####################################################################################

    #E: nada
    #S: lista que representa el arbol completo
    #Retorna el arbol como lista para guardarlo en JSON
    def a_diccionario(self):
        return self.arbol               #el arbol ya es una lista, se guarda directo

    #E: lista con los datos cargados del archivo
    #S: nada
    #Reconstruye el arbol desde los datos cargados
    def desde_diccionario(self, datos):
        self.arbol = datos
        self.nodo_actual = self.arbol   #reiniciamos al nodo raiz


