import entornos_f
from random import choice, random

class NueveCuartos(entornos_f.Entorno):
    """
    Clase para un entorno de tres cuartos.
    
    El estado se define como (robot, cuartos)
    donde robot indica la posición del robot (índice de la lista)
    y cuartos es una lista donde cada elemento puede ser "limpio" o "sucio".

    Las acciones válidas en el entorno son
        ("izq", "der", "limpiar", "nada").

    Los sensores es una tupla (robot, limpio?)
    con la ubicación del robot y el estado de limpieza del cuarto en el que se encuentra
    """
    def accion_legal(self, estado, accion):
        return accion in ("izq", "der", "subir", "bajar", "limpiar", "nada")

    def transicion(self, estado, accion):
        robot, cuartos = estado
        cuartos = cuartos[:]  # Crear una copia de la lista para evitar efectos colaterales

        if accion == "nada":
            return (estado, 0 if all(c == "limpio" for c in cuartos) else 1)
        elif accion == "limpiar":
            cuartos[robot] = "limpio"
            return ((robot, cuartos), 1)
        elif accion == "izq":
            if robot in [1, 2, 4, 5, 7, 8]:
                return ((robot - 1, cuartos), 2)
            return (estado, 1)
        elif accion == "der":
            if robot in [0, 1, 3, 4, 6, 7]:
                return ((robot + 1, cuartos), 2)
            return (estado, 1)
        elif accion == "bajar":
            if robot in [3, 6]:
                return ((robot - 3, cuartos), 3)
            return (estado, 1)
        elif accion == "subir":
            if robot in [2, 5]:
                return ((robot + 3, cuartos), 3)
            return (estado, 1)

    def percepcion(self, estado):
        robot, cuartos = estado
        return (robot, cuartos[robot])
    
class NueveCuartosCiego(NueveCuartos):
    """
    Entorno de nueve cuartos donde el agente solo percibe su ubicación,
    pero no sabe si el cuarto está limpio o sucio.
    """
    def percepcion(self, estado):
        robot, _ = estado
        return robot  # Solo devuelve la posición del robot

class NueveCuartosEstocastico(NueveCuartos):
    """
    Clase para un entorno estocástico de nueve cuartos.
    """
    def transicion(self, estado, accion):
        robot, cuartos = estado
        cuartos = cuartos[:]  # Crear una copia de la lista para evitar efectos colaterales

        if accion == "nada":
            return (estado, 0 if all(c == "limpio" for c in cuartos) else 1)

        if accion == "limpiar":
            # 80% de probabilidad de limpiar correctamente
            if random() < 0.8:
                cuartos[robot] = "limpio"
            return ((robot, cuartos), 1)

        if accion in ("izq", "der", "subir", "bajar"):
            prob = random()
            if prob < 0.8:
                if accion == "izq" and robot in [1, 2, 4, 5, 7, 8]:
                    return ((robot - 1, cuartos), 2)
                elif accion == "der" and robot in [0, 1, 3, 4, 6, 7]:
                    return ((robot + 1, cuartos), 2)
                elif accion == "bajar" and robot in [3, 6]:
                    return ((robot - 3, cuartos), 3)
                elif accion == "subir" and robot in [2, 5]:
                    return ((robot + 3, cuartos), 3)
                else:
                    return (estado, 1)
            elif prob < 0.9:
                # 10% de probabilidad de quedarse en el mismo lugar
                return (estado, 1)
            else:
                # 10% de probabilidad de realizar una acción legal aleatoria
                acciones = ["izq", "der", "subir", "bajar", "limpiar", "nada"]
                accion_aleatoria = choice(acciones)
                return self.transicion(estado, accion_aleatoria)

        return (estado, 1)



class AgenteAleatorioNueveCuartos(entornos_f.Agente):
    """
    Un agente que solo regresa una accion al azar entre las acciones legales
    """
    def __init__(self, acciones):
        self.acciones = acciones

    def programa(self, _):
        return choice(self.acciones)

class AgenteReactivoNueveCuartos(entornos_f.Agente):
    """
    Un agente reactivo simple para tres cuartos
    """
    def programa(self, percepcion):
        robot, situacion = percepcion
        return ('limpiar' if situacion == 'sucio' else  # Limpia si el cuarto donde se encuentra está sucio
                choice(["izq", "der"]) if robot in [1, 4, 7] else # Se mueve si el cuarto donde se encuentra está limpio
                choice(["izq", "subir"]) if robot in [2, 5] else
                choice(["der", "bajar"]) if robot in [3, 6] else
                "izq" if robot == 8 else
                'der')

