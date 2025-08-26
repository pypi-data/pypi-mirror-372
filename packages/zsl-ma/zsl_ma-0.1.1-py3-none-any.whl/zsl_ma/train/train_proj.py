import os

import torch
from torch import nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import EmbeddingDataset
from zsl_ma.models.projection import AttributeProjectionModel, FeatureProjectionModel
from zsl_ma.tools.tool import get_device, setup_save_dirs, create_csv, append_metrics_to_csv
from zsl_ma.tools.train_val_until import train_proj_one_epoch, val_proj_one_epoch


def train_proj(configs, run=None):
    device = get_device()
    print(f'Using device: {device}')
    save_dir, img_dir, model_dir = setup_save_dirs(configs.save_dir, configs.prefix)
    results_file = os.path.join(save_dir, 'proj_metrics.csv')
    metrics = ['epoch','train_loss', 'val_loss', 'lr']
    create_csv(metrics, results_file)

    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = EmbeddingDataset(configs.data_dir, configs.semantic_path, configs.classes,
                                     transform=transform, train_class=configs.train_class, neg_ratio=configs.neg_ratio)
    val_dataset = EmbeddingDataset(configs.data_dir, configs.semantic_path, configs.classes,
                                   transform=transform, train_class=configs.train_class,
                                           mode='val', neg_ratio=configs.neg_ratio)

    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)

    attr_proj = AttributeProjectionModel(attr_dim=configs.attribute_dims*2, embed_dim=configs.embed_dim).to(device)
    feat_proj = FeatureProjectionModel(configs.cnn, embed_dim=configs.embed_dim).to(device)
    all_params = list(attr_proj.parameters()) + list(feat_proj.parameters())
    optimizer = torch.optim.Adam(all_params, lr=configs.lr)
    criterion = nn.CosineEmbeddingLoss(margin=0.3)  # margin设为0.3
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    best = 1e8
    num_epochs = configs.epochs

    patience = configs.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch

    for epoch in range(num_epochs):
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss = train_proj_one_epoch(feat_proj, attr_proj, train_loader, optimizer, device, criterion, epoch)
        print(f'the epoch {epoch + 1} train loss is {train_loss:.6f}')

        val_loss = val_proj_one_epoch(feat_proj, attr_proj, val_loader, device, criterion, epoch)
        lr_scheduler.step(val_loss)
        print(f'the epoch {epoch + 1} val loss is {val_loss:.6f}')
        metric={'epoch': epoch, 'train_loss': train_loss, 'val_loss': val_loss, 'lr': training_lr}
        append_metrics_to_csv(metric, results_file)

        current_score = val_loss
        if current_score < best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(feat_proj.state_dict(), os.path.join(model_dir, 'feat_proj.pth'))
            torch.save(attr_proj.state_dict(), os.path.join(model_dir, 'attr_proj.pth'))
            print(f'Best model saved at epoch {epoch + 1} with loss: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.001) and epoch > (num_epochs * 0.6):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            print(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')
                break

    return save_dir

def get_proj_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--embed_dim', type=int, default=25)
    parser.add_argument('--attribute_dims', type=int, default=64)

    parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
    parser.add_argument('--epochs', type=int, default=1, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=40)
    parser.add_argument('--cnn', type=str,
                        default=r'D:\Code\deep-learning-code\classification\yms_class\run\30分类-特征提取\models\best_model.pth')
    parser.add_argument('--save_dir', type=str, default=r'output')
    parser.add_argument('--semantic_path', type=str,
                        default=r'D:\Code\2-ZSL\1-output\特征解耦结果\exp\class_mean_features\fault_combined')
    parser.add_argument('--data_dir', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen')
    parser.add_argument('--classes', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\zsl_classes.txt')
    parser.add_argument('--train_class', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\train_class.txt')
    parser.add_argument('--neg_ratio', type=int, default=1)
    parser.add_argument('--num_workers', default=0, type=int)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--prefix', type=str, default=None)
    return parser.parse_args(args if args else [])

if __name__ == '__main__':
    opts = get_proj_args()
    print(opts)
    train_proj(opts)


