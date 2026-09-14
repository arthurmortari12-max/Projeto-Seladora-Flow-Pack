import serial
import serial.tools.list_ports
import time


class ComunicacaoESP32:

    def __init__(
        self,
        porta=None,
        velocidade=115200
    ):

        self.porta = porta
        self.velocidade = velocidade

        self.esp32 = None

    # ---------------------------------------------------------
    # ENCONTRAR ESP32
    # ---------------------------------------------------------

    def encontrar_porta(self):

        portas = serial.tools.list_ports.comports()

        for porta in portas:

            descricao = (
                str(porta.description)
                .lower()
            )

            if (
                "esp32" in descricao
                or "cp210" in descricao
                or "ch340" in descricao
                or "usb" in descricao
            ):

                return porta.device

        return None

    # ---------------------------------------------------------
    # CONECTAR
    # ---------------------------------------------------------

    def conectar(self):

        porta = self.porta

        if porta is None:

            porta = self.encontrar_porta()

        if porta is None:

            print(
                "ESP32 não encontrado."
            )

            return False

        try:

            self.esp32 = serial.Serial(
                porta,
                self.velocidade,
                timeout=1
            )

            time.sleep(2)

            print(
                f"ESP32 conectado em {porta}"
            )

            return True

        except Exception as erro:

            print(
                "Erro ao conectar:",
                erro
            )

            return False

    # ---------------------------------------------------------
    # ENVIAR ABERTURA
    # ---------------------------------------------------------

    def enviar_abertura(
        self,
        abertura_cm
    ):

        if self.esp32 is None:

            if not self.conectar():

                return False

        comando = (
            f"ABRIR:{abertura_cm:.2f}\n"
        )

        try:

            self.esp32.write(
                comando.encode()
            )

            print(
                "Comando enviado:",
                comando.strip()
            )

            return True

        except Exception as erro:

            print(
                "Erro ao enviar:",
                erro
            )

            return False

    # ---------------------------------------------------------
    # PARAR ESTEIRA
    # ---------------------------------------------------------

    def parar_esteira(self):

        if self.esp32:

            self.esp32.write(
                b"ESTEIRA:PARAR\n"
            )

    # ---------------------------------------------------------
    # LIGAR ESTEIRA
    # ---------------------------------------------------------

    def ligar_esteira(self):

        if self.esp32:

            self.esp32.write(
                b"ESTEIRA:LIGAR\n"
            )

    # ---------------------------------------------------------
    # FECHAR
    # ---------------------------------------------------------

    def fechar(self):

        if self.esp32:

            self.esp32.close()

            self.esp32 = None