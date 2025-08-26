import argparse
import os

import torch
from torch.nn import MSELoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from zsl_ma.dataset_utils.dataset import create_dataloaders

from zsl_ma.models.VAE import CAE
from zsl_ma.tools import get_device, make_save_dirs
from zsl_ma.tools.train_val_until import train_cae_one_epoch


def main(args, run=None):
    save_dir = args.save_dir
    img_dir, model_dir = make_save_dirs(save_dir)


    device = get_device()
    print("Using {} device training.".format(device.type))

    train_loader, val_loader = create_dataloaders(args.data_dir, args.batch_size)
    metrics = {'train_losses': [], 'val_losses': [], 'lrs': []}

    model = CAE().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=4, min_lr=1e-9)
    criterion = MSELoss()
    best = 1e8
    for epoch in range(0, args.epochs):
        result = train_cae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch)
        lr = lr_scheduler.get_last_lr()[0]
        lr_scheduler.step(result['val_loss'])

        metrics['val_losses'].append(result['val_loss'])
        metrics['train_losses'].append(result['train_loss'])
        metrics['lrs'].append(lr)
        result.update({'lr': lr})

        if run is not None:
            run.log({'decae': result})

        save_file = {
            'epoch': epoch,
            'model': model,
            'optimizer': optimizer,
            'lr_scheduler': lr_scheduler,
        }
        torch.save(save_file, os.path.join(model_dir, 'last_decae.pt'))
        if result['val_loss'] < best:
            best = result['val_loss']
            model.save(os.path.join(model_dir, 'decae.pt'))



def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default=r'/data/coding/data/D0')
    parser.add_argument('--save_dir', type=str, default='/data/coding/results/train_D0')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--batch_size', type=int, default=64)
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = parse_args()
    print(opts)
    main(opts)
