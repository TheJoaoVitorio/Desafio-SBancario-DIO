from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class ContaIterador:

    def __init__(self, contas):
        self.contas = contas
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self.index]
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        except IndexError:
            raise StopIteration
        finally:
            self.index += 1

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):

    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0123'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @saldo.setter
    def saldo(self, valor):
        self._saldo = valor
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def historico(self):
        return self._historico

    @property
    def cliente(self):
        return self._cliente
    
    def sacar(self, valor):
        if valor > self.saldo:
            print('Saldo insuficiente!')
        elif valor > 0:
            self.saldo -= valor
            print(f'Saque realizado!\nSeu saldo atual: {self.saldo}')
            return True
        else:
            print('Ação inválida!')
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            print(f'Depósito realizado!')
        else:
            print('Ação inválida!')
            return False
        
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saque=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saque = limite_saque

    def sacar(self, valor):
        num_saques = len(
            [transacao for transacao in self.historico.transacoes
             if transacao['tipo'] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = num_saques >= self.limite_saque

        if excedeu_limite:
            print('Operação Falhou.\nO valor é maior que o limite permitido!')
        elif excedeu_saques:
            print('Operação Falhou.\nNúmero máximo de saques excedido.')
        else:
            return super().sacar(valor)
        
        return False
        
    def __str__(self):
        return (f"Agência: {self.agencia}\nC/C: {self.numero}\nTitular: {self.cliente.nome}")


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
    
    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao


class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def log_transacao(funcao):
    def envelope(*args, **kwargs):
        resultado = funcao(*args, **kwargs)
        print(f"{datetime.now()}: {funcao.__name__.upper()}")
        return resultado

    return envelope

def menu():
    BancoMenu = """\n
    ========== BANCO ==========\n
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova Conta
    [5]\tNovo Cliente
    [6]\tListar Contas
    [0]\tSair
    => """
    return int(input(BancoMenu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('Cliente não possui conta!')
        return
    
    return cliente.contas[0]

@log_transacao
def depositar(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!')
        return
    
    valor = float(input('Informe o valor do depósito: '))
    transacao = Deposito(valor)
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!')
        return
    
    valor = float(input('Informe o valor do saque: '))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

@log_transacao
def exibir_extrato(clientes):
    cpf = input('Digite o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!')
        return
    
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    print('\n_______EXTRATO_______')
    transacoes = conta.historico.transacoes

    extrato = ""
    tem_transacao = False

    for transacao in conta.historico.gerar_relatorio(tipo_transacao="saque"):
        tem_transacao = True
        extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print('_____________________')

@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print('Conta Criada!')

@log_transacao
def criar_cliente(clientes):
    cpf = input('Informe o CPF: ')
    cliente = filtrar_cliente(cpf, clientes)
    if cliente:
        print("Já existe cliente com esse CPF!")
        return
    
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento: Dia/Mes/Ano: ")
    endereco = input("Informe o endereço: Cidade/Bairro/Numero: ")
    
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")

def listar_contas(contas):
    for conta in contas:
            print("-" * 30)
            print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []
    #menu()
    opcao = menu()
    
    while opcao != 0:
        match opcao:
            case 1:
                #deposito
                depositar(clientes)
                opcao = menu()

            case 2:
                #Saque
                sacar(clientes)
                opcao = menu()
            case 3:
                #Extrato
                exibir_extrato(clientes)
                opcao = menu()
            case 4:
                #Novo usuario
                numero_conta = len(contas) + 1
                criar_conta(numero_conta, clientes, contas)
                opcao = menu()
            case 5:
                #Nova Conta
                criar_cliente(clientes)
                opcao = menu()
            case 6:
                #Listar contas
                listar_contas(contas)
                opcao = menu()
            
                
main()