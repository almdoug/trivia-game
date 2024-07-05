# Documentação do Jogo de Trivia

## Propósito do Software
O software implementa um jogo de trivia para dois jogadores, onde perguntas são enviadas do servidor para os clientes, e os jogadores respondem em tempo real. O objetivo é responder corretamente o maior número de perguntas no menor tempo possível.

## Motivação da Escolha do Protocolo de Transporte
O protocolo de transporte escolhido foi o TCP (Transmission Control Protocol) devido às suas características de confiabilidade e controle de fluxo. Abaixo estão os principais motivos para a escolha do TCP:

### Confiabilidade
O TCP garante a entrega confiável de pacotes de dados entre o cliente e o servidor. Isso é crucial para um jogo de trivia, onde a perda de dados pode resultar em perguntas ou respostas não recebidas, afetando a integridade do jogo.

### Controle de Fluxo
O TCP implementa mecanismos de controle de fluxo que ajudam a gerenciar a quantidade de dados que podem ser enviados antes de receber uma confirmação. Isso evita a sobrecarga da rede e garante que o servidor e os clientes possam processar os dados de maneira eficiente.

### Ordem dos Pacotes
O TCP garante que os pacotes de dados sejam entregues na mesma ordem em que foram enviados. Em um jogo de trivia, a ordem das mensagens é essencial para manter a sequência correta de perguntas e respostas.

### Detecção de Erros
O TCP inclui mecanismos de detecção de erros que garantem que os dados corrompidos sejam retransmitidos. Isso é importante para manter a precisão das informações trocadas entre o cliente e o servidor.

### Conexão Orientada
O TCP é um protocolo orientado a conexão, o que significa que uma conexão deve ser estabelecida antes que os dados possam ser trocados. Isso permite uma comunicação mais estruturada e segura entre o cliente e o servidor.

### Adequação ao Jogo de Trivia
Para um jogo de trivia, onde a precisão e a integridade dos dados são fundamentais, o TCP é a escolha ideal. Ele garante que todas as perguntas, respostas e atualizações de tempo sejam entregues corretamente, proporcionando uma experiência de jogo justa e sem interrupções.

## Requisitos Mínimos de Funcionamento
- Python 3.x
- Bibliotecas: `socket`, `threading`, `json`, `random`
- PyQt5 para a interface gráfica do cliente
- Conexão de rede para comunicação entre cliente e servidor

## Funcionamento do Software

### Cliente
O cliente é responsável por:
- Conectar-se ao servidor
- Enviar o nome do jogador
- Receber perguntas e opções de resposta
- Enviar respostas ao servidor
- Exibir a interface gráfica do jogo

### Servidor
O servidor é responsável por:
- Gerenciar conexões de jogadores
- Enviar perguntas e opções de resposta aos jogadores
- Receber e validar respostas dos jogadores
- Manter o estado do jogo e calcular pontuações
- Enviar atualizações de tempo e resultados aos jogadores

## Documentação do Protocolo de Comunicação

### Eventos e Mensagens

#### Cliente para Servidor
- **Conexão Inicial**: Envia o nome do jogador ao conectar.
  ```json
  "nome_do_jogador"
  ```
  ```python
  class SocketClient(QObject):
      # ... código existente ...
      def connect(self, host, port, name):
          self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.socket.connect((host, port))
          self.socket.send(name.encode())
          threading.Thread(target=self.receive_messages, daemon=True).start()
      # ... código existente ...
  ```

- **Resposta do Jogador**: Envia a resposta escolhida pelo jogador.
  ```json
  {
    "type": "answer",
    "answer": <índice_da_resposta>
  }
  ```
  ```python
  class TriviaGame(QWidget):
      # ... código existente ...
      def sendAnswer(self, index):
          message = json.dumps({"type": "answer", "answer": index})
          self.client.send_message(message)
          for button in self.answerButtons:
              button.setEnabled(False)
          self.timer.stop()
          self.progressBar.setValue(0)
      # ... código existente ...
  ```

#### Servidor para Cliente
- **Início do Jogo**: Envia uma nova pergunta e opções de resposta.
  ```json
  {
    "type": "start_game",
    "pergunta": "Texto da pergunta",
    "opcoes": ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"],
    "tempo_restante": <tempo_em_segundos>
  }
  ```
  ```python
  class Jogo:
      # ... código existente ...
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
      # ... código existente ...
  ```

- **Resposta do Oponente**: Informa que o oponente respondeu.
  ```json
  {
    "type": "player_answered",
    "player": "Nome do jogador"
  }
  ```
  ```python
  class Jogo:
      # ... código existente ...
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
      # ... código existente ...
  ```

