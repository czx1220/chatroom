from PyQt5.QtGui import QFont
import sys
import socket
from threading import Thread
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore
import cv2
import dlib
import time
import json
import numpy as np
import os
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from gui import main, login, register, chatroom
from PyQt5 import QtWidgets


def eye_aspect_ratio(eye):
    # 计算两组垂直距离的平均值
    vertical1 = np.linalg.norm(eye[1] - eye[5])
    vertical2 = np.linalg.norm(eye[2] - eye[4])
    # 计算水平距离
    horizontal = np.linalg.norm(eye[0] - eye[3])
    # 计算并返回纵横比
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear



# 客户端
class Client(QWidget,main.Ui_Form):
    validation_result = QtCore.pyqtSignal(str)
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle("聊天室")
        self.login_button.clicked.connect(self.switch_window_from_main_to_login)  # 将按钮的点击事件连接到注册方法
        self.register_button.clicked.connect(self.switch_window_from_main_to_regis)  # 将按钮的点击事件连接到注册方法
        self.face_login.clicked.connect(self.send_face_msg)  # 将按钮的点击事件连接到发送消息的方法

        # 初始化client属性
        self.client = None
        self.face_list = []

    def switch_window_from_main_to_regis(self):
        client_pos = client.pos()  # 保存主界面的位置
        client.hide()  # 隐藏主界面
        regis.move(client_pos)  # 将注册界面移动到登录界面的位置
        regis.show()  # 打开注册界面

    def switch_window_from_main_to_login(self):
        client_pos = client.pos()  # 保存主界面的位置
        client.hide()  # 隐藏主界面
        log.move(client_pos)  # 将登录界面移动到登录界面的位置
        log.show()  # 打开登录界面


    # 匿名类，线程处理，发送是一个线程，接受是一个线程
    def work_thread(self):
        recv_thread = Thread(target=self.recv_msg)
        recv_thread.daemon = True  # 将接收线程设置为守护线程
        recv_thread.start()

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


   # 发送面部数据
    def send_face_msg(self):
        # 与服务器链接
        self.client = socket.socket()
        self.client.connect(("127.0.0.1", 8989))    
        self.client.send("facelogin".encode())    
             
        recv_pubkey = self.client.recv(1024).decode()
        if recv_pubkey == "server_public_key_sending:":
            server_pubkey = self.client.recv(8192)
        # 加载服务器的公钥
        server_public_key = serialization.load_pem_public_key(server_pubkey, backend=default_backend())
        # 使用服务器公钥进行加密初始向量
        encrypted_iv = encrypt_with_public_key(iv, server_public_key)
        # 发送加密后的初始向量给服务器
        self.client.send(encrypted_iv)
        time.sleep(0.1)  # 等待一段时间，确保发送完整
        
        reply_of_iv = self.client.recv(1024).decode()
        if reply_of_iv == "recv_iv!":

            data_to_encrypt = aes_key
            # 使用服务器公钥加密合并后的数据
            encrypted_data = encrypt_with_public_key(data_to_encrypt, server_public_key)
            # 发送加密后的数据给服务器
            self.client.send(encrypted_data)
            time.sleep(0.1)
                              
            global login_hist
            # 打开摄像头
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Cannot open camera")
                exit()

            detector = dlib.get_frontal_face_detector()

            start_time = time.time()
            next_capture_time = start_time + 5  # 开始捕获的时间
            end_time = start_time + 7

            # 检测眨眼的参数
            EAR_THRESHOLD = 0.2  # EAR阈值
            EAR_CONSEC_FRAMES = 2  # 至少需要的眨眼次数
            blink_counter = 0  # 眨眼次数
            flag = 0

            print("现在开始活体检测，请你眨一眨眼")

            while True:
                current_time = time.time()
                # 捕获帧
                ret, frame = cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
                # 显示当前帧
                cv2.imshow('Camera Preview', frame)

                if current_time < start_time + 4:
                    # 转换到灰度图
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = detector(gray)
                    for face in faces:
                        landmarks = predictor(gray, face)
                        # 分别获取左眼和右眼的坐标
                        leftEye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)],
                                           dtype=np.int32)
                        rightEye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)],
                                            dtype=np.int32)

                        # 计算两只眼睛的EAR
                        leftEAR = eye_aspect_ratio(leftEye)
                        rightEAR = eye_aspect_ratio(rightEye)
                        ear = (leftEAR + rightEAR) / 2.0

                        # 如果EAR小于阈值，增加blink_counter
                        if ear < EAR_THRESHOLD:
                            blink_counter += 1

                            # 重置EAR阈值，防止算作多次眨眼
                            EAR_THRESHOLD = 0.3
                        else:
                            EAR_THRESHOLD = 0.2

                if flag == 0 and current_time > start_time + 4 and blink_counter < EAR_CONSEC_FRAMES :
                    print("活体检测失败，返回主页面")
                    flag = 1


                if next_capture_time <= current_time:
                    #self.face_list.append(face_normalize_hishistogram(frame))
                    
                    hist = face_normalize_hishistogram(frame)
                    hist_list = hist.flatten().tolist()  # 先将直方图数据转换为列表
                    hist_json = json.dumps(hist_list)  # 然后转换为JSON字符串a
                    self.face_list.append(hist_json)
                    next_capture_time += 0.2

                if current_time >= end_time:
                    break

                cv2.waitKey(1)

            print(blink_counter)
                
            self.client.send(json.dumps(self.face_list).encode())

            time.sleep(3)  # 等待一段时间
            # 释放摄像头并关闭所有窗口
            cap.release()
            cv2.destroyAllWindows()
        
        print("login......")
        # 接收验证结果
        validation_result = self.client.recv(1024).decode()
        self.validation_result.emit(validation_result)

    # 重写窗口关闭事件处理函数
    def closeEvent(self, event):
        if self.client is not None:
            self.client.close()
        event.accept()
        sys.exit()


