import socket
import threading
import json
import random

PERGUNTAS = [
    {
        "pergunta": "Qual é a capital do Brasil?",
        "opcoes": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Belo Horizonte"],
        "resposta_correta": 2
    },
    {
        "pergunta": "Quem pintou a Mona Lisa?",
        "opcoes": ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo", "Rembrandt"],
        "resposta_correta": 1
    },
    {
    "pergunta": "Qual o maior planeta do Sistema Solar?",
    "opcoes": ["Terra", "Marte", "Júpiter", "Saturno", "Vênus"],
    "resposta_correta": 2
    },
    {
        "pergunta": "Qual desses países é conhecido por ter uma cidade chamada Casablanca?",
        "opcoes": ["Irã", "Indonésia", "México", "Marrocos", "Índia"],
        "resposta_correta": 3
    },
    {
        "pergunta": "Em que ano o homem pisou na Lua pela primeira vez?",
        "opcoes": ["1969", "1972", "1965", "1958", "1970"],
        "resposta_correta": 0
    },
    {
        "pergunta": "Qual desses elementos é líquido em temperatura ambiente?",
        "opcoes": ["Ouro", "Prata", "Mercúrio", "Cobre", "Alumínio"],
        "resposta_correta": 2
    },
    {
        "pergunta": "Quem escreveu 'Dom Casmurro'?",
        "opcoes": ["Machado de Assis", "José de Alencar", "Graciliano Ramos", "Jorge Amado", "Carlos Drummond de Andrade"],
        "resposta_correta": 0
    },
    {
        "pergunta": "Qual destas cidades é a capital da Austrália?",
        "opcoes": ["Sydney", "Melbourne", "Canberra", "Perth", "Brisbane"],
        "resposta_correta": 2
    },
    {
        "pergunta": "Que elemento químico tem o símbolo 'O'?",
        "opcoes": ["Osmio", "Oxigênio", "Ouro", "Ósmio", "Oligoelemento"],
        "resposta_correta": 1
    },
    {
        "pergunta": "Qual destas frutas é conhecida por ter um caroço grande?",
        "opcoes": ["Maçã", "Banana", "Pêssego", "Laranja", "Kiwi"],
        "resposta_correta": 2
    },
    {
        "pergunta": "Quem é o autor de 'A Metamorfose'?",
        "opcoes": ["Franz Kafka", "Friedrich Nietzsche", "F. Scott Fitzgerald", "Ernest Hemingway", "Leo Tolstoy"],
        "resposta_correta": 0
    }
]

class Jogador:
    def __init__(self, conexao, endereco, nome):
        self.conexao = conexao
        self.endereco = endereco
        self.nome = nome
        self.pontuacao = 0
        self.respostas = 0
        self.respondeu_atual = False

class Jogo:
    def __init__(self):
        self.jogadores = []
        self.pergunta_atual = None
        self.tempo_restante = 60
        self.perguntas_usadas = set()

    def adicionar_jogador(self, conexao, endereco, nome):
        jogador = Jogador(conexao, endereco, nome)
        self.jogadores.append(jogador)
        if len(self.jogadores) == 2:
            self.iniciar_jogo()

    def remover_jogador(self, conexao):
        self.jogadores = [j for j in self.jogadores if j.conexao != conexao]

    def iniciar_jogo(self):
        self.proxima_pergunta()
        threading.Thread(target=self.contar_tempo).start()

    def proxima_pergunta(self):
        perguntas_disponiveis = [p for p in PERGUNTAS if p["pergunta"] not in self.perguntas_usadas]
        if not perguntas_disponiveis:
            self.perguntas_usadas.clear()
            perguntas_disponiveis = PERGUNTAS
        
        self.pergunta_atual = random.choice(perguntas_disponiveis)
        self.perguntas_usadas.add(self.pergunta_atual["pergunta"])
        self.enviar_pergunta()

    def receber_resposta(self, conexao, resposta):
        jogador = next((j for j in self.jogadores if j.conexao == conexao), None)
        if jogador and not jogador.respondeu_atual:
            jogador.respondeu_atual = True
            jogador.respostas += 1
            if resposta == self.pergunta_atual["resposta_correta"]:
                jogador.pontuacao += 1
            
            self.broadcast(json.dumps({
                "type": "player_answered",
                "player": jogador.nome
            }))

            if all(j.respondeu_atual for j in self.jogadores):
                self.proxima_pergunta()

    def enviar_pergunta(self):
        for jogador in self.jogadores:
            jogador.respondeu_atual = False
        mensagem = {
            "type": "start_game",
            "pergunta": self.pergunta_atual["pergunta"],
            "opcoes": self.pergunta_atual["opcoes"],
            "tempo_restante": self.tempo_restante
        }
        self.broadcast(json.dumps(mensagem))

    def contar_tempo(self):
        while self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.broadcast(json.dumps({
                "type": "timer_update",
                "tempo_restante": self.tempo_restante
            }))
            threading.Event().wait(1)
        self.finalizar_jogo()

    def finalizar_jogo(self):
        resultados = [
            {
                "nome": jogador.nome,
                "pontuacao": jogador.pontuacao,
                "respostas": jogador.respostas
            }
            for jogador in self.jogadores
        ]
        self.broadcast(json.dumps({
            "type": "end_game",
            "resultados": resultados
        }))

    def broadcast(self, mensagem):
        for jogador in self.jogadores:
            try:
                jogador.conexao.send((mensagem + '\n').encode())
            except:
                self.remover_jogador(jogador.conexao)

def handle_client(conexao, endereco):
    try:
        nome = conexao.recv(1024).decode()
        jogo.adicionar_jogador(conexao, endereco, nome)
        while True:
            mensagem = conexao.recv(1024).decode()
            data = json.loads(mensagem)
            if data["type"] == "answer":
                jogo.receber_resposta(conexao, data["answer"])
    except:
        pass
    finally:
        jogo.remover_jogador(conexao)
        conexao.close()

jogo = Jogo()

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(('0.0.0.0', 8765))
servidor.listen(2)

print("Servidor iniciado. Aguardando conexões...")

while True:
    conexao, endereco = servidor.accept()
    threading.Thread(target=handle_client, args=(conexao, endereco)).start()
