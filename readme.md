# Documentação do Jogo de Trivia

## Introdução
Este projeto consiste em um jogo de trivia multiplayer, onde dois jogadores competem respondendo perguntas de conhecimento geral. O jogo é composto por um cliente, desenvolvido com PyQt5 para a interface gráfica, e um servidor, que gerencia a lógica do jogo e a comunicação entre os jogadores usando WebSockets.

## Propósito do Software
O propósito deste software é proporcionar uma experiência de jogo interativa e educativa, onde os jogadores podem testar seus conhecimentos em diversas áreas. O jogo é projetado para ser jogado em tempo real, com perguntas sendo enviadas pelo servidor e respostas sendo recebidas dos clientes.

## Motivação da Escolha do Protocolo de Transporte
O protocolo WebSocket foi escolhido para este projeto devido à sua capacidade de fornecer comunicação bidirecional em tempo real entre o cliente e o servidor. Isso é essencial para um jogo multiplayer, onde a latência deve ser mínima para garantir uma experiência de jogo fluida e responsiva.

## Requisitos Mínimos de Funcionamento
- Python 3.7 ou superior
- Bibliotecas: `asyncio`, `websockets`, `json`, `random`, `socket`, `PyQt5`
- Conexão de rede para comunicação entre cliente e servidor

## Funcionamento do Software

### Cliente
O cliente é responsável por:
- Conectar-se ao servidor de trivia
- Enviar o nome do jogador ao servidor
- Receber perguntas e opções de resposta do servidor
- Enviar respostas ao servidor
- Exibir o tempo restante e o status do oponente

### Servidor
O servidor é responsável por:
- Gerenciar a conexão de múltiplos jogadores
- Enviar perguntas e opções de resposta aos jogadores
- Receber e validar respostas dos jogadores
- Manter o tempo restante para cada pergunta
- Enviar atualizações de status e resultados finais aos jogadores

## Protocolo de Comunicação

### Eventos e Mensagens

#### Cliente para Servidor
- **Conexão Inicial**: O cliente envia o nome do jogador ao servidor assim que a conexão é estabelecida.
  ```json
  {
    "type": "connect",
    "name": "Nome do Jogador"
  }
  ```

- **Resposta do Jogador**: O cliente envia a resposta selecionada pelo jogador.
  ```json
  {
    "type": "answer",
    "answer": 2
  }
  ```

#### Servidor para Cliente
- **Início do Jogo**: O servidor envia a primeira pergunta e opções de resposta aos jogadores.
  ```json
  {
    "type": "start_game",
    "pergunta": "Qual é a capital do Brasil?",
    "opcoes": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Belo Horizonte"],
    "tempo_restante": 60
  }
  ```

- **Atualização do Timer**: O servidor envia atualizações periódicas do tempo restante.
  ```json
  {
    "type": "timer_update",
    "tempo_restante": 45
  }
  ```

- **Resposta do Oponente**: O servidor notifica quando o oponente responde.
  ```json
  {
    "type": "player_answered",
    "player": "Nome do Oponente"
  }
  ```

- **Fim do Jogo**: O servidor envia os resultados finais do jogo.
  ```json
  {
    "type": "end_game",
    "resultados": [
      {
        "nome": "Jogador 1",
        "pontuacao": 3,
        "respostas": 5
      },
      {
        "nome": "Jogador 2",
        "pontuacao": 4,
        "respostas": 5
      }
    ]
  }
  ```

### Estados do Jogo
1. **Aguardando Jogadores**: O servidor espera até que dois jogadores estejam conectados.
2. **Enviando Pergunta**: O servidor envia uma pergunta e opções de resposta aos jogadores.
3. **Aguardando Respostas**: O servidor aguarda as respostas dos jogadores.
4. **Atualizando Status**: O servidor atualiza o status do jogo com base nas respostas recebidas.
5. **Finalizando Jogo**: O servidor envia os resultados finais e encerra o jogo.

## Conclusão
Este projeto demonstra a aplicação de WebSockets para criar um jogo multiplayer em tempo real. A escolha do protocolo WebSocket permite uma comunicação eficiente e de baixa latência, essencial para a experiência de jogo. A interface gráfica desenvolvida com PyQt5 proporciona uma experiência de usuário rica e interativa.
