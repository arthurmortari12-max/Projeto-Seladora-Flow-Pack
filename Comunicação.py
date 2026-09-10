import serial
import time


# ============================================================
# CONFIGURAÇÃO DO ARDUINO
# ============================================================

PORTA_ARDUINO = "COM5"
BAUDRATE = 115200

arduino = None


# ============================================================
# CONECTAR
# ============================================================

def conectar_arduino():

    global arduino

    try:

        arduino = serial.Serial(
            PORTA_ARDUINO,
            BAUDRATE,
            timeout=1
        )

        time.sleep(2)

        print(f"Arduino conectado em {PORTA_ARDUINO}")

        return True

    except serial.SerialException as erro:

        print(f"Erro ao conectar ao Arduino: {erro}")

        return False


# ============================================================
# ENVIAR MEDIDAS
# ============================================================

def enviar_medidas(largura_cm, altura_cm):

    if arduino is None or not arduino.is_open:
        print("Arduino não conectado.")
        return

    comando = (
        f"LARGURA:{largura_cm:.1f};"
        f"ALTURA:{altura_cm:.1f}\n"
    )

    try:

        arduino.write(
            comando.encode("utf-8")
        )

        print(
            "Enviado para Arduino:",
            comando.strip()
        )

    except serial.SerialException as erro:

        print(
            f"Erro ao enviar dados: {erro}"
        )


# ============================================================
# FECHAR COMUNICAÇÃO
# ============================================================

def desconectar_arduino():

    global arduino

    if arduino is not None and arduino.is_open:

        arduino.close()

        print("Arduino desconectado.")