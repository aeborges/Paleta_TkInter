"""
Paleta de Cores — utilitário de consulta de cores nomeadas do Tkinter.

Mostra as ~550 cores nomeadas conhecidas pelo Tk, cada uma com nome,
código hexadecimal e grupo de tonalidade em português. Permite buscar
por nome/código e filtrar por grupo de cor.
"""
import colorsys
import tkinter as tk
from tkinter import ttk

from cores_dados import COLORS

# ---------------------------------------------------------------------------
# Paleta visual do próprio app (tokens de cor da interface, não das amostras)
# ---------------------------------------------------------------------------

BG_APP = "#F3F4F8"        # fundo geral, cinza levemente azulado
BG_TOOLBAR = "#FFFFFF"     # barra de busca/filtros, "elevada" sobre o fundo
BG_GRADE = "#EAEBF1"       # área de rolagem das amostras
TEXT = "#1E2130"
TEXT_MUTED = "#6B7086"
BORDER = "#DADCE6"
ACCENT = "#5B5FEF"         # indigo — cor de interação (busca, filtro ativo, hover)
ACCENT_SOFT = "#E7E7FC"
SUCESSO = "#2FAE72"        # feedback de "copiado"

# Cor representativa de cada grupo, usada como "bolinha" no filtro
COR_DOT_GRUPO = {
    "Todas": None,
    "Vermelhos": "#E63946",
    "Laranjas": "#F4A261",
    "Amarelos": "#F6C445",
    "Verdes": "#43AA8B",
    "Ciano": "#2EC4B6",
    "Azuis": "#4A6FE3",
    "Roxos": "#8E5FE0",
    "Rosas": "#F15BB5",
    "Marrons": "#8B5E3C",
    "Neutros": "#9AA0AC",
}

# ---------------------------------------------------------------------------
# Classificação de tonalidade (grupo em português)
# ---------------------------------------------------------------------------

GRUPOS_EM_ORDEM = [
    "Todas", "Vermelhos", "Laranjas", "Amarelos", "Verdes",
    "Ciano", "Azuis", "Roxos", "Rosas", "Marrons", "Neutros",
]

# Termos de busca em português que remetem a cada grupo (a busca por texto
# também casa aqui, não só no nome literal do grupo — "azul" deve achar
# o grupo "Azuis", "cinza" deve achar "Neutros", etc.)
SINONIMOS_GRUPO = {
    "Vermelhos": ["vermelho", "vermelha", "red"],
    "Laranjas": ["laranja", "orange"],
    "Amarelos": ["amarelo", "amarela", "yellow"],
    "Verdes": ["verde", "green"],
    "Ciano": ["ciano", "turquesa", "cyan"],
    "Azuis": ["azul", "blue"],
    "Roxos": ["roxo", "roxa", "violeta", "purple", "lilás", "lilas"],
    "Rosas": ["rosa", "pink", "magenta"],
    "Marrons": ["marrom", "marrons", "castanho", "brown"],
    "Neutros": ["neutro", "cinza", "cinzento", "branco", "preto", "gray", "grey", "white", "black"],
}

# Faixas de matiz (graus, 0-360) -> grupo. Avaliadas em ordem.
_FAIXAS_MATIZ = [
    (15, 45, "Laranjas"),
    (45, 70, "Amarelos"),
    (70, 170, "Verdes"),
    (170, 200, "Ciano"),
    (200, 260, "Azuis"),
    (260, 290, "Roxos"),
    (290, 345, "Rosas"),
]


def classificar_grupo(r, g, b):
    """Classifica uma cor RGB (0-255) num grupo de tonalidade em português."""
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    h_graus = h * 360

    if v < 0.15:
        return "Neutros"          # muito escura (perto de preto)
    if s < 0.15:
        return "Neutros"          # baixa saturação (cinza/branco)

    # marrons: laranja/vermelho escurecido e pouco saturado
    if (h_graus < 45 or h_graus >= 345) and v < 0.6 and s > 0.3:
        return "Marrons"

    if h_graus < 15 or h_graus >= 345:
        return "Vermelhos"
    for inicio, fim, nome in _FAIXAS_MATIZ:
        if inicio <= h_graus < fim:
            return nome
    return "Vermelhos"


