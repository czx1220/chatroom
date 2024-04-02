#server端代码
import socket
from threading import Thread
import time
import sqlite3

# 假设数据库文件为 "users.db"，包含一个名为 "users" 的表，表结构为 (id, username)
DATABASE_FILE = "users.db"

class Server:
    def __init__(self):
        self.server=socket.socket()
        self.server.bind(("127.0.0.1", 8989))
        self.server.listen(5)
        self.clients=[]
        self.clients_name_ip={}
        self.get_conn()
    # 监听客户端链接
    def get_conn(self):
        while True:
            client,address=self.server.accept()
            print(address)
            data="与服务器链接成功，请输入昵称才可以聊天"
            # server与client通信，send() decode
            client.send(data.encode())
            # 链接用户添加到服务器的用户列表
            self.clients.append(client)
            Thread(target=self.get_msg,args=(client,self.clients,self.clients_name_ip,address)).start()

    # 进行所有客户端消息的处理
    def get_msg(self,client,clients,clients_name_ip,address):
        # 接受客户端发来的昵称
        name=client.recv(1024).decode()
        # 昵称与IP进行绑定
        clients_name_ip[address]=name
        # 循环监听客户端消息
        while True:
            try:
                recv_data=client.recv(1024).decode()
            except Exception as e:
                self.close_client(client,address)
                break
            # 如果用户输入Q，退出
            if recv_data.upper()=="Q":
                self.close_client(client,address)
                break
            for c in clients:
                c.send((clients_name_ip[address]+" "+time.strftime("%x")+"\n"+recv_data).encode())
    # 关闭资源
    def close_client(self,client,address):
        self.clients.remove(client)
        client.close()

        print(self.clients_name_ip[address]+"已经离开")
        for c in self.clients:
            c.send((self.clients_name_ip[address]+"已经离开").encode())


if __name__ == '__main__':
    Server()