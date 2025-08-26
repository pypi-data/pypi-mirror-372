import torch
import torch.nn as nn
import torch.nn.functional as F

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


class ZeroShotModel(nn.Module):
    """严格对应图示结构的实现"""

    def __init__(self, attribute_dims=None):
        super().__init__()
        # --------------------- 阶段A ---------------------
        if attribute_dims is None:
            attribute_dims = [3, 4, 4]
        self.num = sum(attribute_dims)
        self.A = nn.Sequential(
            nn.Conv2d(3, 32, 3, 1, 1),  # 3x64x64 → 32x64x64
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )

        # --------------------- 阶段B1 ---------------------
        self.B1 = ConvResBlock(32, 64, stride=2)  # → 64x32x32

        # --------------------- 阶段B2 ---------------------
        self.B2 = ConvResBlock(64, 64, stride=2)  # → 64x16x16

        # --------------------- 阶段Cx3 ---------------------
        self.C3 = nn.Sequential(ResBlock(64), ResBlock(64), ResBlock(64))  # → 64x16x16

        # --------------------- 阶段B3 ---------------------
        self.B3 = ConvResBlock(64, 128, stride=2)  # → 128x8x8

        # --------------------- 阶段C4 ---------------------
        self.C4 = ResBlock(128)  # → 128x8x8

        # --------------------- 阶段B4 ---------------------
        self.B4 = ConvResBlock(128, 128, stride=2)  # → 128x4x4

        # --------------------- 阶段C5 ---------------------
        self.C5 = ResBlock(128)  # → 128x4x4

        # --------------------- 阶段D ---------------------
        self.D = nn.Sequential(
            nn.Flatten(),  # → 128
            nn.Linear(128 * 4 * 4, 2048),  # 保持维度
            nn.ReLU(inplace=True),
        )

        self.classifiers = nn.ModuleList([
            nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(2048, 1024),
                nn.ReLU(),
                nn.Dropout(0.5),
                # nn.Linear(2048, 1024),
                # nn.ReLU(),
                # nn.Dropout(0.5),
                nn.Linear(1024, dim),
            ) for dim in attribute_dims
        ])

    def forward(self, x):
        x = self.A(x)  # [B,3,64,64] → [B,32,64,64]
        x = self.B1(x)  # → [B,64,32,32]
        x = self.B2(x)  # → [B,64,16,16]
        x = self.C3(x)  # → [B,64,16,16]
        x = self.B3(x)  # → [B,128,8,8]
        x = self.C4(x)  # → [B,128,8,8]
        x = self.B4(x)  # → [B,128,4,4]
        x = self.C5(x)  # → [B,128,4,4]
        features = self.D(x)  # → [B,128]

        outputs = [cls(features) for cls in self.classifiers]

        return outputs


class CNN(nn.Module):
    def __init__(self, attribute_dims=None):
        super().__init__()
        if attribute_dims is None:
            attribute_dims = [3, 3, 3]
        self.num = sum(attribute_dims)
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Sequential(
            nn.Linear(256 * 8 * 8, 4096),
            nn.ReLU(),
            # nn.Linear(4096, 2048),
        )
        self.classifiers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(4096, 2048),
                nn.ReLU(inplace=True),
                nn.Linear(2048, 1024),
                nn.ReLU(inplace=True),
                nn.Linear(1024, 1),
            ) for _ in range(self.num)
        ])

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        features = self.fc(x)
        outputs = [cls(features) for cls in self.classifiers]
        return torch.cat(outputs, dim=1)



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


# 编码器
class Encoder(nn.Module):
    def __init__(self, attribute_dims=None):
        super().__init__()
        if attribute_dims is None:
            attribute_dims = [3, 3, 3]
        self.num = sum(attribute_dims)
        # Conv1 + ResidualBlock1
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, 3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            ResidualBlock(16)
        )
        # Conv2 + ResidualBlock2
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            ResidualBlock(32)
        )
        # Conv3 + ResidualBlock3
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            ResidualBlock(64)
        )
        # Conv4 + ResidualBlock4
        self.conv4 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            ResidualBlock(128)
        )
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(128 * 4 * 4, 2048)
        self.classifiers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(2048, 2048),
                nn.ReLU(inplace=True),
                nn.Linear(2048, 1024),
                nn.ReLU(inplace=True),
                nn.Linear(1024, 1),
            ) for _ in range(self.num)
        ])


    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.flatten(x)
        features = self.fc(x)
        outputs = [cls(features) for cls in self.classifiers]
        return torch.cat(outputs, dim=1)


