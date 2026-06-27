import json
import os
from arbol import ArbolDecision

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
                #Permite convertir automáticamente los tipos de datos de Python en su forma equivalente en Json
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
        except (OSError, UnicodeDecodeError) as e:
            return False, f"No se pudo leer el archivo: {e}"
        except Exception as e:
            return False, f"Ocurrió un error inesperado al leer el archivo: {e}"

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
