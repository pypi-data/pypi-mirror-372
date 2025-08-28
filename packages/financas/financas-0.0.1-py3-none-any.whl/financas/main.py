from financas.carteira import Carteira

def menu():
    carteira = Carteira()
    while True:
        print('''
              -------------- SUA CARTEIRA --------------

                        1 - Adicionar Entrada
                        2 - Adicionar Saída
                        3 - Listar Transações
                        4 - Sair 
              ------------------------------------------
              ''')
        
        opcao = input(" DIGITE A OPÇÃO> ")

        if opcao in ["1", "2"]:
            if opcao == '1' :
                tipo = 'ENTRADA'
            else:
                tipo = 'SAIDA'
            valor = float(input(f"Digite o Valor da {tipo}: "))
            categoria = input("Digite a Categoria do Gasto (Comida, Lazer, Luz, Água etc..);\n Digite a Categoria: ")
            carteira.adicionar(valor, categoria, tipo)
        elif opcao == "3":
            carteira.listar()
        elif opcao == "4":
            break

if __name__ == "__main__":
    menu()