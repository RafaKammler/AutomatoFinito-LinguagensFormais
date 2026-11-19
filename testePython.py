#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Léxico - Linguagens Formais (TDE)

Linguagem:
    L(G) = { x | x ∈ (0,1)+ e se x começa com 0 então o nº de 0's é par,
                                 senão o nº de 0's é ímpar }

Execução:  python3 analisador_lexico.py
(No Linux é preciso:  sudo apt install python3-tk)

Como usar:
    0 ou 1   -> lê o símbolo e muda o estado do autômato
    Espaço   -> encerra a sentença e mostra RECONHECIDA / REJEITADA
    Backspace-> desfaz o último símbolo
    Esc      -> limpa a sentença atual
Outros símbolos são ignorados.
"""

import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# ==============================================================================
#  1. ÁREA DE CONFIGURAÇÃO RÁPIDA (DEFINIÇÃO DO AUTÔMATO)
# ==============================================================================

# Descrição que aparece no painel superior direito
TEXTO_LINGUAGEM = (
    "L(G) = { x | x ∈ (0,1)+ e se x começa com 0 então o nº de 0's é par,\n"
    "                              senão o nº de 0's é ímpar }\n"
)

# Símbolos aceitos no teclado e colunas da tabela (ex: ["0", "1"] ou ["a", "b", "c"])
ALFABETO = ["0", "1"]

# Lista de todos os estados do autômato
ESTADOS = ["S", "A", "B", "C", "D"]

# Estado inicial (deve estar em ESTADOS)
INICIAL = "S"

# Conjunto de estados de aceitação/finais
FINAIS = {"B", "D"}

# Tabela de Transição δ:
# Para cada estado, informe a lista de estados de destino seguindo a MESMA ORDEM do ALFABETO.
# Dica: Se não houver transição para um símbolo (AFD incompleto), use None ou "-".
TABELA_TRANSICAO = {
    #        "0"   "1"
    "S": [   "A",  "C" ],
    "A": [   "B",  "A" ],
    "B": [   "A",  "B" ],
    "C": [   "D",  "C" ],
    "D": [   "C",  "D" ],
}

# Explicação de cada estado (Opcional: se criar um estado novo ao vivo, não precisa preencher)
SIGNIFICADO = {
    "S": "nada lido ainda",
    "A": "começou com 0  |  nº de 0's ÍMPAR",
    "B": "começou com 0  |  nº de 0's PAR",
    "C": "começou com 1  |  nº de 0's PAR",
    "D": "começou com 1  |  nº de 0's ÍMPAR",
}

# Teclas de controle da interface
TECLAS_AVALIAR = ("space", "Return", "KP_Enter")
TECLA_APAGAR   = "BackSpace"
TECLA_LIMPAR   = "Escape"

# Layout do Grafo (Opcional: estados sem coordenada aqui são posicionados automaticamente)
POSICOES_FIXAS = {
    "S": (95, 215),
    "A": (310, 105), "B": (530, 105),
    "C": (310, 325), "D": (530, 325),
}
LOOP_PARA_CIMA = {"A", "B"}   # Estados cujo auto-laço (loop) desenha para cima
RAIO_NO = 30                  # Raio do círculo de cada estado


# ==============================================================================
#  2. PRÉ-PROCESSAMENTO E MOTOR DO AUTÔMATO (LÓGICA PURA)
# ==============================================================================

# [MOTOR] Converte TABELA_TRANSICAO no dicionário DELTA: (estado, simbolo) -> destino
def construir_delta():
    """Converte a TABELA_TRANSICAO amigável no dicionário DELTA (estado, simbolo) -> destino."""
    delta = {}
    for estado, destinos in TABELA_TRANSICAO.items():
        for simbolo, destino in zip(ALFABETO, destinos):
            if destino not in (None, "", "-"):
                delta[(estado, simbolo)] = destino
    return delta

DELTA = construir_delta()


def obter_significado(estado):
    """Retorna a descrição do estado sem quebrar caso um estado novo não tenha descrição."""
    if estado == "REJEIÇÃO (Travou)":
        return "Transição indefinida — o autômato travou"
    return SIGNIFICADO.get(estado, f"Estado {estado}")


# [MOTOR] Calcula coordenadas (x, y) dos nós no grafo
def calcular_posicoes():
    """Garante que todo estado tenha uma posição (x, y) na tela, mesmo se adicionado ao vivo."""
    pos = {}
    nao_definidos = [e for e in ESTADOS if e not in POSICOES_FIXAS]
    
    if not nao_definidos:
        return POSICOES_FIXAS.copy()
    
    cx, cy, rx, ry = 330, 215, 220, 135
    total = max(1, len(ESTADOS))
    for i, e in enumerate(ESTADOS):
        ang = math.pi + (2 * math.pi * i) / total
        pos[e] = (cx + rx * math.cos(ang), cy + ry * math.sin(ang))
    return pos

POS = calcular_posicoes()


# [MOTOR] Simulação passo a passo da palavra no AFD
def simular(palavra):
    estado = INICIAL
    passos = []
    travou = False

    for i, simbolo in enumerate(palavra, 1):
        novo = DELTA.get((estado, simbolo))
        if novo is None:
            passos.append((i, simbolo, estado, "—"))
            estado = "REJEIÇÃO (Travou)"
            travou = True
            break
        passos.append((i, simbolo, estado, novo))
        estado = novo

    return passos, estado, travou


# [MOTOR] Verifica se a sentença foi aceita (não vazia, não travou e parou em estado final)
def aceita(palavra, estado, travou):
    if not palavra or travou:
        return False
    return estado in FINAIS


# [MOTOR] Gera a Gramática Regular equivalente a partir de DELTA e FINAIS
def gerar_gramatica():
    linhas = []
    for e in ESTADOS:
        alternativas = [
            f"{a}{DELTA[(e, a)]}"
            for a in ALFABETO
            if (e, a) in DELTA
        ]
        if e in FINAIS:
            alternativas.append("ε")
        if alternativas:
            linhas.append(f"{e} ::= " + " | ".join(alternativas))
    return "\n".join(linhas)


# ==============================================================================
#  3. TEMA, CORES E INTERFACE GRÁFICA (TKINTER)
# ==============================================================================
BG = "#282828"          # Fundo principal (Cinza grafite quente)
PAINEL = "#32302f"      # Fundo secundário dos painéis
BORDA = "#504945"       # Bordas e separadores
TXT = "#d5c4a1"         # Texto principal (Bege/Areia, evita o branco)
TXT2 = "#a89984"        # Texto secundário (Cinza quente)
NO = "#3c3836"          # Fundo dos estados não visitados
NO_VISIT = "#665c54"    # Estados já visitados
ATUAL = "#fabd2f"       # Amarelo (Estado atual)
LINHA = "#928374"       # Cor neutra das arestas 
CAMINHO = "#fe8019"     # Laranja (Caminho percorrido)
ULTIMA = "#fb4934"      # Vermelho (Última transição feita)
OK = "#b8bb26"          # Verde (Sucesso / Estado Final)
ERRO = "#cc241d"        # Vermelho escuro (Erro / Rejeição)

TEXTO_ESCURO = "#282828" # Cor do texto sobre fundos claros (ex: amarelo)

FONTE = "Segoe UI"
MONO = "Consolas"


class App:
    # [UI] Inicialização da janela principal e vinculação do teclado
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Analisador Léxico — Autômato Finito Determinístico")
        raiz.configure(bg=BG)
        raiz.geometry("1340x820")
        raiz.minsize(1180, 740)

        self.palavra = ""
        self.passos = []
        self.estado = INICIAL
        self.travou = False

        self._estilo()
        self._montar()
        self.recomputar()

        raiz.bind("<Key>", self.on_tecla)
        raiz.focus_set()

    # [UI] Estilo da tabela de passos (Treeview) e barra de rolagem
    def _estilo(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("Treeview", background=PAINEL, fieldbackground=PAINEL,
                    foreground=TXT, rowheight=24, borderwidth=0,
                    font=(MONO, 10))
        s.configure("Treeview.Heading", background=BORDA, foreground=TXT,
                    font=(FONTE, 10, "bold"), relief="flat")
        s.map("Treeview", background=[("selected", NO_VISIT)])
        s.configure("Vertical.TScrollbar", background=BORDA,
                    troughcolor=PAINEL, bordercolor=PAINEL, arrowcolor=TXT)

    def _titulo(self, pai, texto):
        return tk.Label(pai, text=texto, bg=BG, fg=TXT2, anchor="w",
                        font=(FONTE, 10, "bold"))

    # ==========================================================================
    #  MONTAGEM DOS PAINÉIS DA INTERFACE
    # ==========================================================================
    def _montar(self):
        # [UI] Divisão da tela em 2 colunas (esquerda: grafo/entrada, direita: teoria/tabelas)
        self.raiz.columnconfigure(0, weight=3)
        self.raiz.columnconfigure(1, weight=2)
        self.raiz.rowconfigure(0, weight=1)

        esq = tk.Frame(self.raiz, bg=BG)
        esq.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=14)
        dir_ = tk.Frame(self.raiz, bg=BG)
        dir_.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=14)

        # ----- COLUNA ESQUERDA -----

        # [UI] DIAGRAMA DO AUTÔMATO (Canvas onde o grafo é desenhado)
        self._titulo(esq, "DIAGRAMA DE TRANSIÇÃO").pack(fill="x")
        self.cv = tk.Canvas(esq, width=640, height=430, bg=PAINEL,
                            highlightthickness=1, highlightbackground=BORDA)
        self.cv.pack(fill="x", pady=(2, 10))
        self._desenhar_estrutura()

        # [UI] CAMPO DE ENTRADA DA SENTENÇA
        str_alfabeto = ", ".join(ALFABETO)
        self._titulo(esq, f"SENTENÇA (digite [{str_alfabeto}]  •  espaço/enter avalia  •  "
                          "backspace desfaz  •  esc limpa)").pack(fill="x")
        caixa = tk.Frame(esq, bg=PAINEL, highlightthickness=2,
                         highlightbackground=CAMINHO)
        caixa.pack(fill="x", pady=(2, 6))
        self.fonte_palavra = tkfont.Font(family=MONO, size=26, weight="bold")
        self.colunas = 30
        self.lbl_palavra = tk.Label(caixa, text="", bg=PAINEL, fg=TXT,
                                    font=self.fonte_palavra, anchor="nw",
                                    justify="left", width=1, padx=12, pady=8)
        self.lbl_palavra.pack(fill="x")
        caixa.bind("<Configure>", self._ao_redimensionar)

        # [UI] STATUS ATUAL E VEREDITO (RECONHECIDA / REJEITADA)
        self.lbl_info = tk.Label(esq, text="", bg=BG, fg=TXT, anchor="w",
                                 justify="left", font=(FONTE, 12))
        self.lbl_info.pack(fill="x", pady=(0, 4))

        self.lbl_veredito = tk.Label(esq, text="", bg=BG, fg=TXT, anchor="w",
                                     font=(FONTE, 18, "bold"))
        self.lbl_veredito.pack(fill="x", pady=(0, 6))

        # [UI] BOTÃO LIMPAR
        barra = tk.Frame(esq, bg=BG)
        barra.pack(fill="x", pady=(0, 6))
        tk.Button(barra, text="Limpar", takefocus=0, bg=BORDA, fg=TXT,
                  activebackground=NO_VISIT, activeforeground=TXT,
                  relief="flat", font=(FONTE, 10), padx=10,
                  command=self.limpar).pack(side="right")

        # ----- COLUNA DIREITA -----

        # [UI] PAINEL DE LINGUAGEM, DEFINIÇÃO FORMAL E GRAMÁTICA REGULAR
        self._titulo(dir_, "LINGUAGEM, AUTÔMATO E GRAMÁTICA REGULAR").pack(fill="x")
        txt = tk.Text(dir_, bg=PAINEL, fg=TXT, bd=0, height=15, wrap="none",
                      highlightthickness=1, highlightbackground=BORDA,
                      font=(MONO, 10), takefocus=0, padx=8, pady=6)
        txt.pack(fill="x", pady=(2, 10))
        formal = (
            TEXTO_LINGUAGEM + "\n"
            "AFD M = (K, Σ, δ, q0, F)\n"
            f"K = {{{', '.join(ESTADOS)}}}   Σ = {{{', '.join(ALFABETO)}}}\n"
            f"q0 = {INICIAL}   F = {{{', '.join(sorted(FINAIS))}}}\n\n"
            "Gramática Regular equivalente (ε marca os estados finais):\n"
            + gerar_gramatica()
        )
        txt.insert("1.0", formal)
        txt.config(state="disabled")

        # [UI] TABELA DE TRANSIÇÕES (δ)
        self._titulo(dir_, "TABELA DE TRANSIÇÕES  (δ)").pack(fill="x")
        self._montar_tabela(dir_)

        # [UI] LOG DE PASSOS DO RECONHECIMENTO (Treeview)
        self._titulo(dir_, "PASSOS DO RECONHECIMENTO").pack(fill="x", pady=(10, 0))
        quadro = tk.Frame(dir_, bg=BG)
        quadro.pack(fill="both", expand=True, pady=(2, 0))
        cols = ("n", "lido", "trans", "sig")
        self.tv = ttk.Treeview(quadro, columns=cols, show="headings",
                               selectmode="none", takefocus=0)
        for c, t, w in [("n", "Passo", 52), ("lido", "Lê", 40),
                        ("trans", "Transição", 170),
                        ("sig", "Significado do novo estado", 260)]:
            self.tv.heading(c, text=t)
            self.tv.column(c, width=w, anchor="w", stretch=(c == "sig"))
        sb = ttk.Scrollbar(quadro, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb.set)
        self.tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tv.tag_configure("final", foreground=OK)
        self.tv.tag_configure("erro", foreground=ERRO)
        self.tv.tag_configure("inicio", foreground=TXT2)

    # [UI] MONTAGEM DA GRADE DA TABELA DE TRANSIÇÕES (δ)
    def _montar_tabela(self, pai):
        quadro = tk.Frame(pai, bg=BORDA)
        quadro.pack(anchor="w", pady=(2, 0))
        self.cel = {}
        self.cel_estado = {}
        self.cel_eps = {}

        def celula(r, c, texto, fonte=(MONO, 11)):
            lb = tk.Label(quadro, text=texto, bg=PAINEL, fg=TXT, width=8,
                          font=fonte, pady=3)
            lb.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
            return lb

        celula(0, 0, "δ", (MONO, 11, "bold")).config(fg=TXT2)
        for j, a in enumerate(ALFABETO, 1):
            celula(0, j, a, (MONO, 11, "bold")).config(fg=TXT2)
        celula(0, len(ALFABETO) + 1, "ε", (MONO, 11, "bold")).config(fg=OK)

        for i, e in enumerate(ESTADOS, 1):
            marca = "→" if e == INICIAL else " "
            self.cel_estado[e] = celula(i, 0, f"{marca} {e}")
            if e in FINAIS:
                self.cel_estado[e].config(fg=OK)
            for j, a in enumerate(ALFABETO, 1):
                destino = DELTA.get((e, a), "—")
                self.cel[(e, a)] = celula(i, j, destino)
            self.cel_eps[e] = celula(i, len(ALFABETO) + 1,
                                     "ε" if e in FINAIS else "")
            self.cel_eps[e].config(fg=OK)

    # ==========================================================================
    #  DESENHO E ATUALIZAÇÃO DO DIAGRAMA DO AUTÔMATO
    # ==========================================================================

    # [DESENHO] Calcula pontos de início, fim e rótulo das setas entre dois estados
    def _ponto_aresta(self, p, q, off):
        (x1, y1), (x2, y2) = p, q
        d = max(1.0, math.hypot(x2 - x1, y2 - y1))
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        nx, ny = -uy, ux
        t = math.sqrt(max(0.0, RAIO_NO * RAIO_NO - off * off))
        s = (x1 + nx * off + ux * t, y1 + ny * off + uy * t)
        e = (x2 + nx * off - ux * t, y2 + ny * off - uy * t)
        m = ((s[0] + e[0]) / 2 + nx * 15 * (1 if off else 0),
             (s[1] + e[1]) / 2 + ny * 15 * (1 if off else 0))
        if not off:
            m = ((s[0] + e[0]) / 2 + nx * -14, (s[1] + e[1]) / 2 + ny * -14)
        return s, e, m

    # [DESENHO] DIAGRAMA DO AUTÔMATO (seta inicial, arestas, auto-laços, nós e legenda)
    def _desenhar_estrutura(self):
        c = self.cv
        self.arestas = {}
        self.nos = {}

        # Seta de início
        x, y = POS[INICIAL]
        c.create_line(x - RAIO_NO - 60, y, x - RAIO_NO, y, arrow=tk.LAST, fill=LINHA, width=2)
        c.create_text(x - RAIO_NO - 38, y - 16, text="início", fill=TXT2,
                      font=(FONTE, 10, "italic"))

        # Agrupa transições que têm a mesma origem e o mesmo destino
        agrupadas = {}
        for (src, simb), dst in DELTA.items():
            agrupadas.setdefault((src, dst), []).append(simb)

        # Desenha arestas e auto-laços
        for (src, dst), simbolos in agrupadas.items():
            rotulo = ", ".join(simbolos)
            if src == dst:
                x, y = POS[src]
                sg = -1 if src in LOOP_PARA_CIMA else 1
                pts = [x - 14, y + sg * (RAIO_NO - 2), x - 28, y + sg * (RAIO_NO + 36),
                       x + 28, y + sg * (RAIO_NO + 36), x + 14, y + sg * (RAIO_NO - 2)]
                ln = c.create_line(*pts, smooth=True, arrow=tk.LAST,
                                   fill=LINHA, width=2)
                lb = c.create_text(x, y + sg * (RAIO_NO + 50), text=rotulo,
                                   fill=TXT, font=(MONO, 13, "bold"))
            else:
                tem_volta = (dst, src) in agrupadas
                off = 14 if tem_volta else 0
                s, e, m = self._ponto_aresta(POS[src], POS[dst], off)
                ln = c.create_line(*s, *e, arrow=tk.LAST, fill=LINHA, width=2)
                lb = c.create_text(*m, text=rotulo, fill=TXT,
                                   font=(MONO, 13, "bold"))

            for simb in simbolos:
                self.arestas[(src, simb)] = (ln, lb)

        # Desenha os nós (estados e círculo duplo para finais)
        for e in ESTADOS:
            x, y = POS[e]
            oval = c.create_oval(x - RAIO_NO, y - RAIO_NO, x + RAIO_NO, y + RAIO_NO,
                                 fill=NO, outline=CAMINHO, width=3)
            inner = None
            if e in FINAIS:
                inner = c.create_oval(x - RAIO_NO + 6, y - RAIO_NO + 6,
                                      x + RAIO_NO - 6, y + RAIO_NO - 6,
                                      fill="", outline=OK, width=2)
            t = c.create_text(x, y, text=e, fill=TXT, font=(FONTE, 13, "bold"))
            self.nos[e] = (oval, inner, t)

        # Legenda de cores do diagrama
        c.create_text(14, 408, anchor="w", fill=TXT2, font=(FONTE, 9),
                      text="amarelo = estado atual   •   laranja = caminho percorrido"
                           "   •   vermelho = última transição   •   círculo duplo = final")

    # ==========================================================================
    #  ATUALIZAÇÃO VISUAL EM TEMPO REAL
    # ==========================================================================

    # [ATUALIZAÇÃO] Pinta estado atual, caminho percorrido e última transição no diagrama
    def _atualizar_diagrama(self):
        c = self.cv
        caminho = {(d, s) for (_, s, d, para) in self.passos if para != "—"}
        ultima = None
        if self.passos and self.passos[-1][3] != "—":
            ultima = (self.passos[-1][2], self.passos[-1][1])
        visitados = {p[3] for p in self.passos if p[3] != "—"} | {INICIAL}

        for e, (oval, inner, t) in self.nos.items():
            if e == self.estado:
                fill, cor_t = ATUAL, TEXTO_ESCURO
            elif e in visitados and self.passos:
                fill, cor_t = NO_VISIT, TXT
            else:
                fill, cor_t = NO, TXT
            c.itemconfig(oval, fill=fill,
                         outline=OK if e in FINAIS else CAMINHO,
                         width=4 if e == self.estado else 3)
            c.itemconfig(t, fill=cor_t)

        for (ln, lb) in set(self.arestas.values()):
            c.itemconfig(ln, fill=LINHA, width=2)
            c.itemconfig(lb, fill=TXT)

        for k, (ln, lb) in self.arestas.items():
            if k in caminho:
                c.itemconfig(ln, fill=CAMINHO, width=3)
                c.itemconfig(lb, fill=CAMINHO)

        if ultima and ultima in self.arestas:
            ln, lb = self.arestas[ultima]
            c.itemconfig(ln, fill=ULTIMA, width=5)
            c.itemconfig(lb, fill=TEXTO_ESCURO)

    # [ATUALIZAÇÃO] Destaca linha do estado atual e célula da última transição na tabela δ
    def _atualizar_tabela(self):
        ultima = (self.passos[-1][2], self.passos[-1][1]) if self.passos else None
        for e, lb in self.cel_estado.items():
            lb.config(bg=ATUAL if e == self.estado else PAINEL,
                      fg=TEXTO_ESCURO if e == self.estado
                      else (OK if e in FINAIS else TXT))
        for e, lb in self.cel_eps.items():
            lb.config(bg=NO_VISIT if e == self.estado else PAINEL)
        for (e, a), lb in self.cel.items():
            if (e, a) == ultima:
                lb.config(bg=ULTIMA, fg=TEXTO_ESCURO)
            elif e == self.estado:
                lb.config(bg=NO_VISIT, fg=TXT)
            else:
                lb.config(bg=PAINEL, fg=TXT)

    # [ATUALIZAÇÃO] Preenche o histórico na tabela de passos do reconhecimento
    def _atualizar_passos(self):
        self.tv.delete(*self.tv.get_children())
        self.tv.insert("", "end", tags=("inicio",),
                       values=("—", "", f"estado inicial = {INICIAL}",
                               obter_significado(INICIAL)))
        for n, s, de, para in self.passos:
            if para == "—":
                self.tv.insert("", "end", tags=("erro",),
                               values=(n, s, f"δ({de}, {s}) = ∅",
                                       "Transição indefinida (Travou ✘)"))
            else:
                tag = ("final",) if para in FINAIS else ()
                sig = obter_significado(para) + ("   ✔ final" if para in FINAIS else "")
                self.tv.insert("", "end", tags=tag,
                               values=(n, s, f"δ({de}, {s}) = {para}", sig))
        filhos = self.tv.get_children()
        if filhos:
            self.tv.see(filhos[-1])

    # [ATUALIZAÇÃO] Quebra de linha automática e exibição da sentença digitada
    def _ao_redimensionar(self, ev):
        sample = ALFABETO[0] if ALFABETO else "0"
        largura_char = max(1, self.fonte_palavra.measure(sample))
        cols = (ev.width - 24 - 4) // largura_char - 1
        cols = max(1, cols)
        if cols != self.colunas:
            self.colunas = cols
            self._render_palavra()

    def _render_palavra(self):
        texto = self.palavra + "▌"
        n = self.colunas
        linhas = [texto[i:i + n] for i in range(0, len(texto), n)]
        self.lbl_palavra.config(text="\n".join(linhas))

    # ==========================================================================
    #  CONTROLE DE ESTADO E EVENTOS DE TECLADO
    # ==========================================================================

    # [CONTROLE] Reexecuta a simulação e atualiza todos os painéis da tela
    def recomputar(self):
        self.passos, self.estado, self.travou = simular(self.palavra)
        self._render_palavra()
        ok = aceita(self.palavra, self.estado, self.travou)

        if not self.palavra:
            marca = "aguardando digitação (sentença vazia ε não pertence a L)"
            cor_info = TXT
        elif self.travou:
            marca = "TRAVOU ✘ (transição indefinida)"
            cor_info = ERRO
        elif ok:
            marca = "FINAL ✔ (aceitaria se encerrasse agora)"
            cor_info = OK
        else:
            marca = "não final ✘ (rejeitaria se encerrasse agora)"
            cor_info = TXT

        self.lbl_info.config(
            text=f"Estado atual: {self.estado}  —  {obter_significado(self.estado)}\n"
                 f"Situação: {marca}",
            fg=cor_info)
        self._atualizar_diagrama()
        self._atualizar_tabela()
        self._atualizar_passos()

    # [EVENTOS] Ações de entrada: digitar, apagar, limpar e avaliar sentença
    def digitar(self, c):
        self.lbl_veredito.config(text="")
        self.palavra += c
        self.recomputar()

    def apagar(self):
        if self.palavra:
            self.lbl_veredito.config(text="")
            self.palavra = self.palavra[:-1]
            self.recomputar()

    def limpar(self):
        self.palavra = ""
        self.lbl_veredito.config(text="")
        self.recomputar()
        self.raiz.focus_set()

    def avaliar(self):
        if not self.palavra:
            return
        ok = aceita(self.palavra, self.estado, self.travou)
        txt = "RECONHECIDA" if ok else "REJEITADA"
        cor = OK if ok else ERRO
        self.lbl_veredito.config(
            text=f"“{self.palavra}”  →  {txt}   (parou em {self.estado})", fg=cor)
        self.palavra = ""
        self.recomputar()

    # [EVENTOS] Captura global de teclas
    def on_tecla(self, ev):
        k, c = ev.keysym, ev.char
        if c in ALFABETO:
            self.digitar(c)
        elif k == TECLA_APAGAR:
            self.apagar()
        elif k in TECLAS_AVALIAR:
            self.avaliar()
        elif k == TECLA_LIMPAR:
            self.limpar()
        return "break"


if __name__ == "__main__":
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()