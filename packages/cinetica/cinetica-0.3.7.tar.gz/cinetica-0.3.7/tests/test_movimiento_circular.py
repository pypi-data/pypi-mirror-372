import pytest
from cinetica.movimiento_circular import MovimientoCircular
import math

def test_init_valid_params():
    mc = MovimientoCircular(radio=5.0, posicion_angular_inicial=0.0, velocidad_angular_inicial=2.0, aceleracion_angular_inicial=0.5)
    assert mc.radio == 5.0
    assert mc.posicion_angular_inicial == 0.0
    assert mc.velocidad_angular_inicial == 2.0
    assert mc.aceleracion_angular_inicial == 0.5

def test_init_invalid_radio():
    with pytest.raises(ValueError, match="El radio debe ser un valor positivo."):
        MovimientoCircular(radio=0.0)
    with pytest.raises(ValueError, match="El radio debe ser un valor positivo."):
        MovimientoCircular(radio=-1.0)

# MCU Tests
def test_mcu_posicion_angular():
    mc = MovimientoCircular(radio=1.0, posicion_angular_inicial=0.0, velocidad_angular_inicial=math.pi/2)
    assert mc.mcu_posicion_angular(tiempo=1.0) == pytest.approx(math.pi/2)
    assert mc.mcu_posicion_angular(tiempo=2.0) == pytest.approx(math.pi)
    assert mc.mcu_posicion_angular(tiempo=0.0) == pytest.approx(0.0)

def test_mcu_posicion_angular_invalid_tiempo():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=1.0)
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo."):
        mc.mcu_posicion_angular(tiempo=-1.0)

def test_mcu_velocidad_angular():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=3.0)
    assert mc.mcu_velocidad_angular() == 3.0

def test_mcu_velocidad_tangencial():
    mc = MovimientoCircular(radio=2.0, velocidad_angular_inicial=3.0)
    assert mc.mcu_velocidad_tangencial() == 6.0

def test_mcu_aceleracion_centripeta():
    mc = MovimientoCircular(radio=2.0, velocidad_angular_inicial=3.0)
    assert mc.mcu_aceleracion_centripeta() == pytest.approx(3.0**2 * 2.0) # 18.0

def test_mcu_periodo():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=math.pi)
    assert mc.mcu_periodo() == pytest.approx(2.0) # T = 2*pi / pi = 2

def test_mcu_periodo_zero_omega():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=0.0)
    assert mc.mcu_periodo() == math.inf

def test_mcu_frecuencia():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=math.pi)
    assert mc.mcu_frecuencia() == pytest.approx(0.5) # f = pi / (2*pi) = 0.5

def test_mcu_frecuencia_zero_omega():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=0.0)
    assert mc.mcu_frecuencia() == 0.0

# MCUV Tests
def test_mcuv_posicion_angular():
    mc = MovimientoCircular(radio=1.0, posicion_angular_inicial=0.0, velocidad_angular_inicial=1.0, aceleracion_angular_inicial=0.5)
    # theta = 0 + 1*2 + 0.5*0.5*2^2 = 2 + 0.5*0.5*4 = 2 + 1 = 3
    assert mc.mcuv_posicion_angular(tiempo=2.0) == pytest.approx(3.0)
    assert mc.mcuv_posicion_angular(tiempo=0.0) == pytest.approx(0.0)

def test_mcuv_posicion_angular_invalid_tiempo():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=1.0)
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo."):
        mc.mcuv_posicion_angular(tiempo=-1.0)

def test_mcuv_velocidad_angular():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=1.0, aceleracion_angular_inicial=0.5)
    # omega = 1 + 0.5*2 = 2
    assert mc.mcuv_velocidad_angular(tiempo=2.0) == pytest.approx(2.0)
    assert mc.mcuv_velocidad_angular(tiempo=0.0) == pytest.approx(1.0)

def test_mcuv_velocidad_angular_invalid_tiempo():
    mc = MovimientoCircular(radio=1.0, velocidad_angular_inicial=1.0)
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo."):
        mc.mcuv_velocidad_angular(tiempo=-1.0)

def test_mcuv_aceleracion_angular():
    mc = MovimientoCircular(radio=1.0, aceleracion_angular_inicial=0.75)
    assert mc.mcuv_aceleracion_angular() == 0.75

def test_mcuv_velocidad_tangencial():
    mc = MovimientoCircular(radio=2.0, velocidad_angular_inicial=1.0, aceleracion_angular_inicial=0.5)
    # omega(2s) = 1 + 0.5*2 = 2
    # v = omega * R = 2 * 2 = 4
    assert mc.mcuv_velocidad_tangencial(tiempo=2.0) == pytest.approx(4.0)

def test_mcuv_aceleracion_tangencial():
    mc = MovimientoCircular(radio=2.0, aceleracion_angular_inicial=0.5)
    # at = alpha * R = 0.5 * 2 = 1
    assert mc.mcuv_aceleracion_tangencial() == pytest.approx(1.0)

def test_mcuv_aceleracion_centripeta():
    mc = MovimientoCircular(radio=2.0, velocidad_angular_inicial=1.0, aceleracion_angular_inicial=0.5)
    # omega(2s) = 2
    # ac = omega^2 * R = 2^2 * 2 = 8
    assert mc.mcuv_aceleracion_centripeta(tiempo=2.0) == pytest.approx(8.0)

def test_mcuv_aceleracion_total():
    mc = MovimientoCircular(radio=2.0, velocidad_angular_inicial=1.0, aceleracion_angular_inicial=0.5)
    # at = 1.0
    # ac(2s) = 8.0
    # a_total = sqrt(1^2 + 8^2) = sqrt(1 + 64) = sqrt(65) approx 8.062
    assert mc.mcuv_aceleracion_total(tiempo=2.0) == pytest.approx(math.sqrt(65))
