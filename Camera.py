import cv2


class CameraFlowPack:

    def __init__(
        self,
        indice_camera=1,
        pixels_por_cm=28,
        area_minima=3000
    ):

        self.indice_camera = indice_camera
        self.pixels_por_cm = pixels_por_cm
        self.area_minima = area_minima

        self.camera = None

    # =================================================
    # ABRIR
    # =================================================

    def abrir(self):

        self.camera = cv2.VideoCapture(
            self.indice_camera,
            cv2.CAP_DSHOW
        )

        if not self.camera.isOpened():

            print(
                f"Câmera {self.indice_camera} não abriu."
            )

            if self.indice_camera != 0:

                self.camera.release()

                self.camera = cv2.VideoCapture(
                    0,
                    cv2.CAP_DSHOW
                )

            if not self.camera.isOpened():

                print(
                    "Nenhuma câmera encontrada."
                )

                self.camera = None

                return False

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            1280
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            720
        )

        return True

    # =================================================
    # PROCESSAR FRAME
    # =================================================

    def ler_produto(self):

        if self.camera is None:

            if not self.abrir():

                return None, None, None

        ret, frame = (
            self.camera.read()
        )

        if not ret:

            return None, None, None

        # ---------------------------------------------
        # CINZA
        # ---------------------------------------------

        cinza = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # ---------------------------------------------
        # DESFOQUE
        # ---------------------------------------------

        desfoque = cv2.GaussianBlur(
            cinza,
            (5, 5),
            0
        )

        # ---------------------------------------------
        # BORDAS
        # ---------------------------------------------

        bordas = cv2.Canny(
            desfoque,
            50,
            150
        )

        # ---------------------------------------------
        # CONTORNOS
        # ---------------------------------------------

        contornos, _ = cv2.findContours(
            bordas,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        maior_contorno = None
        maior_area = 0

        for contorno in contornos:

            area = cv2.contourArea(
                contorno
            )

            if (
                area >= self.area_minima
                and area > maior_area
            ):

                maior_area = area
                maior_contorno = contorno

        # ---------------------------------------------
        # NENHUM PRODUTO
        # ---------------------------------------------

        if maior_contorno is None:

            cv2.putText(
                frame,
                "Nenhum produto detectado",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            return (
                frame,
                None,
                None
            )

        # ---------------------------------------------
        # RETÂNGULO
        # ---------------------------------------------

        x, y, largura_px, altura_px = (
            cv2.boundingRect(
                maior_contorno
            )
        )

        # ---------------------------------------------
        # MEDIDAS
        # ---------------------------------------------

        largura_cm = (
            largura_px /
            self.pixels_por_cm
        )

        comprimento_cm = (
            altura_px /
            self.pixels_por_cm
        )

        # ---------------------------------------------
        # RETÂNGULO VERDE
        # ---------------------------------------------

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

        # ---------------------------------------------
        # CENTRO
        # ---------------------------------------------

        centro_x = (
            x +
            largura_px // 2
        )

        centro_y = (
            y +
            altura_px // 2
        )

        cv2.circle(
            frame,
            (centro_x, centro_y),
            5,
            (0, 255, 0),
            -1
        )

        # ---------------------------------------------
        # TEXTOS
        # ---------------------------------------------

        cv2.putText(
            frame,
            f"Largura: {largura_cm:.2f} cm",
            (
                x,
                max(y - 30, 25)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Comprimento: {comprimento_cm:.2f} cm",
            (
                x,
                max(y - 5, 50)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        return (
            frame,
            largura_cm,
            comprimento_cm
        )

    # =================================================
    # CALIBRAÇÃO
    # =================================================

    def definir_pixels_por_cm(
        self,
        valor
    ):

        if valor > 0:

            self.pixels_por_cm = (
                float(valor)
            )

    # =================================================
    # FECHAR
    # =================================================

    def fechar(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        cv2.destroyAllWindows()