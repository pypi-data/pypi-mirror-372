import os
import sys

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from zsl_ma.tools.distributed_utils import MetricLogger, SmoothedValue, warmup_lr_scheduler
from zsl_ma.tools.predict_untils import merge_to_192d
from zsl_ma.tools.tool import generate_image_dataframe


def update_average_loss(avg_loss, current_loss, step):
    """更新平均损失（累积计算）"""
    return (avg_loss * step + current_loss.detach()) / (step + 1)


def get_warmup_scheduler(optimizer, train_loader, epoch):
    if epoch == 0:
        warmup_factor = 1.0 / 1000
        warmup_iters = min(1000, len(train_loader) - 1)

        return warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)
    return None


def train_cls_one_epoch(model, train_loader, device, optimizer, criterion, epoch, warmup=True):
    metric_logger = MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = f'Train Epoch:[{epoch}]'

    # lr_scheduler = None
    lr_scheduler = get_warmup_scheduler(optimizer, train_loader, epoch) if warmup else None
    # if epoch == 0 and warmup is True:  # 当训练第一轮（epoch=0）时，启用warmup训练方式，可理解为热身训练
    #     warmup_factor = 1.0 / 1000
    #     warmup_iters = min(1000, len(train_loader) - 1)
    #
    #     lr_scheduler = warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)

    train_loss = torch.zeros(1).to(device)
    all_predictions = []
    all_labels = []
    model.train()
    # train_iterator = tqdm(train_loader, file=sys.stdout, desc=f' the {epoch + 1} epoch is training....', colour='blue')
    for step, (images, labels) in enumerate(metric_logger.log_every(train_loader, 50, header)):
        # 将数据转移到设备
        images, labels = images.to(device), labels.to(device)
        # 梯度清0
        optimizer.zero_grad()
        # 前向传播
        outputs = model(images)
        # 计算损失
        loss = criterion(outputs, labels)
        # 反向传播
        loss.backward()
        # 更新参数
        optimizer.step()

        # mean_loss = (mean_loss * step + loss.detach()) / (step + 1)
        train_loss = update_average_loss(train_loss, loss, step)
        _, predicted = torch.max(outputs, 1)
        # 设置进度条
        # train_iterator.set_postfix(loss=loss.item(), mean_loss=mean_loss.item())

        if lr_scheduler:
            lr_scheduler.step()

        metric_logger.update(loss=train_loss)
        now_lr = optimizer.param_groups[0]["lr"]
        metric_logger.update(lr=now_lr)

        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    train_accuracy = accuracy_score(y_true=all_labels, y_pred=all_predictions)
    return train_loss.item(), train_accuracy


@torch.no_grad()
def eval_cls_one_epoch(model, val_loader, device, criterion, epoch):
    metric_logger = MetricLogger(delimiter="  ")
    header = 'Validation Epoch: [{}]'.format(epoch)

    result = {"y_pred": [], "y_true": [], 'val_loss': 0.}
    val_loss = torch.zeros(1).to(device)
    model.eval()
    # val_iterator = tqdm(val_loader, file=sys.stdout, desc=f'{epoch + 1} epoch is validation...', colour='GREEN')
    for step, (images, labels) in enumerate(metric_logger.log_every(val_loader, 50, header)):
        # 将数据转移到设备
        images, labels = images.to(device), labels.to(device)
        # 计算结果
        outputs = model(images)
        # 计算损失
        loss = criterion(outputs, labels)
        # 计算数据集上的全部损失
        # val_loss = (val_loss * step + loss.detach()) / (step + 1)
        val_loss = update_average_loss(val_loss, loss, step)
        # 计算预测正确的样本
        _, predicted = torch.max(outputs, 1)
        # val_iterator.set_postfix(loss=loss.item(), val_loss=val_loss.item())
        metric_logger.update(loss=val_loss)

        result["y_pred"].extend(predicted.cpu().numpy())
        result["y_true"].extend(labels.cpu().numpy())

    result['val_loss'] = val_loss.item()
    return result


