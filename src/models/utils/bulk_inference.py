#!/usr/scripts/env python
# encoding: utf-8

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: bulk_inference.py
@time: 5/27/22 4:49 PM
@function: 根据训练模型，推断图片中互作类型，并记录相关信息到指定文件
"""

import os
import json
import torch
from PIL import Image
from torchvision import transforms
import glob

from model import efficientnetv2_l as create_model


class BulkInfer(object):
    def __init__(self, img_path, json_path, model_weight_path, info_path=None):
        self.img_path = img_path
        self.json_path = json_path
        self.model_weight_path = model_weight_path
        self.info_path = info_path

    def bulk_infer(self):
        if self.info_path is None:
            self.info_path = os.path.join(self.img_path, "type_info.txt")

        # 查找格式
        temp_path = os.path.join(self.img_path, "**/*.jpg")

        # 查找所有图片
        f = glob.glob(temp_path, recursive=True)
        img_paths = []
        for i in f:
            img_paths.append(i)

        temp_para = self.load_model()

        # 结果统计
        result = {}

        with open(self.info_path, 'a+') as f:
            for i in img_paths:
                infer_result = BulkInfer.inference(
                    i, self.json_path, temp_para)

                t = i + "    " + infer_result[0] + "    " + \
                    "{:.3}".format(infer_result[1]) + "\n"

                # 类型结果统计
                if infer_result[0] in result.keys():
                    result[infer_result[0]] += 1
                else:
                    result[infer_result[0]] = 1

                f.writelines(str(t))

    def load_model(self):
        # - 检查GPU/CUDA是否可用
        if torch.cuda.is_available():
            print("USE CUDA")

        # - 查看CUDA可用设备
        temp = torch.cuda.current_device()
        torch.cuda.current_device()

        # - 查看GPU名称
        if torch.cuda.get_device_name(temp):
            print("GPU : ", torch.cuda.get_device_name(temp))

        # - 默认设置
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # create model
        # take much time
        model = create_model(num_classes=5).to(device)

        model.load_state_dict(
            torch.load(
                self.model_weight_path,
                map_location=device))
        model.eval()

        return model

    @staticmethod
    def inference(img_paths, json_path, model):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # read class_indict
        assert os.path.exists(
            json_path), "file: '{}' dose not exist.".format(json_path)

        with open(json_path, "r") as f:
            class_indict = json.load(f)

        # - 图像大小
        # 模型与尺寸， 可以根据自己的数据，进行调整
        img_size = {"s": [300, 384],  # train_size, val_size
                    "m": [384, 480],
                    "l": [384, 480]}

        # 选择模型尺寸
        num_model = "l"

        # - 数据预处理
        data_transform = transforms.Compose([transforms.Resize(img_size[num_model][1]), transforms.CenterCrop(
            img_size[num_model][1]), transforms.ToTensor(), transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])])

        # 判断图片是否存在
        assert os.path.exists(
            img_paths), "file: '{}' dose not exist.".format(img_paths)

        # 通道转换 [N, C, H, W]
        img = Image.open(img_paths).convert('RGB')
        # plt.imshow(img)

        # - 数据处理
        img = data_transform(img)
        # expand batch dimension
        img = torch.unsqueeze(img, dim=0)

        with torch.no_grad():
            # predict class
            output = torch.squeeze(model(img.to(device))).cpu()
            predict = torch.softmax(output, dim=0)
            predict_cla = torch.argmax(predict).numpy()

        print_res = "class: {}   prob: {:.3}".format(
            class_indict[str(predict_cla)], predict[predict_cla].numpy())

        max_prob = {}
        for i in range(len(predict)):
            max_prob[class_indict[str(i)]] = predict[i].numpy()

        max_prob = {
            k: v for k,
            v in sorted(
                max_prob.items(),
                key=lambda item: item[1])}

        max_prob = list(max_prob.items())

        max_prob_value = max_prob[-1]  # 最长的contig

        return max_prob_value[0], max_prob_value[1]


def main():
    img_path = "/home/jovyan/datasets/error_classify/GSE71831"
    json_path = '/home/jovyan/Error-Classify/EfficientNetV2/class_indices.json'
    model_weight_path = "/home/jovyan/Error-Classify/EfficientNetV2/pre-weights/2-train-best.pth"

    temp = BulkInfer(img_path, json_path, model_weight_path)
    temp.bulk_infer()


if __name__ == "__main__":
    main()
