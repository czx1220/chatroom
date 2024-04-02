import cv2
import dlib
import time

import json
import mysql.connector

import numpy as np

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



def register():
    print("准备人脸识别录入...")

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="ZTH7452135",
        database="face"
    )

    cursor = mydb.cursor()

    cursor.execute("SHOW TABLES LIKE 'histograms'")
    result = cursor.fetchone()
    if result:
        print("Table 'histograms' already exists.")
    else:
        # 创建 histograms 表
        create_table_query = """
                    CREATE TABLE histograms (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        hist_data BLOB
                    );
                    """
        cursor.execute(create_table_query)
        mydb.commit()
        print("Table 'histograms' created successfully.")

    # 打开摄像头
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
            hist_json = json.dumps(hist_list)  # 然后转换为JSON字符串

            sql_insert_blob_query = """INSERT INTO histograms (hist_data) VALUES (%s)"""
            cursor.execute(sql_insert_blob_query, (hist_json,))

            mydb.commit()

            next_capture_time += 0.5
            photo_count += 1

        # 判断是否达到6秒，如果是，则退出循环
        if current_time >= end_time:
            break

        cv2.waitKey(1)

    # 释放摄像头并关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()
    mydb.close()


def login():
    global login_hist
    similarity = []
    flag = 0

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="ZTH7452135",
        database="face"
    )

    cursor = mydb.cursor()

    sql_select_query = """SELECT hist_data FROM histograms"""
    cursor.execute(sql_select_query)
    records = cursor.fetchall()

    mydb.close()

    histograms = []

    for record in records:
        # 将JSON字符串转换回Python列表
        hist_list = json.loads(record[0])

        # 将列表转换为numpy数组
        hist = np.array(hist_list, dtype=np.float32)

        histograms.append(hist)
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    start_time = time.time()
    next_capture_time = start_time + 3  # 开始捕获的时间
    end_time = start_time + 5


    while True:
        current_time = time.time()

        # 捕获帧
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # 显示当前帧
        cv2.imshow('Camera Preview', frame)

        if next_capture_time <= current_time:
            login_hist = face_normalize_hishistogram(frame)
            similarity_iter = 0
            for hist in histograms:
                similarity_iter = similarity_iter + cv2.compareHist(hist, login_hist, cv2.HISTCMP_CORREL)

            similarity.append(similarity_iter / len(histograms))

            next_capture_time += 0.2

        if current_time >= end_time:
            break

        cv2.waitKey(1)


    # 释放摄像头并关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()

    similarity.remove(max(similarity))
    similarity.remove(min(similarity))


    similarity_result = sum(similarity) / len(similarity)
    print(similarity_result)

    if(similarity_result > 0.8):
        print("login successfully!")

    else:
        print("login failed!")




login()