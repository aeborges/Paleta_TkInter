# Paleta de Cores

Utilitário de consulta das ~480 cores nomeadas conhecidas pelo Tk (X11 named
colors). Reconstruído a partir de um script antigo (`legado/cores_tkinter.py`)
que só desenhava a lista inteira em tela cheia, sem busca nem código de cor.

## Funcionalidades

- **Busca por nome, código hex ou termo em português** — digitar "azul",
  "vermelho", "cinza" etc. encontra o grupo de tonalidade correspondente,
  além de casar com o nome literal da cor (ex: "navy") ou com o hex
  (ex: "#FF").
- **Filtro por grupo de tonalidade em português** — Vermelhos, Laranjas,
  Amarelos, Verdes, Ciano, Azuis, Roxos, Rosas, Marrons, Neutros. Calculado
  a partir do matiz/saturação/valor (HSV) de cada cor, não é uma lista
  fixa — funciona pra qualquer cor nova que entrar em `cores_dados.py`.
- **Código hexadecimal exibido em cada amostra**, resolvido via
  `winfo_rgb` (o valor real que o Tk usa, não uma tabela separada que
  pode ficar desatualizada).
- **Clique numa cor copia o código hex** pra área de transferência.
- Janela com tamanho fixo razoável (1000×680, redimensionável), não ocupa
  a tela inteira — grade se reajusta ao redimensionar a janela.

## Estrutura

```
Cores_Tkinter/
  main.py                  # aplicativo (classificação de grupo + interface)
  Paleta_de_Cores.pyw      # lançador sem console (clique duas vezes)
  cores_dados.py           # lista de nomes de cores X11 conhecidos pelo Tk
  legado/                  # script original, mantido como referência histórica
```

## Rodar

Uso normal, sem a janela preta do terminal atrás do app — dê duplo clique em
`Paleta_de_Cores.pyw` (Windows abre `.pyw` com `pythonw.exe` automaticamente),
ou rode:

```
pythonw Paleta_de_Cores.pyw
```

Pra depurar com saída de erro visível no terminal:

```
python main.py
```

Sem dependências externas — só a biblioteca padrão (`tkinter`, `colorsys`).

## Limitações conhecidas

- A classificação por grupo é geométrica (matiz/saturação/valor), não
  semântica — cores de nome composto tipo "dark slate gray" podem cair
  num grupo diferente do que o nome sugere (nesse caso, "Ciano", por ter
  leve tendência azul-esverdeada, mesmo "gray" estando no nome).
- Nomes das cores continuam em inglês (são os nomes reais que o Tk aceita
  em código — traduzir só o rótulo quebraria a utilidade de "copiar o
  nome pra usar no código"). Só os grupos de busca/filtro são em
  português.
