import asyncio
import websockets
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
    def __init__(self, websocket, nome):
        self.websocket = websocket
        self.nome = nome
        self.pontuacao = 0
        self.respostas = 0
        self.respondeu_atual = False

class Jogo:
    def __init__(self):
        self.jogadores = []
        self.pergunta_atual = None
        self.tempo_restante = 60  # 60 segundos de jogo
        self.perguntas_usadas = set()

    async def adicionar_jogador(self, websocket, nome):
        jogador = Jogador(websocket, nome)
        self.jogadores.append(jogador)
        if len(self.jogadores) == 2:
            await self.iniciar_jogo()

    async def remover_jogador(self, websocket):
        self.jogadores = [j for j in self.jogadores if j.websocket != websocket]

    async def iniciar_jogo(self):
        await self.proxima_pergunta()
        asyncio.create_task(self.contar_tempo())

    async def proxima_pergunta(self):
        perguntas_disponiveis = [p for p in PERGUNTAS if p["pergunta"] not in self.perguntas_usadas]
        if not perguntas_disponiveis:
            self.perguntas_usadas.clear()
            perguntas_disponiveis = PERGUNTAS
        
        self.pergunta_atual = random.choice(perguntas_disponiveis)
        self.perguntas_usadas.add(self.pergunta_atual["pergunta"])
        await self.enviar_pergunta()

    async def receber_resposta(self, websocket, resposta):
        jogador = next((j for j in self.jogadores if j.websocket == websocket), None)
        if jogador and not jogador.respondeu_atual:
            jogador.respondeu_atual = True
            jogador.respostas += 1
            if resposta == self.pergunta_atual["resposta_correta"]:
                jogador.pontuacao += 1
            
            await self.broadcast(json.dumps({
                "type": "player_answered",
                "player": jogador.nome
            }))

            if all(j.respondeu_atual for j in self.jogadores):
                await self.proxima_pergunta()

    async def enviar_pergunta(self):
        for jogador in self.jogadores:
            jogador.respondeu_atual = False
        mensagem = {
            "type": "start_game",
            "pergunta": self.pergunta_atual["pergunta"],
            "opcoes": self.pergunta_atual["opcoes"],
            "tempo_restante": self.tempo_restante
        }
        await self.broadcast(json.dumps(mensagem))

    async def contar_tempo(self):
        try:
            while self.tempo_restante > 0:
                await asyncio.sleep(1)
                self.tempo_restante -= 1
                await self.broadcast(json.dumps({
                    "type": "timer_update",
                    "tempo_restante": self.tempo_restante
                }))
            await self.finalizar_jogo()
        except asyncio.CancelledError:
            pass

    async def receber_resposta(self, websocket, resposta):
        jogador = next((j for j in self.jogadores if j.websocket == websocket), None)
        if jogador and not jogador.respondeu_atual:
            jogador.respondeu_atual = True
            jogador.respostas += 1
            if resposta == self.pergunta_atual["resposta_correta"]:
                jogador.pontuacao += 1
            
            await self.broadcast(json.dumps({
                "type": "player_answered",
                "player": jogador.nome
            }))

            if all(j.respondeu_atual for j in self.jogadores):
                self.pergunta_atual = random.choice(PERGUNTAS)
                await self.enviar_pergunta()

    async def finalizar_jogo(self):
        resultados = [
            {
                "nome": jogador.nome,
                "pontuacao": jogador.pontuacao,
                "respostas": jogador.respostas
            }
            for jogador in self.jogadores
        ]
        await self.broadcast(json.dumps({
            "type": "end_game",
            "resultados": resultados
        }))

    async def broadcast(self, mensagem):
        for jogador in self.jogadores:
            try:
                await jogador.websocket.send(mensagem)
            except websockets.exceptions.ConnectionClosed:
                await self.remover_jogador(jogador.websocket)

jogo = Jogo()

async def handle_connection(websocket, path):
    try:
        nome = await websocket.recv()
        await jogo.adicionar_jogador(websocket, nome)
        async for mensagem in websocket:
            data = json.loads(mensagem)
            if data["type"] == "answer":
                await jogo.receber_resposta(websocket, data["answer"])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await jogo.remover_jogador(websocket)

start_server = websockets.serve(handle_connection, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()