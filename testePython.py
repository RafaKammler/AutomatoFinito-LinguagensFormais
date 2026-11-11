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

# =====================================================================
#  DEFINIÇÃO DO AUTÔMATO
# =====================================================================
ALFABETO = ["0", "1"]
ESTADOS = ["S", "A", "B", "C", "D"]
INICIAL = "S"
FINAIS = {"B", "D"}

# Função de transição δ : K x Σ -> K   (tabela TOTAL, não existe estado indefinido)
DELTA = {
    ("S", "0"): "A", ("S", "1"): "C",
    ("A", "0"): "B", ("A", "1"): "A",
    ("B", "0"): "A", ("B", "1"): "B",
    ("C", "0"): "D", ("C", "1"): "C",
    ("D", "0"): "C", ("D", "1"): "D",
}

SIGNIFICADO = {
    "S": "nada lido ainda",
    "A": "começou com 0  |  nº de 0's ÍMPAR",
    "B": "começou com 0  |  nº de 0's PAR",
    "C": "começou com 1  |  nº de 0's PAR",
    "D": "começou com 1  |  nº de 0's ÍMPAR",
}

TEXTO_LINGUAGEM = (
    "L(G) = { x | x ∈ (0,1)+ e se x começa com 0 então o nº de 0's é par,\n"
    "                              senão o nº de 0's é ímpar }\n"
)

# Posição dos estados no diagrama
POS = {
    "S": (95, 215),
    "A": (310, 105), "B": (530, 105),
    "C": (310, 325), "D": (530, 325),
}
LOOP_PARA_CIMA = {"A", "B"}   # os demais têm o laço desenhado embaixo
R = 30                          # raio dos estados

# =====================================================================
#  LÓGICA DO AUTÔMATO  (máquina de estados pura, sem interface)
# =====================================================================
def simular(palavra):
    """Executa o AFD símbolo a símbolo.
    Retorna (lista de passos, estado final alcançado).
    Cada passo = (nº, símbolo lido, estado anterior, novo estado)."""
    estado = INICIAL
    passos = []
    for i, simbolo in enumerate(palavra, 1):
        novo = DELTA[(estado, simbolo)]          # δ(estado, símbolo)
        passos.append((i, simbolo, estado, novo))
        estado = novo
    return passos, estado


def aceita(estado):
    return estado in FINAIS


def gerar_gramatica():
    """Gramática Regular obtida do AFD (padrão visto em aula):
       δ(X,a) = Y     -> X ::= aY
       X ∈ F (final)  -> X ::= ε   (o estado final é identificado pelo ε)"""
    linhas = []
    for e in ESTADOS:
        alternativas = [f"{a}{DELTA[(e, a)]}" for a in ALFABETO]
        if e in FINAIS:
            alternativas.append("ε")
        linhas.append(f"{e} ::= " + " | ".join(alternativas))
    return "\n".join(linhas)


# =====================================================================
#  INTERFACE
# =====================================================================
BG = "#1e1e2e"
PAINEL = "#27273a"
BORDA = "#3b3b55"
TXT = "#e6e6f0"
TXT2 = "#9a9ab5"
NO = "#313244"
NO_VISIT = "#44476a"
ATUAL = "#f9e2af"
LINHA = "#6c7086"
CAMINHO = "#89b4fa"
ULTIMA = "#fab387"
OK = "#a6e3a1"
ERRO = "#f38ba8"

