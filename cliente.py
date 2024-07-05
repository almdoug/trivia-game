import sys
import json
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QLinearGradient, QPainter, QBrush

class SocketClient(QObject):
    messageReceived = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.socket = None
        self.buffer = ""

    def connect(self, host, port, name):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.send(name.encode())
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024).decode()
                self.buffer += data
                while '\n' in self.buffer:
                    message, self.buffer = self.buffer.split('\n', 1)
                    try:
                        json_message = json.loads(message)
                        self.messageReceived.emit(json.dumps(json_message))
                    except json.JSONDecodeError:
                        print(f"Erro ao decodificar JSON: {message}")
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

    def send_message(self, message):
        self.socket.send((message + '\n').encode())

class TriviaGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client = SocketClient()
        self.client.messageReceived.connect(self.handleMessage)
        self.startGame()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgressBar)
        self.progress_value = 60  # Inicializa com 60 segundos
        self.server_address = "localhost"  # Endereço padrão

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

        # Área do endereço do servidor
        server_layout = QHBoxLayout()
        self.serverInput = QLineEdit(self)
        self.serverInput.setPlaceholderText("Endereço do servidor (ex: 192.168.0.10)")
        server_layout.addWidget(self.serverInput)
        main_layout.addLayout(server_layout)

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
        pass

    def connectToServer(self):
        name = self.nameInput.text()
        self.server_address = self.serverInput.text() or "localhost"
        if name:
            self.nameInput.setEnabled(False)
            self.serverInput.setEnabled(False)
            self.startButton.setEnabled(False)
            self.client.connect(self.server_address, 8765, name)

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
        message = json.dumps({"type": "answer", "answer": index})
        self.client.send_message(message)
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