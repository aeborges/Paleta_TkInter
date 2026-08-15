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
ESPACO = 6


class PaletaDeCores(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paleta de Cores TkInter")
        self.geometry("1100x700")
        self.minsize(700, 600)

        self.grupo_ativo = tk.StringVar(value="Todas")
        self.termo_busca = tk.StringVar()
        self._largura_atual = 0
        self._resize_job = None

        self._preparar_dados()
        self._montar_interface()
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
        estilo.configure("Grupo.TButton", padding=(10, 4))
        estilo.configure("GrupoAtivo.TButton", padding=(10, 4))

        topo = ttk.Frame(self, padding=(12, 10, 12, 6))
        topo.pack(fill="x")

        ttk.Label(topo, text="Buscar:").pack(side="left")
        entrada = ttk.Entry(topo, textvariable=self.termo_busca, width=28)
        entrada.pack(side="left", padx=(6, 16))
        entrada.bind("<KeyRelease>", lambda e: self._renderizar())
        entrada.focus_set()

        self.label_contagem = ttk.Label(topo, text="", foreground="#666666")
        self.label_contagem.pack(side="right")

        barra_grupos = ttk.Frame(self, padding=(12, 0, 12, 8))
        barra_grupos.pack(fill="x")
        self._botoes_grupo = {}
        for grupo in GRUPOS_EM_ORDEM:
            btn = ttk.Button(
                barra_grupos, text=grupo, style="Grupo.TButton",
                command=lambda g=grupo: self._selecionar_grupo(g),
            )
            btn.pack(side="left", padx=(0, 4))
            self._botoes_grupo[grupo] = btn
        self._atualizar_destaque_grupo()

        self.status = tk.StringVar(value="Clique numa cor para copiar o código hexadecimal.")
        ttk.Label(self, textvariable=self.status, padding=(12, 0, 12, 6),
                  foreground="#666666").pack(fill="x")

        corpo = ttk.Frame(self)
        corpo.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.canvas = tk.Canvas(corpo, highlightthickness=0, bg="#FAFAFA")
        scroll = ttk.Scrollbar(corpo, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.grade = tk.Frame(self.canvas, bg="#FAFAFA")
        self._janela_grade = self.canvas.create_window((0, 0), window=self.grade, anchor="nw")

        self.grade.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._ao_redimensionar)
        self.canvas.bind_all("<MouseWheel>", self._rolar_mouse)

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
        for grupo, botao in self._botoes_grupo.items():
            botao.configure(style="GrupoAtivo.TButton" if grupo == ativo else "Grupo.TButton")

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
            highlightbackground="#D0D0D0", highlightthickness=1, cursor="hand2",
        )
        quadro.grid(row=linha, column=coluna, padx=ESPACO // 2, pady=ESPACO // 2, sticky="nsew")
        quadro.grid_propagate(False)

        nome_label = tk.Label(
            quadro, text=c["nome"], bg=c["hex"], fg=c["fg"],
            font=("Segoe UI", 9, "bold"), cursor="hand2",
        )
        nome_label.place(x=8, y=8)

        hex_label = tk.Label(
            quadro, text=c["hex"], bg=c["hex"], fg=c["fg"],
            font=("Consolas", 9), cursor="hand2",
        )
        hex_label.place(x=8, y=ALTURA_SWATCH - 26)

        for widget in (quadro, nome_label, hex_label):
            widget.bind("<Button-1>", lambda e, cor=c: self._copiar_hex(cor))

    def _copiar_hex(self, cor):
        self.clipboard_clear()
        self.clipboard_append(cor["hex"])
        self.status.set(f"Copiado: {cor['hex']}  ({cor['nome']}, grupo {cor['grupo']})")


if __name__ == "__main__":
    app = PaletaDeCores()
    app.mainloop()
