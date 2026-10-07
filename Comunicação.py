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

    # =================================================
    # LISTAR PORTAS
    # =================================================

    def listar_portas(self):

        portas = serial.tools.list_ports.comports()

        print("\nPORTAS ENCONTRADAS:")

        for porta in portas:

            print(
                f"{porta.device} - "
                f"{porta.description}"
            )

        return portas

    # =================================================
    # ENCONTRAR ESP32
    # =================================================

    def encontrar_porta(self):

        portas = (
            serial.tools.list_ports.comports()
        )

        candidatos = []

        for porta in portas:

            descricao = str(
                porta.description
            ).lower()

            fabricante = str(
                porta.manufacturer
            ).lower()

            texto = (
                descricao +
                " " +
                fabricante
            )

            if (
                "esp32" in texto
                or "cp210" in texto
                or "ch340" in texto
                or "silicon labs" in texto
            ):

                candidatos.append(
                    porta.device
                )

        if not candidatos:

            print(
                "\nESP32 não encontrado."
            )

            self.listar_portas()

            return None

        if len(candidatos) > 1:

            print(
                "\nMais de um dispositivo encontrado:"
            )

            for item in candidatos:

                print(
                    f" - {item}"
                )

        return candidatos[0]

    # =================================================
    # CONECTAR
    # =================================================

    def conectar(self):

        if (
            self.esp32 is not None
            and self.esp32.is_open
        ):

            return True

        porta = self.porta

        if porta is None:

            porta = self.encontrar_porta()

        if porta is None:

            return False

        try:

            print(
                f"Conectando em {porta}..."
            )

            self.esp32 = serial.Serial(
                port=porta,
                baudrate=self.velocidade,
                timeout=1
            )

            time.sleep(2)

            self.esp32.reset_input_buffer()

            print(
                f"ESP32 conectado em {porta}"
            )

            return True

        except PermissionError as erro:

            print(
                f"Acesso negado à {porta}."
            )

            print(
                "Feche o Monitor Serial."
            )

            print(
                "Feche também outros programas "
                "que possam estar usando a porta."
            )

            print(erro)

            self.esp32 = None

            return False

        except serial.SerialException as erro:

            print(
                "Erro na comunicação serial:"
            )

            print(erro)

            self.esp32 = None

            return False

    # =================================================
    # ENVIAR
    # =================================================

    def enviar(
        self,
        comando
    ):

        if not self.conectar():

            return False

        try:

            mensagem = (
                comando.strip() +
                "\n"
            )

            self.esp32.write(
                mensagem.encode(
                    "utf-8"
                )
            )

            self.esp32.flush()

            print(
                "Enviado:",
                comando
            )

            return True

        except Exception as erro:

            print(
                "Erro ao enviar:",
                erro
            )

            return False

    # =================================================
    # CANALETAS
    # =================================================

    def enviar_abertura(
        self,
        abertura_cm
    ):

        return self.enviar(
            f"ABRIR:{float(abertura_cm):.2f}"
        )

    # =================================================
    # ESTEIRA
    # =================================================

    def ligar_esteira(self):

        return self.enviar(
            "ESTEIRA:LIGAR"
        )

    def parar_esteira(self):

        return self.enviar(
            "ESTEIRA:PARAR"
        )

    def reverso_esteira(self):

        return self.enviar(
            "ESTEIRA:REVERSO"
        )

    # =================================================
    # VELOCIDADE
    # =================================================

    def definir_velocidade(
        self,
        velocidade
    ):

        velocidade = max(
            0,
            min(
                255,
                int(velocidade)
            )
        )

        return self.enviar(
            f"ESTEIRA:VELOCIDADE:{velocidade}"
        )

    # =================================================
    # TESTES
    # =================================================

    def teste_esteira(self):

        return self.enviar(
            "TESTE:ESTEIRA"
        )

    def teste_canaletas(self):

        return self.enviar(
            "TESTE:CANALETAS"
        )

    def solicitar_status(self):

        return self.enviar(
            "STATUS"
        )

    # =================================================
    # FECHAR
    # =================================================

    def fechar(self):

        if self.esp32 is not None:

            try:

                if self.esp32.is_open:

                    self.esp32.close()

            except Exception:

                pass

            self.esp32 = None

            print(
                "Comunicação encerrada."
            )