# 用户端登录页面
class Login(QWidget,login.Ui_Form):
    validation_result = QtCore.pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle("聊天室")

        # 初始化client属性
        self.client = None
        self.face_list = []

        self.button.clicked.connect(self.send_msg)  # 将按钮的点击事件连接到发送消息的方法
        self.back_main.clicked.connect(self.switch_window_from_login_to_main)

    def switch_window_from_login_to_main(self):
        login_pos = log.pos()  # 保存主界面的位置
        log.hide()  # 隐藏主界面
        client.move(login_pos)  # 将注册界面移动到登录界面的位置
        client.show()  # 打开注册界面

    # 发送文本消息
    def send_msg(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # 与服务器链接
        self.client = socket.socket()
        self.client.connect(("127.0.0.1", 8989))
        self.client.send("login".encode())
             
        recv_pubkey = self.client.recv(1024).decode()
        if recv_pubkey == "server_public_key_sending:":
            server_pubkey = self.client.recv(8192)
        # 加载服务器的公钥
        server_public_key = serialization.load_pem_public_key(server_pubkey, backend=default_backend())
        # 使用服务器公钥进行加密初始向量
        encrypted_iv = encrypt_with_public_key(iv, server_public_key)
        # 发送加密后的初始向量给服务器
        self.client.send(encrypted_iv)
        time.sleep(0.1)  # 等待一段时间，确保发送完整
        
        reply_of_iv = self.client.recv(1024).decode()
        if reply_of_iv == "recv_iv!":
            # 加密用户名和密码
            encrypted_username = aes_encrypt(aes_key, username.encode(), iv)
            encrypted_password = aes_encrypt(aes_key, password.encode(), iv)

            # 将 AES 密钥、加密的用户名和加密的密码合并为一个字节串
            data_to_encrypt = aes_key + encrypted_username + encrypted_password

            # 使用服务器公钥加密合并后的数据
            encrypted_data = encrypt_with_public_key(data_to_encrypt, server_public_key)
            # 发送加密后的数据给服务器
            self.client.send(encrypted_data)
            time.sleep(0.1)
            
        # 接收验证结果
        validation_result = self.client.recv(1024).decode()
        self.validation_result.emit(validation_result)

    # 接受消息
    def recv_msg(self):
        if self.client is not None:
            # 验证用户名和密码
            validation_result = self.client.recv(1024).decode()
            self.validation_result.emit(validation_result)

    # 匿名类，线程处理，发送是一个线程，接受是一个线程
    def work_thread(self):
        recv_thread = Thread(target=self.recv_msg)
        recv_thread.daemon = True  # 将接收线程设置为守护线程
        recv_thread.start()

    # 重写窗口关闭事件处理函数
    def closeEvent(self, event):
        if self.client is not None:
            self.client.close()
        event.accept()
        sys.exit()

# 聊天界面
class ChatWindow(QWidget, chatroom.Ui_Form):
    def __init__(self, client):
        QWidget.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle("聊天室")
        self.client = client.client  # 保存对客户端实例的引用
        self.work_thread()  # 启动工作线程

        self.send_button.clicked.connect(self.send_msg)  # Connect the button's clicked signal to the send_message method

    # 发送消息
    def send_msg(self):
        msg = self.message.text()
        print("msg:",msg)
        enc_msg = aes_encrypt(aes_key, msg.encode(), iv)
        self.client.send(enc_msg)
        if msg.upper() == "Q":
            self.client.close()
            self.destroy()
            sys.exit()  # 终止程序运行
        self.message.clear()


    # 接受消息
    def recv_msg(self):
        while True:
            try:
                enc_data = self.client.recv(1024)
                data = aes_decrypt(aes_key, enc_data, iv).decode()
                #print(data)
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
        self.send_button.clicked.connect(self.send_msg)

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
        


# 用户端注册页面
class Regis(QWidget,register.Ui_Form):
    validation_result = QtCore.pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle("聊天室")

        # 初始化client属性
        self.client = None
        self.face_flag = 0
        self.hist_regis = []

        self.button.clicked.connect(self.send_msg)  # 将按钮的点击事件连接到发送消息的方法 
        self.back_main.clicked.connect(self.switch_window_from_regis_to_main)

    def switch_window_from_regis_to_main(self):
        regis_pos = regis.pos()  # 保存主界面的位置
        regis.hide()  # 隐藏主界面
        client.move(regis_pos)  # 将注册界面移动到登录界面的位置
        client.show()  # 打开注册界面

    # 发送消息
    def send_msg(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_input = self.confirm_input.text()
        email = self.email_input.text()       
        # 与服务器链接
        self.client = socket.socket()
        self.client.connect(("127.0.0.1", 8989))
        self.client.send("regis".encode())
        time.sleep(0.1)

        recv_pubkey = self.client.recv(1024).decode()
        print(recv_pubkey)
        if recv_pubkey == "server_public_key_sending:":
            server_pubkey = self.client.recv(8192)
        # 加载服务器的公钥
        server_public_key = serialization.load_pem_public_key(server_pubkey, backend=default_backend())
        # 使用服务器公钥进行加密初始向量
        encrypted_iv = encrypt_with_public_key(iv, server_public_key)
        # 发送加密后的初始向量给服务器
        self.client.send(encrypted_iv)
        time.sleep(0.1)  # 等待一段时间，确保发送完整

        reply_of_iv = self.client.recv(1024).decode()
        if reply_of_iv == "recv_iv!":
            # 加密用户名和密码
            encrypted_username = aes_encrypt(aes_key, username.encode(), iv)
            encrypted_password = aes_encrypt(aes_key, password.encode(), iv)
            encrypted_confirm_password = aes_encrypt(aes_key, confirm_input.encode(), iv)
            encrypted_email = aes_encrypt(aes_key, email.encode(), iv)
            # 将 AES 密钥、加密的用户名和加密的密码合并为一个字节串
            data_to_encrypt = aes_key + encrypted_username + encrypted_password + encrypted_confirm_password + encrypted_email    
            # 使用服务器公钥加密合并后的数据
            encrypted_data = encrypt_with_public_key(data_to_encrypt, server_public_key)
            # 发送加密后的数据给服务器
            self.client.send(encrypted_data)
            time.sleep(0.1)
        
        
        # 接收验证结果
        validation_result = self.client.recv(1024).decode()
        self.validation_result.emit(validation_result)
        print("1 regis result:", validation_result)
        self.switch_window_from_regis_to_login(validation_result)
        self.register_face()

    # 重写窗口关闭事件处理函数
    def closeEvent(self, event):
        if self.client is not None:
            self.client.close()
        event.accept()
        sys.exit()

    # 修改函数参数，去掉result参数
    def switch_window_from_regis_to_login(self, result):
        print("2 regis result:", result)
        if result == "success":
            regis_pos = regis.pos()  # 保存登录界面的位置
            regis.hide()  # 隐藏登录界面
            client.move(regis_pos)  # 将聊天界面移动到登录界面的位置
            client.show()  # 打开聊天界面
            self.client.close()
            
    def register_face(self):
        print("准备人脸识别录入...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        start_time = time.time()
        next_capture_time = start_time + 3  # 开始捕获的时间
        end_time = start_time + 6  # 结束程序的时间
        photo_count = 0
       
        while True:
            current_time = time.time()
            # 捕获帧
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # 显示当前帧
            cv2.imshow('Camera Preview', frame)
            # 判断当前时间是否在3到5秒内，如果是，则每0.5秒拍摄一张照片
            if next_capture_time <= current_time <= end_time:
                hist = face_normalize_hishistogram(frame)
                hist_list = hist.flatten().tolist()  # 先将直方图数据转换为列表
                hist_json = json.dumps(hist_list)  # 然后转换为JSON字符串a
                self.hist_regis.append(hist_json)
                next_capture_time += 0.4
                photo_count += 1
            # 判断是否达到6秒，如果是，则退出循环
            if current_time >= end_time:
                break
            cv2.waitKey(1)

        # 释放摄像头并关闭所有窗口
        cap.release()
        cv2.destroyAllWindows()

def face_normalize_hishistogram(frame):
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

def switch_window(result, window1,window2):
    print("switch result:",result)
    if result == "success":
        window1_pos = window1.pos()
        window1.hide()  
        window2.move(window1_pos) 
        window2.show()  
    else:
        print("用户名或密码错误")
        # 在这里添加处理登录失败的逻辑


def switch_window_from_login_to_room(result):
    chat_window = ChatWindow(log)  # 将客户端实例传递给聊天界面
    if result == "success":
        log_pos = log.pos()  # 保存登录界面的位置
        log.hide()  # 隐藏登录界面
        chat_window.move(log_pos)  # 将聊天界面移动到登录界面的位置
        chat_window.show()  # 打开聊天界面
    else:
        print("用户名或密码错误")
        # 在这里添加处理登录失败的逻辑

def switch_window_from_client_to_room(result):
    chat_window = ChatWindow(client)  # 将客户端实例传递给聊天界面
    if result == "success":
        client_pos = client.pos()  # 保存登录界面的位置
        client.hide()  # 隐藏登录界面
        chat_window.move(client_pos)  # 将聊天界面移动到登录界面的位置
        chat_window.show()  # 打开聊天界面
    else:
        print("用户名或密码错误")
        # 在这里添加处理登录失败的逻辑
# AES加密器
def aes_encrypt(key, data, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(256).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

# AES解密器
def aes_decrypt(key, data, iv):
    print(iv)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(256).unpadder()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data

# RSA公钥加密器
def encrypt_with_public_key(data, public_key):
    encrypted_data = public_key.encrypt(
        data,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data

if __name__ == "__main__":
    # 加载预训练的关键点检测模型
    predictor = dlib.shape_predictor("dat/shape_predictor_68_face_landmarks.dat")

    app = QApplication(sys.argv)
    app.setFont(QFont("微软雅黑", 10))
    # 生成随机的初始向量
    iv = os.urandom(16)
    # 生成 AES 密钥
    aes_key = os.urandom(32)
    
    cropped_face = None  # 声明并初始化 cropped_face 变量
    client = Client()
    log = Login()
    regis = Regis()


    log.validation_result.connect(switch_window_from_login_to_room)
    client.validation_result.connect(switch_window_from_client_to_room)
    #client.validation_result.connect(lambda result: switch_window(result, client, chat_window))
    client.show()
    client.work_thread()
    sys.exit(app.exec_())


# '''
#     # AES加密器
#     def aes_encrypt(key, data):
#         # 选择 AES 加密算法和加密模式（例如 ECB、CBC 等）
#         cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())

#         # 创建加密器
#         encryptor = cipher.encryptor()

#         # 对数据进行加密
#         encrypted_data = encryptor.update(data) + encryptor.finalize()

#         return encrypted_data

#     # client端 密钥协商
#     def key_negotiation(self):
#         msg = "key_negotiation"
#         self.client.send(msg.encode())

#         # 循环
#         while True:
#             data = self.client.recv(1024).decode()
#             if data.startswith("key_negotiation"):
#                 # 取出加密过的共享密钥
#                 encrypted_data = received_data[len("key_negotiation"):]  # 去除开头的 "key_negotiation"
#                 print("提取出的加密数据:", encrypted_data)
#                 # 假设 private_key_filename 是私钥文件的路径和文件名
#                 private_key_filename = "path/to/private_key.pem"

#                 # 从私钥文件加载私钥
#                 with open(private_key_filename, "rb") as key_file:
#                     private_key = serialization.load_pem_private_key(
#                         key_file.read(),
#                         password=None,
#                         backend=default_backend()
#                     )

#                 # 使用私钥 RSA 解密数据
#                 decrypted_data = private_key.decrypt(
#                     encrypted_data,
#                     padding.OAEP(
#                         mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                         algorithm=hashes.SHA256(),
#                         label=None
#                     )
#                 )
#                 print("获得了共享密钥decrypted_data")
#             return decrypted_data

#     ### 注册时用用户名生成私钥，并把公钥发送给server
#     def generate_private_key(username):
#         # 将用户名转换为字节序列
#         username_bytes = username.encode()

#         # 使用哈希函数生成固定长度的字节序列
#         hash_value = hashlib.sha256(username_bytes).digest()

#         # 使用哈希值作为种子生成私钥
#         private_key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend(),
#             seed=hash_value
#         )

#         # 序列化私钥为 PEM 格式
#         pem_private_key = private_key.private_bytes(
#             encoding=serialization.Encoding.PEM,
#             format=serialization.PrivateFormat.PKCS8,
#             encryption_algorithm=serialization.NoEncryption()
#         )

#         return pem_private_key

#     # server端 密钥协商
#         recv_data = client.recv(1024).decode()
#         recv_data == "key_negotiation"
#         # 生成随机密钥,并保留
#         random_bytes = secrets.token_bytes(32)
#         random_key = random_bytes.hex()
#         print("随机密钥:", random_key)
#         # 查询client的公钥public_key
#         # 使用公钥 RSA 加密数据 A，并加密random_key
#         encrypted_data = public_key.encrypt(
#             b'random_key', 
#             padding.OAEP(
#                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                 algorithm=hashes.SHA256(),
#                 label=None
#             )
#         )
#         client.send(("key_negotiation"+encrypted_data).encode())
#         # 后续server收到的聊天内容是用random_key,AES加密过的，需解密。
# '''