import torch
from torch import nn
import torch.nn.functional as F


# 定义残差块
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.res = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )

    def forward(self, x):
        residual = x
        out = self.res(x)
        return out + residual


class ConvResBlock(nn.Module):
    """严格匹配图示尺寸的Conv-Res-Block"""

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        # 主分支卷积序列
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, stride, 1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1),
            nn.BatchNorm2d(out_channels)
        )

        # 残差捷径
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride),
                nn.BatchNorm2d(out_channels)
            )

        # 将ReLU作为模块成员
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        return self.relu(self.conv(x) + self.shortcut(x))  # 使用模块定义的ReLU


class ResBlock(nn.Module):
    """保持尺寸不变的Res-Block"""

    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, 1, 1),
            nn.BatchNorm2d(channels)
        )

    def forward(self, x):
        return x + self.block(x)


class DisentangledModel(nn.Module):
    """监督学习解耦网络，确保三个特征空间独立"""

    def __init__(self, class_dims, attribute_dim=64, ortho_weight=2, reg_method='euclidean', margin=10.0):
        super().__init__()
        self.num_attributes = len(class_dims)
        self.ortho_weight = ortho_weight
        self.reg_method = reg_method  # 正则化方法选择
        self.margin = margin

        # --------------------- 共享特征提取层 ---------------------
        self.shared_backbone = nn.Sequential(
            # 阶段A: 初始卷积
            nn.Conv2d(3, 32, 3, 1, 1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            # 阶段B1-B2: 下采样
            ConvResBlock(32, 64, stride=2),
            ConvResBlock(64, 64, stride=2),

            # 阶段C3: 残差块
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),

            # 阶段B3: 下采样
            ConvResBlock(64, 128, stride=2),

            # 阶段C4: 残差块
            ResBlock(128),

            # 阶段B4: 下采样
            ConvResBlock(128, 128, stride=2),

            # 阶段C5: 残差块
            ResBlock(128)
        )

        # --------------------- 解耦分支层 ---------------------
        # 每个属性独立的特征提取路径
        self.branches = nn.ModuleList([
            nn.Sequential(
                # 独立的下采样路径
                nn.Conv2d(128, 128, 3, 1, 1),
                nn.ReLU(inplace=True),
                nn.Flatten(),

                # 特征变换层
                nn.Linear(2048, 1024),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),

                # 正交投影层
                nn.Linear(1024, attribute_dim),
                nn.ReLU(inplace=True)
            ) for _ in range(self.num_attributes)
        ])

        # --------------------- 解耦分类器 ---------------------
        self.classifiers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(attribute_dim, dim),
                nn.LogSoftmax(dim=1)  # 适用于分类任务
            ) for dim in class_dims
        ])

    def forward(self, x):
        # 共享特征提取
        shared_features = self.shared_backbone(x)  # [B, 128, 4, 4]

        # 独立分支处理
        branch_outputs = []
        for branch in self.branches:
            branch_outputs.append(branch(shared_features))

        # 分类预测
        predictions = [cls(feat) for cls, feat in zip(self.classifiers, branch_outputs)]

        return predictions, branch_outputs

    def orthogonal_regularization(self, features, labels):
        """
        特征解耦正则化 - 根据选择的reg_method调用不同的实现
        """
        if self.reg_method == 'cosine':
            return self._cosine_regularization(features, labels)
        elif self.reg_method == 'euclidean':
            return self._euclidean_regularization(features, labels)
        elif self.reg_method == 'center':
            return self._center_regularization(features, labels)
        elif self.reg_method == 'inter_branch':
            return self._inter_branch_regularization(features)
        else:
            raise ValueError(f"Unknown regularization method: {self.reg_method}")

    def _cosine_regularization(self, features, labels):
        """
        基于余弦相似度的正则化（原始方法）：
        - 同一属性内，标签相同的样本特征尽可能相近
        - 同一属性内，标签不同的样本特征尽可能远离
        """
        batch_size = features.size(0)
        if batch_size <= 1:
            return 0.0

        # 特征L2归一化，使点积等价于余弦相似度
        normalized_feats = F.normalize(features, p=2, dim=1)

        # 计算所有样本对的相似度矩阵
        sim_matrix = torch.matmul(normalized_feats, normalized_feats.T)

        # 创建标签匹配矩阵
        label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
        mask = 1 - torch.eye(batch_size, device=features.device)
        label_eq_matrix = label_eq_matrix * mask
        label_ne_matrix = (1 - label_eq_matrix) * mask

        # 同标签损失：相似度应接近1
        same_label_loss = torch.mean((1 - sim_matrix) * label_eq_matrix)

        # 异标签损失：相似度应接近-1
        diff_label_loss = torch.mean((1 + sim_matrix) * label_ne_matrix)

        return self.ortho_weight * (same_label_loss + diff_label_loss)

    def _euclidean_regularization(self, features, labels):
        """
        基于欧几里得距离的正则化：
        - 同一属性内，标签相同的样本特征距离尽可能小
        - 同一属性内，标签不同的样本特征距离尽可能大
        """
        batch_size = features.size(0)
        if batch_size <= 1:
            return 0.0

        # 计算所有样本对之间的欧几里得距离平方
        norms = torch.sum(features ** 2, dim=1)
        dist_matrix = norms.unsqueeze(0) + norms.unsqueeze(1) - 2 * torch.matmul(features, features.T)

        # 创建标签匹配矩阵
        label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
        mask = 1 - torch.eye(batch_size, device=features.device)
        label_eq_matrix = label_eq_matrix * mask
        label_ne_matrix = (1 - label_eq_matrix) * mask

        # 同标签损失：距离应接近0
        same_label_loss = torch.mean(dist_matrix * label_eq_matrix)

        # 异标签损失：距离应尽可能大，使用边际损失
        # margin = 10.0
        diff_label_loss = torch.mean(torch.clamp(self.margin - dist_matrix, min=0) * label_ne_matrix)

        return self.ortho_weight * (same_label_loss + diff_label_loss)

    def _center_regularization(self, features, labels):
        """
        基于类别中心的正则化：
        - 同一属性内，样本特征尽可能接近其类别中心
        - 同一属性内，不同类别的中心尽可能远离
        """
        unique_labels = torch.unique(labels)
        if len(unique_labels) <= 1:
            return 0.0

        # 计算每个类别的中心
        centers = []
        for label in unique_labels:
            mask = (labels == label)
            if torch.sum(mask) > 0:
                center = torch.mean(features[mask], dim=0)
                centers.append(center)

        if len(centers) <= 1:
            return 0.0

        centers = torch.stack(centers)

        # 类内损失：样本到其类别中心的距离
        intra_loss = 0.0
        for i, label in enumerate(unique_labels):
            mask = (labels == label)
            if torch.sum(mask) > 0:
                class_features = features[mask]
                center = centers[i]
                distances = torch.norm(class_features - center, dim=1)
                intra_loss += torch.mean(distances)

        intra_loss /= len(unique_labels)

        # 类间损失：类别中心之间的距离
        inter_loss = 0.0
        num_pairs = 0
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                distance = torch.norm(centers[i] - centers[j])
                margin = 5.0
                inter_loss += torch.clamp(margin - distance, min=0)
                num_pairs += 1

        if num_pairs > 0:
            inter_loss /= num_pairs
        else:
            inter_loss = 0.0

        return self.ortho_weight * (intra_loss + inter_loss)

    def _inter_branch_regularization(self, features_list):
        """
        分支间正交正则化：
        - 确保不同分支提取的特征相互正交
        - 不依赖于标签信息
        """
        reg_loss = 0.0
        num_branches = len(features_list)

        for i in range(num_branches):
            for j in range(i + 1, num_branches):
                # 归一化特征
                feat_i = F.normalize(features_list[i], p=2, dim=1)
                feat_j = F.normalize(features_list[j], p=2, dim=1)

                # 计算相关性矩阵
                correlation = torch.matmul(feat_i.T, feat_j)

                # 计算非对角线元素的和（希望它们接近0）
                reg_loss += torch.sum(correlation ** 2) - torch.sum(torch.diag(correlation) ** 2)

        return self.ortho_weight * reg_loss / (num_branches * (num_branches - 1) / 2)



