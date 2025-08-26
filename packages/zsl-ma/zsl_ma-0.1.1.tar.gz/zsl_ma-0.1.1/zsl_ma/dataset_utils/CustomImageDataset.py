import os
import random
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.FactorLabelMapper import FactorLabelMapper, load_class_list


class ImageClassificationDataset(Dataset):
    """
    自定义数据集类
    """

    def __init__(self, root_dir, transform=None, train_class=None, pred_class=None, mode='train'):
        """
        初始化数据集

        参数:
            root_dir (str): 数据集根目录路径
            transform (callable, optional): 应用于图像的变换/增强
            target_transform (callable, optional): 应用于标签的变换
            mode (str): 数据集模式，如 'train', 'val', 'test'
        """
        self.root_dir = Path(root_dir)
        self.mode = mode
        self.transform = transform

        # 构建数据路径
        self.data_dir = self.root_dir / mode

        # 确保目录存在
        if not self.data_dir.exists():
            raise ValueError(f"目录不存在: {self.data_dir}")

        self.pred_class_path = pred_class if pred_class is not None else train_class
        # 1. 初始化预测类别映射器（构建class_to_idx的基准）
        self.pred_mapper = FactorLabelMapper(
            data_dir=self.root_dir,  # 当pred_class_path不存在时，从root_dir子文件夹提取预测类别
            class_list_path=self.pred_class_path
        )
        self.classes = self.pred_mapper.classes  # 实际预测的所有类别
        self.class_to_idx = self.pred_mapper.class_to_idx  # 基于预测类别构建的映射

        # 2. 初始化训练类别映射器
        self.train_mapper = FactorLabelMapper(
            data_dir=self.data_dir,  # 当train_class不存在时，从当前模式目录提取训练类别
            class_list_path=train_class
        )
        self.train_classes = self.train_mapper.classes  # 训练使用的类别

        # 3. 验证：训练类别必须完全包含在预测类别中
        for cls in self.train_classes:
            if cls not in self.classes:
                raise ValueError(f"训练类别 '{cls}' 不在预测类别列表中，请确保预测类别包含所有训练类别")



        # # 获取所有类别文件夹
        # self.maper = FactorLabelMapper(self.data_dir, train_class)
        # self.classes = self.maper.classes
        # if not self.classes:
        #     raise ValueError(f"在 {self.data_dir} 中未找到任何类别文件夹")
        #
        # # 创建类别到索引的映射
        # self.class_to_idx = self.maper.class_to_idx

        # 收集所有图像路径和对应的标签
        self.image_paths = []
        self.labels = []

        for class_name in self.train_classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]

            # 获取此类别的所有图像文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            for ext in image_extensions:
                for img_path in class_dir.glob(f'*{ext}'):
                    self.image_paths.append(img_path)
                    self.labels.append(class_idx)

        if not self.image_paths:
            raise ValueError(f"在 {self.data_dir} 中未找到任何图像文件")

    def __len__(self):
        """返回数据集中的样本数量"""
        return len(self.image_paths)

    def __getitem__(self, idx):
        """
        获取单个样本

        参数:
            idx (int): 样本索引

        返回:
            tuple: (图像, 标签)
        """
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # 加载图像
        image = Image.open(img_path).convert('RGB')  # 确保图像是RGB格式

        # 应用变换
        if self.transform:
            image = self.transform(image)

        return image, label

    def get_class_distribution(self):
        """返回每个类别的样本数量"""
        class_counts = {cls: 0 for cls in self.classes}
        for label in self.labels:
            class_name = self.classes[label]
            class_counts[class_name] += 1
        return class_counts

    def get_class_num(self):
        return len(self.classes)


