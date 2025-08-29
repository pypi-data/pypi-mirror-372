import torch
import torch.nn as nn


class ContrastiveLoss(nn.Module):
    """
    对比损失函数（无权重参数）：
    - 当target=1时，x1和x2属于同一类别，应最小化它们之间的距离
    - 当target=-1时，x1和x2属于不同类别，应最大化它们之间的距离（至少保持margin）
    """

    def __init__(self, margin=10.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin  # 不同类别样本间的最小距离阈值

    def forward(self, x1, x2, target):
        """
        参数:
            x1: 第一个样本的特征向量，形状为(batch_size, feature_dim)
            x2: 第二个样本的特征向量，形状为(batch_size, feature_dim)
            target: 标签，1表示同一类别，-1表示不同类别，形状为(batch_size,)
        返回:
            计算得到的损失值（无额外权重）
        """
        # 计算x1和x2之间的欧几里得距离平方
        dist_sq = torch.sum((x1 - x2) ** 2, dim=1)

        # 同一类别损失：距离应尽可能小
        same_class_mask = (target == 1).float()
        same_class_loss = torch.mean(dist_sq * same_class_mask)

        # 不同类别损失：距离应至少为margin，否则产生损失
        diff_class_mask = (target == -1).float()
        diff_class_loss = torch.mean(
            torch.clamp(self.margin - dist_sq, min=0.0) * diff_class_mask
        )

        # 总损失（直接返回损失和，无权重参数）
        total_loss = same_class_loss + diff_class_loss
        return total_loss