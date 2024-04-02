import socket
from threading import Thread
import time
import mysql.connector
import sys
import json
import numpy as np
import cv2
import dlib
import re
import test
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
class Server:
    def __init__(self):
        self.client_keys = {}  # Dictionary to store AES keys for clients
        self.server = socket.socket()
        self.server.bind(("127.0.0.1", 8989))
        self.server.listen(5)
        self.clients = []
        self.clients_name_ip = []
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="wuzheng123",
            database="chatroom"
        )
        self.cursor = self.db.cursor()
        self.running = True


    def start(self):
        # 启动监听线程
        Thread(target=self.listen_clients).start()

    def listen_clients(self):
        while self.running:
            client, address = self.server.accept()
            print(address)
            #data = "与服务器链接成功，请输入用户名与密码才可以聊天"
            #判断用户的请求是登录还是注册
            mod = client.recv(1024).decode()
            print(mod)
            if mod == "login":                
                client.send("server_public_key_sending:".encode())       
                # 加载PEM格式的公钥文件
                with open('public_key.pem', 'rb') as f:
                    pem_public_key = f.read()
                # 发送公钥数据
                client.sendall(pem_public_key)
                
                # 接收加密iv并解密
                encrypted_iv = client.recv(8192)
                # 使用服务器的私钥进行解密
                iv = decrypt_with_private_key(encrypted_iv, server_private_key)
                print(iv)
                # 解密后通知client
                client.send("recv_iv!".encode())
                time.sleep(0.1)  # 等待一段时间，确保发送完整 
                        
                # 接收加密数据
                encrypted_data = client.recv(8196)
                print("encrypted_data:",encrypted_data)
                # 使用服务器的私钥解密加密后的数据
                decrypted_data = decrypt_with_private_key(encrypted_data, server_private_key)

                # 拆分解密后的数据
                aes_key = decrypted_data[:32]
                encrypted_username = decrypted_data[32:64]
                encrypted_password = decrypted_data[64:]

                # 解密用户名和密码
                username = aes_decrypt(aes_key, encrypted_username, iv).decode()
                password = aes_decrypt(aes_key, encrypted_password, iv).decode()
                print("username:",username)
                print("password:",password)
                # 验证用户名和密码等
                query = "SELECT * FROM users WHERE username = %s AND password = %s"
                values = (username, password)
                self.cursor.execute(query, values)
                result = self.cursor.fetchone()

                if result:
                    # 用户名和密码验证通过，将用户信息添加到列表中
                    print("success login")
                    self.client_keys[address] = (aes_key, iv)
                    client.send("success".encode())
                    self.clients_name_ip.append((address, username))
                    self.clients.append(client)
                    Thread(target=self.get_msg, args=(client, address)).start()
                else:
                    # 用户名和密码验证失败，关闭客户端连接
                    print("failed login!")
                    client.send("用户名或密码错误!".encode())
                    client.close()

                    
            if mod == "regis":
                client.settimeout(5)  # Set a timeout of 5 seconds
                client.send("server_public_key_sending:".encode())  
                time.sleep(0.1)     
                # 加载PEM格式的公钥文件
                with open('public_key.pem', 'rb') as f:
                    pem_public_key = f.read()
                # 发送公钥数据
                client.sendall(pem_public_key)
                
                # 接收加密iv并解密
                encrypted_iv = client.recv(8192)
                # 使用服务器的私钥进行解密
                iv = decrypt_with_private_key(encrypted_iv, server_private_key)
                print(iv)
                # 解密后通知client
                client.send("recv_iv!".encode())
                time.sleep(0.1)  # 等待一段时间，确保发送完整 
                
                # 接收加密数据
                enc_data = client.recv(8196)
                print("encrypted_data:",enc_data)
                # 使用服务器的私钥解密加密后的数据
                dec_data = decrypt_with_private_key(enc_data, server_private_key)
                
                aes_key = dec_data[0:32]
                enc_username = dec_data[32:64]
                enc_password = dec_data[64:96]
                enc_confirm_password = dec_data[96:128]
                enc_email = dec_data[128:]
                
                username = aes_decrypt(aes_key, enc_username, iv).decode()
                password = aes_decrypt(aes_key, enc_password, iv).decode()
                password_rep = aes_decrypt(aes_key, enc_confirm_password, iv).decode()
                email = aes_decrypt(aes_key, enc_email, iv).decode()
                print(username,password,email)
                
                
                try:
                    received_data = client.recv(8192 * 6).decode()
                    face = json.loads(received_data)
                    # Process the received data
                except socket.timeout:
                    print("No data received within the timeout period. Continuing with execution.")
                    face = [None] * 6
                # 查询数据库，检查用户名是否已存在
                query = "SELECT * FROM users WHERE username = %s"
                values = (username,)
                self.cursor.execute(query, values)
                existing_user = self.cursor.fetchone()
                
                if existing_user:
                    client.send("用户名已存在!".encode())
                    client.close()
                elif password != password_rep:
                    client.send("密码不匹配!".encode())
                    client.close()
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    client.send("邮箱格式不正确!".encode())
                    client.close()
                elif len(password) < 6 or not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
                    client.send("密码不符合安全要求! 密码长度至少为6位，且需包含字母和数字.".encode())
                    client.close()
                else:
                    query = "INSERT INTO users (username, password, email, vector_1, vector_2, vector_3, vector_4, vector_5, vector_6) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (username, password, email, face[0], face[1], face[2], face[3], face[4], face[5])
                    self.cursor.execute(query, values)
                    self.db.commit()
                    client.send("success".encode())
                    client.close()
                    
            if mod == "facelogin":
                client.send("server_public_key_sending:".encode())       
                # 加载PEM格式的公钥文件
                with open('public_key.pem', 'rb') as f:
                    pem_public_key = f.read()
                # 发送公钥数据
                client.sendall(pem_public_key)
                
                # 接收加密iv并解密
                encrypted_iv = client.recv(8192)
                # 使用服务器的私钥进行解密
                iv = decrypt_with_private_key(encrypted_iv, server_private_key)
                print(iv)
                # 解密后通知client
                client.send("recv_iv!".encode())
                time.sleep(0.1)  # 等待一段时间，确保发送完整 
                # 接收加密数据
                encrypted_data = client.recv(8196)
                print("encrypted_data:",encrypted_data)
                # 使用服务器的私钥解密加密后的数据
                aes_key = decrypt_with_private_key(encrypted_data, server_private_key)

                login_hist = []  # 存储登录时的照片
                similarity = []
                received_face = client.recv(81920 * 44).decode()
                faces = json.loads(received_face)
                print(faces)
                for face in faces:
                    # 将JSON字符串转换回Python列表
                    hist_list = json.loads(face)

                    # 将列表转换为numpy数组
                    hist = np.array(hist_list, dtype=np.float32)

                    login_hist.append(hist)
                # 查询数据库，遍历查询每条记录的 vector1 到 vector6
                query = "SELECT vector_1, vector_2, vector_3, vector_4, vector_5, vector_6 FROM users"
                self.cursor.execute(query)
                results = self.cursor.fetchall()

                for result in results:
                    register_hist = []
                    vectors = [result[0], result[1], result[2], result[3], result[4], result[5]]
                    for vector in vectors:
                        if vector is not None:
                            hist_list_0 = json.loads(vector)
                            hist_0 = np.array(hist_list_0, dtype=np.float32)
                            register_hist.append(hist_0)

                    similarity_login = []
                    for login in login_hist:
                        similarity_iter = 0
                        for register in register_hist:
                            similarity_iter = similarity_iter + cv2.compareHist(login, register, cv2.HISTCMP_CORREL)
                        similarity_login.append(similarity_iter / len(register_hist))
                    similarity_login.remove(max(similarity_login))
                    similarity_login.remove(min(similarity_login))
                    similarity.append(sum(similarity_login) / len(similarity_login))
                max_index = np.argmax(similarity)
                print(similarity)
                print(max_index)
                print(max(similarity))

                query = "SELECT username FROM users"
                self.cursor.execute(query)
                usernames = [result[0] for result in self.cursor.fetchall()]
                max_username = usernames[max_index]
                print("Username: ", max_username)
                self.client_keys[address] = (aes_key, iv)
                client.send("success".encode())
                self.clients_name_ip.append((address, max_username))
                self.clients.append(client)
                Thread(target=self.get_msg, args=(client, address)).start()
                

    def get_msg(self, client, address):
        aes_key, iv = self.client_keys[address]
        username =  self.get_client_name(address) 
        # 循环监听客户端消息
        while True:
            try:
                enc_recv_data = client.recv(1024)
                recv_data = aes_decrypt(aes_key, enc_recv_data, iv).decode()
                if recv_data.strip() == '':
                    continue  # 跳过后续操作，接收到的内容为空
                print(recv_data)
            except Exception as e:
                self.close_client(client, address)
                break
            # 如果用户输入Q，退出
            if recv_data.upper() == "Q":
                self.close_client(client, address)
                break

            for c in self.clients:
               classification_result = test.classify(recv_data)
               if classification_result == 0:
                  print(self.get_client_name(address))
                  msg = self.get_client_name(address) + " " + time.strftime("%x") + "\n" + recv_data
                  print("msg:",msg)
                  enc_msg = aes_encrypt(aes_key, msg.encode(), iv)
                  c.send(enc_msg)
               else:
                  # 如果分类结果为1，发送提示消息
                  tip_msg = self.get_client_name(address) + "的发言有冒犯性，消息已被屏蔽"
                  enc_tip_msg = aes_encrypt(aes_key, tip_msg.encode(), iv)
                  c.send(enc_tip_msg)
                    
    def get_client_name(self, address):
        for client in self.clients_name_ip:
            if client[0] == address:
                return client[1]
        return ""

    def close_client(self, client, address):
        self.clients.remove(client)
        client.close()

        client_name = self.get_client_name(address)
        print(client_name + "已经离开")
        for c in self.clients:
            c.send((client_name + "已经离开").encode())

    def stop(self):
        self.running = False
        self.server.close()

