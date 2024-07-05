import sys
import json
import asyncio
import websockets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QLinearGradient, QPainter, QBrush
import socket

class WebSocketClient(QObject):
    messageReceived = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.websocket = None

    async def connect(self, uri, name):
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(name)

        while True:
            try:
                message = await self.websocket.recv()
                self.messageReceived.emit(message)
            except websockets.exceptions.ConnectionClosed:
                break

class TriviaGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client = WebSocketClient()
        self.client.messageReceived.connect(self.handleMessage)
        self.asyncLoop = asyncio.get_event_loop()
        self.startGame()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgressBar)
        self.progress_value = 60
        self.server_address = None

    def initUI(self):
        self.setWindowTitle('Jogo de Trivia')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E2E;
                color: #CDD6F4;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #89B4FA;
                color: #1E1E2E;
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B4BEFE;
            }
            QPushButton:disabled {
                background-color: #6C7086;
                color: #BAC2DE;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #89B4FA;
                border-radius: 5px;
                font-size: 16px;
                background-color: #313244;
                color: #CDD6F4;
            }
            QLabel {
                font-size: 18px;
                color: #CDD6F4;
            }
            QFrame {
                border: 2px solid #89B4FA;
                border-radius: 15px;
            }
        """)

        main_layout = QVBoxLayout()

        # Área de entrada do nome
        name_layout = QHBoxLayout()
        self.nameInput = QLineEdit(self)
        self.nameInput.setPlaceholderText("Digite seu nome")
        self.startButton = QPushButton('Iniciar Jogo', self)
        self.startButton.clicked.connect(self.connectToServer)
        name_layout.addWidget(self.nameInput)
        name_layout.addWidget(self.startButton)
        main_layout.addLayout(name_layout)

        # Área de descoberta do servidor
        discover_layout = QHBoxLayout()
        self.discoverButton = QPushButton('Descobrir Servidor', self)
        self.discoverButton.clicked.connect(self.discoverServer)
        discover_layout.addWidget(self.discoverButton)
        main_layout.addLayout(discover_layout)

        # Área da pergunta
        question_frame = QFrame(self)
        question_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        question_layout = QVBoxLayout(question_frame)
        self.questionLabel = QLabel('', self)
        self.questionLabel.setAlignment(Qt.AlignCenter)
        self.questionLabel.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.questionLabel.setWordWrap(True)
        question_layout.addWidget(self.questionLabel)
        main_layout.addWidget(question_frame)

        # Área das respostas
        answer_layout = QVBoxLayout()
        self.answerButtons = []
        for i in range(5):
            button = QPushButton('', self)
            button.clicked.connect(lambda _, idx=i: self.sendAnswer(idx))
            button.hide()
            answer_layout.addWidget(button)
            self.answerButtons.append(button)
        main_layout.addLayout(answer_layout)

        # Área de informações
        info_layout = QHBoxLayout()
        self.timerLabel = QLabel('', self)
        self.opponentLabel = QLabel('', self)
        info_layout.addWidget(self.timerLabel)
        info_layout.addWidget(self.opponentLabel)
        main_layout.addLayout(info_layout)

        # Barra de progresso para o timer
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 60)
        self.progressBar.setValue(60)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #89B4FA;
                border-radius: 5px;
                background-color: #313244;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #89B4FA;
            }
        """)
        main_layout.addWidget(self.progressBar)

        self.setLayout(main_layout)

        # Adicionar sombra aos widgets
        self.addShadowEffect(question_frame)
        for button in self.answerButtons:
            self.addShadowEffect(button)

    def addShadowEffect(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def startGame(self):
        self.asyncLoop.run_in_executor(None, self.asyncLoop.run_forever)

    def discoverServer(self):
        self.discoverButton.setEnabled(False)
        self.discoverButton.setText("Procurando servidor...")
        asyncio.run_coroutine_threadsafe(self.discover(), self.asyncLoop)

    async def discover(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)

        try:
            sock.sendto(b'DISCOVER_TRIVIA_SERVER', ('<broadcast>', 5000))
            data, addr = sock.recvfrom(1024)
            self.server_address = data.decode()
            self.discoverButton.setText(f"Servidor encontrado: {self.server_address}")
            self.startButton.setEnabled(True)
        except socket.timeout:
            self.discoverButton.setText("Servidor não encontrado. Tente novamente.")
            self.discoverButton.setEnabled(True)
        finally:
            sock.close()

    def connectToServer(self):
        name = self.nameInput.text()
        if name and self.server_address:
            self.nameInput.setEnabled(False)
            self.discoverButton.setEnabled(False)
            self.startButton.setEnabled(False)
            asyncio.run_coroutine_threadsafe(
                self.client.connect(f'ws://{self.server_address}:8765', name),
                self.asyncLoop
            )

    def handleMessage(self, message):
        data = json.loads(message)
        if data['type'] == 'start_game':
            self.showQuestion(data)
        elif data['type'] == 'player_answered':
            self.updateOpponentStatus(data)
        elif data['type'] == 'end_game':
            self.showResults(data)
        elif data['type'] == 'timer_update':
            self.updateTimer(data)

    def updateTimer(self, data):
        tempo_restante = int(data['tempo_restante'])
        self.timerLabel.setText(f"Tempo restante: {tempo_restante} segundos")
        self.progress_value = tempo_restante
        self.progressBar.setValue(tempo_restante)

    def showQuestion(self, data):
        self.questionLabel.setText(data['pergunta'])
        for i, option in enumerate(data['opcoes']):
            self.answerButtons[i].setText(option)
            self.answerButtons[i].show()
            self.answerButtons[i].setEnabled(True)
        self.timerLabel.setText(f"Tempo restante: {data['tempo_restante']} segundos")
        self.opponentLabel.setText("Aguardando resposta do oponente")
        
        # Reiniciar e iniciar o timer
        self.progress_value = 60
        self.progressBar.setValue(60)
        self.progressBar.show()  # Garante que a barra esteja visível
        self.timer.start(1000)  # Atualiza a cada segundo

    def sendAnswer(self, index):
        asyncio.run_coroutine_threadsafe(
            self.client.websocket.send(json.dumps({"type": "answer", "answer": index})),
            self.asyncLoop
        )
        for button in self.answerButtons:
            button.setEnabled(False)
        self.timer.stop()
        self.progressBar.setValue(0)

    def updateOpponentStatus(self, data):
        self.opponentLabel.setText(f"{data['player']} respondeu!")

    def showResults(self, data):
        resultText = "Fim de jogo!\n\nResultados:\n"
        for player in data['resultados']:
            resultText += f"{player['nome']}: {player['pontuacao']} pontos ({player['respostas']} respostas)\n"
        self.questionLabel.setText(resultText)
        for button in self.answerButtons:
            button.hide()
        self.timerLabel.setText('')
        self.opponentLabel.setText('')
        self.progressBar.hide()
        self.timer.stop()

    def updateProgressBar(self):
        self.progress_value -= 1
        if self.progress_value >= 0:
            self.progressBar.setValue(self.progress_value)
        else:
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = TriviaGame()
    game.show()
    sys.exit(app.exec_())