class AgenteReactivoModeloNueveCuartos(entornos_f.Agente):
    """
    Un agente reactivo basado en modelo para tres cuartos
    """
    def __init__(self, n_cuartos):
        """
        Inicializa el modelo interno en el peor de los casos
        """
        self.modelo = [0] + ['sucio'] * n_cuartos  # [robot, cuartos]

    def programa(self, percepcion):
        robot, situacion = percepcion

        # Actualiza el modelo interno
        self.modelo[0] = robot
        self.modelo[1 + robot] = situacion

        # Decide sobre el modelo interno
        cuartos = self.modelo[1:]
        return ('nada' if all(c == 'limpio' for c in cuartos) else # No hace nada si todo está limpio
                'limpiar' if situacion == 'sucio' else  # Limpia si el cuarto donde se encuentra está sucio
                choice(["izq", "der"]) if robot in [1, 4, 7] else # Se mueve si el cuarto donde se encuentra está limpio
                choice(["izq", "subir"]) if robot in [2, 5] else
                choice(["der", "bajar"]) if robot in [3, 6] else
                "izq" if robot == 8 else
                'der')
    
class AgenteReactivoModeloNueveCuartosCiego(entornos_f.Agente):
    """
    Un agente reactivo basado en modelo para el entorno NueveCuartosCiego.
    Mantiene un modelo interno para rastrear el estado de los cuartos.
    """
    def __init__(self, n_cuartos):
        self.modelo = [0] + ["sucio"] * n_cuartos  # [robot, cuartos]

    def programa(self, percepcion):
        robot = percepcion
        self.modelo[0] = robot

        cuartos = self.modelo[1:]
        if all(c == "limpio" for c in cuartos):
            return "nada"
        if self.modelo[1 + robot] == "sucio":
            self.modelo[1 + robot] = "limpio"
            return "limpiar"
        if robot in [1, 4, 7]: return choice(["izq", "der"])
        elif robot in [2, 5]: return choice(["izq", "subir"])
        elif robot in [3, 6]: return choice(["der", "bajar"])
        elif robot == 8: return "izq"
        return 'der'
    
class AgenteRacionalNueveCuartosEstocastico(entornos_f.Agente):
    """
    Agente racional para el entorno estocástico.
    """
    def __init__(self, n_cuartos):
        self.modelo = [0] + ["sucio"] * n_cuartos  # [robot, cuartos]

    def programa(self, percepcion):
        robot, situacion = percepcion

        # Actualizar el modelo interno
        self.modelo[0] = robot
        self.modelo[1 + robot] = situacion

        # Verificar si todo está limpio
        cuartos = self.modelo[1:]
        if all(c == "limpio" for c in cuartos):
            return "nada"       # No hace nada si todo está limpio

        # Limpiar si está sucio
        if situacion == "sucio":
            return "limpiar"    # Limpia si el cuarto donde se encuentra está sucio

        # Decidir movimiento basado en el modelo interno
        vecinos = []
        if robot in [1, 2, 4, 5, 7, 8]:
            vecinos.append("izq")
        if robot in [0, 1, 3, 4, 6, 7]:
            vecinos.append("der")
        if robot in [3, 6]:
            vecinos.append("bajar")
        if robot in [2, 5]:
            vecinos.append("subir")

        # Priorizar cuartos sucios
        for accion in vecinos:
            nuevo_estado, _ = NueveCuartosEstocastico().transicion((robot, cuartos), accion)
            if nuevo_estado[1][nuevo_estado[0]] == "sucio":
                return accion

        # Movimiento aleatorio si no hay prioridad
        return choice(vecinos)
    
def prueba_agente(agente, entorno_class):
    entornos_f.imprime_simulacion(
        entornos_f.simulador(
            entorno_class(),
            agente,
            (0, ["sucio"] * 9),  # Estado inicial
            200
        ),
        [0, ["sucio"] * 9]
    )

def test():
    """
    Prueba del entorno de nueve cuartos y los agentes
    """
    print("Prueba del entorno con un agente aleatorio")
    prueba_agente(AgenteAleatorioNueveCuartos(['izq', 'der', "subir", "bajar", 'limpiar', 'nada']), NueveCuartos)

    print("Prueba del entorno con un agente reactivo")
    prueba_agente(AgenteReactivoNueveCuartos(), NueveCuartos)

    print("Prueba del entorno con un agente reactivo con modelo")
    prueba_agente(AgenteReactivoModeloNueveCuartos(9), NueveCuartos)

def test_ciego():
    """
    Prueba del entorno de nueve cuartos ciego y los agentes
    """
    print("Prueba del entorno NueveCuartosCiego con un agente aleatorio")
    prueba_agente(AgenteAleatorioNueveCuartos(['izq', 'der', "subir", "bajar", 'limpiar', 'nada']), NueveCuartosCiego)

    print("Prueba del entorno NueveCuartosCiego con un agente reactivo basado en modelo")
    prueba_agente(AgenteReactivoModeloNueveCuartosCiego(9), NueveCuartosCiego)

def test_estocastico():
    """
    Prueba del entorno estocástico y los agentes
    """
    print("Prueba del entorno NueveCuartosEstocastico con un agente aleatorio")
    prueba_agente(AgenteAleatorioNueveCuartos(["izq", "der", "subir", "bajar", "limpiar", "nada"]), NueveCuartosEstocastico)

    print("Prueba del entorno NueveCuartosEstocasticocon un agente racional")
    prueba_agente(AgenteRacionalNueveCuartosEstocastico(9), NueveCuartosEstocastico)


if __name__ == "__main__":
    # test()
    # test_ciego()
    test_estocastico()
