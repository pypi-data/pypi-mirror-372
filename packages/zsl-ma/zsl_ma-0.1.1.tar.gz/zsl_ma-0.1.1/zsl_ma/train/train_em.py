import argparse
import os
import sys

import numpy as np
import torch
from torch import nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm

from zsl_ma.dataset_utils.em_dataset import AttributeImageDataset, ImageSemanticDataset
from zsl_ma.models.projection import ProjectionNet, LSELoss, AttributeProjectionModel, FeatureProjectionModel
from zsl_ma.tools.distributed_utils import MetricLogger, SmoothedValue
from zsl_ma.tools.tool import get_device, create_next_numbered_folder, make_save_dirs, calculate_metric


def main(configs):
    device = get_device()
    print(f"Using {device.type} device training.")
    save_dir = create_next_numbered_folder(configs.save_dir,configs.prefix)
    img_dir, model_dir = make_save_dirs(save_dir)
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = ImageSemanticDataset(configs.data_root, configs.att_dir, transform=transform, split='train')
    val_dataset = ImageSemanticDataset(configs.data_root, configs.att_dir, transform=transform, split='val')
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False)

    # model = ProjectionNet(configs.cnn).to(device)
    attr_proj = AttributeProjectionModel().to(device)
    feat_proj = FeatureProjectionModel(configs.cnn).to(device)
    all_params = list(attr_proj.parameters()) + list(feat_proj.parameters())
    optimizer = torch.optim.Adam(all_params, lr=configs.lr)
    # optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
    criterion = nn.CosineEmbeddingLoss(margin=0.3)  # margin设为0.3
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    best = 1e8

    for epoch in range(configs.epochs):
        # metric_logger = MetricLogger(delimiter="  ")
        # metric_logger.add_meter('lr', SmoothedValue(window_size=1, fmt='{value:.6f}'))
        # header = f'Train Epoch:[{epoch}]'

        # model.train()
        attr_proj.train()
        feat_proj.train()
        train_loss = torch.zeros(1).to(device)
        train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
        for step, (images, att, target) in enumerate(train_iterator):
            images, att, target = images.to(device), att.to(device), target.to(device)
            optimizer.zero_grad()
            # img_embed, attr_embed = model(images, att)
            img_embed = feat_proj(images)
            attr_embed = attr_proj(att)
            loss = criterion(img_embed, attr_embed, target)
            loss.backward()
            optimizer.step()
            train_loss = (train_loss * step + loss.detach()) / (step + 1)
            # metric_logger.update(loss=train_loss)
            train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())

        print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
        # model.eval()
        feat_proj.eval()
        attr_proj.eval()
        val_loss = torch.zeros(1).to(device)
        val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
        # metric_logger = MetricLogger(delimiter="  ")
        # header = 'Validation Epoch: [{}]'.format(epoch)
        # all_predictions = []
        # all_labels = []
        with torch.no_grad():
            for step, (images, att, target) in enumerate(val_iterator):
                images, att, target = images.to(device), att.to(device), target.to(device)
                # outputs = model(images)
                # img_embed, attr_embed = model(images, att)
                img_embed = feat_proj(images)
                attr_embed = attr_proj(att)
                loss = criterion(img_embed, attr_embed, target)
                val_loss = (val_loss * step + loss.detach()) / (step + 1)

                # distances = torch.cdist(outputs, att_matrix, p=2)
                # _, predicted = torch.min(distances, dim=1)
                # all_predictions.extend(predicted.cpu().numpy())
                # all_labels.extend(label.cpu().numpy())
                # metric_logger.update(loss=val_loss)
                val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())

        lr_scheduler.step(val_loss)
        print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
        # res = calculate_metric(all_labels, all_predictions, classes=train_dataset.classes)
        # print(res)
        if val_loss.item() < best:
            best = val_loss.item()
            # torch.save(model.state_dict(), os.path.join(model_dir, 'best.pth'))
            torch.save(feat_proj.state_dict(), os.path.join(model_dir, 'feat_proj.pth'))
            torch.save(attr_proj.state_dict(), os.path.join(model_dir, 'attr_proj.pth'))


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
    parser.add_argument('--epochs', type=int, default=150, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=150)
    parser.add_argument('--cnn', type=str, default=r'D:\Code\deep-learning-code\classification\yms_class\run\30分类-特征提取\models\best_model.pth')
    parser.add_argument('--save_dir', type=str, default=r'output')
    parser.add_argument('--att_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果\exp\class_mean_features\fault_combined')
    parser.add_argument('--data_root', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\data\seen')
    parser.add_argument('--prefix', type=str, default='exp')
    return parser.parse_args(args if args else [])

if __name__ == '__main__':
    args = parse_args()
    main(args)
