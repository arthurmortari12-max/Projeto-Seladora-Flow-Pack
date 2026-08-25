import cv2
import numpy as np

# ============================================================
# CONFIGURAÇÃO DA WEBCAM
# ============================================================

INDICE_CAM = 1

webcam = cv2.VideoCapture(INDICE_CAM)

if not webcam.isOpened():
    print(f"Erro: Não foi possível acessar a webcam no índice {INDICE_CAM}.")
    print("Dica: Tente mudar o índice do código de 1 para 0.")
    exit()

webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Webcam aberta!")
print("Pressione 'q' para fechar.")


# ============================================================
# CALIBRAÇÃO
# ============================================================

# Valor provisório.
# Depois vamos calibrar utilizando uma medida conhecida.
PIXELS_POR_CM = 25.0


# ============================================================
# RETÂNGULO TRACEJADO
# ============================================================

def desenhar_tracejado(imagem, x, y, largura, altura):

    cor = (0, 255, 0)
    espessura = 2
    tamanho_traco = 10

    # Parte superior e inferior
    for inicio in range(x, x + largura, tamanho_traco * 2):

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

    # Laterais
    for inicio in range(y, y + altura, tamanho_traco * 2):

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
        print("Erro ao capturar imagem.")
        break

    frame = cv2.resize(frame, (1280, 720))

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

        area = cv2.contourArea(contorno)

        if area > maior_area:
            maior_area = area
            maior_contorno = contorno

    # ========================================================
    # SE ENCONTROU UM PRODUTO
    # ========================================================

    if maior_contorno is not None and maior_area > 2000:

        x, y, largura_px, altura_px = cv2.boundingRect(
            maior_contorno
        )

        # Medidas
        largura_cm = largura_px / PIXELS_POR_CM
        altura_cm = altura_px / PIXELS_POR_CM

        # Desenha a marcação
        desenhar_tracejado(
            frame,
            x,
            y,
            largura_px,
            altura_px
        )

        # ====================================================
        # MEDIDAS NA IMAGEM
        # ====================================================

        cv2.putText(
            frame,
            f"Largura: {largura_cm:.1f} cm",
            (x, max(y - 35, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Altura: {altura_cm:.1f} cm",
            (x, max(y - 8, 50)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    # ========================================================
    # MOSTRAR CÂMERA
    # ========================================================

    cv2.imshow(
        "Flow Pack - Visao Computacional",
        frame
    )

    # Q encerra
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ============================================================
# ENCERRAMENTO
# ============================================================

webcam.release()
cv2.destroyAllWindows()