import os
from typing import List, Optional

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from PIL import Image
from sklearn.metrics import classification_report
from tqdm import tqdm

from zsl_ma.tools.tool import generate_image_dataframe, generate_zsl_image_dataframe


def batch_concat_vectors(features):
    """
    将n个形状为[batch, dim_i]的向量沿特征维度拼接为[batch, n*dim_sum]的向量，
    其中n为向量数量，dim_sum为所有输入向量的特征维度之和（即n*dim_sum = sum(dim_i)）。
    每个批次中对应索引的样本（如idx=0到batch-1）的特征会被依次拼接。

    参数：
        features - 长度为n的列表，每个元素是形状为[batch, dim_i]的张量（n≥1，batch尺寸需一致）。

    返回：
        拼接后的张量，形状为[batch, sum(dim_i)]，其中sum(dim_i)为所有输入向量的特征维度之和。

    异常：
        ValueError - 若输入列表为空、张量维度不是2维，或各张量的batch尺寸不一致。
    """
    # 1. 校验输入有效性
    if not features:
        raise ValueError("输入特征列表不能为空，请至少提供1个向量")

    # 获取第一个张量的batch尺寸作为基准
    batch_size = features[0].size(0)

    # 检查所有张量的维度和batch尺寸
    for i, tensor in enumerate(features):
        if tensor.dim() != 2:
            raise ValueError(f"第{i}个张量维度错误，需为2维[batch, dim]，实际为{tensor.dim()}维")
        if tensor.size(0) != batch_size:
            raise ValueError(f"第{i}个张量batch尺寸不匹配，基准为{batch_size}，实际为{tensor.size(0)}")

    # 2. 沿特征维度（dim=1）拼接所有向量
    # 每个样本的特征会按输入顺序拼接，最终维度为各dim之和
    merged = torch.cat(features, dim=1)

    return merged


@torch.no_grad()
def disent_predict(model,
                   data_dir: str,
                   device: torch.device,
                   transform,
                   image_subdir: str,
                   class_list_path: Optional[str] = None,
                   factor_index_map_path: Optional[str] = None,  # 新增：用于获取因子映射
                   ignore_factors: Optional[List[str]] = None,  # 新增：传递忽略因子
                   batch_size: int = 32):
    """
    特征解耦模型批量预测函数（支持动态因子数量）

    参数:
        model: 训练好的解纠缠预测模型（输出logits和特征数量需与因子数量一致）
        data_dir: 数据根目录
        device: 模型运行设备
        transform: 图片预处理流水线
        image_subdir: 图片类别文件夹的父目录
        class_list_path: 类别列表txt路径（可选）
        factor_index_map_path: 因子索引映射文件路径（用于动态获取因子信息）
        ignore_factors: 需要忽略的因子列表（纯因子名）
        batch_size: 批量预测大小

    返回:
        Tuple包含：
            - result_df: 原始信息+动态因子预测结果的DataFrame
            - factor_features: 各因子特征列表（顺序与mapper.factor_base_names一致）
            - img_features: 合并后的图像特征列表
    """
    model = model.to(device)
    model.eval()

    # 1. 生成图像数据框并获取因子映射器（关键：通过mapper获取实际因子信息）
    image_df, mapper = generate_image_dataframe(
        root_dir=data_dir,
        image_subdir=image_subdir,
        class_list_path=class_list_path,
        factor_index_map_path=factor_index_map_path,  # 传入因子映射文件路径
        ignore_factors=ignore_factors  # 传入忽略因子
    )
    total_imgs = len(image_df)
    num_factors = mapper.num_factors  # 动态获取因子数量
    factor_names = mapper.factor_base_names  # 动态获取因子名称（纯因子名）
    classes = mapper.classes
    # 2. 初始化存储列表（根据因子数量动态生成）
    factor_features: List[List[np.ndarray]] = [[] for _ in range(num_factors)]  # 每个因子的特征列表
    img_features: List[np.ndarray] = []
    pred_labels_list: List[int] = []
    # 动态生成每个因子的预测ID存储列表
    pred_factor_ids_lists: List[List[int]] = [[] for _ in range(num_factors)]

    # 3. 批量预测主循环
    for batch_start in tqdm(range(0, total_imgs, batch_size), desc="批量预测"):
        batch_end = min(batch_start + batch_size, total_imgs)
        batch_df = image_df.iloc[batch_start:batch_end]
        batch_img_paths = batch_df["图片路径"].tolist()

        # 3.1 批量读取并预处理图片
        batch_imgs = []
        for img_path in batch_img_paths:
            img_pil = Image.open(img_path).convert("RGB")
            img_tensor = transform(img_pil)
            batch_imgs.append(img_tensor)
        batch_tensor = torch.stack(batch_imgs, dim=0).to(device)

        # 3.2 批量前向传播（假设model输出的logits和features数量与num_factors一致）
        pred_logits, features = model(batch_tensor)
        if len(pred_logits) != num_factors or len(features) != num_factors:
            raise ValueError(
                f"模型输出的logits/features数量({len(pred_logits)}/{len(features)})与因子数量({num_factors})不匹配")

        # 3.3 解析各因子预测ID
        batch_pred_indices = []
        for factor_logit in pred_logits:
            factor_softmax = torch.softmax(factor_logit, dim=1)
            _, factor_pred_idx = torch.max(factor_softmax, dim=1)
            batch_pred_indices.append(factor_pred_idx.cpu())  # 每个元素是(batch_size,)的tensor
        # 转换为shape: (batch_size, num_factors)的numpy数组
        batch_pred_indices = torch.stack(batch_pred_indices, dim=0).T.numpy()

        # 3.4 获取最终预测类别
        batch_pred_labels = mapper.get_labels_from_indices_batch(batch_pred_indices)

        # 3.5 提取特征（按因子顺序存储）
        for i in range(num_factors):
            batch_factor_feat = features[i].detach().cpu().numpy()
            factor_features[i].extend(batch_factor_feat)
        # 合并特征（假设存在merge_to_192d函数）
        batch_merge_feat = batch_concat_vectors(features).detach().cpu().numpy()
        img_features.extend(batch_merge_feat)

        # 3.6 存储预测结果
        pred_labels_list.extend(batch_pred_labels)
        # 按因子顺序存储预测ID
        for i in range(num_factors):
            pred_factor_ids_lists[i].extend(batch_pred_indices[:, i])

    # 4. 构建动态结果DataFrame
    # 4.1 构建预测结果字典（表头随因子名称动态变化）
    pred_data = {"类别预测ID": pred_labels_list}
    for i, factor_name in enumerate(factor_names):
        pred_data[f"{factor_name}预测ID"] = pred_factor_ids_lists[i]
    pred_df = pd.DataFrame(pred_data)

    # 4.2 拼接原始数据和预测结果
    result_df = pd.concat([image_df, pred_df], axis=1)
    print(classification_report(image_df['标注类别ID'].values, pred_labels_list,
                                target_names=classes,digits=4))

    return result_df, factor_features, img_features


