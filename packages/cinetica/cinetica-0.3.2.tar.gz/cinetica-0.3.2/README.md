# Cinetica

Cinetica is a Python library designed to provide various modules for physics calculations and simulations.

## Installation

```bash
pip install cinetica
```

## Usage

### Movimiento Rectilíneo

El módulo `movimiento_rectilineo` proporciona la clase `MovimientoRectilineo` para calcular posición, velocidad y aceleración en Movimiento Rectilíneo Uniforme (MRU) y Movimiento Rectilíneo Uniformemente Variado (MRUV).

**Ejemplo de uso:**

```python
from cinetica.movimiento_rectilineo import MovimientoRectilineo

# MRU
mru = MovimientoRectilineo(posicion_inicial=10.0, velocidad_inicial=2.0)
posicion_mru = mru.mru_posicion(tiempo=5.0)
velocidad_mru = mru.mru_velocidad()
print(f"MRU - Posición a los 5s: {posicion_mru} m, Velocidad: {velocidad_mru} m/s")

# MRUV
mruv = MovimientoRectilineo(posicion_inicial=0.0, velocidad_inicial=10.0, aceleracion_inicial=2.0)
posicion_mruv = mruv.mruv_posicion(tiempo=3.0)
velocidad_mruv = mruv.mruv_velocidad(tiempo=3.0)
aceleracion_mruv = mruv.mruv_aceleracion()
print(f"MRUV - Posición a los 3s: {posicion_mruv} m, Velocidad: {velocidad_mruv} m/s, Aceleración: {aceleracion_mruv} m/s^2")

# MRUV sin tiempo
mruv_sin_tiempo = MovimientoRectilineo(posicion_inicial=0.0, velocidad_inicial=0.0, aceleracion_inicial=2.0)
velocidad_final_sin_tiempo = mruv_sin_tiempo.mruv_velocidad_sin_tiempo(posicion_final=16.0)
print(f"MRUV - Velocidad final sin tiempo (para posición 16m): {velocidad_final_sin_tiempo} m/s")
```

### Movimiento Parabólico

El módulo `movimiento_parabolico` proporciona la clase `MovimientoParabolico` para simular trayectorias, alcance y tiempo de vuelo de un proyectil.

**Ejemplo de uso:**

```python
from cinetica.movimiento_parabolico import MovimientoParabolico

# Lanzamiento con velocidad inicial de 20 m/s y ángulo de 45 grados
mp = MovimientoParabolico(velocidad_inicial=20.0, angulo_grados=45)

# Calcular posición a los 1.5 segundos
pos_x, pos_y = mp.posicion(tiempo=1.5)
print(f"MP - Posición a los 1.5s: x={pos_x:.2f} m, y={pos_y:.2f} m")

# Calcular velocidad a los 1.5 segundos
vel_x, vel_y = mp.velocidad(tiempo=1.5)
print(f"MP - Velocidad a los 1.5s: vx={vel_x:.2f} m/s, vy={vel_y:.2f} m/s")

# Calcular tiempo de vuelo, altura máxima y alcance máximo
tiempo_vuelo = mp.tiempo_vuelo()
altura_maxima = mp.altura_maxima()
alcance_maximo = mp.alcance_maximo()
print(f"MP - Tiempo de vuelo: {tiempo_vuelo:.2f} s")
print(f"MP - Altura máxima: {altura_maxima:.2f} m")
print(f"MP - Alcance máximo: {alcance_maximo:.2f} m")
```

### Movimiento Circular

El módulo `movimiento_circular` proporciona la clase `MovimientoCircular` para calcular y simular Movimiento Circular Uniforme (MCU) y Movimiento Circular Uniformemente Variado (MCUV).

**Ejemplo de uso:**

```python
from cinetica.movimiento_circular import MovimientoCircular
import math

# MCU con radio de 2m y velocidad angular de pi/2 rad/s
mcu = MovimientoCircular(radio=2.0, velocidad_angular_inicial=math.pi/2)

# Posición angular a los 1s
pos_angular_mcu = mcu.mcu_posicion_angular(tiempo=1.0)
print(f"MCU - Posición angular a 1s: {pos_angular_mcu:.2f} rad")

# Velocidad tangencial y aceleración centrípeta
vel_tangencial_mcu = mcu.mcu_velocidad_tangencial()
acel_centripeta_mcu = mcu.mcu_aceleracion_centripeta()
print(f"MCU - Velocidad tangencial: {vel_tangencial_mcu:.2f} m/s, Aceleración centrípeta: {acel_centripeta_mcu:.2f} m/s^2")

# MCUV con radio de 1m, vel. angular inicial 1 rad/s, acel. angular 0.5 rad/s^2
mcuv = MovimientoCircular(radio=1.0, velocidad_angular_inicial=1.0, aceleracion_angular_inicial=0.5)

# Velocidad angular a los 2s
vel_angular_mcuv = mcuv.mcuv_velocidad_angular(tiempo=2.0)
print(f"MCUV - Velocidad angular a 2s: {vel_angular_mcuv:.2f} rad/s")

# Aceleración tangencial y centrípeta a los 2s
acel_tangencial_mcuv = mcuv.mcuv_aceleracion_tangencial()
acel_centripeta_mcuv = mcuv.mcuv_aceleracion_centripeta(tiempo=2.0)
acel_total_mcuv = mcuv.mcuv_aceleracion_total(tiempo=2.0)
print(f"MCUV - Aceleración tangencial: {acel_tangencial_mcuv:.2f} m/s^2, Aceleración centrípeta: {acel_centripeta_mcuv:.2f} m/s^2, Aceleración total: {acel_total_mcuv:.2f} m/s^2")
```

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
