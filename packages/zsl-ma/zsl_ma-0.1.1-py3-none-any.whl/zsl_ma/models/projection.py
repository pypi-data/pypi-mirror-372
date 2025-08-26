import torch
from torch import nn


class CNN(nn.Module):
    def __init__(self, num_classes: int = 12) -> None:
        super().__init__()
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
            nn.Linear(256 * 16 * 16, 4096),
            nn.ReLU(),
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


# 1. 语义属性投影模型
class AttributeProjectionModel(nn.Module):
    def __init__(self, attr_dim=128, embed_dim=25):
        super().__init__()

        # 属性投影分支
        self.attr_projector = nn.Sequential(
            nn.Linear(attr_dim, 64),
            nn.ReLU(),
            nn.Linear(64, embed_dim)
        )

    def forward(self, attr):
        # 处理属性输入
        attr_embed = self.attr_projector(attr)
        return attr_embed


# 2. 特征投影模型
class FeatureProjectionModel(nn.Module):
    def __init__(self, cnn_path=None, embed_dim=25):
        super().__init__()

        # 图像投影分支
        self.img_projector = nn.Sequential(
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, embed_dim),
            # nn.ReLU(),
            # nn.Linear(512, 256),
            # nn.ReLU(),
            # nn.Linear(256, embed_dim)
        )

        # 图像特征提取器 (冻结参数)
        self.cnn_model = CNN(num_classes=30)  # 假设CNN类已定义
        if cnn_path is not None:
            self.cnn_model.load_state_dict(
                torch.load(cnn_path, weights_only=True, map_location='cpu')
            )
        for param in self.cnn_model.parameters():
            param.requires_grad = False
        self.cnn = self.cnn_model.features

    def get_fc1_output(self, x):
        # 1. 通过卷积层提取特征
        conv_features = self.cnn(x)  # 形状为[batch_size, 256, 16, 16]

        # 2. 扁平化特征
        flattened = torch.flatten(conv_features, 1)  # 形状为[batch_size, 256*16*16]

        # 3. 获取nn.Linear(256*16*16, 4096)层的输出
        fc1_output = self.cnn_model.fc[0](flattened)  # 形状为[batch_size, 4096]

        return fc1_output

    def forward(self, img):
        # 处理图像输入
        img_feat = self.get_fc1_output(img)
        img_embed = self.img_projector(img_feat)
        return img_embed


# 2. 嵌入模型
class ProjectionNet(nn.Module):
    def __init__(self, cnn_path=None, attr_dim=128, embed_dim=25):
        super().__init__()

        # # 属性投影分支
        self.attr_projector = nn.Sequential(
            nn.Linear(attr_dim, 64),
            nn.ReLU(),
            nn.Linear(64, embed_dim)
        )

        # 图像投影分支
        self.img_projector = nn.Sequential(
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, embed_dim),
            # nn.ReLU(),
            # nn.Linear(512, 256),
            # nn.ReLU(),
            # nn.Linear(256, embed_dim)
        )

        # 图像特征提取器 (冻结参数)
        self.cnn_model = CNN(num_classes=30)
        if cnn_path is not None:
            self.cnn_model.load_state_dict(
                torch.load(cnn_path, weights_only=True, map_location='cpu')
            )
        for param in self.cnn_model.parameters():
            param.requires_grad = False
        self.cnn = self.cnn_model.features

    def get_fc1_output(self, x):
        # 1. 通过卷积层提取特征
        conv_features = self.cnn(x)  # 形状为[batch_size, 256, 16, 16]

        # 2. 扁平化特征
        flattened = torch.flatten(conv_features, 1)  # 形状为[batch_size, 256*16*16]

        # 3. 获取nn.Linear(256*16*16, 4096)层的输出
        fc1_output = self.cnn_model.fc[0](flattened)  # 形状为[batch_size, 4096]

        return fc1_output

    def forward(self, img, attr):
        # 处理图像输入
        img_feat = self.get_fc1_output(img)
        img_embed = self.img_projector(img_feat)

        # 处理属性输入
        attr_embed = self.attr_projector(attr)

        return img_embed, attr_embed
        # return img_embed


class LSELoss(nn.Module):
    def __init__(self, hsa_matrix):
        """
               LSE损失函数实现
               Args:
                   hsa_matrix (Tensor): HSA矩阵 [num_classes, feature_dim]
               """
        super().__init__()
        self.register_buffer('hsa', hsa_matrix)  # 注册为buffer保证设备一致性

    def forward(self, embedded_features, targets):
        """
        前向计算
        Args:
            embedded_features (Tensor): 嵌入特征 [batch_size, feature_dim]
            targets (LongTensor): 类别标签 [batch_size]
        Returns:
            Tensor: 损失值
        """
        # 选择对应类别的HSA向量
        selected_hsa = self.hsa[targets]  # [batch_size, feature_dim]

        # 计算最小二乘误差
        loss = torch.sum((embedded_features - selected_hsa) ** 2) / targets.size(0)

        return loss


if __name__ == '__main__':
    model = ProjectionNet(r'D:\Code\deep-learning-code\classification\yms_class\run\output1\models\best_model.pth')
    data = torch.randn(1, 3, 64, 64)
    y = model(data)
    print(y.size())
