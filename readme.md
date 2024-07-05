# Documentação do Jogo de Trivia

## Introdução
Este projeto consiste em um jogo de trivia multiplayer, onde dois jogadores competem respondendo perguntas de conhecimento geral. O jogo é composto por um cliente, desenvolvido com PyQt5 para a interface gráfica, e um servidor, que gerencia a lógica do jogo e a comunicação entre os jogadores usando WebSockets.

## Propósito do Software
O propósito deste software é proporcionar uma experiência de jogo interativa e educativa, onde os jogadores podem testar seus conhecimentos em diversas áreas. O jogo é projetado para ser jogado em tempo real, com perguntas sendo enviadas pelo servidor e respostas sendo recebidas dos clientes.

## Motivação da Escolha do Protocolo de Transporte

O protocolo WebSocket oferece uma série de características essenciais que se alinham perfeitamente com as necessidades específicas deste ambiente de jogo.

### WebSocket e TCP

O WebSocket é um protocolo que opera sobre TCP (Transmission Control Protocol), aproveitando-se das vantagens que o TCP oferece, enquanto adiciona funcionalidades específicas para comunicação bidirecional em tempo real.

- **Comunicação Bidirecional em Tempo Real**:
  O WebSocket permite comunicação bidirecional entre o cliente e o servidor em tempo real. Isso é crucial para garantir que as perguntas sejam enviadas rapidamente e que as respostas dos jogadores sejam recebidas sem atrasos.

- **Conexão Persistente**:
  Diferente do modelo tradicional de requisição-resposta do HTTP, o WebSocket mantém uma conexão aberta e persistente. Isso elimina a necessidade de estabelecer novas conexões para cada mensagem enviada, melhorando a eficiência da comunicação.

- **Facilidade de Implementação de Funcionalidades em Tempo Real**:
  A implementação de funcionalidades como atualizações de tempo, notificações de respostas de oponentes e atualizações de status do jogo é facilitada pelo WebSocket. A capacidade de enviar e receber dados em tempo real permite que o servidor mantenha todos os jogadores sincronizados, proporcionando uma experiência de jogo coesa.

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
1. **Conexão Inicial**: O cliente envia o nome do jogador ao servidor assim que a conexão é estabelecida.
   ```json
   {
     "type": "connect",
     "name": "Nome do Jogador"
   }
   ```
   **Código do Cliente**:
   ```python
   async def connect_to_server():
       uri = "ws://localhost:8765"
       async with websockets.connect(uri) as websocket:
           # Enviar o nome do jogador ao servidor
           connect_message = {"type": "connect", "name": "Nome do Jogador"}
           await websocket.send(json.dumps(connect_message))
           # Aguardar resposta do servidor
           response = await websocket.recv()
           print(response)
   ```

2. **Resposta do Jogador**: O cliente envia a resposta selecionada pelo jogador.
   ```json
   {
     "type": "answer",
     "answer": 2
   }
   ```
   **Código do Cliente**:
   ```python
   async def send_answer(websocket, answer):
       # Enviar resposta do jogador ao servidor
       answer_message = {"type": "answer", "answer": answer}
       await websocket.send(json.dumps(answer_message))
   ```

#### Servidor para Cliente
1. **Início do Jogo**: O servidor envia a primeira pergunta e opções de resposta aos jogadores.
   ```json
   {
     "type": "start_game",
     "pergunta": "Qual é a capital do Brasil?",
     "opcoes": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Belo Horizonte"],
     "tempo_restante": 60
   }
   ```
   **Código do Servidor**:
   ```python
   async def start_game(websocket, players):
       question = {
           "type": "start_game",
           "pergunta": "Qual é a capital do Brasil?",
           "opcoes": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Belo Horizonte"],
           "tempo_restante": 60
       }
       await asyncio.wait([player.send(json.dumps(question)) for player in players])
   ```

2. **Atualização do Timer**: O servidor envia atualizações periódicas do tempo restante.
   ```json
   {
     "type": "timer_update",
     "tempo_restante": 45
   }
   ```
   **Código do Servidor**:
   ```python
   async def update_timer(websocket, players, tempo_restante):
       timer_message = {"type": "timer_update", "tempo_restante": tempo_restante}
       await asyncio.wait([player.send(json.dumps(timer_message)) for player in players])
   ```

3. **Resposta do Oponente**: O servidor notifica quando o oponente responde.
   ```json
   {
     "type": "player_answered",
     "player": "Nome do Oponente"
   }
   ```
   **Código do Servidor**:
   ```python
   async def notify_opponent_answered(websocket, opponent_name):
       player_answered_message = {"type": "player_answered", "player": opponent_name}
       await websocket.send(json.dumps(player_answered_message))
   ```

4. **Fim do Jogo**: O servidor envia os resultados finais do jogo.
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
   **Código do Servidor**:
   ```python
   async def end_game(websocket, players, resultados):
       end_game_message = {
           "type": "end_game",
           "resultados": resultados
       }
       await asyncio.wait([player.send(json.dumps(end_game_message)) for player in players])
   ```

## Fluxo de Eventos

### Cliente
1. **Conexão Inicial**:
   - O cliente conecta-se ao servidor e envia o nome do jogador.
   ```python
   await connect_to_server()
   ```

2. **Recepção da Pergunta**:
   - O cliente recebe a pergunta e opções de resposta do servidor.
   ```python
   response = await websocket.recv()
   ```

3. **Envio da Resposta**:
   - O cliente envia a resposta selecionada ao servidor.
   ```python
   await send_answer(websocket, selected_answer)
   ```

### Servidor
1. **Gerenciamento de Conexões**:
   - O servidor gerencia conexões de múltiplos jogadores e inicia o jogo quando ambos estão conectados.
   ```python
   start_server = websockets.serve(handle_client, "localhost", 8765)
   ```

2. **Envio da Pergunta**:
   - O servidor envia a primeira pergunta e opções de resposta aos jogadores.
   ```python
   await start_game(websocket, players)
   ```

3. **Atualização do Timer**:
   - O servidor envia atualizações periódicas do tempo restante.
   ```python
   await update_timer(websocket, players, tempo_restante)
   ```

4. **Recepção de Respostas**:
   - O servidor recebe e valida respostas dos jogadores.
   ```python
   async for message in websocket:
       data = json.loads(message)
       if data["type"] == "answer":
           # Processar resposta
   ```

5. **Notificação de Resposta do Oponente**:
   - O servidor notifica o jogador quando o oponente responde.
   ```python
   await notify_opponent_answered(websocket, opponent_name)
   ```

6. **Envio dos Resultados Finais**:
   - O servidor envia os resultados finais do jogo.
   ```python
   await end_game(websocket, players, resultados)
   ```

### Estados do Jogo
1. **Aguardando Jogadores**: O servidor espera até que dois jogadores estejam conectados.
2. **Enviando Pergunta**: O servidor envia uma pergunta e opções de resposta aos jogadores.
3. **Aguardando Respostas**: O servidor aguarda as respostas dos jogadores.
4. **Atualizando Status**: O servidor atualiza o status do jogo com base nas respostas recebidas.
5. **Finalizando Jogo**: O servidor envia os resultados finais e encerra o jogo.

## Conclusão
Este projeto demonstra a aplicação de WebSockets para criar um jogo multiplayer em tempo real. A escolha do protocolo WebSocket permite uma comunicação eficiente e de baixa latência, essencial para a experiência de jogo. A interface gráfica desenvolvida com PyQt5 proporciona uma experiência de usuário rica e interativa.
