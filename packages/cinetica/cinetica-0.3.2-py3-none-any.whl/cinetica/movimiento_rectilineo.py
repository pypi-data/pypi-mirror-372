import math

class MovimientoRectilineo:
    """
    Clase para calcular posición, velocidad y aceleración en Movimiento Rectilíneo Uniforme (MRU)
    y Movimiento Rectilíneo Uniformemente Variado (MRUV).
    """

    def __init__(self, posicion_inicial: float = 0.0, velocidad_inicial: float = 0.0, aceleracion_inicial: float = 0.0):
        """
        Inicializa el objeto MovimientoRectilineo con condiciones iniciales.

        Args:
            posicion_inicial (float): Posición inicial del objeto (m).
            velocidad_inicial (float): Velocidad inicial del objeto (m/s).
            aceleracion_inicial (float): Aceleración inicial del objeto (m/s^2).
        """
        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial
        self.aceleracion_inicial = aceleracion_inicial

    # Métodos para MRU (Movimiento Rectilíneo Uniforme)
    def mru_posicion(self, tiempo: float) -> float:
        """
        Calcula la posición en MRU.
        Ecuación: x = x0 + v * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición final (m).
        """
        return self.posicion_inicial + self.velocidad_inicial * tiempo

    def mru_velocidad(self) -> float:
        """
        Calcula la velocidad en MRU (es constante).
        Ecuación: v = v0

        Returns:
            float: Velocidad (m/s).
        """
        return self.velocidad_inicial

    # Métodos para MRUV (Movimiento Rectilíneo Uniformemente Variado)
    def mruv_posicion(self, tiempo: float) -> float:
        """
        Calcula la posición en MRUV.
        Ecuación: x = x0 + v0 * t + 0.5 * a * t^2

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición final (m).
        """
        return self.posicion_inicial + self.velocidad_inicial * tiempo + 0.5 * self.aceleracion_inicial * (tiempo ** 2)

    def mruv_velocidad(self, tiempo: float) -> float:
        """
        Calcula la velocidad en MRUV.
        Ecuación: v = v0 + a * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Velocidad final (m/s).
        """
        return self.velocidad_inicial + self.aceleracion_inicial * tiempo

    def mruv_aceleracion(self) -> float:
        """
        Calcula la aceleración en MRUV (es constante).
        Ecuación: a = a0

        Returns:
            float: Aceleración (m/s^2).
        """
        return self.aceleracion_inicial

    def mruv_velocidad_sin_tiempo(self, posicion_final: float) -> float:
        """
        Calcula la velocidad final en MRUV sin conocer el tiempo.
        Ecuación: v^2 = v0^2 + 2 * a * (x - x0)

        Args:
            posicion_final (float): Posición final del objeto (m).

        Returns:
            float: Velocidad final (m/s).
        """
        delta_x = posicion_final - self.posicion_inicial
        v_squared = (self.velocidad_inicial ** 2) + 2 * self.aceleracion_inicial * delta_x
        if v_squared < 0:
            raise ValueError("No se puede calcular la velocidad real (velocidad al cuadrado negativa).")
        return math.sqrt(v_squared)
