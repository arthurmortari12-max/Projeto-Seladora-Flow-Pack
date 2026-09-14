import tkinter as tk

from tkinter import (
    messagebox,
    simpledialog
)

import json
import os

from Camera import CameraFlowPack
from Comunicação import ComunicacaoESP32


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_PRODUTOS = "produtos.json"

FOLGA_CANALETAS = 0.5

PORTA_ESP32 = None


# ============================================================
# PRODUTOS
# ============================================================

def carregar_produtos():

    if not os.path.exists(
        ARQUIVO_PRODUTOS
    ):

        return []

    try:

        with open(
            ARQUIVO_PRODUTOS,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(
                arquivo
            )

    except:

        return []


def salvar_produtos(produtos):

    with open(
        ARQUIVO_PRODUTOS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            produtos,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


def gerar_codigo(produtos):

    if not produtos:

        return "001"

    numeros = []

    for produto in produtos:

        try:

            numeros.append(
                int(
                    produto["codigo"]
                )
            )

        except:

            pass

    if not numeros:

        return "001"

    proximo = (
        max(numeros) + 1
    )

    return f"{proximo:03d}"


# ============================================================
# SISTEMA
# ============================================================

class FlowPack:

    def __init__(self):

        self.janela = tk.Tk()

        self.janela.title(
            "Sistema Inteligente - Flow Pack"
        )

        self.janela.geometry(
            "950x650"
        )

        self.produtos = (
            carregar_produtos()
        )

        self.camera = CameraFlowPack(
            indice_camera=1,

            # ESTE VALOR PRECISA SER CALIBRADO
            pixels_por_cm=25.0
        )

        self.comunicacao = (
            ComunicacaoESP32(
                porta=PORTA_ESP32
            )
        )

        self.criar_interface()

        self.atualizar_lista()

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        titulo = tk.Label(

            self.janela,

            text=(
                "SISTEMA INTELIGENTE "
                "DE AJUSTE - FLOW PACK"
            ),

            font=(
                "Arial",
                20,
                "bold"
            )
        )

        titulo.pack(
            pady=15
        )

        # ----------------------------------------------------
        # FRAME ESQUERDO
        # ----------------------------------------------------

        esquerda = tk.Frame(
            self.janela
        )

        esquerda.pack(
            side="left",
            fill="y",
            padx=20
        )

        tk.Label(

            esquerda,

            text="HISTÓRICO DE PRODUTOS",

            font=(
                "Arial",
                12,
                "bold"
            )
        ).pack(
            pady=10
        )

        self.lista = tk.Listbox(

            esquerda,

            width=35,

            height=20
        )

        self.lista.pack()

        self.lista.bind(
            "<<ListboxSelect>>",
            self.selecionar_produto
        )

        tk.Button(

            esquerda,

            text=(
                "CADASTRAR NOVO PRODUTO"
            ),

            width=30,

            command=self.cadastrar_produto
        ).pack(
            pady=10
        )

        tk.Button(

            esquerda,

            text="ABRIR CÂMERA",

            width=30,

            command=self.abrir_camera
        ).pack(
            pady=5
        )

        # ----------------------------------------------------
        # FRAME DIREITO
        # ----------------------------------------------------

        direita = tk.Frame(
            self.janela,

            relief="groove",

            borderwidth=2
        )

        direita.pack(
            side="right",

            fill="both",

            expand=True,

            padx=20,

            pady=10
        )

        tk.Label(

            direita,

            text="CONTROLE DO PRODUTO",

            font=(
                "Arial",
                15,
                "bold"
            )
        ).pack(
            pady=20
        )

        self.informacoes = tk.Label(

            direita,

            text=(
                "Selecione um produto."
            ),

            font=(
                "Arial",
                12
            ),

            justify="left"
        )

        self.informacoes.pack(
            pady=20
        )

        self.status = tk.Label(

            direita,

            text=(
                "Status: aguardando"
            ),

            font=(
                "Arial",
                11
            )
        )

        self.status.pack(
            pady=20
        )

    # ========================================================
    # ATUALIZAR LISTA
    # ========================================================

    def atualizar_lista(self):

        self.lista.delete(
            0,
            tk.END
        )

        for produto in self.produtos:

            texto = (
                f"{produto['codigo']} - "
                f"{produto['nome']}"
            )

            self.lista.insert(
                tk.END,
                texto
            )

    # ========================================================
    # CADASTRAR PRODUTO
    # ========================================================

    def cadastrar_produto(self):

        nome = simpledialog.askstring(

            "Novo produto",

            "Digite o nome do produto:"
        )

        if not nome:

            return

        escolha = messagebox.askyesno(

            "Método de cadastro",

            "Deseja medir o produto "
            "utilizando a webcam?\n\n"
            "SIM = câmera\n"
            "NÃO = inserir manualmente"
        )

        if escolha:

            self.cadastrar_camera(
                nome
            )

        else:

            self.cadastrar_manual(
                nome
            )

    # ========================================================
    # CADASTRO MANUAL
    # ========================================================

    def cadastrar_manual(
        self,
        nome
    ):

        largura = simpledialog.askfloat(

            "Largura",

            "Largura do produto (cm):"
        )

        if largura is None:

            return

        comprimento = simpledialog.askfloat(

            "Comprimento",

            "Comprimento do produto (cm):"
        )

        if comprimento is None:

            return

        altura = simpledialog.askfloat(

            "Altura",

            "Altura do produto (cm):"
        )

        if altura is None:

            return

        self.salvar_produto(

            nome,

            largura,

            comprimento,

            altura
        )

    # ========================================================
    # CADASTRO COM CÂMERA
    # ========================================================

    def cadastrar_camera(
        self,
        nome
    ):

        if not self.camera.iniciar():

            messagebox.showerror(

                "Erro",

                "Webcam não encontrada."
            )

            return

        messagebox.showinfo(

            "Medição",

            "Coloque o produto sob a câmera.\n\n"

            "ENTER = confirmar medida\n"

            "ESC = cancelar"
        )

        while True:

            sucesso, frame = (
                self.camera.camera.read()
            )

            if not sucesso:

                break

            imagem, produto = (
                self.camera.processar(
                    frame
                )
            )

            cv2 = __import__(
                "cv2"
            )

            cv2.imshow(

                "Cadastro do Produto",

                imagem
            )

            tecla = (
                cv2.waitKey(1)
                & 0xFF
            )

            if tecla == 13:

                if produto is None:

                    messagebox.showwarning(

                        "Produto",

                        "Nenhum produto detectado."
                    )

                    continue

                largura = (
                    produto["largura_cm"]
                )

                comprimento = (
                    produto[
                        "comprimento_cm"
                    ]
                )

                altura = simpledialog.askfloat(

                    "Altura",

                    "Digite a altura do produto (cm):"
                )

                if altura is None:

                    break

                self.salvar_produto(

                    nome,

                    largura,

                    comprimento,

                    altura
                )

                break

            elif tecla == 27:

                break

        self.camera.fechar()

    # ========================================================
    # SALVAR PRODUTO
    # ========================================================

    def salvar_produto(

        self,

        nome,

        largura,

        comprimento,

        altura
    ):

        codigo = gerar_codigo(
            self.produtos
        )

        abertura = (
            largura +
            FOLGA_CANALETAS
        )

        produto = {

            "codigo": codigo,

            "nome": nome,

            "largura_cm": round(
                largura,
                2
            ),

            "comprimento_cm": round(
                comprimento,
                2
            ),

            "altura_cm": round(
                altura,
                2
            ),

            "abertura_canaletas_cm": round(
                abertura,
                2
            )
        }

        self.produtos.append(
            produto
        )

        salvar_produtos(
            self.produtos
        )

        self.atualizar_lista()

        messagebox.showinfo(

            "Produto cadastrado",

            f"Produto: {nome}\n"
            f"Código: {codigo}\n\n"

            f"Largura: {largura:.2f} cm\n"
            f"Comprimento: {comprimento:.2f} cm\n"
            f"Altura: {altura:.2f} cm\n\n"

            f"Abertura das canaletas: "
            f"{abertura:.2f} cm"
        )

    # ========================================================
    # SELECIONAR PRODUTO
    # ========================================================

    def selecionar_produto(
        self,
        evento
    ):

        selecao = (
            self.lista.curselection()
        )

        if not selecao:

            return

        indice = selecao[0]

        produto = (
            self.produtos[indice]
        )

        texto = (

            f"Código: "
            f"{produto['codigo']}\n\n"

            f"Produto: "
            f"{produto['nome']}\n\n"

            f"Largura: "
            f"{produto['largura_cm']} cm\n"

            f"Comprimento: "
            f"{produto['comprimento_cm']} cm\n"

            f"Altura: "
            f"{produto['altura_cm']} cm\n\n"

            f"Abertura das canaletas: "
            f"{produto['abertura_canaletas_cm']} cm"
        )

        self.informacoes.config(
            text=texto
        )

        # ----------------------------------------------------
        # ENVIA PARA O ESP32
        # ----------------------------------------------------

        abertura = (
            produto[
                "abertura_canaletas_cm"
            ]
        )

        enviado = (
            self.comunicacao
            .enviar_abertura(
                abertura
            )
        )

        if enviado:

            self.status.config(

                text=(

                    "ESP32 conectado\n"

                    f"Canaletas configuradas: "
                    f"{abertura:.2f} cm"
                )
            )

        else:

            self.status.config(

                text=(

                    "Produto selecionado.\n"

                    "ESP32 não conectado."
                )
            )

    # ========================================================
    # ABRIR CAMERA
    # ========================================================

    def abrir_camera(self):

        if not self.camera.iniciar():

            messagebox.showerror(

                "Erro",

                "Não foi possível abrir a webcam."
            )

            return

        while True:

            sucesso, frame = (
                self.camera.camera.read()
            )

            if not sucesso:

                break

            imagem, produto = (
                self.camera.processar(
                    frame
                )
            )

            cv2 = __import__(
                "cv2"
            )

            cv2.imshow(

                "Visao Computacional - Flow Pack",

                imagem
            )

            tecla = (
                cv2.waitKey(1)
                & 0xFF
            )

            if tecla == ord("q"):

                break

        self.camera.fechar()

    # ========================================================
    # EXECUTAR
    # ========================================================

    def executar(self):

        self.janela.mainloop()


# ============================================================
# INÍCIO
# ============================================================

if __name__ == "__main__":

    programa = FlowPack()

    programa.executar()