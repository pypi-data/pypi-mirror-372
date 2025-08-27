# ejercicios/ejercicio.py
# -------------------------------
# Requierements
# -------------------------------
from abc import ABC
from trackerfit.utils.angulos import calcular_angulo_landmarks
from trackerfit.utils.tipo_esfuerzo_enum import TipoEsfuerzo

# -------------------------------
# Helpers
# -------------------------------

class Ejercicio(ABC):
    """
    Clase base para ejercicios. Define la lógica general de conteo de repeticiones
    basada en el análisis de ángulos entre tres landmarks clave.
    """
    def __init__(self, angulo_min, angulo_max, puntos, tipo_esfuerzo : TipoEsfuerzo = TipoEsfuerzo.CONTRACCION):
        """
        Inicializa un ejercicio con umbrales y puntos clave.

        Args:
            angulo_min (float): Ángulo mínimo esperado (posición contraída).
            angulo_max (float): Ángulo máximo esperado (posición extendida).
            puntos (tuple): IDs de 3 landmarks (id1, id2, id3) en orden.
            tipo_esfuerzo (TipoEsfuerzo) : CONTRACCION o AMPLITUD
        """
        self.reps = 0
        self.arriba = False
        self.abajo = False
        
        self.angulo_min = angulo_min
        self.angulo_max = angulo_max
        
        self.id1, self.id2, self.id3 = puntos
        
        self.umbral_validacion = 90 # Valor por defecto, en las subclases se sobrescribe
        self.tipo_esfuerzo = tipo_esfuerzo
        self._esforzandose = None

    def actualizar(self, puntos_detectados):
        """
        Actualiza el estado del ejercicio con los puntos detectados.

        Returns:
            tuple: (ángulo actual, repeticiones acumuladas)
        """
        if not all(k in puntos_detectados for k in [self.id1, self.id2, self.id3]):
            return None, self.reps

        # Frame a frame iremos calculando el ángulo que forman los puntos clave del ejercicio,buscando detectar transiciones.
        angulo = calcular_angulo_landmarks(puntos_detectados, self.id1, self.id2, self.id3)
        self.detectar_transicion(angulo) # Si se detectara una transición entre arriba y abajo, se agregaría una repetición.
        
        return angulo, self.reps

    def detectar_transicion(self, angulo: float | None):
        """
        Detecta si ha habido una transición válida (subida y bajada) para contar una repetición.
        """

        esforzandose = self.esfuerzo_activo(angulo)
        
        if self._esforzandose is None:
            self._esforzandose = esforzandose
            return
                
        if self._esforzandose is False and esforzandose is True:
            self.reps += 1
            
        self._esforzandose = esforzandose
        # if angulo >= self.angulo_max:
        #     self.arriba = True
        # if self.arriba and not self.abajo and angulo <= self.angulo_min:
        #     self.abajo = True
        # if self.arriba and self.abajo and angulo >= self.angulo_max:
        #     self.reps += 1 # Cuando detectamos que ya ha subido y bajado añadimos una repetición
        #     self.arriba = False
        #     self.abajo = False

    def reset(self):
        """Reinicia el conteo de repeticiones."""
        self.reps = 0
        self.arriba = False
        self.abajo = False
        self._esforzandose = None

    def get_reps(self):
        """Devuelve el número actual de repeticiones."""
        return self.reps

    def esfuerzo_activo(self, angulo: float | None) -> bool:
        """
        True si, para el ángulo dado, el estado corresponde al esfuerzo del ejercicio
        según su tipo de esfuerzo
        """
        if angulo is None:
            return false
        
        if self.tipo_esfuerzo == TipoEsfuerzo.CONTRACCION:
            return angulo <= self.angulo_min
        
        if self.tipo_esfuerzo == TipoEsfuerzo.AMPLITUD:
            return angulo >= self.angulo_max
    
    def estado_angulo(self, angulo: float | None) -> str:
        """
        'esfuerzo' o 'relajación' para colorear en tiempo real.
        """
        return "esfuerzo" if self.esfuerzo_activo(angulo) else "relajacion"