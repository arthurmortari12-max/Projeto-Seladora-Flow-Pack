import cv2


class CameraFlowPack:

    def __init__(
        self,
        indice_camera=1,
        pixels_por_cm=11,
        area_minima=3000
    ):

        self.indice_camera = indice_camera
        self.pixels_por_cm = pixels_por_cm
        self.area_minima = area_minima

        self.camera = None

    # ---------------------------------------------------------
    # INICIAR CÂMERA
    # ---------------------------------------------------------

    def iniciar(self):

        self.camera = cv2.VideoCapture(
            self.indice_camera
        )

        # Se câmera 1 não funcionar, tenta câmera 0
        if not self.camera.isOpened():

            self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():

            return False

        return True

    # ---------------------------------------------------------
    # DETECTAR PRODUTO
    # ---------------------------------------------------------

    def detectar(self, frame):

        cinza = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Reduz ruídos
        cinza = cv2.GaussianBlur(
            cinza,
            (5, 5),
            0
        )

        # Detecta bordas
        bordas = cv2.Canny(
            cinza,
            50,
            150
        )

        # Encontra contornos
        contornos, _ = cv2.findContours(
            bordas,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contornos:

            return None

        # Maior objeto encontrado
        maior = max(
            contornos,
            key=cv2.contourArea
        )

        area = cv2.contourArea(
            maior
        )

        if area < self.area_minima:

            return None

        x, y, largura_px, altura_px = cv2.boundingRect(
            maior
        )

        if largura_px <= 0 or altura_px <= 0:

            return None

        largura_cm = (
            largura_px /
            self.pixels_por_cm
        )

        comprimento_cm = (
            altura_px /
            self.pixels_por_cm
        )

        return {

            "x": x,
            "y": y,

            "largura_px": largura_px,
            "altura_px": altura_px,

            "largura_cm": largura_cm,
            "comprimento_cm": comprimento_cm
        }

    # ---------------------------------------------------------
    # PROCESSAR IMAGEM
    # ---------------------------------------------------------

    def processar(self, frame):

        produto = self.detectar(
            frame
        )

        if produto is None:

            return frame, None

        x = produto["x"]
        y = produto["y"]

        largura_px = produto["largura_px"]
        altura_px = produto["altura_px"]

        largura_cm = produto["largura_cm"]
        comprimento_cm = produto["comprimento_cm"]

        # -----------------------------------------------------
        # RETÂNGULO VERDE
        # -----------------------------------------------------

        cv2.rectangle(
            frame,

            (x, y),

            (
                x + largura_px,
                y + altura_px
            ),

            (0, 255, 0),

            2
        )

        # -----------------------------------------------------
        # MEDIDAS
        # -----------------------------------------------------

        texto_largura = (
            f"Largura: {largura_cm:.2f} cm"
        )

        texto_comprimento = (
            f"Comprimento: {comprimento_cm:.2f} cm"
        )

        cv2.putText(
            frame,
            texto_largura,
            (x, max(y - 30, 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            texto_comprimento,
            (x, max(y - 5, 55)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        return frame, produto

    # ---------------------------------------------------------
    # FECHAR
    # ---------------------------------------------------------

    def fechar(self):

        if self.camera:

            self.camera.release()

            self.camera = None

        cv2.destroyAllWindows()