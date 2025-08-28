from datetime import datetime

class Transacao:
    def __init__(self, valor, categoria, tipo):
        self.valor = valor
        self.categoria = categoria
        self.tipo = tipo  # "entrada" ou "saida"
        self.data = datetime.now().strftime("%d-%m-%Y %H:%M")

    def __str__(self):
        sinal = "+" if self.tipo == "ENTRADA" else "-"
        return f"[{self.data}] {sinal}R${self.valor:.2f} ({self.categoria})"