def train_disent_one_epoch(model, train_loader, optimizer, device, criterion, epoch, warmup=True):
    metric_logger = MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = f'Train Epoch:[{epoch}]'

    lr_scheduler = get_warmup_scheduler(optimizer, train_loader, epoch) if warmup else None

    # lr_scheduler = None
    # if epoch == 0 and warmup is True:  # 当训练第一轮（epoch=0）时，启用warmup训练方式，可理解为热身训练
    #     warmup_factor = 1.0 / 1000
    #     warmup_iters = min(1000, len(train_loader) - 1)
    #
    #     lr_scheduler = warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)

    train_loss = torch.zeros(1).to(device)
    model.train()

    for step, (images, indices, label) in enumerate(metric_logger.log_every(train_loader, 50, header)):
        images = images.to(device)

        optimizer.zero_grad()
        predictions, features = model(images)
        loss = torch.zeros(1).to(device)
        for output, feature, index in zip(predictions, features, indices):
            loss += criterion(output, index.to(device))
            ortho_loss = model.orthogonal_regularization(feature.to(device), index.to(device))
            loss = loss + ortho_loss

        loss.backward()
        optimizer.step()

        if lr_scheduler is not None:
            lr_scheduler.step()

        # train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_loss = update_average_loss(train_loss, loss, step)
        metric_logger.update(loss=train_loss)
        now_lr = optimizer.param_groups[0]["lr"]
        metric_logger.update(lr=now_lr)

    return train_loss.item()


@torch.no_grad()
def val_disent_one_epoch(model, val_loader, device, criterion, epoch):
    metric_logger = MetricLogger(delimiter="  ")
    header = 'Validation Epoch: [{}]'.format(epoch)

    val_loss = torch.zeros(1).to(device)
    model.eval()
    all_predictions = []
    all_labels = []

    for step, (images, indices, label) in enumerate(metric_logger.log_every(val_loader, 50, header)):
        images, label = images.to(device), label.to(device)
        # outputs = model(images)
        predictions, features = model(images)
        loss = torch.zeros(1).to(device)

        predicted_indices = []

        # 计算损失并获取每个因子的预测索引
        for output, feature, index in zip(predictions, features, indices):
            loss += criterion(output, index.to(device))
            _, predicted = torch.max(output, 1)
            predicted_indices.append(predicted)  # 保存预测的因子索引
            ortho_loss = model.orthogonal_regularization(feature.to(device), index.to(device))
            loss = loss + ortho_loss

        predicted_indices = torch.stack(predicted_indices, dim=1).cpu().numpy()
        # 转换为最终预测的label
        pred_labels = val_loader.dataset.maper.get_labels_from_indices_batch(predicted_indices)

        all_predictions.extend(pred_labels)

        # val_loss = (val_loss * step + loss.detach()) / (step + 1)

        val_loss = update_average_loss(val_loss, loss, step)

        # test_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())

        all_labels.extend(label.cpu().numpy())
        metric_logger.update(loss=val_loss)

    return val_loss, all_predictions, all_labels


def train_proj_one_epoch(feat_proj, attr_proj, train_loader, optimizer, device, criterion, epoch, warmup=True):
    metric_logger = MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = f'Train Epoch:[{epoch}]'

    lr_scheduler = get_warmup_scheduler(optimizer, train_loader, epoch) if warmup else None
    # lr_scheduler = None
    # if epoch == 0 and warmup is True:  # 当训练第一轮（epoch=0）时，启用warmup训练方式，可理解为热身训练
    #     warmup_factor = 1.0 / 1000
    #     warmup_iters = min(1000, len(train_loader) - 1)
    #
    #     lr_scheduler = warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)

    feat_proj.train()
    attr_proj.train()
    train_loss = torch.zeros(1).to(device)
    for step, (images, attributes, target) in enumerate(metric_logger.log_every(train_loader, 50, header)):
        images, attributes, target = images.to(device), attributes.to(device), target.to(device)
        optimizer.zero_grad()
        feat_embed = feat_proj(images)
        attr_embed = attr_proj(attributes)

        loss = criterion(feat_embed, attr_embed, target)
        loss.backward()
        optimizer.step()

        # train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_loss = update_average_loss(train_loss, loss, step)
        if lr_scheduler is not None:
            lr_scheduler.step()

        metric_logger.update(loss=train_loss)
        now_lr = optimizer.param_groups[0]["lr"]
        metric_logger.update(lr=now_lr)

    return train_loss.item()


@torch.no_grad()
def val_proj_one_epoch(feat_proj, attr_proj, val_loader, device, criterion, epoch):
    metric_logger = MetricLogger(delimiter="  ")
    header = 'Validation Epoch: [{}]'.format(epoch)

    val_loss = torch.zeros(1).to(device)
    feat_proj.eval()
    attr_proj.eval()

    for step, (images, attributes, target) in enumerate(metric_logger.log_every(val_loader, 50, header)):
        images, attributes, target = images.to(device), attributes.to(device), target.to(device)
        feat_embed = feat_proj(images)
        attr_embed = attr_proj(attributes)

        loss = criterion(feat_embed, attr_embed, target)
        val_loss = update_average_loss(val_loss, loss, step)
        # val_loss = (val_loss * step + loss.detach()) / (step + 1)
        metric_logger.update(loss=val_loss)

    return val_loss.item()


