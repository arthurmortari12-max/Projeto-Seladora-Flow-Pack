import cv2
import numpy as np

from Comunicação import (
    conectar_arduino,
    enviar_medidas,
    desconectar_arduino
)


# ============================================================
# CONFIGURAÇÃO DA WEBCAM
# ============================================================

INDICE_CAM = 1

webcam = cv2.VideoCapture(INDICE_CAM)

if not webcam.isOpened():

    print(
        f"Erro: Não foi possível acessar "
        f"a webcam no índice {INDICE_CAM}."
    )

    print(
        "Dica: tente mudar o índice de 1 para 0."
    )

    exit()


webcam.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

webcam.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)


print("Webcam aberta!")
print("Pressione 'q' para fechar.")


# ============================================================
# CONEXÃO COM ARDUINO
# ============================================================

arduino_conectado = conectar_arduino()


# ============================================================
# CALIBRAÇÃO
# ============================================================

PIXELS_POR_CM = 25.0


# ============================================================
# CONTROLE DO ENVIO
# ============================================================

produto_detectado_anteriormente = False

largura_anterior = None
altura_anterior = None


# ============================================================
# RETÂNGULO TRACEJADO
# ============================================================

def desenhar_tracejado(
    imagem,
    x,
    y,
    largura,
    altura
):

    cor = (0, 255, 0)

    espessura = 2

    tamanho_traco = 10


    # --------------------------------------------------------
    # PARTE SUPERIOR E INFERIOR
    # --------------------------------------------------------

    for inicio in range(
        x,
        x + largura,
        tamanho_traco * 2
    ):

        fim = min(
            inicio + tamanho_traco,
            x + largura
        )

        cv2.line(
            imagem,
            (inicio, y),
            (fim, y),
            cor,
            espessura
        )

        cv2.line(
            imagem,
            (inicio, y + altura),
            (fim, y + altura),
            cor,
            espessura
        )


    # --------------------------------------------------------
    # LATERAIS
    # --------------------------------------------------------

    for inicio in range(
        y,
        y + altura,
        tamanho_traco * 2
    ):

        fim = min(
            inicio + tamanho_traco,
            y + altura
        )

        cv2.line(
            imagem,
            (x, inicio),
            (x, fim),
            cor,
            espessura
        )

        cv2.line(
            imagem,
            (x + largura, inicio),
            (x + largura, fim),
            cor,
            espessura
        )


# ============================================================
# LOOP DA CÂMERA
# ============================================================

while True:

    validacao, frame = webcam.read()


    if not validacao:

        print(
            "Erro ao capturar imagem."
        )

        break


    frame = cv2.resize(
        frame,
        (1280, 720)
    )


    # ========================================================
    # PROCESSAMENTO
    # ========================================================

    cinza = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    blur = cv2.GaussianBlur(
        cinza,
        (5, 5),
        0
    )


    bordas = cv2.Canny(
        blur,
        50,
        150
    )


    # ========================================================
    # CONTORNOS
    # ========================================================

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


        if area > maior_area:

            maior_area = area

            maior_contorno = contorno


    # ========================================================
    # CONTROLE DA DETECÇÃO
    # ========================================================

    produto_detectado = False


    # ========================================================
    # SE ENCONTROU UM PRODUTO
    # ========================================================

    if (
        maior_contorno is not None
        and maior_area > 2000
    ):

        produto_detectado = True


        x, y, largura_px, altura_px = cv2.boundingRect(
            maior_contorno
        )


        # ----------------------------------------------------
        # MEDIDAS
        # ----------------------------------------------------

        largura_cm = (
            largura_px /
            PIXELS_POR_CM
        )

        altura_cm = (
            altura_px /
            PIXELS_POR_CM
        )


        # ----------------------------------------------------
        # DESENHA RETÂNGULO
        # ----------------------------------------------------

        desenhar_tracejado(
            frame,
            x,
            y,
            largura_px,
            altura_px
        )


        # ----------------------------------------------------
        # MOSTRA LARGURA
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Largura: {largura_cm:.1f} cm",
            (x, max(y - 35, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        # ----------------------------------------------------
        # MOSTRA ALTURA
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Altura: {altura_cm:.1f} cm",
            (x, max(y - 8, 50)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        # ====================================================
        # VERIFICA SE DEVE ENVIAR
        # ====================================================

        nova_medida = (

            largura_anterior is None

            or abs(
                largura_cm -
                largura_anterior
            ) >= 0.5

            or abs(
                altura_cm -
                altura_anterior
            ) >= 0.5
        )


        produto_novo = (
            not produto_detectado_anteriormente
        )


        # ====================================================
        # ENVIA PARA O ARDUINO
        # ====================================================

        if (
            arduino_conectado
            and (
                produto_novo
                or nova_medida
            )
        ):

            enviar_medidas(
                largura_cm,
                altura_cm
            )


            largura_anterior = largura_cm

            altura_anterior = altura_cm


    else:

        # ----------------------------------------------------
        # PRODUTO NÃO ESTÁ MAIS SENDO DETECTADO
        # ----------------------------------------------------

        largura_anterior = None

        altura_anterior = None


    # ========================================================
    # MOSTRAR CÂMERA
    # ========================================================

    cv2.imshow(
        "Flow Pack - Visao Computacional",
        frame
    )


    # ========================================================
    # SAIR
    # ========================================================

    if (
        cv2.waitKey(1) & 0xFF
        == ord('q')
    ):

        break


    produto_detectado_anteriormente = (
        produto_detectado
    )


# ============================================================
# ENCERRAMENTO
# ============================================================

webcam.release()

cv2.destroyAllWindows()

desconectar_arduino()