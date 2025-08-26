import os

import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import FeatureDecouplingDataset
from zsl_ma.model import DisentangledModel
from zsl_ma.tools.tool import get_device, setup_save_dirs, create_csv, calculate_metric, append_metrics_to_csv
from zsl_ma.tools.train_val_until import train_disent_one_epoch, val_disent_one_epoch
import warnings

warnings.filterwarnings("ignore")


def train_disent(configs, run=None):
    device = get_device()
    print(f"Using {device.type} device training.")
    save_dir, img_dir, model_dir = setup_save_dirs(configs.save_dir, configs.prefix)
    results_file = os.path.join(save_dir, 'disent_metrics.csv')
    metrics = ['train_loss', 'val_loss', 'accuracy', 'precision', 'recall', 'f1-score', 'lr']
    create_csv(metrics, results_file)

    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = FeatureDecouplingDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                             factor_index_map_path=configs.factor_index_map_path)
    val_dataset = FeatureDecouplingDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                           mode='val', factor_index_map_path=configs.factor_index_map_path)
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)

    classes = train_dataset.classes

    model = DisentangledModel(class_dims=configs.class_dims, attribute_dim=configs.attribute_dim,
                              ortho_weight=configs.ortho_weight).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    criterion = CrossEntropyLoss()
    best = -1
    num_epochs = configs.epochs

    # 添加早停相关参数
    patience = configs.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch

    for epoch in range(num_epochs):
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss = train_disent_one_epoch(model, train_loader, optimizer, device, criterion, epoch)
        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.5f},lr: {training_lr}')

        val_loss, all_predictions, all_labels = val_disent_one_epoch(model, val_loader, device, criterion, epoch)
        result = calculate_metric(all_labels, all_predictions, classes)
        lr_scheduler.step(val_loss)

        result.update({'train_loss': train_loss, 'val_loss': val_loss.item(), 'lr': training_lr, 'epoch': epoch})
        append_metrics_to_csv(result, results_file)
        print(f'val epoch {epoch + 1}, result: {result}')

        if run is not None:
            run.log(result)

        # torch.save(model.state_dict(), os.path.join(model_dir, 'last_disent.pth'))
        # 早停逻辑
        current_score = result['f1-score']
        if current_score > best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model.state_dict(), os.path.join(model_dir, 'best_disent.pth'))
            print(f'Best model saved at epoch {epoch + 1} with F1-score: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.001) and epoch > (num_epochs * 0.6):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            print(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')
                break

    model.load_state_dict(torch.load(os.path.join(model_dir, 'best_disent.pth'), weights_only=True, map_location='cpu'))

    return model


def get_disent_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--class_dims', type=int, nargs='+', default=[4, 4])
    parser.add_argument('--attribute_dim', type=int, default=64)
    parser.add_argument('--ortho_weight', type=float, default=2)

    parser.add_argument('--data_dir', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹')
    parser.add_argument('--save_dir', type=str, default=r'output\exp-1')
    parser.add_argument('--train_class', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen_classes.txt')
    parser.add_argument('factor_index_map_path', type=str, default='t.txt')
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--batch_size', default=40, type=int)
    parser.add_argument('--lr', default=1e-3, type=float)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--num_workers', default=0, type=int)
    parser.add_argument('--prefix', type=str, default=None)

    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = get_disent_args()
    print(opts)
    train_disent(opts)