# class DisentangledModel(nn.Module):
#     """监督学习解耦网络，确保三个特征空间独立"""
#
#     def __init__(self, class_dims, attribute_dim=64, ortho_weight=2):
#         super().__init__()
#         # if attribute_dims is None:
#         #     attribute_dims = [3, 4, 4]
#         self.num_attributes = len(class_dims)
#
#         # --------------------- 共享特征提取层 ---------------------
#         self.shared_backbone = nn.Sequential(
#             # 阶段A: 初始卷积
#             nn.Conv2d(3, 32, 3, 1, 1),
#             nn.BatchNorm2d(32),
#             nn.ReLU(inplace=True),
#
#             # 阶段B1-B2: 下采样
#             ConvResBlock(32, 64, stride=2),
#             ConvResBlock(64, 64, stride=2),
#
#             # 阶段C3: 残差块
#             ResBlock(64),
#             ResBlock(64),
#             ResBlock(64),
#
#             # 阶段B3: 下采样
#             ConvResBlock(64, 128, stride=2),
#
#             # 阶段C4: 残差块
#             ResBlock(128),
#
#             # 阶段B4: 下采样
#             ConvResBlock(128, 128, stride=2),
#
#             # 阶段C5: 残差块
#             ResBlock(128)
#         )
#
#         # --------------------- 解耦分支层 ---------------------
#         # 每个属性独立的特征提取路径
#         self.branches = nn.ModuleList([
#             nn.Sequential(
#                 # 独立的下采样路径
#                 nn.Conv2d(128, 128, 3, 1, 1),
#                 # nn.BatchNorm2d(128),
#                 nn.ReLU(inplace=True),
#                 # nn.AdaptiveAvgPool2d(1),  # 全局平均池化
#                 nn.Flatten(),
#
#                 # 特征变换层
#                 nn.Linear(2048, 1024),
#                 nn.ReLU(inplace=True),
#                 nn.Dropout(0.3),
#
#                 # 正交投影层
#                 nn.Linear(1024, attribute_dim),
#                 nn.ReLU(inplace=True)
#             ) for _ in range(self.num_attributes)
#         ])
#
#         # --------------------- 解耦分类器 ---------------------
#         self.classifiers = nn.ModuleList([
#             nn.Sequential(
#                 nn.Linear(attribute_dim, dim),
#                 nn.LogSoftmax(dim=1)  # 适用于分类任务
#             ) for dim in class_dims
#         ])
#
#         # 正交正则化权重
#         self.ortho_weight = ortho_weight
#         # self.register_buffer(
#         #     'ortho_weight',
#         #     torch.tensor(ortho_weight, dtype=torch.float32)
#         # )
#
#     def forward(self, x):
#         # 共享特征提取
#         shared_features = self.shared_backbone(x)  # [B, 128, 4, 4]
#
#         # 独立分支处理
#         branch_outputs = []
#         for branch in self.branches:
#             branch_outputs.append(branch(shared_features))
#
#         # 分类预测
#         predictions = [cls(feat) for cls, feat in zip(self.classifiers, branch_outputs)]
#
#         return predictions, branch_outputs
#
#     # def orthogonal_regularization(self, features):
#     #     """
#     #     特征正交正则化损失
#     #     确保不同分支的特征向量相互正交
#     #     """
#     #     reg_loss = 0.0
#     #     num_features = len(features)
#     #
#     #     for i in range(num_features):
#     #         for j in range(i + 1, num_features):
#     #             # 计算特征向量间的点积（相似度）
#     #             dot_product = torch.mean(features[i] * features[j], dim=1)
#     #             # 计算正交损失（L2范数）
#     #             reg_loss += torch.mean(dot_product ** 2)
#     #
#     #     return self.ortho_weight * reg_loss
#     def orthogonal_regularization(self, features, labels):
#         """
#         改进的特征正则化损失（针对单个属性）：
#         - 同一属性内，标签相同的样本特征尽可能相近
#         - 同一属性内，标签不同的样本特征尽可能远离
#
#         参数:
#             features: 单个属性的特征张量，形状为 [batch_size, feature_dim]
#             labels: 该属性对应的标签张量，形状为 [batch_size]
#         """
#         batch_size = features.size(0)
#         if batch_size <= 1:
#             return 0.0  # 样本数不足时无损失
#
#         # 特征L2归一化，使点积等价于余弦相似度（范围[-1,1]）
#         normalized_feats = F.normalize(features, p=2, dim=1)  # [batch_size, feature_dim]
#
#         # 计算所有样本对的相似度矩阵 [batch_size, batch_size]
#         # 矩阵中[i,j]表示第i个样本与第j个样本的特征相似度
#         sim_matrix = torch.matmul(normalized_feats, normalized_feats.T)
#
#         # 创建标签匹配矩阵：[i,j]为1表示i和j标签相同，0表示不同
#         label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()  # [batch_size, batch_size]
#
#         # 排除样本自身与自身的对比（对角线元素设为0）
#         mask = 1 - torch.eye(batch_size, device=features.device)  # [batch_size, batch_size]，对角线为0
#         label_eq_matrix = label_eq_matrix * mask
#         label_ne_matrix = (1 - label_eq_matrix) * mask  # 标签不同的掩码
#
#         # 1. 同标签损失：相似度应接近1，损失为(1 - 相似度)的均值
#         same_label_loss = torch.mean((1 - sim_matrix) * label_eq_matrix)
#
#         # 2. 异标签损失：相似度应接近-1，损失为(1 + 相似度)的均值
#         # 注：对异标签样本，若相似度为-1则损失为0，若相似度高则损失大
#         diff_label_loss = torch.mean((1 + sim_matrix) * label_ne_matrix)
#
#         # 总损失 = 同标签损失 + 异标签损失，乘以权重
#         return self.ortho_weight * (same_label_loss + diff_label_loss)
