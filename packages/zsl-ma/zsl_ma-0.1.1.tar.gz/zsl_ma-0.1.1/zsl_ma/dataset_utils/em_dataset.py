import os
import random
import re
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.dataset import FactorLabelMapper


class AttributeImageDataset(Dataset):
    def __init__(self, root_dir, mode, attr_dir, transform=None):
        self.img_dir = Path(root_dir) / mode
        self.transform = transform
        self.images = [f for f in os.listdir(self.img_dir) if f.endswith(('.bmp', '.jpg', '.png'))]
        self.maper = FactorLabelMapper(root_dir)

        self.attr_dir = attr_dir
        self.classes = self.maper.classes

        self.attr_dict = []
        for cls_name in self.classes:
            npy_path = os.path.join(self.attr_dir, f"{cls_name}.npy")
            self.attr_dict.append(np.load(npy_path, allow_pickle=True))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = os.path.join(self.img_dir, self.images[idx])

        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        base_filename = os.path.splitext(self.images[idx])[0]
        class_name = base_filename.split('_')[0]
        label = self.maper.get_label_from_class(class_name)

        # 获取对应的语义属性向量
        # attr_vector = self.attr_dict[class_name]

        return image, label  # torch.tensor(attr_vector, dtype=torch.float32)


def load_class_to_label(txt_path):
    class_to_label = {}
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cls, label = line.split(',')
            class_to_label[cls] = int(label)
    return class_to_label

class ImageSemanticDataset(Dataset):
    def __init__(self, root_dir, semantic_path, transform, split="train", neg_ratio=1):

        self.img_dir = Path(root_dir) / split
        self.transform = transform
        self.neg_ratio = neg_ratio
        # self.maper = load_class_to_label(os.path.join(root_dir, 'zsl_classes.txt'))

        self.class_to_label = load_class_to_label(os.path.join(root_dir, 'zsl_classes.txt'))
        self.semantic_attrs = []
        self.classes = list(self.class_to_label.keys())
        self.semantic_path = semantic_path

        for cls_name in self.classes:
            npy_path = os.path.join(self.semantic_path, f"{cls_name}.npy")
            self.semantic_attrs.append(np.load(npy_path, allow_pickle=True))

        # 2. 收集图片路径及对应的类别（核心：统一提取B-XXX作为类别）
        self.img_info = []  # 元素格式：(img_path, class_id)，class_id如"B-007"
        for img_name in os.listdir(self.img_dir):
            if not img_name.endswith(("jpg", "jpeg", "png")):
                continue
            # 解析文件名，提取类别（忽略开头数字，兼容两种格式）
            try:
                # 示例1："0-No_1.jpg" → 前缀为"0-No" → 分割为["0", "No"] → 取"No"
                # 示例2："0-B-007_0.jpg" → 前缀为"0-B-007" → 分割为["0", "B", "007"] → 取"B-007"
                prefix_part = img_name.split("_")[0]  # 提取"0-No"或"0-B-007"
                parts = prefix_part.split("-")  # 按"-"分割为列表

                # 至少需要2部分（如"0-No"），否则格式错误
                if len(parts) < 2:
                    raise ValueError(f"文件名格式错误（至少需'数字-类别'两部分）：{img_name}")

                # 提取类别：取分割后第2部分及以后（兼容2部分和3+部分）
                # 2部分时（如["0", "No"]）→ 取["No"] → 拼接为"No"
                # 3+部分时（如["0", "B", "007"]）→ 取["B", "007"] → 拼接为"B-007"
                class_id = "-".join(parts[1:])

                # 验证类别是否在语义映射中
                if class_id not in self.class_to_label:
                    raise ValueError(f"类别 {class_id} 无对应语义属性（文件：{img_name}）")

                self.img_info.append((os.path.join(self.img_dir, img_name), class_id))
            except Exception as e:
                raise RuntimeError(f"解析文件 {img_name} 失败：{str(e)}")

    def __len__(self):
        # 总样本数 = 图片数量 × (1个正样本 + neg_ratio个负样本)
        return len(self.img_info) * (1 + self.neg_ratio)

    def __getitem__(self, idx):
        # 1. 确定当前样本对应的图片和正负标签
        img_idx = idx // (1 + self.neg_ratio)  # 原始图片索引
        is_positive = (idx % (1 + self.neg_ratio)) == 0  # 第0个为正样本，其余为负样本

        # 2. 获取图片特征x1
        img_path, class_id = self.img_info[img_idx]
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)

        # 3. 获取语义属性x2（根据正负样本选择类别）
        # label = self.class_to_label[class_id]
        if is_positive:
            # 正样本：x2为当前类别对应的语义属性
            sem_idx = self.class_to_label[class_id]
            x2 = torch.tensor(self.semantic_attrs[sem_idx], dtype=torch.float32)  # (M,)
            y = torch.tensor(1.0, dtype=torch.float32)
        else:
            # 负样本：x2为其他类别对应的语义属性（随机选择）
            other_classes = [cls for cls in self.classes if cls != class_id]
            neg_class = random.choice(other_classes)
            sem_idx = self.class_to_label[neg_class]
            x2 = torch.tensor(self.semantic_attrs[sem_idx], dtype=torch.float32)  # (M,)
            y = torch.tensor(-1.0, dtype=torch.float32)

        return img, x2, y


if __name__ == '__main__':
    print()
    # data = AttributeImageDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\单文件夹格式', 'train',
    #                              r'D:\Code\2-ZSL\1-output\特征解耦结果\best-3\class_mean_features\fault_combined')
    # print(len(data))
    # data = ImageSemanticDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\data\seen',
    #                             r'D:\Code\2-ZSL\1-output\特征解耦结果\exp\class_mean_features\fault_combined',
    #                             split='val',
    #                             transform=transforms.ToTensor(),
    #                             neg_ratio=0)
    # dataloader = DataLoader(data, batch_size=10, shuffle=True)
    # for i,(img, x2, y) in enumerate(dataloader):
    #     print(y)
