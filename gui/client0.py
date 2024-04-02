from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
import sys
import socket
from threading import Thread
import time
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Client(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(600, 300, 360, 300)
        self.setWindowTitle("聊天室")
        palette = QtGui.QPalette()
        bg = QtGui.QPixmap(r"./img/background.png")
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(bg))
        self.setPalette(palette)
        self.add_ui()

        # 与服务器链接
        self.client = socket.socket()
        self.client.connect(("127.0.0.1", 8989))

        # 调用线程
        self.work_thread()

    # 设置界面组件
    def add_ui(self):
        self.content = QTextBrowser(self)
        self.content.setGeometry(30, 30, 300, 150)

        # 单行文本
        self.message = QLineEdit(self)
        self.message.setPlaceholderText("请输入发送内容")
        self.message.setGeometry(30, 200, 300, 30)
        # 发送按钮
        self.button = QPushButton("发送", self)
        self.button.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.button.setGeometry(270, 250, 60, 30)

    # 发送消息
    def send_msg(self):
        msg = self.message.text()

        self.client.send(msg.encode())
        if msg.upper() == "Q":
            self.client.close()
            self.destroy()
            sys.exit()  # 终止程序运行
        self.message.clear()
    
    # 接受消息
    def recv_msg(self):
        while True:
            try:
                data = self.client.recv(1024).decode()

                print(data)

                data = data + "\n"
                self.content.append(data)
                # 设置滚动条到最底部
                self.content.ensureCursorVisible()  # 游标可用
                cursor = self.content.textCursor()  # 设置游标
                pos = len(self.content.toPlainText())  # 获取文本尾部的位置
                cursor.setPosition(pos)  # 游标位置设置为底部
                self.content.setTextCursor(cursor)  # 滚动到游标位置
            except:
                break

    def btn_send(self):
        self.button.clicked.connect(self.send_msg)


    # 匿名类，线程处理，发送是一个线程，接受是一个线程
    def work_thread(self):
        Thread(target=self.btn_send).start()
        recv_thread = Thread(target=self.recv_msg)
        recv_thread.daemon = True  # 将接收线程设置为守护线程
        recv_thread.start()
    
    # 重写窗口关闭事件处理函数
    def closeEvent(self, event):
        self.client.close()
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())