FONTE = "Segoe UI"
MONO = "Consolas"


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Analisador Léxico — Autômato Finito Determinístico")
        raiz.configure(bg=BG)
        raiz.geometry("1340x820")
        raiz.minsize(1180, 740)

        self.palavra = ""
        self.passos = []
        self.estado = INICIAL

        self._estilo()
        self._montar()
        self.recomputar()

        raiz.bind("<Key>", self.on_tecla)
        raiz.focus_set()

    # ------------------------------------------------------------ estilo
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

    # ------------------------------------------------------------ montagem
    def _montar(self):
        self.raiz.columnconfigure(0, weight=3)
        self.raiz.columnconfigure(1, weight=2)
        self.raiz.rowconfigure(0, weight=1)

        esq = tk.Frame(self.raiz, bg=BG)
        esq.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=14)
        dir_ = tk.Frame(self.raiz, bg=BG)
        dir_.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=14)

        # ----- coluna esquerda -----
        self._titulo(esq, "DIAGRAMA DE TRANSIÇÃO").pack(fill="x")
        self.cv = tk.Canvas(esq, width=640, height=430, bg=PAINEL,
                            highlightthickness=1, highlightbackground=BORDA)
        self.cv.pack(fill="x", pady=(2, 10))
        self._desenhar_estrutura()

        self._titulo(esq, "SENTENÇA (digite 0 e 1  •  espaço avalia  •  "
                          "backspace desfaz  •  esc limpa)").pack(fill="x")
        caixa = tk.Frame(esq, bg=PAINEL, highlightthickness=2,
                         highlightbackground=CAMINHO)
        caixa.pack(fill="x", pady=(2, 6))
        self.fonte_palavra = tkfont.Font(family=MONO, size=26, weight="bold")
        self.colunas = 30      # nº de símbolos por linha (recalculado ao redimensionar)
        self.lbl_palavra = tk.Label(caixa, text="", bg=PAINEL, fg=TXT,
                                    font=self.fonte_palavra, anchor="nw",
                                    justify="left", width=1, padx=12, pady=8)
        self.lbl_palavra.pack(fill="x")
        caixa.bind("<Configure>", self._ao_redimensionar)

        self.lbl_info = tk.Label(esq, text="", bg=BG, fg=TXT, anchor="w",
                                 justify="left", font=(FONTE, 12))
        self.lbl_info.pack(fill="x", pady=(0, 4))

        self.lbl_veredito = tk.Label(esq, text="", bg=BG, fg=TXT, anchor="w",
                                     font=(FONTE, 18, "bold"))
        self.lbl_veredito.pack(fill="x", pady=(0, 6))

        barra = tk.Frame(esq, bg=BG)
        barra.pack(fill="x", pady=(0, 6))
        tk.Button(barra, text="Limpar", takefocus=0, bg=BORDA, fg=TXT,
                  activebackground=NO_VISIT, activeforeground=TXT,
                  relief="flat", font=(FONTE, 10), padx=10,
                  command=self.limpar).pack(side="right")


        # ----- coluna direita -----
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

        self._titulo(dir_, "TABELA DE TRANSIÇÕES  (δ)").pack(fill="x")
        self._montar_tabela(dir_)

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
        self.tv.tag_configure("inicio", foreground=TXT2)

    def _montar_tabela(self, pai):
        quadro = tk.Frame(pai, bg=BORDA)
        quadro.pack(anchor="w", pady=(2, 0))
        self.cel = {}
        self.cel_estado = {}
        self.cel_eps = {}

        def celula(r, c, texto, fonte=(MONO, 11)):
            lb = tk.Label(quadro, text=texto, bg=PAINEL, fg=TXT, width=9,
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
                self.cel[(e, a)] = celula(i, j, DELTA[(e, a)])
            self.cel_eps[e] = celula(i, len(ALFABETO) + 1,
                                     "ε" if e in FINAIS else "")
            self.cel_eps[e].config(fg=OK)

    # ------------------------------------------------------------ desenho
    def _ponto_aresta(self, p, q, off):
        (x1, y1), (x2, y2) = p, q
        d = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        nx, ny = -uy, ux
        t = math.sqrt(R * R - off * off)
        s = (x1 + nx * off + ux * t, y1 + ny * off + uy * t)
        e = (x2 + nx * off - ux * t, y2 + ny * off - uy * t)
        m = ((s[0] + e[0]) / 2 + nx * 15 * (1 if off else 0),
             (s[1] + e[1]) / 2 + ny * 15 * (1 if off else 0))
        if not off:  # arestas sem par: rótulo deslocado para o lado
            m = ((s[0] + e[0]) / 2 + nx * -14, (s[1] + e[1]) / 2 + ny * -14)
        return s, e, m

    def _desenhar_estrutura(self):
        c = self.cv
        self.arestas = {}
        self.nos = {}

        # seta de início
        x, y = POS[INICIAL]
        c.create_line(x - R - 60, y, x - R, y, arrow=tk.LAST, fill=LINHA, width=2)
        c.create_text(x - R - 38, y - 16, text="início", fill=TXT2,
                      font=(FONTE, 10, "italic"))

        # arestas
        for (src, simb), dst in DELTA.items():
            if src == dst:
                x, y = POS[src]
                sg = -1 if src in LOOP_PARA_CIMA else 1
                pts = [x - 14, y + sg * (R - 2), x - 28, y + sg * (R + 36),
                       x + 28, y + sg * (R + 36), x + 14, y + sg * (R - 2)]
                ln = c.create_line(*pts, smooth=True, arrow=tk.LAST,
                                   fill=LINHA, width=2)
                lb = c.create_text(x, y + sg * (R + 50), text=simb,
                                   fill=TXT, font=(MONO, 13, "bold"))
            else:
                par = (dst, [a for a in ALFABETO if DELTA[(dst, a)] == src])
                tem_volta = bool(par[1])
                off = 14 if tem_volta else 0
                s, e, m = self._ponto_aresta(POS[src], POS[dst], off)
                ln = c.create_line(*s, *e, arrow=tk.LAST, fill=LINHA, width=2)
                lb = c.create_text(*m, text=simb, fill=TXT,
                                   font=(MONO, 13, "bold"))
            self.arestas[(src, simb)] = (ln, lb)

        # estados
        for e in ESTADOS:
            x, y = POS[e]
            oval = c.create_oval(x - R, y - R, x + R, y + R, fill=NO,
                                 outline=CAMINHO, width=3)
            inner = None
            if e in FINAIS:
                inner = c.create_oval(x - R + 6, y - R + 6, x + R - 6, y + R - 6,
                                      fill="", outline=OK, width=2)
            t = c.create_text(x, y, text=e, fill=TXT, font=(FONTE, 13, "bold"))
            self.nos[e] = (oval, inner, t)

        # legenda
        c.create_text(14, 408, anchor="w", fill=TXT2, font=(FONTE, 9),
                      text="amarelo = estado atual   •   azul = caminho percorrido"
                           "   •   laranja = última transição   •   círculo duplo = final")

    def _atualizar_diagrama(self):
        c = self.cv
        caminho = {(d, s) for (_, s, d, _) in self.passos}
        ultima = (self.passos[-1][2], self.passos[-1][1]) if self.passos else None
        visitados = {p[3] for p in self.passos} | {INICIAL}

        for e, (oval, inner, t) in self.nos.items():
            if e == self.estado:
                fill, cor_t = ATUAL, "#1e1e2e"
            elif e in visitados and self.passos:
                fill, cor_t = NO_VISIT, TXT
            else:
                fill, cor_t = NO, TXT
            c.itemconfig(oval, fill=fill,
                         outline=OK if e in FINAIS else CAMINHO,
                         width=4 if e == self.estado else 3)
            c.itemconfig(t, fill=cor_t)

        for k, (ln, lb) in self.arestas.items():
            if k == ultima:
                c.itemconfig(ln, fill=ULTIMA, width=5)
                c.itemconfig(lb, fill=ULTIMA)
            elif k in caminho:
                c.itemconfig(ln, fill=CAMINHO, width=3)
                c.itemconfig(lb, fill=CAMINHO)
            else:
                c.itemconfig(ln, fill=LINHA, width=2)
                c.itemconfig(lb, fill=TXT)

    def _atualizar_tabela(self):
        ultima = (self.passos[-1][2], self.passos[-1][1]) if self.passos else None
        for e, lb in self.cel_estado.items():
            lb.config(bg=ATUAL if e == self.estado else PAINEL,
                      fg="#1e1e2e" if e == self.estado
                      else (OK if e in FINAIS else TXT))
        for e, lb in self.cel_eps.items():
            lb.config(bg=NO_VISIT if e == self.estado else PAINEL)
        for (e, a), lb in self.cel.items():
            if (e, a) == ultima:
                lb.config(bg=ULTIMA, fg="#1e1e2e")
            elif e == self.estado:
                lb.config(bg=NO_VISIT, fg=TXT)
            else:
                lb.config(bg=PAINEL, fg=TXT)

    def _atualizar_passos(self):
        self.tv.delete(*self.tv.get_children())
        self.tv.insert("", "end", tags=("inicio",),
                       values=("—", "", f"estado inicial = {INICIAL}",
                               SIGNIFICADO[INICIAL]))
        for n, s, de, para in self.passos:
            tag = ("final",) if para in FINAIS else ()
            self.tv.insert("", "end", tags=tag,
                           values=(n, s, f"δ({de}, {s}) = {para}",
                                   SIGNIFICADO[para]
                                   + ("   ✔ final" if para in FINAIS else "")))
        filhos = self.tv.get_children()
        if filhos:
            self.tv.see(filhos[-1])

    # ------------------------------------------------------------ campo de entrada
    def _ao_redimensionar(self, ev):
        """Recalcula quantos símbolos cabem por linha na largura atual."""
        largura_char = max(1, self.fonte_palavra.measure("0"))
        cols = (ev.width - 24 - 4) // largura_char - 1   # -1: espaço para o cursor
        cols = max(1, cols)
        if cols != self.colunas:
            self.colunas = cols
            self._render_palavra()

    def _render_palavra(self):
        """Mostra a sentença quebrando em várias linhas (cresce para baixo)."""
        texto = self.palavra + "▌"
        n = self.colunas
        linhas = [texto[i:i + n] for i in range(0, len(texto), n)]
        self.lbl_palavra.config(text="\n".join(linhas))

    # ------------------------------------------------------------ estado
    def recomputar(self):
        """Refaz a simulação a partir da sentença atual e atualiza tudo."""
        self.passos, self.estado = simular(self.palavra)
        self._render_palavra()
        marca = "FINAL ✔ (aceitaria se encerrasse agora)" if aceita(self.estado) \
            else "não final ✘ (rejeitaria se encerrasse agora)"
        self.lbl_info.config(
            text=f"Estado atual: {self.estado}  —  {SIGNIFICADO[self.estado]}\n"
                 f"Situação: {marca}",
            fg=OK if aceita(self.estado) else TXT)
        self._atualizar_diagrama()
        self._atualizar_tabela()
        self._atualizar_passos()

    # ------------------------------------------------------------ ações
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
        ok = aceita(self.estado)
        txt = "RECONHECIDA" if ok else "REJEITADA"
        cor = OK if ok else ERRO
        self.lbl_veredito.config(
            text=f"“{self.palavra}”  →  {txt}   (parou em {self.estado})", fg=cor)
        # reinicia o autômato para a próxima sentença
        self.palavra = ""
        self.recomputar()

    def on_tecla(self, ev):
        k, c = ev.keysym, ev.char
        if c in ("0", "1"):
            self.digitar(c)
        elif k == "BackSpace":
            self.apagar()
        elif k in ("space", "Return", "KP_Enter"):
            self.avaliar()
        elif k == "Escape":
            self.limpar()
        return "break"           # qualquer outro símbolo é ignorado


if __name__ == "__main__":
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()