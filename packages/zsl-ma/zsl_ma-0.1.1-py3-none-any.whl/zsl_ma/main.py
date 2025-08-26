import argparse
import os
import warnings

import numpy as np
import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import transforms

from zsl_ma.dataset_utils.dataset import create_dataloaders
from zsl_ma.model import DisentangledModel
from zsl_ma.tools.tool import calculate_metric, make_save_dirs, get_device, create_csv, create_next_numbered_folder, \
    append_metrics_to_csv
from zsl_ma.tools.train_val_until import val_one_epoch, train_one_epoch

warnings.filterwarnings("ignore")


def main(configs, run=None):
    # save_dir = create_next_numbered_folder(configs.save_dir, configs.prefix)
    save_dir = configs.save_dir
    img_dir, model_dir = make_save_dirs(save_dir)
    device = get_device()
    print(f"Using {device.type} device training.")

    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    train_loader, val_loader = create_dataloaders(configs.seen_data,
                                                  configs.batch_size,
                                                  transform=transform,
                                                  val_shuffle=True
                                                  )
    metrics = {'epoch': [], 'train_loss': [], 'val_loss': [], 'accuracy': [], 'precision': [], 'recall': [],
               'f1-score': [],
               'lr': []}
    create_csv(metrics, os.path.join(save_dir, 'metrics.csv'))

    model = DisentangledModel(class_dims=[3, 4, 4], attribute_dim=32, ortho_weight=2).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=configs.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=5, min_lr=1e-9)
    criterion = CrossEntropyLoss()
    best = -1
    epochs = configs.epochs
    for epoch in range(epochs):
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss = train_one_epoch(model, train_loader, optimizer, device, criterion, epoch)
        val_loss, all_predictions, all_labels = val_one_epoch(model, val_loader, device, criterion, epoch)

        # 获取实际出现的所有类别ID
        unique_labels = np.unique(np.concatenate([all_labels, all_predictions]))
        # 根据实际类别ID筛选对应的名称（假设classes是按ID排序的列表）
        actual_target_names = [train_loader.dataset.maper.classes[i] for i in unique_labels]

        result = calculate_metric(all_labels, all_predictions, actual_target_names)

        print(result)
        lr_scheduler.step(val_loss)
        result.update({'train_loss': train_loss, 'val_loss': val_loss.item(), 'lr': training_lr, 'epoch': epoch})
        append_metrics_to_csv(result, os.path.join(save_dir, 'metrics.csv'))
        if run is not None:
            run.log(result)
        metrics['train_loss'].append(train_loss)
        metrics['val_loss'].append(val_loss.item())
        metrics['accuracy'].append(result['accuracy'])
        metrics['precision'].append(result['precision'])
        metrics['recall'].append(result['recall'])
        metrics['f1-score'].append(result['f1-score'])
        metrics['lr'].append(training_lr)
        metrics['epoch'].append(epoch)

        if best < result['f1-score']:
            best = result['f1-score']
            torch.save(model.state_dict(), os.path.join(model_dir, 'best.pth'))
        torch.save(model.state_dict(), os.path.join(model_dir, 'last.pth'))

    if run is not None:
        run.finish()


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lr', type=float, default=0.01, help='learning rate')
    parser.add_argument('--epochs', type=int, default=150, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=150)
    parser.add_argument('--seen_data', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\data\seen')
    parser.add_argument('--save_dir', type=str, default=r'output')
    parser.add_argument('--prefix', type=str, default='exp')
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = parse_args()
    print(opts)
    main(opts)
