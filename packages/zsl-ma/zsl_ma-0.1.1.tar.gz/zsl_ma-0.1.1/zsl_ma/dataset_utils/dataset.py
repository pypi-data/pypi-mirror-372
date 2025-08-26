import os
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


class FactorLabelMapper:
    def __init__(self, label_maps_dir, class_to_label_name="classes_to_label.txt"):
        """
        初始化映射管理器
        :param label_maps_dir: 标签映射文件所在目录（包含classes_to_label.txt等）
        """
        # 固定故障类型映射（No为0，B为1，IR为2，OR为3）

        self.fault_type_to_idx = {
            'No': 0,
            'B': 1,
            'IR': 2,
            'OR': 3
        }
        self.idx_to_fault_type = {v: k for k, v in self.fault_type_to_idx.items()}


        # 1. 加载基础映射（class与label的映射）
        self.class_to_label = self._load_class_to_label(
            os.path.join(label_maps_dir, class_to_label_name)
        )
        self.classes = list(self.class_to_label.keys())  # 类别名称列表
        self.label_to_class = {v: k for k, v in self.class_to_label.items()}

        # 2. 解析三因子与class的关联
        self.class_to_factors = self._parse_class_factors()  # 字典变量：class→三因子

        # 3. 构建工况和故障程度到整数的映射
        self.condition_to_idx, self.severity_to_idx = self._build_other_factor_maps()
        self.idx_to_condition = {v: k for k, v in self.condition_to_idx.items()}
        self.idx_to_severity = {v: k for k, v in self.severity_to_idx.items()}

        # 预构建三因子整数编码到label的快速查询表（加速批量处理）
        self._build_batch_lookup_table()

    def _load_class_to_label(self, txt_path):
        """加载class到label的映射（从classes_to_label.txt）"""
        class_to_label = {}
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cls, label = line.split(',')
                class_to_label[cls] = int(label)
        return class_to_label

    def _parse_class_factors(self):
        """从class名称解析三因子（condition, fault_type, severity）"""
        class_to_factors = {}
        for cls in self.class_to_label.keys():
            parts = cls.split('-')
            if len(parts) == 2 and parts[1] == 'No':
                # 正常样本：工况-No → 故障程度固定为'0'
                condition = parts[0]
                fault_type = 'No'
                severity = '0'
            elif len(parts) == 3:
                # 故障样本：工况-故障类型-程度
                condition, fault_type, severity = parts
                # 验证故障类型是否合法
                if fault_type not in self.fault_type_to_idx:
                    raise ValueError(f"无效的故障类型：{fault_type}，允许的值为{list(self.fault_type_to_idx.keys())}")
            else:
                raise ValueError(f"无效的class格式：{cls}，需符合'工况-No'或'工况-类型-程度'")
            class_to_factors[cls] = (condition, fault_type, severity)
        return class_to_factors

    def _build_other_factor_maps(self):
        """自动收集工况和故障程度的可能值，构建到整数的映射"""
        conditions = set()
        severities = set()

        for factors in self.class_to_factors.values():
            conditions.add(factors[0])
            severities.add(factors[2])

        # 排序后映射为整数（确保一致性）
        condition_to_idx = {v: i for i, v in enumerate(sorted(conditions))}
        severity_to_idx = {v: i for i, v in enumerate(sorted(severities))}

        return condition_to_idx, severity_to_idx

    def _build_batch_lookup_table(self):
        """构建三因子整数编码到label的查询表，加速批量处理"""
        self.lookup_table = {}
        # 遍历所有可能的三因子组合
        for cond_idx in self.idx_to_condition:
            for fault_idx in self.idx_to_fault_type:
                for sev_idx in self.idx_to_severity:
                    try:
                        label = self.get_label_from_indices(cond_idx, fault_idx, sev_idx)
                        self.lookup_table[(cond_idx, fault_idx, sev_idx)] = label
                    except:
                        # 跳过无效组合
                        continue

    def get_labels_from_indices_batch(self, indices_tensor):
        """
        批量从三因子整数编码获取label
        :param indices_tensor: 形状为[batch, 3]的张量，每行包含(cond_idx, fault_idx, sev_idx)
        :return: 形状为[batch]的张量，包含对应的label
        """
        # 确保输入是张量
        if  isinstance(indices_tensor, torch.Tensor):
            indices_tensor = indices_tensor.cpu().numpy()
        # else:
        #     indices_np = indices_tensor

        # 转换为CPU处理（字典查询需在CPU上进行）

        # 批量查询
        labels = []
        for idx in indices_tensor:
            cond_idx, fault_idx, sev_idx = idx
            key = (int(cond_idx), int(fault_idx), int(sev_idx))
            labels.append(self.lookup_table.get(key, 6))

        # 转换为张量并返回原设备
        return labels

    # ------------------------------
    # class与三因子转换
    # ------------------------------
    def get_factors_from_class(self, cls):
        """从class获取三因子原始值"""
        if cls not in self.class_to_factors:
            raise ValueError(f"未知的class：{cls}")
        return self.class_to_factors[cls]

    def get_class_from_factors(self, condition, fault_type, severity):
        """从三因子原始值获取class名称"""
        if fault_type == 'No':
            return f"{condition}-{fault_type}"
        return f"{condition}-{fault_type}-{severity}"

    # ------------------------------
    # class与label转换
    # ------------------------------
    def get_label_from_class(self, cls):
        """从class获取label"""
        return self.class_to_label.get(cls, 6)

    def get_class_from_label(self, label):
        """从label获取class"""
        return self.label_to_class.get(label, "")

    # ------------------------------
    # 三因子与整数编码转换
    # ------------------------------
    def get_indices_from_factors(self, condition, fault_type, severity):
        """从三因子原始值获取整数编码"""
        return (
            self.condition_to_idx[condition],
            self.fault_type_to_idx[fault_type],
            self.severity_to_idx[severity]
        )

    def get_factors_from_indices(self, cond_idx, fault_idx, sev_idx):
        """从整数编码获取三因子原始值"""
        return (
            self.idx_to_condition[cond_idx],
            self.idx_to_fault_type[fault_idx],
            self.idx_to_severity[sev_idx]
        )

    # ------------------------------
    # label与三因子转换
    # ------------------------------
    def get_factors_from_label(self, label):
        """从label获取三因子的原始值（如0→('0', 'No', '0')）"""
        cls = self.get_class_from_label(label)
        if not cls:
            raise ValueError(f"未知的label：{label}")
        return self.get_factors_from_class(cls)

    def get_indices_from_label(self, label):
        """从label获取三因子的整数编码（如0→(0, 0, 0)）"""
        condition, fault_type, severity = self.get_factors_from_label(label)
        return (
            self.condition_to_idx[condition],
            self.fault_type_to_idx[fault_type],
            self.severity_to_idx[severity]
        )

    def get_label_from_factors(self, condition, fault_type, severity):
        """从三因子原始值获取label（如('0', 'B', '007')→7）"""
        cls = self.get_class_from_factors(condition, fault_type, severity)
        return self.get_label_from_class(cls)

    def get_label_from_indices(self, cond_idx, fault_idx, sev_idx):
        """从三因子整数编码获取label（如(0, 1, 1)→7）"""
        condition = self.idx_to_condition[cond_idx]
        fault_type = self.idx_to_fault_type[fault_idx]
        severity = self.idx_to_severity[sev_idx]
        return self.get_label_from_factors(condition, fault_type, severity)

    # ------------------------------
    # 辅助方法
    # ------------------------------
    def print_mappings(self):
        """打印所有映射关系（调试用）"""
        print("=== class与label映射 ===")
        for cls, label in self.class_to_label.items():
            print(f"{cls} → {label}")

        print("\n=== 三因子与整数编码映射 ===")
        print("工况：", self.condition_to_idx)
        print("故障类型：", self.fault_type_to_idx)
        print("故障程度：", self.severity_to_idx)