def attribute_projection(model, semantic_attribute, semantic_embed, device):
    """
    批量处理npy文件，适配1维输入的模型

    假设npy文件中存储的是1维数组，形状为 (n_features,)
    """
    model = model.to(device)
    model.eval()

    npy_files = [f for f in os.listdir(semantic_attribute) if f.endswith('.npy')]

    if not npy_files:
        print(f"在输入目录 {semantic_attribute} 中未找到npy文件")
        return

    for file_idx, filename in enumerate(npy_files, 1):
        try:
            input_path = os.path.join(semantic_attribute, filename)
            output_path = os.path.join(semantic_embed, filename)

            # 读取1维数据
            data = np.load(input_path)

            # 检查数据维度是否为1维
            if data.ndim != 1:
                raise ValueError(f"文件 {filename} 不是1维数据，实际维度: {data.ndim}")

            # 数据预处理 - 适配1维输入模型
            # 转换为张量并添加批次维度 (1, n_features)
            input_tensor = torch.from_numpy(data).float().to(device)
            input_tensor = input_tensor.unsqueeze(0)  # 添加批次维度

            # 模型推理
            with torch.no_grad():  # 关闭梯度计算以提高效率
                output_tensor = model(input_tensor)

            # 处理输出 - 移除批次维度并转换为numpy数组
            processed_data = output_tensor.squeeze(0).cpu().numpy()

            # 保存结果
            np.save(output_path, processed_data)


        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")














def train_one_epoch(model, train_loader, optimizer, device, criterion, epoch, warmup=True):
    metric_logger = MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = f'Train Epoch:[{epoch}]'

    lr_scheduler = None
    if epoch == 0 and warmup is True:  # 当训练第一轮（epoch=0）时，启用warmup训练方式，可理解为热身训练
        warmup_factor = 1.0 / 1000
        warmup_iters = min(1000, len(train_loader) - 1)

        lr_scheduler = warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)

    train_loss = torch.zeros(1).to(device)
    model.train()

    for step, (images, indices, label) in enumerate(metric_logger.log_every(train_loader, 50, header)):
        images = images.to(device)

        optimizer.zero_grad()
        predictions, features = model(images)
        loss = torch.zeros(1).to(device)
        for output, feature, index in zip(predictions, features, indices):
            loss += criterion(output, index.to(device))
            ortho_loss = model.orthogonal_regularization(feature.to(device), index.to(device))
            loss = loss + ortho_loss

        loss.backward()
        optimizer.step()

        if lr_scheduler is not None:
            lr_scheduler.step()

        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        metric_logger.update(loss=train_loss)
        now_lr = optimizer.param_groups[0]["lr"]
        metric_logger.update(lr=now_lr)

    return train_loss.item()


@torch.no_grad()
def val_one_epoch(model, val_loader, device, criterion, epoch):
    metric_logger = MetricLogger(delimiter="  ")
    header = 'Validation Epoch: [{}]'.format(epoch)

    val_loss = torch.zeros(1).to(device)
    model.eval()
    all_predictions = []
    all_labels = []

    for step, (images, indices, label) in enumerate(metric_logger.log_every(val_loader, 50, header)):
        images, label = images.to(device), label.to(device)
        # outputs = model(images)
        predictions, features = model(images)
        loss = torch.zeros(1).to(device)

        predicted_indices = []

        # 计算损失并获取每个因子的预测索引
        for output, feature, index in zip(predictions, features, indices):
            loss += criterion(output, index.to(device))
            _, predicted = torch.max(output, 1)
            predicted_indices.append(predicted)  # 保存预测的因子索引
            ortho_loss = model.orthogonal_regularization(feature.to(device), index.to(device))
            loss = loss + ortho_loss

        predicted_indices = torch.stack(predicted_indices, dim=1).cpu().numpy()
        # 转换为最终预测的label
        pred_labels = val_loader.dataset.maper.get_labels_from_indices_batch(predicted_indices)

        all_predictions.extend(pred_labels)

        val_loss = (val_loss * step + loss.detach()) / (step + 1)

        # test_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())

        all_labels.extend(label.cpu().numpy())
        metric_logger.update(loss=val_loss)

    return val_loss, all_predictions, all_labels