class FeatureDecouplingDataset(Dataset):
    def __init__(self, root_dir, transform=None, train_class=None, mode='train', factor_index_map_path=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.data_dir = self.root_dir / mode

        self.maper = FactorLabelMapper(self.data_dir, train_class, parse_factors=True,
                                       build_lookup_table=True, factor_index_map_path=factor_index_map_path)

        self.classes = self.maper.classes

        # 创建类别到索引的映射
        self.class_to_idx = self.maper.class_to_idx

        # 收集所有图像路径和对应的标签
        self.image_paths = []
        self.labels = []
        self.indices = []

        for class_name in self.classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]

            # 获取此类别的所有图像文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            for ext in image_extensions:
                for img_path in class_dir.glob(f'*{ext}'):
                    self.image_paths.append(img_path)
                    self.labels.append(class_idx)
                    self.indices.append(
                        self.maper.get_indices_from_factors(self.maper.get_factors_from_class(class_name)))

        if not self.image_paths:
            raise ValueError(f"在 {self.data_dir} 中未找到任何图像文件")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # 加载图像
        image = Image.open(img_path).convert('RGB')  # 确保图像是RGB格式

        # 应用变换
        if self.transform:
            image = self.transform(image)
        indices = self.indices[idx]

        return image, indices, label


class EmbeddingDataset(Dataset):
    """用于嵌入学习任务的数据集类"""

    def __init__(self, root_dir, semantic_path, classes, train_class, transform=None, mode='train', neg_ratio=1):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.data_dir = self.root_dir / mode
        self.neg_ratio = neg_ratio
        self.semantic_path = semantic_path

        self.data_class = load_class_list(train_class)
        self.classes = load_class_list(classes)
        self.class_to_idx: Dict[str, int] = {cls: idx for idx, cls in enumerate(self.classes)}  # 类别→索引
        self.idx_to_class: Dict[int, str] = {idx: cls for cls, idx in self.class_to_idx.items()}  # 索引→类别（反向映射）

        # 收集所有图像路径和对应的标签
        self.image_info = []
        # self.labels = []
        for class_name in self.data_class:
            class_dir = self.data_dir / class_name
            prefix_part = class_name.split("_")[0]  # 提取"0-No"或"0-B-007"
            parts = prefix_part.split("-")  # 按"-"分割为列表
            class_id = "-".join(parts[1:])
            # class_idx = self.class_to_idx[class_id]

            # 获取此类别的所有图像文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            for ext in image_extensions:
                for img_path in class_dir.glob(f'*{ext}'):
                    self.image_info.append((img_path, class_id))
                    # self.labels.append(class_idx)

        if not self.image_info:
            raise ValueError(f"在 {self.data_dir} 中未找到任何图像文件")

        self.semantic_attributes = []
        for cls_name in self.classes:
            npy_path = os.path.join(self.semantic_path, f"{cls_name}.npy")
            self.semantic_attributes.append(np.load(npy_path, allow_pickle=True))

    def __len__(self):
        # 总样本数 = 图片数量 × (1个正样本 + neg_ratio个负样本)
        return len(self.image_info) * (1 + self.neg_ratio)

    def __getitem__(self, idx):
        # 1. 确定当前样本对应的图片和正负标签
        img_idx = idx // (1 + self.neg_ratio)  # 原始图片索引
        is_positive = (idx % (1 + self.neg_ratio)) == 0  # 第0个为正样本，其余为负样本

        img_path, class_id = self.image_info[img_idx]
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)

        if is_positive:
            sem_idx = self.class_to_idx[class_id]
            x2 = torch.tensor(self.semantic_attributes[sem_idx], dtype=torch.float32)
            target = torch.tensor(1.0, dtype=torch.float32)
        else:
            other_classes = [cls for cls in self.classes if cls != class_id]
            neg_class = random.choice(other_classes)
            sem_idx = self.class_to_idx[neg_class]
            x2 = torch.tensor(self.semantic_attributes[sem_idx], dtype=torch.float32)  # (M,)
            target = torch.tensor(-1.0, dtype=torch.float32)

        return img, x2, target


if __name__ == '__main__':
    print()
    data = EmbeddingDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen',
                            r'D:\Code\2-ZSL\1-output\特征解耦结果\exp\class_mean_features\fault_combined',
                            train_class=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\train_class.txt',
                            transform=transforms.ToTensor(),
                            mode='val',
                            classes=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\zsl_classes.txt',
                            )
    dataloader = DataLoader(data, batch_size=10, shuffle=False)
    # for img, x2, target in dataloader:
    #     print(target)
