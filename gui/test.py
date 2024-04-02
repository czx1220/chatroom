from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Window")
        self.resize(400, 600)

        self.message_list = QTextEdit()
        self.message_list.setReadOnly(True)
        self.message_list.setStyleSheet(
            '''
            QTextEdit {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 10px;
            }
            '''
        )

        self.message_input = QTextEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.message_list)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_message(self):
        message = self.message_input.toPlainText()
        if message:
            self.add_message("You", message, align_right=True)
            self.message_input.clear()

    def add_message(self, sender, message, align_right=False):
        sender_message = f"{sender}: {message}"
        bubble_style = "background-color: #DCF8C6; padding: 10px; border-radius: 10px;"
        if align_right:
            bubble_style += "margin-left: auto;"

        self.message_list.moveCursor(QTextCursor.End)
        self.message_list.insertHtml(
            f'<p style="{bubble_style}">{sender_message}</p>'
        )
        self.message_list.moveCursor(QTextCursor.End)

if __name__ == "__main__":
    app = QApplication([])
    window = ChatWindow()
    window.show()
    app.exec_()