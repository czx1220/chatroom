import torch
from models.bert import Model
from importlib import import_module


#def modelload():
#   model_name = 'bert'
#   x = import_module('models.' + model_name)

#   dataset = 'COLDataset'
#   config = x.Config(dataset)

    # 创建模型实例
#   model = Model(config)

    # 加载模型权重
#   model.load_state_dict(torch.load(r'C:\Users\81591\Desktop\chat\COLDataset\saved_dict4\bert.ckpt'))

    # 将模型设置为评估模式
#   model.eval()


def classify(text_to_classify):

    model_name = 'bert'
    x = import_module('models.' + model_name)
    dataset = 'COLDataset'
    config = x.Config(dataset)
    model = Model(config)
    model.load_state_dict(torch.load(r'C:\Users\81591\Desktop\chat\COLDataset\saved_dict4\bert.ckpt'))
    model.eval()
    # 自定义最大长度
    max_input_length = 128  # 你可以根据需要调整这个值

    # 处理输入数据
    tokenized_text = config.tokenizer.tokenize(text_to_classify)

    # 将输入长度限制为自定义的最大长度
    if len(tokenized_text) > max_input_length:
       tokenized_text = tokenized_text[:max_input_length]

    indexed_tokens = config.tokenizer.convert_tokens_to_ids(tokenized_text)
    padded_tokens = indexed_tokens + [0] * (max_input_length - len(indexed_tokens))
    mask = [1] * len(indexed_tokens) + [0] * (max_input_length - len(indexed_tokens))

    # 构建输入数据
    input_data = (torch.tensor([padded_tokens]), torch.tensor([len(indexed_tokens)]), torch.tensor([mask]))

    # 推理
    with torch.no_grad():
         output = model(input_data)

    # 处理输出
    predicted_class = torch.argmax(output, dim=1).item()

    # 输出分类结果
    #print("待分类的文本:", text_to_classify)
    #print("预测的类别索引:", predicted_class)
    #print("预测的类别名称:", config.class_list[predicted_class])
    return predicted_class