@torch.no_grad()
def predict(model, data_dir, device, transform, image_subdir):
    """
    模型预测函数，返回DataFrame格式的预测结果（n行×m列）

    参数:
    - n: 取top-n预测结果
    - idx_to_labels: 类别索引到名称的映射字典
    - classes: 所有类别名称列表
    """
    model.eval()
    df_data, maper = generate_image_dataframe(data_dir, image_subdir)
    condition_features = []
    fault_type_features = []
    severity_features = []
    df_pred = pd.DataFrame()
    att = []
    for inx, row in tqdm(df_data.iterrows()):
        img_path = row['图片路径']
        img_pil = Image.open(img_path).convert('RGB')
        input_img = transform(img_pil).to(device)  # 预处理
        input_img = input_img.unsqueeze(0)
        pred_logits, features = model(input_img)  # 执行前向预测，得到所有类别的 logit 预测分数
        predicted_indices = []

        for pred_logit in pred_logits:
            pred_softmax = torch.softmax(pred_logit, dim=1)
            _, predicted = torch.max(pred_softmax, 1)
            predicted_indices.append(predicted.cpu())  # 保存预测的因子索引

        condition_features.append(features[0].squeeze().detach().cpu().numpy())
        fault_type_features.append(features[1].squeeze().detach().cpu().numpy())
        severity_features.append(features[2].squeeze().detach().cpu().numpy())
        att.append(merge_to_192d(features).squeeze().detach().cpu().numpy())

        # 转换为最终预测的label
        predicted_indices = torch.stack(predicted_indices, dim=1).numpy()
        pred_label = maper.get_labels_from_indices_batch(predicted_indices)
        pred_dict = {
            '类别预测ID': pred_label[0] if len(pred_label) == 1 else pred_label,
            '工况预测ID': predicted_indices[0, 0] if len(predicted_indices) == 1 else predicted_indices[:, 0],
            '故障类型预测ID': predicted_indices[0, 1] if len(predicted_indices) == 1 else predicted_indices[:, 1],
            '故障程度预测ID': predicted_indices[0, 2] if len(predicted_indices) == 1 else predicted_indices[:, 2]
        }
        df_pred = pd.concat([df_pred, pd.DataFrame([pred_dict])], ignore_index=True)

    df = pd.concat([df_data, df_pred], axis=1)

    return df, condition_features, fault_type_features, severity_features, att


def train_cae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch):
    result = {'train_loss': 0., 'val_loss': 0., 'epoch': 0}
    train_loss = torch.zeros(1).to(device)
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
    for step, (images, label) in enumerate(train_iterator):
        images = images.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, images)

        loss.backward()
        optimizer.step()

        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())

    print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
    val_loss = torch.zeros(1).to(device)
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
    with torch.no_grad():
        for step, (images, label) in enumerate(val_iterator):
            images = images.to(device)

            outputs = model(images)
            loss = criterion(outputs, images)
            val_loss = (val_loss * step + loss.detach()) / (step + 1)

            val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
    print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
    result['train_loss'] = train_loss.item()
    result['val_loss'] = val_loss.item()
    result['epoch'] = epoch + 1
    return result


@torch.no_grad()
def extract_features_from_csv(model, csv_path, device, transform):
    """
    根据CSV文件中的图片路径提取对应图片的特征（不处理异常，出错直接终止）

    参数:
    - model: 训练好的模型（输出格式为 (预测logits, 特征列表)）
    - csv_path: 包含图片路径的CSV文件路径（需有"图片路径"列）
    - device: 运行设备（如torch.device('cuda')）
    - transform: 图片预处理变换
    """
    model.eval()
    condition_features = []
    fault_type_features = []
    severity_features = []

    # 读取CSV文件
    df = pd.read_csv(csv_path)
    if "图片路径" not in df.columns:
        raise ValueError("CSV文件必须包含'图片路径'列")

    # 遍历图片路径提取特征（无异常处理）
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="提取特征"):
        img_path = row["图片路径"]

        # 加载图片并预处理（无异常捕获，出错直接报错）
        img_pil = Image.open(img_path).convert("RGB")
        input_img = transform(img_pil).to(device)
        input_img = input_img.unsqueeze(0)

        # 前向传播获取特征
        pred_logits, features = model(input_img)

        # 提取并保存特征
        condition_features.append(features[0].squeeze().detach().cpu().numpy())
        fault_type_features.append(features[1].squeeze().detach().cpu().numpy())
        severity_features.append(features[2].squeeze().detach().cpu().numpy())

    return condition_features, fault_type_features, severity_features
