import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import cv2

from Camera import CameraFlowPack
from Comunicação import ComunicacaoESP32


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_PRODUTOS = "produtos.json"

# Folga adicionada à largura do produto
FOLGA_CANALETAS = 0.3

# Coloque None para detectar automaticamente
# ou, por exemplo, "COM14"
PORTA_ESP32 = None

# Limites físicos das canaletas
ABERTURA_MINIMA = 2.5
ABERTURA_MAXIMA = 34.5


# ============================================================
# ARQUIVO DE PRODUTOS
# ============================================================

def carregar_produtos():
    if not os.path.exists(ARQUIVO_PRODUTOS):
        return []

    try:
        with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

            return []

    except Exception as erro:
        print("Erro ao carregar produtos:", erro)
        return []


def salvar_produtos(produtos):
    try:
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

        return True

    except Exception as erro:
        messagebox.showerror(
            "Erro",
            f"Não foi possível salvar o produto:\n{erro}"
        )

        return False


def gerar_codigo(produtos):

    if not produtos:
        return "001"

    maior_codigo = 0

    for produto in produtos:

        try:
            codigo = int(produto.get("codigo", 0))

            if codigo > maior_codigo:
                maior_codigo = codigo

        except:
            pass

    return f"{maior_codigo + 1:03d}"


# ============================================================
# APLICAÇÃO
# ============================================================

