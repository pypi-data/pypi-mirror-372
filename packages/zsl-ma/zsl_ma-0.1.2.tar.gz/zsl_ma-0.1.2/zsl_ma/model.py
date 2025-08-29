import torch
import torch.nn as nn

from zsl_ma.models.DisentangledModel import ConvResBlock, ResBlock, ResidualBlock, DisentangledModel


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