@torch.no_grad()
def similarity_predict(model,
                       data_path,
                       semantic_path,
                       test_image_class,
                       factor_index_map_path,
                       device: torch.device,
                       transform,
                       ignore_factors,
                       batch_size: int = 32):
    # 模型准备
    model = model.to(device)
    model.eval()
    # 将注意力矩阵移至目标设备
    image_df, maper = generate_image_dataframe(data_path, 'val',
                                               test_image_class, factor_index_map_path,
                                               ignore_factors=ignore_factors,
                                               need_parse_factors=False)
    classes = maper.classes
    attributes = []
    for cls_name in classes:
        npy_path = os.path.join(semantic_path, f"{cls_name}.npy")
        attributes.append(np.load(npy_path, allow_pickle=True))
    attributes = torch.tensor(attributes).to(device)
    total_samples = len(image_df)
    pred_labels_list: List[int] = []

    # 批量预测主循环
    for batch_start in tqdm(range(0, total_samples, batch_size)):
        # 获取当前批次数据
        batch_end = min(batch_start + batch_size, total_samples)
        batch_df = image_df.iloc[batch_start:batch_end]

        # 读取并预处理图片
        batch_imgs = []
        for img_path in batch_df["图片路径"].tolist():
            img_pil = Image.open(img_path).convert("RGB")
            img_tensor = transform(img_pil)
            batch_imgs.append(img_tensor)
        batch_tensor = torch.stack(batch_imgs, dim=0).to(device)

        # 模型前向传播
        outputs = model(batch_tensor)

        # 计算余弦相似度并获取预测结果
        distances = F.cosine_similarity(
            outputs.unsqueeze(1),
            attributes.unsqueeze(0),
            dim=2,
            eps=1e-8
        )
        _, predicted = torch.max(distances, dim=1)
        pred_labels_list.extend(predicted.cpu().numpy())

    pred_df = pd.DataFrame({
        "类别预测ID": pred_labels_list
    })
    result_df = pd.concat([image_df, pred_df], axis=1)
    result = classification_report(image_df['标注类别ID'].values, pred_labels_list,
                                target_names=classes)
    print(result)

    return result_df,result