class DisentangledModel(nn.Module):
    """监督学习解耦网络，确保三个特征空间独立"""

    def __init__(self, class_dims, attribute_dim=64, ortho_weight=2):
        super().__init__()
        # if attribute_dims is None:
        #     attribute_dims = [3, 4, 4]
        self.num_attributes = len(class_dims)

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
                # nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                # nn.AdaptiveAvgPool2d(1),  # 全局平均池化
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

        # 正交正则化权重
        self.ortho_weight = ortho_weight
        # self.register_buffer(
        #     'ortho_weight',
        #     torch.tensor(ortho_weight, dtype=torch.float32)
        # )

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

    # def orthogonal_regularization(self, features):
    #     """
    #     特征正交正则化损失
    #     确保不同分支的特征向量相互正交
    #     """
    #     reg_loss = 0.0
    #     num_features = len(features)
    #
    #     for i in range(num_features):
    #         for j in range(i + 1, num_features):
    #             # 计算特征向量间的点积（相似度）
    #             dot_product = torch.mean(features[i] * features[j], dim=1)
    #             # 计算正交损失（L2范数）
    #             reg_loss += torch.mean(dot_product ** 2)
    #
    #     return self.ortho_weight * reg_loss
    def orthogonal_regularization(self, features, labels):
        """
        改进的特征正则化损失（针对单个属性）：
        - 同一属性内，标签相同的样本特征尽可能相近
        - 同一属性内，标签不同的样本特征尽可能远离

        参数:
            features: 单个属性的特征张量，形状为 [batch_size, feature_dim]
            labels: 该属性对应的标签张量，形状为 [batch_size]
        """
        batch_size = features.size(0)
        if batch_size <= 1:
            return 0.0  # 样本数不足时无损失

        # 特征L2归一化，使点积等价于余弦相似度（范围[-1,1]）
        normalized_feats = F.normalize(features, p=2, dim=1)  # [batch_size, feature_dim]

        # 计算所有样本对的相似度矩阵 [batch_size, batch_size]
        # 矩阵中[i,j]表示第i个样本与第j个样本的特征相似度
        sim_matrix = torch.matmul(normalized_feats, normalized_feats.T)

        # 创建标签匹配矩阵：[i,j]为1表示i和j标签相同，0表示不同
        label_eq_matrix = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()  # [batch_size, batch_size]

        # 排除样本自身与自身的对比（对角线元素设为0）
        mask = 1 - torch.eye(batch_size, device=features.device)  # [batch_size, batch_size]，对角线为0
        label_eq_matrix = label_eq_matrix * mask
        label_ne_matrix = (1 - label_eq_matrix) * mask  # 标签不同的掩码

        # 1. 同标签损失：相似度应接近1，损失为(1 - 相似度)的均值
        same_label_loss = torch.mean((1 - sim_matrix) * label_eq_matrix)

        # 2. 异标签损失：相似度应接近-1，损失为(1 + 相似度)的均值
        # 注：对异标签样本，若相似度为-1则损失为0，若相似度高则损失大
        diff_label_loss = torch.mean((1 + sim_matrix) * label_ne_matrix)

        # 总损失 = 同标签损失 + 异标签损失，乘以权重
        return self.ortho_weight * (same_label_loss + diff_label_loss)
# --------------------- 尺寸验证 ---------------------
if __name__ == "__main__":

    model = DisentangledModel(class_dims=[3, 4, 4])
    print(model.state_dict())
    # test_input = torch.randn(1, 3, 64, 64)
    #
    # print("输入尺寸:", test_input.shape)
    # y = model(test_input)
    #
    # for i, out in enumerate(y):
    #     print(f"属性{i + 1}输出尺寸: {out.shape}")  # 应为 [2,3]
