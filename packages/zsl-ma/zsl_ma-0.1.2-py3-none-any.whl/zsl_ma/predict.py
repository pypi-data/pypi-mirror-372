import argparse
import os

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.dataset import TestDataset
from zsl_ma.tools import calculate_metric
from zsl_ma.tools.train_val_until import unseen_predict, get_true_attributes


def predict(configs):
    device = torch.device('cuda' if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    test_dataset = TestDataset(configs.unseen_data, np.load(configs.classes_to_idx, allow_pickle=True).item(), transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=configs.batch_size)
    idx_to_labels = np.load(configs.idx_to_labels, allow_pickle=True).item()
    classes = np.load(configs.classes)
    true_attributes = get_true_attributes(configs.unseen_att).to(device)
    test_model = torch.load(configs.model, map_location='cpu', weights_only=False).to(device)

    df = unseen_predict(test_model, test_loader, device, true_attributes,1, idx_to_labels, classes)
    report = calculate_metric(df['标注类别ID'],df['top-1-预测ID'], classes, class_metric=True)
    df_report = pd.DataFrame(report).transpose()
    print(df_report)
    df.to_csv(os.path.join(configs.save_dir, '不可见类测试集预测结果.csv'), index=False, encoding="utf-8-sig")
    df_report.to_csv(os.path.join(configs.save_dir, '不可见类测试集各类别准确率评估指标.csv'), index_label='类别', encoding="utf-8-sig")

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch_size', type=int, default=40)
    parser.add_argument('--save_dir', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\输出结果\CRWU_B_Experiment_001')
    parser.add_argument('--unseen_att', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\B\unseen\unseen_att.npz')
    parser.add_argument('--unseen_data', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\B\unseen\images')
    parser.add_argument('--model', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\输出结果\CRWU_B_Experiment_001\checkpoints\best.pth')
    parser.add_argument('--idx_to_labels', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\B\unseen\idx_to_labels.npy')
    parser.add_argument('--classes', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\B\unseen\classes.npy')
    parser.add_argument('--classes_to_idx', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\B\unseen\classes_to_idx.npy')
    return parser.parse_args()

if __name__ == '__main__':
    opt = parse_args()
    predict(opt)