class SmartpackApp:

    def __init__(self, janela):

        self.janela = janela

        self.janela.title("SMARTPACK - Sistema Flow Pack")

        self.janela.geometry("1150x700")

        self.janela.protocol(
            "WM_DELETE_WINDOW",
            self.fechar_programa
        )

        # ----------------------------------------------------
        # DADOS
        # ----------------------------------------------------

        self.produtos = carregar_produtos()

        self.produto_selecionado = None

        self.camera = None

        # ----------------------------------------------------
        # COMUNICAÇÃO ESP32
        # ----------------------------------------------------

        self.comunicacao = ComunicacaoESP32(
            porta=PORTA_ESP32,
            velocidade=115200
        )

        # ----------------------------------------------------
        # FRAME PRINCIPAL
        # ----------------------------------------------------

        self.frame_principal = tk.Frame(
            self.janela
        )

        self.frame_principal.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # ====================================================
        # LADO ESQUERDO
        # ====================================================

        self.frame_produtos = tk.LabelFrame(
            self.frame_principal,
            text="Produtos cadastrados",
            font=("Arial", 12, "bold")
        )

        self.frame_produtos.pack(
            side="left",
            fill="y",
            padx=(0, 10)
        )

        # Lista

        self.lista_produtos = tk.Listbox(
            self.frame_produtos,
            width=35,
            height=25,
            font=("Arial", 11)
        )

        self.lista_produtos.pack(
            padx=10,
            pady=10
        )

        self.lista_produtos.bind(
            "<<ListboxSelect>>",
            self.selecionar_produto
        )

        # Botão cadastrar

        tk.Button(
            self.frame_produtos,
            text="➕ CADASTRAR PRODUTO",
            font=("Arial", 11, "bold"),
            command=self.cadastrar_produto,
            height=2
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

        # ====================================================
        # INFORMAÇÕES DO PRODUTO
        # ====================================================

        self.label_info = tk.Label(
            self.frame_produtos,
            text="Nenhum produto selecionado",
            justify="left",
            anchor="w",
            font=("Arial", 10)
        )

        self.label_info.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # ====================================================
        # LADO DIREITO
        # ====================================================

        self.frame_controle = tk.LabelFrame(
            self.frame_principal,
            text="Controle da máquina",
            font=("Arial", 12, "bold")
        )

        self.frame_controle.pack(
            side="right",
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # CÂMERA
        # ----------------------------------------------------

        frame_camera = tk.LabelFrame(
            self.frame_controle,
            text="Sistema de visão",
            font=("Arial", 11, "bold")
        )

        frame_camera.pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Button(
            frame_camera,
            text="📷 ABRIR CÂMERA",
            font=("Arial", 11, "bold"),
            command=self.abrir_camera
        ).pack(
            side="left",
            padx=10,
            pady=10
        )

        tk.Button(
            frame_camera,
            text="✖ FECHAR CÂMERA",
            font=("Arial", 11, "bold"),
            command=self.fechar_camera
        ).pack(
            side="left",
            padx=10,
            pady=10
        )

        # ----------------------------------------------------
        # CANALETAS
        # ----------------------------------------------------

        frame_canaletas = tk.LabelFrame(
            self.frame_controle,
            text="Canaletas",
            font=("Arial", 11, "bold")
        )

        frame_canaletas.pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Button(
            frame_canaletas,
            text="AJUSTAR PRODUTO SELECIONADO",
            font=("Arial", 11, "bold"),
            command=self.ajustar_produto
        ).pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Button(
            frame_canaletas,
            text="TESTAR CANALETAS",
            font=("Arial", 11),
            command=self.testar_canaletas
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

        # ----------------------------------------------------
        # ESTEIRA
        # ----------------------------------------------------

        frame_esteira = tk.LabelFrame(
            self.frame_controle,
            text="Esteira - Motor de vidro elétrico",
            font=("Arial", 11, "bold")
        )

        frame_esteira.pack(
            fill="x",
            padx=10,
            pady=10
        )

        frame_botoes = tk.Frame(
            frame_esteira
        )

        frame_botoes.pack(
            pady=10
        )

        tk.Button(
            frame_botoes,
            text="▶ LIGAR",
            bg="green",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            command=self.ligar_esteira
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tk.Button(
            frame_botoes,
            text="■ PARAR",
            bg="red",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            command=self.parar_esteira
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Button(
            frame_botoes,
            text="◀ REVERSO",
            font=("Arial", 11, "bold"),
            width=12,
            command=self.reverso_esteira
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        # ----------------------------------------------------
        # VELOCIDADE
        # ----------------------------------------------------

        tk.Label(
            frame_esteira,
            text="Velocidade do motor:",
            font=("Arial", 10, "bold")
        ).pack(
            pady=(10, 0)
        )

        self.velocidade = tk.IntVar(
            value=100
        )

        self.slider_velocidade = tk.Scale(
            frame_esteira,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.velocidade,
            length=400
        )

        self.slider_velocidade.pack()

        tk.Button(
            frame_esteira,
            text="APLICAR VELOCIDADE",
            font=("Arial", 10, "bold"),
            command=self.aplicar_velocidade
        ).pack(
            pady=5
        )

        tk.Button(
            frame_esteira,
            text="TESTAR MOTOR",
            font=("Arial", 10),
            command=self.testar_motor
        ).pack(
            pady=5
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.label_status = tk.Label(
            self.frame_controle,
            text="Status: Sistema aguardando comando",
            font=("Arial", 11, "bold")
        )

        self.label_status.pack(
            pady=20
        )

        # ----------------------------------------------------
        # ATUALIZA LISTA
        # ----------------------------------------------------

        self.atualizar_lista_produtos()

    # ========================================================
    # LISTA DE PRODUTOS
    # ========================================================

    def atualizar_lista_produtos(self):

        self.lista_produtos.delete(
            0,
            tk.END
        )

        for produto in self.produtos:

            codigo = produto.get(
                "codigo",
                "---"
            )

            nome = produto.get(
                "nome",
                "Sem nome"
            )

            self.lista_produtos.insert(
                tk.END,
                f"{codigo} - {nome}"
            )

    # ========================================================
    # SELECIONAR PRODUTO
    # ========================================================

    def selecionar_produto(self, evento=None):

        selecao = self.lista_produtos.curselection()

        if not selecao:
            return

        indice = selecao[0]

        self.produto_selecionado = self.produtos[indice]

        produto = self.produto_selecionado

        texto = (
            f"Código: {produto.get('codigo')}\n"
            f"Nome: {produto.get('nome')}\n\n"
            f"Largura: {produto.get('largura_cm'):.2f} cm\n"
            f"Comprimento: {produto.get('comprimento_cm'):.2f} cm\n"
            f"Altura: {produto.get('altura_cm'):.2f} cm\n\n"
            f"Abertura das canaletas: "
            f"{produto.get('abertura_canaletas_cm'):.2f} cm"
        )

        self.label_info.config(
            text=texto
        )

    # ========================================================
    # CADASTRAR PRODUTO
    # ========================================================

    def cadastrar_produto(self):

        # ----------------------------------------------------
        # NOME
        # ----------------------------------------------------

        nome = simpledialog.askstring(
            "Novo produto",
            "Digite o nome do produto:"
        )

        if not nome:
            return

        # ----------------------------------------------------
        # ESCOLHA DO MÉTODO DE MEDIÇÃO
        # ----------------------------------------------------

        escolha = messagebox.askyesnocancel(
            "Como medir o produto?",
            "Escolha como deseja obter as medidas.\n\n"
            "SIM = 📷 Medir pela CÂMERA\n\n"
            "NÃO = ✏️ Inserir medidas MANUALMENTE\n\n"
            "CANCELAR = Cancelar cadastro"
        )

        # Cancelar

        if escolha is None:
            return

        # ====================================================
        # MEDIÇÃO PELA CÂMERA
        # ====================================================

        if escolha is True:

            resultado = self.medir_produto_camera()

            if resultado is None:
                return

            largura, comprimento = resultado

            # Altura ainda será informada manualmente
            altura = simpledialog.askfloat(
                "Altura do produto",
                "Digite a altura do produto em centímetros:",
                minvalue=0.1
            )

            if altura is None:
                return

        # ====================================================
        # MEDIÇÃO MANUAL
        # ====================================================

        else:

            largura = simpledialog.askfloat(
                "Largura",
                "Digite a largura do produto em centímetros:",
                minvalue=0.1
            )

            if largura is None:
                return

            comprimento = simpledialog.askfloat(
                "Comprimento",
                "Digite o comprimento do produto em centímetros:",
                minvalue=0.1
            )

            if comprimento is None:
                return

            altura = simpledialog.askfloat(
                "Altura",
                "Digite a altura do produto em centímetros:",
                minvalue=0.1
            )

            if altura is None:
                return

        # ====================================================
        # CALCULAR ABERTURA
        # ====================================================

        abertura = largura + FOLGA_CANALETAS

        if abertura < ABERTURA_MINIMA:
            abertura = ABERTURA_MINIMA

        if abertura > ABERTURA_MAXIMA:

            messagebox.showwarning(
                "Produto muito largo",
                f"A abertura calculada seria "
                f"{abertura:.2f} cm.\n\n"
                f"O limite das canaletas é "
                f"{ABERTURA_MAXIMA:.2f} cm."
            )

            abertura = ABERTURA_MAXIMA

        # ====================================================
        # GERAR CÓDIGO
        # ====================================================

        codigo = gerar_codigo(
            self.produtos
        )

        # ====================================================
        # CRIAR PRODUTO
        # ====================================================

        produto = {
            "codigo": codigo,
            "nome": nome,
            "largura_cm": round(largura, 2),
            "comprimento_cm": round(comprimento, 2),
            "altura_cm": round(altura, 2),
            "abertura_canaletas_cm": round(abertura, 2)
        }

        # ====================================================
        # SALVAR
        # ====================================================

        self.produtos.append(
            produto
        )

        if salvar_produtos(
            self.produtos
        ):

            self.atualizar_lista_produtos()

            messagebox.showinfo(
                "Produto cadastrado",
                f"Produto cadastrado com sucesso!\n\n"
                f"Código: {codigo}\n"
                f"Nome: {nome}\n\n"
                f"Largura: {largura:.2f} cm\n"
                f"Comprimento: {comprimento:.2f} cm\n"
                f"Altura: {altura:.2f} cm\n\n"
                f"Abertura das canaletas: "
                f"{abertura:.2f} cm"
            )

    # ========================================================
    # MEDIR PRODUTO PELA CÂMERA
    # ========================================================

    def medir_produto_camera(self):

        messagebox.showinfo(
            "Medição pela câmera",
            "A câmera será aberta.\n\n"
            "Coloque o produto sobre a esteira.\n\n"
            "Aguarde o sistema detectar o produto.\n\n"
            "Pressione Q para cancelar."
        )

        camera = CameraFlowPack(
            indice_camera=1,
            pixels_por_cm=28,
            area_minima=3000
        )

        if not camera.abrir():

            messagebox.showerror(
                "Erro de câmera",
                "Não foi possível abrir a câmera."
            )

            return None

        largura_detectada = None
        comprimento_detectado = None

        while True:

            frame, largura, comprimento = camera.ler_produto()

            if frame is None:
                break

            cv2.imshow(
                "SMARTPACK - Medicao do Produto",
                frame
            )

            # Se detectou produto
            if largura is not None and comprimento is not None:

                largura_detectada = largura
                comprimento_detectado = comprimento

                # Mostra a medição por alguns segundos
                cv2.putText(
                    frame,
                    "PRODUTO DETECTADO",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.imshow(
                    "SMARTPACK - Medicao do Produto",
                    frame
                )

                tecla = cv2.waitKey(1000) & 0xFF

                break

            tecla = cv2.waitKey(30) & 0xFF

            # Q cancela
            if tecla == ord("q"):

                largura_detectada = None
                comprimento_detectado = None

                break

        camera.fechar()

        if largura_detectada is None:

            messagebox.showwarning(
                "Produto não detectado",
                "A câmera não conseguiu detectar "
                "um produto."
            )

            return None

        # ----------------------------------------------------
        # CONFIRMAÇÃO
        # ----------------------------------------------------

        confirmar = messagebox.askyesno(
            "Confirmar medição",
            f"Produto detectado!\n\n"
            f"Largura: {largura_detectada:.2f} cm\n"
            f"Comprimento: {comprimento_detectado:.2f} cm\n\n"
            f"Deseja utilizar essas medidas?"
        )

        if not confirmar:

            return None

        return (
            largura_detectada,
            comprimento_detectado
        )

    # ========================================================
    # ABRIR CÂMERA
    # ========================================================

    def abrir_camera(self):

        if self.camera is not None:
            return

        self.camera = CameraFlowPack(
            indice_camera=1,
            pixels_por_cm=28,
            area_minima=3000
        )

        if not self.camera.abrir():

            self.camera = None

            messagebox.showerror(
                "Erro",
                "Não foi possível abrir a câmera."
            )

            return

        self.label_status.config(
            text="Status: Câmera ligada"
        )

        self.atualizar_camera()

    # ========================================================
    # ATUALIZAR CÂMERA
    # ========================================================

    def atualizar_camera(self):

        if self.camera is None:
            return

        frame, largura, comprimento = (
            self.camera.ler_produto()
        )

        if frame is not None:

            cv2.imshow(
                "SMARTPACK - Camera",
                frame
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):

                self.fechar_camera()

                return

        self.janela.after(
            30,
            self.atualizar_camera
        )

    # ========================================================
    # FECHAR CÂMERA
    # ========================================================

    def fechar_camera(self):

        if self.camera is not None:

            self.camera.fechar()

            self.camera = None

        cv2.destroyAllWindows()

        self.label_status.config(
            text="Status: Câmera desligada"
        )

    # ========================================================
    # AJUSTAR CANALETAS
    # ========================================================

    def ajustar_produto(self):

        if self.produto_selecionado is None:

            messagebox.showwarning(
                "Nenhum produto",
                "Selecione um produto primeiro."
            )

            return

        abertura = self.produto_selecionado[
            "abertura_canaletas_cm"
        ]

        sucesso = self.comunicacao.enviar_abertura(
            abertura
        )

        if sucesso:

            self.label_status.config(
                text=(
                    f"Status: Canaletas ajustadas "
                    f"para {abertura:.2f} cm"
                )
            )

            messagebox.showinfo(
                "Canaletas",
                f"Canaletas ajustadas para:\n\n"
                f"{abertura:.2f} cm"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível enviar o comando "
                "para o ESP32."
            )

    # ========================================================
    # TESTAR CANALETAS
    # ========================================================

    def testar_canaletas(self):

        sucesso = self.comunicacao.teste_canaletas()

        if sucesso:

            self.label_status.config(
                text="Status: Teste das canaletas iniciado"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível testar as canaletas."
            )

    # ========================================================
    # ESTEIRA - LIGAR
    # ========================================================

    def ligar_esteira(self):

        sucesso = self.comunicacao.ligar_esteira()

        if sucesso:

            self.label_status.config(
                text="Status: Esteira LIGADA"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível ligar a esteira."
            )

    # ========================================================
    # ESTEIRA - PARAR
    # ========================================================

    def parar_esteira(self):

        sucesso = self.comunicacao.parar_esteira()

        if sucesso:

            self.label_status.config(
                text="Status: Esteira PARADA"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível parar a esteira."
            )

    # ========================================================
    # ESTEIRA - REVERSO
    # ========================================================

    def reverso_esteira(self):

        sucesso = self.comunicacao.reverso_esteira()

        if sucesso:

            self.label_status.config(
                text="Status: Esteira em REVERSO"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível inverter a esteira."
            )

    # ========================================================
    # VELOCIDADE
    # ========================================================

    def aplicar_velocidade(self):

        velocidade = self.velocidade.get()

        sucesso = self.comunicacao.definir_velocidade(
            velocidade
        )

        if sucesso:

            self.label_status.config(
                text=f"Status: Velocidade = {velocidade}/255"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível alterar a velocidade."
            )

    # ========================================================
    # TESTAR MOTOR
    # ========================================================

    def testar_motor(self):

        sucesso = self.comunicacao.teste_esteira()

        if sucesso:

            self.label_status.config(
                text="Status: Teste do motor iniciado"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Não foi possível testar o motor."
            )

    # ========================================================
    # FECHAR PROGRAMA
    # ========================================================

    def fechar_programa(self):

        try:

            self.comunicacao.parar_esteira()

        except:
            pass

        self.fechar_camera()

        self.comunicacao.fechar()

        self.janela.destroy()


# ============================================================
# INICIAR SISTEMA
# ============================================================

if __name__ == "__main__":

    janela = tk.Tk()

    app = SmartpackApp(
        janela
    )

    janela.mainloop()