- **Atualização do Timer**: Envia a atualização do tempo restante.
  ```json
  {
    "type": "timer_update",
    "tempo_restante": <tempo_em_segundos>
  }
  ```
  ```python
  class Jogo:
      # ... código existente ...
      def contar_tempo(self):
          while self.tempo_restante > 0:
              self.tempo_restante -= 1
              self.broadcast(json.dumps({
                  "type": "timer_update",
                  "tempo_restante": self.tempo_restante
              }))
              threading.Event().wait(1)
          self.finalizar_jogo()
      # ... código existente ...
  ```

- **Fim do Jogo**: Envia os resultados finais do jogo.
  ```json
  {
    "type": "end_game",
    "resultados": [
      {
        "nome": "Nome do jogador",
        "pontuacao": <pontuacao>,
        "respostas": <numero_de_respostas>
      },
      ...
    ]
  }
  ```
  ```python
  class Jogo:
      # ... código existente ...
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
      # ... código existente ...
  ```

## Fluxo de Eventos

### Eventos do Cliente
1. **O cliente se conecta ao servidor e envia o nome do jogador.**
   ```python
   class SocketClient(QObject):
       # ... código existente ...
       def connect(self, host, port, name):
           self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           self.socket.connect((host, port))
           self.socket.send(name.encode())
           threading.Thread(target=self.receive_messages, daemon=True).start()
       # ... código existente ...
   ```

2. **O cliente recebe a primeira pergunta e opções de resposta.**
   ```python
   class TriviaGame(QWidget):
       # ... código existente ...
       def handleMessage(self, message):
           data = json.loads(message)
           if data['type'] == 'start_game':
               self.showQuestion(data)
       # ... código existente ...
   ```

3. **Os jogadores enviam suas respostas ao servidor.**
   ```python
   class TriviaGame(QWidget):
       # ... código existente ...
       def sendAnswer(self, index):
           message = json.dumps({"type": "answer", "answer": index})
           self.client.send_message(message)
           for button in self.answerButtons:
               button.setEnabled(False)
           self.timer.stop()
           self.progressBar.setValue(0)
       # ... código existente ...
   ```

4. **O cliente recebe atualizações de tempo e status das respostas dos jogadores.**
   ```python
   class TriviaGame(QWidget):
       # ... código existente ...
       def handleMessage(self, message):
           data = json.loads(message)
           if data['type'] == 'timer_update':
               self.updateTimer(data)
           elif data['type'] == 'player_answered':
               self.updateOpponentStatus(data)
       # ... código existente ...
   ```

5. **O cliente recebe os resultados finais do jogo.**
   ```python
   class TriviaGame(QWidget):
       # ... código existente ...
       def handleMessage(self, message):
           data = json.loads(message)
           if data['type'] == 'end_game':
               self.showResults(data)
       # ... código existente ...
   ```

### Eventos do Servidor
1. **O servidor aguarda a conexão de dois jogadores.**
   ```python
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
   ```

2. **O servidor inicia o jogo enviando a primeira pergunta e opções de resposta.**
   ```python
   class Jogo:
       # ... código existente ...
       def iniciar_jogo(self):
           self.proxima_pergunta()
           threading.Thread(target=self.contar_tempo).start()

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
       # ... código existente ...
   ```

3. **O servidor valida as respostas e atualiza as pontuações.**
   ```python
   class Jogo:
       # ... código existente ...
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
       # ... código existente ...
   ```

4. **O servidor envia atualizações de tempo e status das respostas dos jogadores.**
   ```python
   class Jogo:
       # ... código existente ...
       def contar_tempo(self):
           while self.tempo_restante > 0:
               self.tempo_restante -= 1
               self.broadcast(json.dumps({
                   "type": "timer_update",
                   "tempo_restante": self.tempo_restante
               }))
               threading.Event().wait(1)
           self.finalizar_jogo()
       # ... código existente ...
   ```

5. **O servidor envia os resultados finais aos jogadores.**
   ```python
   class Jogo:
       # ... código existente ...
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
       # ... código existente ...
   ```

### Estados do Jogo
1. **Aguardando Jogadores**: O servidor espera até que dois jogadores estejam conectados.
2. **Enviando Pergunta**: O servidor envia uma pergunta e opções de resposta aos jogadores.
3. **Aguardando Respostas**: O servidor aguarda as respostas dos jogadores.
4. **Atualizando Status**: O servidor atualiza o status do jogo com base nas respostas recebidas.
5. **Finalizando Jogo**: O servidor envia os resultados finais e encerra o jogo.

## Conclusão
Este projeto demonstra a aplicação de um protocolo TCP para criar um jogo multiplayer em tempo real. A escolha do protocolo TCP permite uma comunicação eficiente e de baixa latência, essencial para a experiência de jogo. A interface gráfica desenvolvida com PyQt5 proporciona uma experiência de usuário rica e interativa.