def luminancia_relativa(r, g, b):
    """Luminância relativa (0-255) para escolher texto preto ou branco legível."""
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# ---------------------------------------------------------------------------
# Aplicativo
# ---------------------------------------------------------------------------

LARGURA_SWATCH = 172
ALTURA_SWATCH = 64
ESPACO = 8


class PaletaDeCores(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paleta de Cores TkInter — consulta de cores nomeadas")
        self.geometry("1100x700")
        self.minsize(700, 600)
        self.configure(bg=BG_APP)

        self.grupo_ativo = tk.StringVar(value="Todas")
        self.termo_busca = tk.StringVar()
        self._resize_job = None
        self._flash_jobs = {}
        self._chips_grupo = {}

        self._preparar_dados()
        self._montar_interface()
        # Força o Tk a calcular a geometria real da janela antes do primeiro
        # desenho — sem isso, canvas.winfo_width() ainda reporta o valor de
        # stub (1px) e a grade inteira cai numa única coluna.
        self.update_idletasks()
        self._renderizar()

    # -- dados ---------------------------------------------------------

    def _preparar_dados(self):
        """Resolve nome -> (hex, grupo) usando o Tk já inicializado."""
        self.info_cores = []
        for nome in COLORS:
            try:
                r16, g16, b16 = self.winfo_rgb(nome)
            except tk.TclError:
                continue
            r, g, b = r16 // 256, g16 // 256, b16 // 256
            hexcode = f"#{r:02X}{g:02X}{b:02X}"
            grupo = classificar_grupo(r, g, b)
            self.info_cores.append({
                "nome": nome,
                "hex": hexcode,
                "grupo": grupo,
                "fg": "#111111" if luminancia_relativa(r, g, b) > 140 else "#F5F5F5",
            })

    # -- interface -------------------------------------------------------

    def _montar_interface(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TFrame", background=BG_APP)
        estilo.configure("Toolbar.TFrame", background=BG_TOOLBAR)
        estilo.configure("TLabel", background=BG_APP, foreground=TEXT)
        estilo.configure("Toolbar.TLabel", background=BG_TOOLBAR, foreground=TEXT)
        estilo.configure("Muted.TLabel", background=BG_TOOLBAR, foreground=TEXT_MUTED)
        estilo.configure(
            "Busca.TEntry", fieldbackground="#FFFFFF", bordercolor=BORDER,
            lightcolor=BORDER, darkcolor=BORDER, padding=6,
        )
        estilo.map("Busca.TEntry", bordercolor=[("focus", ACCENT)])

        toolbar = tk.Frame(self, bg=BG_TOOLBAR, highlightbackground=BORDER, highlightthickness=1)
        toolbar.pack(fill="x")

        topo = ttk.Frame(toolbar, padding=(14, 12, 14, 8), style="Toolbar.TFrame")
        topo.pack(fill="x")

        ttk.Label(topo, text="🔍", style="Toolbar.TLabel", font=("Segoe UI", 11)).pack(side="left")
        entrada = ttk.Entry(topo, textvariable=self.termo_busca, width=32, style="Busca.TEntry")
        entrada.pack(side="left", padx=(6, 16), ipady=2)
        entrada.bind("<KeyRelease>", lambda e: self._renderizar())
        entrada.focus_set()

        ttk.Label(topo, text="Nome, código hex ou termo em português", style="Muted.TLabel",
                  font=("Segoe UI", 8)).pack(side="left")

        self.label_contagem = ttk.Label(topo, text="", style="Muted.TLabel", font=("Segoe UI", 9, "bold"))
        self.label_contagem.pack(side="right")

        barra_grupos = ttk.Frame(toolbar, padding=(14, 0, 14, 12), style="Toolbar.TFrame")
        barra_grupos.pack(fill="x")
        for grupo in GRUPOS_EM_ORDEM:
            self._criar_chip_grupo(barra_grupos, grupo)
        self._padronizar_largura_chips()

        rodape_status = tk.Frame(self, bg=BG_APP)
        rodape_status.pack(fill="x")
        self.status = tk.StringVar(value="Clique numa cor para copiar o código hexadecimal.")
        tk.Label(rodape_status, textvariable=self.status, bg=BG_APP, fg=TEXT_MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=14, pady=(8, 6))

        corpo = tk.Frame(self, bg=BG_APP)
        corpo.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.canvas = tk.Canvas(corpo, highlightthickness=0, bg=BG_GRADE)
        scroll = ttk.Scrollbar(corpo, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.grade = tk.Frame(self.canvas, bg=BG_GRADE)
        self._janela_grade = self.canvas.create_window((0, 0), window=self.grade, anchor="nw")

        self.grade.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._ao_redimensionar)
        self.canvas.bind_all("<MouseWheel>", self._rolar_mouse)

    def _criar_chip_grupo(self, parent, grupo):
        cor_dot = COR_DOT_GRUPO.get(grupo)
        ativo = grupo == self.grupo_ativo.get()
        bg = ACCENT_SOFT if ativo else BG_TOOLBAR
        borda = ACCENT if ativo else BORDER
        fg = ACCENT if ativo else TEXT

        chip = tk.Frame(parent, bg=bg, highlightbackground=borda, highlightthickness=1, cursor="hand2")
        chip.pack(side="left", padx=(0, 6), pady=2)

        # conteúdo (bolinha + texto) fica num frame interno, centralizado
        # dentro do chip — assim todo chip pode ter a mesma largura fixa
        # sem o conteúdo grudar na borda esquerda.
        conteudo = tk.Frame(chip, bg=bg)
        conteudo.pack(expand=True, pady=6)

        widgets = [chip, conteudo]
        dot = None
        if cor_dot:
            dot = tk.Canvas(conteudo, width=10, height=10, bg=bg, highlightthickness=0)
            dot.create_oval(1, 1, 9, 9, fill=cor_dot, outline="")
            dot.pack(side="left", padx=(0, 4))
            widgets.append(dot)

        label = tk.Label(
            conteudo, text=grupo, bg=bg, fg=fg,
            font=("Segoe UI", 9, "bold" if ativo else "normal"),
        )
        label.pack(side="left")
        widgets.append(label)

        for w in widgets:
            w.bind("<Button-1>", lambda e, g=grupo: self._selecionar_grupo(g))

        self._chips_grupo[grupo] = {"chip": chip, "conteudo": conteudo, "label": label, "dot": dot}

    def _padronizar_largura_chips(self):
        """Deixa todos os chips com a mesma largura do chip 'Vermelhos'
        (o texto mais longo entre os grupos), pra alinhar a barra."""
        self.update_idletasks()
        referencia = self._chips_grupo["Vermelhos"]["chip"]
        largura = referencia.winfo_reqwidth()
        altura = referencia.winfo_reqheight()
        for refs in self._chips_grupo.values():
            refs["chip"].configure(width=largura, height=altura)
            refs["chip"].pack_propagate(False)

    def _ao_redimensionar(self, evento):
        self.canvas.itemconfig(self._janela_grade, width=evento.width)
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(120, self._renderizar)

    def _rolar_mouse(self, evento):
        self.canvas.yview_scroll(int(-evento.delta / 120), "units")

    def _selecionar_grupo(self, grupo):
        self.grupo_ativo.set(grupo)
        self._atualizar_destaque_grupo()
        self._renderizar()

    def _atualizar_destaque_grupo(self):
        ativo = self.grupo_ativo.get()
        for grupo, refs in self._chips_grupo.items():
            ligado = grupo == ativo
            bg = ACCENT_SOFT if ligado else BG_TOOLBAR
            borda = ACCENT if ligado else BORDER
            fg = ACCENT if ligado else TEXT
            refs["chip"].configure(bg=bg, highlightbackground=borda)
            refs["conteudo"].configure(bg=bg)
            refs["label"].configure(bg=bg, fg=fg, font=("Segoe UI", 9, "bold" if ligado else "normal"))
            if refs["dot"] is not None:
                refs["dot"].configure(bg=bg)

    # -- filtragem e desenho ---------------------------------------------

    def _cores_filtradas(self):
        termo = self.termo_busca.get().strip().lower()
        grupo = self.grupo_ativo.get()
        resultado = []
        for c in self.info_cores:
            if grupo != "Todas" and c["grupo"] != grupo:
                continue
            if termo:
                sinonimos = " ".join(SINONIMOS_GRUPO.get(c["grupo"], []))
                alvo = f"{c['nome'].lower()} {c['hex'].lower()} {c['grupo'].lower()} {sinonimos}"
                if termo.replace("_", " ") not in alvo.replace("_", " "):
                    continue
            resultado.append(c)
        return resultado

    def _renderizar(self):
        for widget in self.grade.winfo_children():
            widget.destroy()
        self._flash_jobs.clear()

        cores = self._cores_filtradas()
        self.label_contagem.configure(text=f"{len(cores)} cor(es)")

        largura_canvas = self.canvas.winfo_width() or 1000
        colunas = max(1, largura_canvas // (LARGURA_SWATCH + ESPACO))

        for indice, c in enumerate(cores):
            linha, coluna = divmod(indice, colunas)
            self._criar_swatch(c, linha, coluna)

        for col in range(colunas):
            self.grade.grid_columnconfigure(col, weight=1)

    def _criar_swatch(self, c, linha, coluna):
        quadro = tk.Frame(
            self.grade, bg=c["hex"], width=LARGURA_SWATCH, height=ALTURA_SWATCH,
            highlightbackground="#C9CAD4", highlightthickness=1, cursor="hand2",
        )
        quadro.grid(row=linha, column=coluna, padx=ESPACO // 2, pady=ESPACO // 2, sticky="nsew")
        quadro.grid_propagate(False)

        nome_label = tk.Label(
            quadro, text=c["nome"], bg=c["hex"], fg=c["fg"],
            font=("Segoe UI", 9, "bold"), cursor="hand2",
        )
        nome_label.place(x=10, y=9)

        hex_label = tk.Label(
            quadro, text=c["hex"], bg=c["hex"], fg=c["fg"],
            font=("Consolas", 9), cursor="hand2",
        )
        hex_label.place(x=10, y=ALTURA_SWATCH - 27)

        widgets = (quadro, nome_label, hex_label)
        for widget in widgets:
            widget.bind("<Button-1>", lambda e, cor=c, q=quadro: self._copiar_hex(cor, q))
            widget.bind("<Enter>", lambda e, q=quadro: self._hover_swatch(q, True))
            widget.bind("<Leave>", lambda e, q=quadro: self._hover_swatch(q, False))

    def _hover_swatch(self, quadro, entrando):
        if str(quadro) in self._flash_jobs:
            return  # não interfere com a animação de "copiado"
        if entrando:
            quadro.configure(highlightbackground=TEXT, highlightthickness=2)
        else:
            quadro.configure(highlightbackground="#C9CAD4", highlightthickness=1)

    def _copiar_hex(self, cor, quadro):
        self.clipboard_clear()
        self.clipboard_append(cor["hex"])
        self.status.set(f"Copiado: {cor['hex']}  ({cor['nome']}, grupo {cor['grupo']})")

        chave = str(quadro)
        quadro.configure(highlightbackground=SUCESSO, highlightthickness=3)

        def restaurar():
            self._flash_jobs.pop(chave, None)
            if quadro.winfo_exists():
                quadro.configure(highlightbackground="#C9CAD4", highlightthickness=1)

        job = self.after(350, restaurar)
        self._flash_jobs[chave] = job


if __name__ == "__main__":
    app = PaletaDeCores()
    app.mainloop()