@torch.no_grad()
def cls_predict(model,
                data_path,
                test_image_class,
                device: torch.device,
                transform,
                batch_size: int = 32):
    # 模型准备
    model = model.to(device)
    model.eval()
    # 将注意力矩阵移至目标设备
    image_df, maper = generate_image_dataframe(data_path, 'val',
                                               test_image_class,
                                               need_parse_factors=False)

    total_samples = len(image_df)
    pred_labels_list: List[int] = []

    # 批量预测主循环
    for batch_start in tqdm(range(0, total_samples, batch_size)):
        # 获取当前批次数据
        batch_end = min(batch_start + batch_size, total_samples)
        batch_df = image_df.iloc[batch_start:batch_end]

        # 读取并预处理图片
        batch_imgs = []
        for img_path in batch_df["图片路径"].tolist():
            img_pil = Image.open(img_path).convert("RGB")
            img_tensor = transform(img_pil)
            batch_imgs.append(img_tensor)
        batch_tensor = torch.stack(batch_imgs, dim=0).to(device)

        # 模型前向传播
        outputs = model(batch_tensor)
        _, predicted = torch.max(outputs, 1)
        pred_labels_list.extend(predicted.cpu().numpy())

    pred_df = pd.DataFrame({
        "类别预测ID": pred_labels_list
    })
    result_df = pd.concat([image_df, pred_df], axis=1)
    result = classification_report(image_df['标注类别ID'].values, pred_labels_list,
                                digits=4)
    print(result)

    return result_df, result


@torch.no_grad()
def euclidean_distance_predict(  # 函数名修改：体现欧几里得距离预测
    model,
    data_path,
    semantic_path,
    test_image_class,
    factor_index_map_path,
    device: torch.device,
    transform,
    ignore_factors,
    batch_size: int = 32
):
    # 模型准备：保持不变（eval模式+设备迁移）
    model = model.to(device)
    model.eval()

    # 生成图片数据框和类别映射器：保持原数据处理逻辑
    image_df, maper = generate_image_dataframe(
        data_path, 'val',
        test_image_class, factor_index_map_path,
        ignore_factors=ignore_factors,
        need_parse_factors=False
    )
    classes = maper.classes  # 类别列表（用于后续分类报告）
    total_samples = len(image_df)
    pred_labels_list: List[int] = []

    # 加载类别语义特征（attributes）：保持原加载逻辑
    attributes = []
    for cls_name in classes:
        npy_path = os.path.join(semantic_path, f"{cls_name}.npy")
        attributes.append(np.load(npy_path, allow_pickle=True))
    attributes = torch.tensor(attributes).to(device)  # shape: [num_classes, feature_dim]

    # 批量预测主循环：核心修改在「距离计算」和「预测结果选择」
    for batch_start in tqdm(range(0, total_samples, batch_size)):
        batch_end = min(batch_start + batch_size, total_samples)
        batch_df = image_df.iloc[batch_start:batch_end]

        # 1. 读取并预处理图片：保持原逻辑
        batch_imgs = []
        for img_path in batch_df["图片路径"].tolist():
            img_pil = Image.open(img_path).convert("RGB")
            img_tensor = transform(img_pil)
            batch_imgs.append(img_tensor)
        batch_tensor = torch.stack(batch_imgs, dim=0).to(device)  # shape: [batch_size, C, H, W]

        # 2. 模型前向传播：保持原逻辑（获取图片特征）
        outputs = model(batch_tensor)  # shape: [batch_size, feature_dim]

        # 3. 核心修改：计算欧几里得距离（替换原余弦相似度）
        # 扩展维度以实现「批量样本-所有类别」的距离计算
        # outputs.unsqueeze(1): [batch_size, 1, feature_dim]
        # attributes.unsqueeze(0): [1, num_classes, feature_dim]
        # 欧几里得距离 = L2范数，沿特征维度（dim=2）计算
        distances = F.pairwise_distance(
            outputs.unsqueeze(1),  # 批量样本扩展类别维度
            attributes.unsqueeze(0),  # 类别特征扩展样本维度
            p=2  # p=2 对应欧几里得距离（L2范数）
        )  # 最终shape: [batch_size, num_classes]（每个样本到每个类别的距离）

        # 4. 核心修改：选择「距离最小」的类别作为预测结果（原逻辑是选相似度最大）
        _, predicted = torch.min(distances, dim=1)  # dim=1：对每个样本的所有类别距离取最小
        pred_labels_list.extend(predicted.cpu().numpy())  # 保存预测ID

    # 结果整理：保持原逻辑（拼接数据框+生成分类报告）
    pred_df = pd.DataFrame({"类别预测ID": pred_labels_list})
    result_df = pd.concat([image_df, pred_df], axis=1)

    # 计算分类报告（标注ID vs 预测ID）
    result = classification_report(
        image_df['标注类别ID'].values,
        pred_labels_list,
        target_names=classes
    )
    print(result)

    return result_df, result


