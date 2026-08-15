"""
Lançador sem console (Windows associa .pyw ao pythonw.exe automaticamente).

Clique duas vezes neste arquivo pra abrir o app sem a janela preta do
terminal. Pra depurar com saída de erro visível, rode `python main.py`.
"""
from main import PaletaDeCores

if __name__ == "__main__":
    app = PaletaDeCores()
    app.mainloop()
