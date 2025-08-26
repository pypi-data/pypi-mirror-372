import torch
import torch.nn as nn
import torch.nn.functional as F


class FeatureNormProjection(nn.Module):
    """特征归一化投影层，增强特征稳定性"""

    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.projection = nn.Sequential(
            nn.Linear(in_dim, out_dim),
            nn.BatchNorm1d(out_dim),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        x = self.projection(x)
        # L2归一化增强特征稳定性
        return F.normalize(x, p=2, dim=1)


class DisentangledModel(nn.Module):
    """监督学习解耦网络，确保特征空间独立且同类特征相关性强"""

    def __init__(self, attribute_dims=None, ortho_weight=2500, intra_corr_weight=0.5):
        super().__init__()
        if attribute_dims is None:
            attribute_dims = [3, 4, 4]  # 假设3个属性：工况、故障类型、严重程度
        self.num_attributes = len(attribute_dims)
        self.ortho_weight = ortho_weight
        self.intra_corr_weight = intra_corr_weight

        # --------------------- 共享特征提取层 ---------------------
        self.shared_backbone = nn.Sequential(
            nn.Conv2d(3, 32, 3, 1, 1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            ConvResBlock(32, 64, stride=2),
            ConvResBlock(64, 64, stride=2),
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),
            ConvResBlock(64, 128, stride=2),
            ResBlock(128),
            ConvResBlock(128, 128, stride=2),
            ResBlock(128)
        )

        # --------------------- 解耦分支层 ---------------------
        # 添加特征归一化层增强同类特征相关性
        self.branches = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(128, 128, 3, 1, 1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(128, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                FeatureNormProjection(256, 256)  # 添加特征归一化
            ) for _ in range(self.num_attributes)
        ])

        # --------------------- 解耦分类器 ---------------------
        self.classifiers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(256, dim),
                nn.LogSoftmax(dim=1)
            ) for dim in attribute_dims
        ])

    def forward(self, x):
        shared_features = self.shared_backbone(x)
        branch_outputs = []
        for branch in self.branches:
            branch_outputs.append(branch(shared_features))
        predictions = [cls(feat) for cls, feat in zip(self.classifiers, branch_outputs)]
        return predictions, branch_outputs

    def orthogonal_regularization(self, features):
        """改进的正交正则化：确保不同属性特征空间解耦"""
        reg_loss = 0.0
        num_features = len(features)

        # 归一化特征向量
        normalized_features = [F.normalize(feat, p=2, dim=1) for feat in features]

        # 计算不同属性特征间的正交性
        for i in range(num_features):
            for j in range(i + 1, num_features):
                # 计算余弦相似度
                cos_sim = torch.sum(normalized_features[i] * normalized_features[j], dim=1)
                reg_loss += torch.mean(cos_sim ** 2)

        return self.ortho_weight * reg_loss

    def intra_attribute_correlation(self, features, attribute_labels):
        """
        增强同类特征相关性损失 - 特定于每个属性
        确保相同属性(工况/故障类型/严重程度)的同类样本特征相似
        """
        intra_loss = 0.0

        # 遍历每个属性分支
        for attr_idx, feat in enumerate(features):
            # 获取当前属性的标签
            attr_labels = attribute_labels[:, attr_idx]
            unique_labels = torch.unique(attr_labels)

            for label in unique_labels:
                # 提取同类样本特征
                class_mask = (attr_labels == label)
                class_feat = feat[class_mask]

                if class_feat.size(0) < 2:  # 需要至少2个样本才能计算
                    continue

                # 计算类内特征均值
                class_mean = class_feat.mean(dim=0, keepdim=True)

                # 计算类内特征与均值的余弦相似度
                norm_feat = F.normalize(class_feat, p=2, dim=1)
                norm_mean = F.normalize(class_mean, p=2, dim=1)

                # 最大化类内相似度 (1 - 余弦距离)
                intra_sim = torch.sum(norm_feat * norm_mean, dim=1)
                intra_loss += 1.0 - torch.mean(intra_sim)

        return self.intra_corr_weight * intra_loss


# 保持原有的ConvResBlock和ResBlock不变
class ConvResBlock(nn.Module):
    """卷积残差块"""

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels)
        )
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = self.conv(x) + self.shortcut(x)
        return F.relu(out, inplace=True)


class ResBlock(nn.Module):
    """标准残差块"""

    def __init__(self, channels):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(channels)
        )

    def forward(self, x):
        return F.relu(x + self.conv(x), inplace=True)