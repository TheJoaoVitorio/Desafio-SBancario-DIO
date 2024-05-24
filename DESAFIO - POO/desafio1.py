from abc import ABC , abstractclassmethod , abstractproperty
from datetime import datetime

class Cliente:
    
    def __init__(self, endereco):
        self.endereco = endereco
        contas = []
    
    def realizarTransacao(self, Conta, Transacao):
        pass
    
    def adicionarConta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):

    def __init__(self,nome,cpf,data_nascimento, endereco):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

        super().__init__(endereco)


class Conta:
    
    def __init__(self, numero , cliente):
        self.saldo = 0
        self.numero = numero
        self.agencia = '0123'
        self.cliente = cliente
        self.historico - Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return f'Saldo : {self._saldo}'
    
    
    def sacar(self, valor):
        saldo = self.saldo

        if valor > saldo:
            print('Saldo insuficiente! ')
        elif valor > 0:
            self.saldo -= valor
            print(f'Saque realizado!\nSeu saldo atual: {self.saldo}')
            
        else:
            print('Ação inválida!')
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f'Deposito realizado!\nSeu saldo atual é: {self.saldo}')
        else:
            print('Ação invalida!')

    @property
    def numero(self):
        return self.numero
    
    @property
    def agencia(self):
        return self.agencia
    
    @property
    def historico(self):
        return self.historico

    @property
    def cliente(self):
        return self.cliente
    

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saque=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saque = limite_saque

    def sacar(self, valor):
        num_saques = len(
            [transacao for transacao in self.historico.transacoes
             if transacao['tipo:'] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = num_saques >= self.limite_saque

        if excedeu_limite:
            print('Operação Falhou.\nO valor é maior que o limite permitido!')
        elif excedeu_saques:
            print('Operação Falhou.\nNúmero máximo de saques excedido.')

        else:
            return super().sacar(valor)
        
    def __str__(self):
        return (f"Agência: {self.agencia}\nC/C: {self.numero}\nTitular: {self.cliente.nome}")


class Historico:
    def __init__(self):
        self.transacoes = []

    @property
    def transacoes(self):
        return self.transacoes
    
    def adicionar_transacao(self,transacao):
        self.transacoes.append(
            {
                "tipo":transacao.__class__.__name__,
                "valor":transacao.valor,
                "data":datetime.now().strftime("%d-%m-%Y %H:%M:M%s"),
            }
        )


class Transacao(ABC):

    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def Registrar(self,conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @property
    def valor(self):
        return self.valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @property
    def valor(self):
        return self.valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)