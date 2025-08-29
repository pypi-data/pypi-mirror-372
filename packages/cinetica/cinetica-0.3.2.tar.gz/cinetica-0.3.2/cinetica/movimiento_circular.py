import math

class MovimientoCircular:
    """
    Clase para calcular y simular Movimiento Circular Uniforme (MCU)
    y Movimiento Circular Uniformemente Variado (MCUV).
    """

    def __init__(self, radio: float, posicion_angular_inicial: float = 0.0, velocidad_angular_inicial: float = 0.0, aceleracion_angular_inicial: float = 0.0):
        """
        Inicializa el objeto MovimientoCircular con las condiciones iniciales.

        Args:
            radio (float): Radio de la trayectoria circular (m).
            posicion_angular_inicial (float): Posición angular inicial (radianes).
            velocidad_angular_inicial (float): Velocidad angular inicial (rad/s).
            aceleracion_angular_inicial (float): Aceleración angular inicial (rad/s^2).
        """
        if radio <= 0:
            raise ValueError("El radio debe ser un valor positivo.")

        self.radio = radio
        self.posicion_angular_inicial = posicion_angular_inicial
        self.velocidad_angular_inicial = velocidad_angular_inicial
        self.aceleracion_angular_inicial = aceleracion_angular_inicial

    # Métodos para MCU (Movimiento Circular Uniforme)
    def mcu_posicion_angular(self, tiempo: float) -> float:
        """
        Calcula la posición angular en MCU.
        Ecuación: theta = theta0 + omega * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición angular final (radianes).
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_angular_inicial + self.velocidad_angular_inicial * tiempo

    def mcu_velocidad_angular(self) -> float:
        """
        Calcula la velocidad angular en MCU (es constante).
        Ecuación: omega = omega0

        Returns:
            float: Velocidad angular (rad/s).
        """
        return self.velocidad_angular_inicial

    def mcu_velocidad_tangencial(self) -> float:
        """
        Calcula la velocidad tangencial en MCU.
        Ecuación: v = omega * R

        Returns:
            float: Velocidad tangencial (m/s).
        """
        return self.mcu_velocidad_angular() * self.radio

    def mcu_aceleracion_centripeta(self) -> float:
        """
        Calcula la aceleración centrípeta en MCU.
        Ecuación: ac = omega^2 * R = v^2 / R

        Returns:
            float: Aceleración centrípeta (m/s^2).
        """
        return (self.mcu_velocidad_angular() ** 2) * self.radio

    def mcu_periodo(self) -> float:
        """
        Calcula el período en MCU.
        Ecuación: T = 2 * pi / omega

        Returns:
            float: Período (s).
        """
        if self.velocidad_angular_inicial == 0:
            raise ValueError("La velocidad angular inicial no puede ser cero para calcular el período en MCU.")
        return (2 * math.pi) / self.velocidad_angular_inicial

    def mcu_frecuencia(self) -> float:
        """
        Calcula la frecuencia en MCU.
        Ecuación: f = 1 / T = omega / (2 * pi)

        Returns:
            float: Frecuencia (Hz).
        """
        if self.velocidad_angular_inicial == 0:
            raise ValueError("La velocidad angular inicial no puede ser cero para calcular la frecuencia en MCU.")
        return self.velocidad_angular_inicial / (2 * math.pi)

    # Métodos para MCUV (Movimiento Circular Uniformemente Variado)
    def mcuv_posicion_angular(self, tiempo: float) -> float:
        """
        Calcula la posición angular en MCUV.
        Ecuación: theta = theta0 + omega0 * t + 0.5 * alpha * t^2

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición angular final (radianes).
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_angular_inicial + self.velocidad_angular_inicial * tiempo + 0.5 * self.aceleracion_angular_inicial * (tiempo ** 2)

    def mcuv_velocidad_angular(self, tiempo: float) -> float:
        """
        Calcula la velocidad angular en MCUV.
        Ecuación: omega = omega0 + alpha * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Velocidad angular final (rad/s).
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_angular_inicial + self.aceleracion_angular_inicial * tiempo

    def mcuv_aceleracion_angular(self) -> float:
        """
        Calcula la aceleración angular en MCUV (es constante).
        Ecuación: alpha = alpha0

        Returns:
            float: Aceleración angular (rad/s^2).
        """
        return self.aceleracion_angular_inicial

    def mcuv_velocidad_tangencial(self, tiempo: float) -> float:
        """
        Calcula la velocidad tangencial en MCUV.
        Ecuación: v = omega * R

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Velocidad tangencial (m/s).
        """
        return self.mcuv_velocidad_angular(tiempo) * self.radio

    def mcuv_aceleracion_tangencial(self) -> float:
        """
        Calcula la aceleración tangencial en MCUV.
        Ecuación: at = alpha * R

        Returns:
            float: Aceleración tangencial (m/s^2).
        """
        return self.aceleracion_angular_inicial * self.radio

    def mcuv_aceleracion_centripeta(self, tiempo: float) -> float:
        """
        Calcula la aceleración centrípeta en MCUV.
        Ecuación: ac = omega^2 * R

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Aceleración centrípeta (m/s^2).
        """
        return (self.mcuv_velocidad_angular(tiempo) ** 2) * self.radio

    def mcuv_aceleracion_total(self, tiempo: float) -> float:
        """
        Calcula la magnitud de la aceleración total en MCUV.
        Ecuación: a_total = sqrt(at^2 + ac^2)

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Magnitud de la aceleración total (m/s^2).
        """
        at = self.mcuv_aceleracion_tangencial()
        ac = self.mcuv_aceleracion_centripeta(tiempo)
        return math.sqrt(at**2 + ac**2)