def face_normalize_hishistogram(frame):
    global cropped_face
    detector = dlib.get_frontal_face_detector()
    face = detector(frame)

    # 获取人脸照片
    for i, d in enumerate(face):
        x, y, w, h = d.left(), d.top(), d.width(), d.height()
        cropped_face = frame[y:y + h, x:x + w]

    face_gray = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY) if cropped_face.ndim == 3 else face

    # 计算直方图
    hist = cv2.calcHist([face_gray], [0], None, [512], [0, 512])

    # 归一化直方图
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    return hist


# RSA私钥解密器
def decrypt_with_private_key(encrypted_data, private_key):
    decrypted_data = private_key.decrypt(
        encrypted_data,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

# AES加密器
def aes_encrypt(key, data,iv):
    print(iv)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(256).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

# AES解密器
def aes_decrypt(key, data,iv):
    print(iv)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(256).unpadder()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data

if __name__ == '__main__':
    
    server = Server()
    server.start()
    # 加载私钥
    with open('private_key.pem', 'rb') as key_file:
        server_private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # 如果私钥有密码，请提供密码字符串
            backend=default_backend()
        )
    # 等待用户输入命令来停止服务器
    while True:
        user_input = input("输入 'stop' 停止服务器: ")
        if user_input.lower() == "stop":
            server.stop()
            break