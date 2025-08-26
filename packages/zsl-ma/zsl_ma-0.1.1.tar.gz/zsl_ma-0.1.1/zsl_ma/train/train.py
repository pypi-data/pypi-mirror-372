import argparse
import os

import numpy as np

from torchvision import transforms

from zsl_ma.tools.predict_untils import disent_predict
from zsl_ma.tools.tool import get_device, save_class_mean_features, concat_fault_features
from zsl_ma.train.train_cls import get_cls_args, train_cls
from zsl_ma.train.train_disent import get_disent_args, train_disent
from zsl_ma.train.train_proj import get_proj_args, train_proj


def run(configs):
    device = get_device()
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    cls_opts = get_cls_args(['--data_dir', str(configs.data_dir),
                             '--save_dir', str(configs.save_dir),
                             '--train_class', str(configs.train_class),
                             '--epochs', str(1),
                             '--batch_size', str(40)
                             ])
    print(cls_opts)
    save_dir, cls_model = train_cls(cls_opts)

    disent_opts = get_disent_args(['--data_dir', str(configs.data_dir),
                                   '--save_dir', str(save_dir),
                                   '--train_class', str(configs.train_class),
                                   '--epochs', str(1),
                                   '--batch_size', str(40)
                                   ])
    print(disent_opts)
    disent_model = train_disent(disent_opts)

    pred_df, condition_features, fault_type_features, severity_features, features = disent_predict(disent_model,
                                                                                                   configs.data_dir,
                                                                                                   device, transform,
                                                                                                   'val',
                                                                                                   configs.train_class)
    pred_df.to_csv(os.path.join(save_dir, '特征解耦预测结果.csv'), index=False, encoding="utf-8-sig")
    np.save(os.path.join(save_dir, 'attributes', '故障工况.npy'), condition_features)
    np.save(os.path.join(save_dir, 'attributes', '故障类型.npy'), fault_type_features)
    np.save(os.path.join(save_dir, 'attributes', '故障程度.npy'), severity_features)
    np.save(os.path.join(save_dir, 'attributes', '语义属性.npy'), features)

    save_class_mean_features(os.path.join(save_dir, 'attributes'),
                             os.path.join(save_dir, '特征解耦预测结果.csv'),
                             '故障类型',
                             os.path.join(save_dir, 'attributes', 'avg_disent_feats'))

    save_class_mean_features(os.path.join(save_dir, 'attributes'),
                             os.path.join(save_dir, '特征解耦预测结果.csv'),
                             '故障程度',
                             os.path.join(save_dir, 'attributes', 'avg_disent_feats'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_B.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_007英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_B.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_014英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_B.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_021英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_IR.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_007英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_IR.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_014英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_IR.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_021英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_OR.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_007英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_OR.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_014英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_OR.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_021英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    concat_fault_features(os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障类型_No.npy'),
                          os.path.join(save_dir, 'attributes', 'avg_disent_feats', '故障程度_0英寸.npy'),
                          os.path.join(save_dir, 'attributes', 'semantic_attribute'))

    proj_opts = get_proj_args(['--data_dir', str(configs.data_dir),
                               '--save_dir', str(save_dir),
                               '--train_class', str(configs.train_class),
                               '--cnn', str(os.path.join(save_dir, 'checkpoints', 'best_cnn.pth')),
                               '--semantic_path', str(os.path.join(save_dir, 'attributes', 'semantic_attribute')),
                               '--classes', str(configs.classes),
                               '--epochs', str(1),
                               '--batch_size', str(40)])
    print(proj_opts)
    train_proj(proj_opts)


def get_train_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen')
    parser.add_argument('--save_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果')
    parser.add_argument('--train_class', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\train_class.txt')
    parser.add_argument('--classes', type=str,
                        default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\zsl_classes.txt')

    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    # opts = get_train_args(['--data_dir', r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen',
    #                        '--save_dir', r'D:\Code\2-ZSL\1-output\特征解耦结果',
    #                        '--train_class', r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\train_class.txt',
    #                        '--classes', r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\多文件夹\seen\zsl_classes.txt'])
    opts = get_train_args()
    run(opts)
