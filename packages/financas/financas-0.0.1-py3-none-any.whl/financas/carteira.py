from financas.transacao import Transacao

class Carteira:
    def __init__(self):
        self.transacoes = []

    def adicionar(self, valor, categoria, tipo):
        t = Transacao(valor, categoria, tipo)
        self.transacoes.append(t)
        print(f'Adicionado: {t}')

    def saldo(self):
        total = 0
        for t in self.transacoes:
            if t.tipo == "ENTRADA":
                total += t.valor
            else:
                total -= t.valor
        return total

    def listar(self):
        for t in self.transacoes:
            print(t)
        print(f"\nSaldo atual: R${self.saldo():.2f}")
