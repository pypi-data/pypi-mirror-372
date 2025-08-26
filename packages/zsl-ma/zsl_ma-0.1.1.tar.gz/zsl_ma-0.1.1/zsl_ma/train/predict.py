import argparse
import os

import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.em_dataset import AttributeImageDataset, ImageSemanticDataset
from zsl_ma.models.projection import ProjectionNet, FeatureProjectionModel, CNN
from zsl_ma.tools.predict_untils import cls_predict
from zsl_ma.tools.tool import get_device, calculate_metric
import torch.nn.functional as F

def predict(configs):
    device = get_device()
    print(f"Using {device.type} device training.")
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    test_dataset = ImageSemanticDataset(configs.data_root, configs.att_dir, transform=transform, split='val', neg_ratio=0)
    test_loader = DataLoader(test_dataset, batch_size=configs.batch_size, shuffle=False)
    att_np = np.array(test_dataset.semantic_attrs)  # 合并为单一numpy数组
    att_matrix = torch.tensor(att_np).to(device)  # 从单一numpy数组创建张量，效率更高


    model = FeatureProjectionModel()
    state_dict = torch.load(os.path.join(configs.model_dir, 'feat_proj.pth'))
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    all_predictions = []
    all_labels = []
    with torch.no_grad():
        for images, _, _, label in test_loader:
            images = images.to(device)
            outputs = model(images)

            distances = F.cosine_similarity(outputs.unsqueeze(1), att_matrix.unsqueeze(0), dim=2, eps=1e-8)
            _, predicted = torch.max(distances, dim=1)
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(label.cpu().numpy())
    res = calculate_metric(all_labels, all_predictions, classes=test_dataset.classes)
    print(res)

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch_size', type=int, default=10)
    parser.add_argument('--cnn', type=str,
                        default=r'D:\Code\deep-learning-code\classification\yms_class\run\output1\models\best_model.pth')
    parser.add_argument('--att_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果\exp\class_mean_features\嵌入')
    parser.add_argument('--data_root', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\data\seen')
    parser.add_argument('--model_dir', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\MA-ZSL\zsl_ma\train\output\exp-2\checkpoints')
    return parser.parse_args(args if args else [])

if __name__ == '__main__':
    # args = parse_args()
    # predict(args)
    device = get_device()
    model = CNN(num_classes=10)
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    model.load_state_dict(torch.load(r'D:\Code\deep-learning-code\classification\yms_class\run\10分类\models\best_cnn.pth', map_location='cpu', weights_only=True))
    df = cls_predict(model, r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu',
                     r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\p.txt',
                     device,
                     transform
                     )
    # df.to_csv(r'D:\Code\2-ZSL\1-output\特征解耦结果\exp-1\预测结果.csv', index=False, encoding='utf-8-sig')