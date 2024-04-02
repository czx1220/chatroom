import pandas as pd

# 读取CSV文件
train_data = pd.read_csv("train.csv")
dev_data = pd.read_csv("dev.csv")
test_data = pd.read_csv("test.csv")

# 写入train.txt
with open("train.txt", "w", encoding="utf-8") as f:
    for index, row in train_data.iterrows():
        text = row["TEXT"]
        label = row["label"]
        f.write(f"{text}\t{label}\n")

# 写入dev.txt
with open("dev.txt", "w", encoding="utf-8") as f:
    for index, row in dev_data.iterrows():
        text = row["TEXT"]
        label = row["label"]
        f.write(f"{text}\t{label}\n")

# 写入test.txt
with open("test.txt", "w", encoding="utf-8") as f:
    for index, row in test_data.iterrows():
        text = row["TEXT"]
        label = row["label"]
        f.write(f"{text}\t{label}\n")