class CustomDataset(Dataset):
    def __init__(self, root_dir, mode, transform):
        self.img_dir = Path(root_dir)/mode
        self.transform = transform
        self.images = [f for f in os.listdir(self.img_dir) if f.endswith(('.bmp', '.jpg', '.png'))]
        self.maper = FactorLabelMapper(root_dir)
    #     self.classes_to_label, self.label_to_classes, self.classes = load_label_mappings(root_dir)
    #     self.condition_map, self.fault_type_map, self.severity_map = read_all_label_maps(os.path.join(root_dir, 'label_maps.txt'))
    #
    #     # 如果没有提供class_to_label字典，我们在这里创建它
    #     if not self.classes_to_label:
    #         self._create_class_to_label_mapping()
    #         self.label_to_classes = {value: key for key, value in self.classes_to_label.items()}
    #
    # def _create_class_to_label_mapping(self):
    #     # 假设类别是从0开始编号的连续整数
    #     self.classes = sorted(file for file in self.images)
    #     self.class_to_label = {cls: i for i, cls in enumerate(self.classes)}

    # def get_class_to_label(self):
    #     return self.classes_to_label

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # 获取图片路径
        image_path = os.path.join(self.img_dir, self.images[idx])
        # 打开图片并转换为RGB格式
        image = Image.open(image_path)
        # 如果有变换，则进行变换
        if self.transform:
            image = self.transform(image)

        # 提取文件名中的类别
        base_filename = os.path.splitext(self.images[idx])[0]
        class_name = base_filename.split('_')[0]
        label = self.maper.get_label_from_class(class_name)
        indices = self.maper.get_indices_from_label(label)
        # 将类别转换为标签
        # label = self.class_to_label[class_name]
        # condition, fault_type, severity = encode_new_filename(class_name, self.condition_map, self.fault_type_map, self.severity_map)

        return image, indices, label


def create_dataloaders(data_dir, batch_size, transform=transforms.ToTensor(), num_workers=0,
                       val_shuffle=False):
    # 训练集数据加载器
    train_dataset = CustomDataset(root_dir=data_dir, mode='train',transform=transform)
    # 初始化验证集Dataset

    validation_dataset = CustomDataset(root_dir=data_dir, mode='val', transform=transform)

    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers)
    val_loader = DataLoader(dataset=validation_dataset, batch_size=batch_size, shuffle=val_shuffle)
    return train_loader, val_loader


if __name__ == '__main__':
    print()
    transform = transforms.Compose([transforms.ToTensor()])
    train_data = CustomDataset(root_dir=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\data\seen',
                               mode='val',
                               transform=transform)
    data_loader = DataLoader(train_data, batch_size=64, shuffle=False)

    for img , indices, label in data_loader:
        print(type(indices))
    # maper = FactorLabelMapper(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\data\seen')
    # print()