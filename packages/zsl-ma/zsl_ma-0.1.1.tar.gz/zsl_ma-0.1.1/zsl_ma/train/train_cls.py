import os

import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.CustomImageDataset import ImageClassificationDataset
from zsl_ma.models.projection import CNN
from zsl_ma.tools.tool import get_device, create_csv, calculate_metric, \
    append_metrics_to_csv, setup_save_dirs
from zsl_ma.tools.train_val_until import train_cls_one_epoch, eval_cls_one_epoch
import warnings

warnings.filterwarnings("ignore")


def train_cls(configs, run=None):
    device = get_device()
    print(f"Using {device.type} device training.")
    # save_dir = create_next_numbered_folder(configs.save_dir, configs.prefix)
    save_dir, img_dir, model_dir = setup_save_dirs(configs.save_dir, configs.prefix)
    results_file = os.path.join(save_dir, 'cls_metrics.csv')
    metrics = ['epoch','train_loss', 'val_loss', 'accuracy', 'precision', 'recall', 'f1-score', 'lr']
    create_csv(metrics, results_file)

    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class)
    val_dataset = ImageClassificationDataset(configs.data_dir, transform=transform, train_class=configs.train_class,
                                             mode='val')
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True,
                              num_workers=configs.num_workers)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False, num_workers=configs.num_workers)

    classes = train_dataset.classes

    model = CNN(num_classes=len(classes))
    model = model.to(device)
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
        train_loss, train_accuracy = train_cls_one_epoch(model=model, train_loader=train_loader, device=device,
                                                         optimizer=optimizer, criterion=criterion, epoch=epoch)
        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.5f}, Train Accuracy: {train_accuracy:.4%},'
              f'lr: {training_lr}')

        result = eval_cls_one_epoch(model=model, val_loader=val_loader,
                                    device=device, criterion=criterion, epoch=epoch)

        metric = calculate_metric(result['y_true'], result['y_pred'], classes)
        print(f'val epoch {epoch + 1}, val loss: {result["val_loss"]:.4f}, accuracy: {metric["accuracy"]:.2%}')
        metric.update({'epoch': epoch, 'train_loss': train_loss, 'val_loss': result['val_loss'], 'lr': training_lr})
        append_metrics_to_csv(metric, results_file)

        if run is not None:
            run.log(metric)

        # torch.save(model.state_dict(), os.path.join(model_dir, 'last_cnn.pth'))
        # 早停逻辑
        current_score = metric['f1-score']
        if current_score > best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model.state_dict(), os.path.join(model_dir, 'best_cnn.pth'))
            print(f'Best model saved at epoch {epoch + 1} with F1-score: {best:.4f}')
        elif patience > 0 and training_lr < (configs.lr * 0.001) and epoch > (num_epochs * 0.6):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            print(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')
                break

    model.load_state_dict(torch.load(os.path.join(model_dir, 'best_cnn.pth'), weights_only=True, map_location='cpu'))

    return save_dir, model


def get_cls_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data_dir', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen')
    parser.add_argument('--save_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果')
    parser.add_argument('--train_class', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\train_classes.txt')
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--batch_size', default=20, type=int)
    parser.add_argument('--lr', default=1e-3, type=float)
    parser.add_argument('--weight_decay', default=1e-5, type=float)
    parser.add_argument('--patience', default=10, type=int)
    parser.add_argument('--num_workers', default=0, type=int)
    parser.add_argument('--prefix', type=str, default='exp')

    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = get_cls_args()
    print(opts)
    train_cls(opts)
