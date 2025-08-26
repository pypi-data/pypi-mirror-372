import os

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import classification_report
from tqdm import tqdm

from zsl_ma.tools.tool import generate_image_dataframe, generate_zsl_image_dataframe
from typing import List, Tuple, Optional
import torch.nn.functional as F


def merge_to_192d(features):
    """
    将3个64维张量拼接为192维向量。
    参数：features - 长度为3的列表，每个元素是64维张量（支持(64,)或(1,64)形状）。
    返回：192维张量（形状: (192,)）。
    """
    # 1. 统一处理每个张量的形状（挤压为1D）
    processed = []
    for tensor in features:
        # 挤压多余维度（如(1,64) → (64,)）
        squeezed = tensor.squeeze()
        processed.append(squeezed)

    # 2. 沿特征维度拼接（3个64维 → 192维）
    merged = torch.cat(processed, dim=0)
    return merged


#
# @torch.no_grad()
# def disent_predict(model,
#                    data_dir: str,
#                    device: torch.device,
#                    transform,
#                    image_subdir: str,
#                    class_list_path: Optional[str] = None,
#                    batch_size: int = 32) -> Tuple[
#     pd.DataFrame, List[np.ndarray], List[np.ndarray]]:
#     """
#     特征解耦模型批量预测函数（适配任意数量因子，返回类型符合 tuple[DataFrame, list[ndarray], list[ndarray]]）
#
#     参数:
#         model: 训练好的解纠缠预测模型（支持批量输入，输出logits/features长度=因子数）
#         data_dir: 数据根目录
#         device: 模型运行设备（如torch.device('cuda:0')）
#         transform: 图片预处理流水线
#         image_subdir: 图片类别文件夹的父目录
#         class_list_path: 类别列表txt路径（可选）
#         batch_size: 批量预测大小（默认32，可根据GPU显存调整）
#
#     返回:
#         Tuple包含：
#             - result_df: 原始信息+预测结果的DataFrame（含动态因子预测列）
#             - factor_features_list: 各因子特征列表（每个元素是单个ndarray，形状[总样本数, 特征维度]，顺序=因子顺序）
#             - img_features: 合并后的192d图像特征列表（每个元素是单个样本的ndarray，形状[192,]）
#     """
#     model = model.to(device)
#     model.eval()
#
#     # 1. 生成图像DataFrame并获取因子映射器（动态获取因子信息）
#     image_df, maper = generate_image_dataframe(
#         data_dir, image_subdir, class_list_path=class_list_path, parse_factors=True
#     )
#     if not maper.parse_factors or maper.num_factors is None:
#         raise RuntimeError(
#             "因子解析未开启或失败！请确保 generate_image_dataframe 中 parse_factors=True，"
#             "且 FactorLabelMapper 成功解析出因子数量（num_factors）"
#         )
#     num_factors = maper.num_factors  # 动态因子总数
#     factor_names = maper.factor_names if maper.factor_names else [
#         f"因子{i + 1}" for i in range(num_factors)
#     ]
#     total_imgs = len(image_df)
#
#     # 2. 初始化存储列表（关键：因子特征用列表暂存批量ndarray，后续拼接为单个ndarray）
#     pred_labels_list: List[int] = []
#     pred_factor_ids_list: List[List[int]] = [[] for _ in range(num_factors)]
#
#     # 因子特征暂存：每个元素是「批量特征ndarray列表」（后续用np.concatenate合并）
#     factor_feats_batch_list: List[List[np.ndarray]] = [[] for _ in range(num_factors)]
#     img_features: List[np.ndarray] = []  # 保持原格式：每个元素是单个样本的192d特征
#
#     # 3. 批量预测主循环
#     for batch_start in tqdm(range(0, total_imgs, batch_size), desc="批量预测"):
#         batch_end = min(batch_start + batch_size, total_imgs)
#         batch_df = image_df.iloc[batch_start:batch_end]
#         batch_img_paths = batch_df["图片路径"].tolist()
#
#         # 3.1 图片预处理
#         batch_imgs = []
#         for img_path in batch_img_paths:
#             img_pil = Image.open(img_path).convert("RGB")
#             img_tensor = transform(img_pil)
#             batch_imgs.append(img_tensor)
#         batch_tensor = torch.stack(batch_imgs, dim=0).to(device)
#
#         # 3.2 前向传播（校验模型输出与因子数匹配）
#         pred_logits, features = model(batch_tensor)
#         if len(pred_logits) != num_factors or len(features) != num_factors:
#             raise ValueError(
#                 f"模型输出因子数量与数据因子数量不匹配！"
#                 f"模型输出：logits={len(pred_logits)}个, features={len(features)}个；"
#                 f"数据解析：{num_factors}个因子"
#             )
#
#         # 3.3 解析预测结果
#         batch_pred_indices = []
#         for factor_logit in pred_logits:
#             factor_softmax = torch.softmax(factor_logit, dim=1)
#             _, factor_pred_idx = torch.max(factor_softmax, dim=1)
#             batch_pred_indices.append(factor_pred_idx.cpu().tolist())
#         batch_pred_indices = list(zip(*batch_pred_indices))  # [batch_size, num_factors]
#         batch_pred_labels = maper.get_labels_from_indices_batch(np.array(batch_pred_indices))
#
#         # 3.4 提取特征（暂存批量ndarray，不直接extend）
#         # 因子特征：每个批量特征是ndarray（形状[batch_size, 特征维度]），存入暂存列表
#         for factor_idx in range(num_factors):
#             batch_feat = features[factor_idx].detach().cpu().numpy()  # [batch_size, dim]
#             factor_feats_batch_list[factor_idx].append(batch_feat)
#         # 合并特征：保持原格式（每个样本是独立ndarray）
#         batch_merge_feat = merge_to_192d(features).detach().cpu().numpy()  # [batch_size, 192]
#         img_features.extend([feat for feat in batch_merge_feat])  # 拆解为单个样本特征
#
#         # 3.5 存储预测结果
#         pred_labels_list.extend(batch_pred_labels)
#         for factor_idx in range(num_factors):
#             factor_pred_ids = [sample_pred[factor_idx] for sample_pred in batch_pred_indices]
#             pred_factor_ids_list[factor_idx].extend(factor_pred_ids)
#
#     # 4. 关键：合并因子特征（将每个因子的批量列表拼接为单个ndarray）
#     factor_features_list: List[np.ndarray] = []
#     for factor_idx in range(num_factors):
#         # 拼接该因子的所有批量特征（形状从 [batch1, dim], [batch2, dim] → [total_imgs, dim]）
#         merged_feat = np.concatenate(factor_feats_batch_list[factor_idx], axis=0)
#         factor_features_list.append(merged_feat)
#         # 校验：拼接后样本数与总样本数一致
#         if merged_feat.shape[0] != total_imgs:
#             raise RuntimeError(
#                 f"因子{factor_idx + 1}特征拼接后样本数不匹配！"
#                 f"预期{total_imgs}个，实际{merged_feat.shape[0]}个"
#             )
#
#     # 5. 构建结果DataFrame
#     pred_df_dict = {"类别预测ID": pred_labels_list}
#     for factor_idx in range(num_factors):
#         pred_df_dict[f"{factor_names[factor_idx]}预测ID"] = pred_factor_ids_list[factor_idx]
#     pred_df = pd.DataFrame(pred_df_dict)
#     result_df = pd.concat([image_df, pred_df], axis=1)
#
#     # 6. 返回符合类型要求的结果
#     return result_df, factor_features_list, img_features
@torch.no_grad()
def disent_predict(model,
                   data_dir: str,
                   device: torch.device,
                   transform,
                   image_subdir: str,
                   factor_names,
                   class_list_path: Optional[str] = None,
                   batch_size: int = 32) -> Tuple[
    pd.DataFrame, List[np.ndarray], List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
    """
    特征解耦模型批量预测函数

    参数:
        model: 训练好的解纠缠预测模型（支持批量输入）
        data_dir: 数据根目录
        device: 模型运行设备（如torch.device('cuda:0')）
        transform: 图片预处理流水线
        image_subdir: 图片类别文件夹的父目录
        class_list_path: 类别列表txt路径（可选）
        batch_size: 批量预测大小（默认32，可根据GPU显存调整）

    返回:
        Tuple包含：
            - result_df: 原始信息+预测结果的DataFrame
            - condition_features: 工况因子特征列表
            - fault_type_features: 故障类型因子特征列表
            - severity_features: 故障程度因子特征列表
            - img_features: 合并后的192d图像特征列表
    """
    model = model.to(device)
    model.eval()
    image_df, maper = generate_image_dataframe(data_dir, image_subdir, class_list_path=class_list_path,
                                               parse_factors=True, factor_names=factor_names)
    total_imgs = len(image_df)
    # 2. 初始化存储列表
    condition_features: List[np.ndarray] = []
    fault_type_features: List[np.ndarray] = []
    severity_features: List[np.ndarray] = []
    img_features: List[np.ndarray] = []
    pred_labels_list: List[int] = []
    pred_condition_ids_list: List[int] = []
    pred_fault_type_ids_list: List[int] = []
    pred_severity_ids_list: List[int] = []
    # 3. 批量预测主循环
    for batch_start in tqdm(range(0, total_imgs, batch_size), desc="批量预测"):
        # 3.1 获取当前批次图片
        batch_end = min(batch_start + batch_size, total_imgs)
        batch_df = image_df.iloc[batch_start:batch_end]
        batch_img_paths = batch_df["图片路径"].tolist()

        # 3.2 批量读取并预处理图片
        batch_imgs = []
        for img_path in batch_img_paths:
            img_pil = Image.open(img_path).convert("RGB")
            img_tensor = transform(img_pil)
            batch_imgs.append(img_tensor)
        batch_tensor = torch.stack(batch_imgs, dim=0).to(device)

        # 3.3 批量前向传播
        pred_logits, features = model(batch_tensor)

        # 3.4 解析预测结果
        # 3.4.1 获取各因子预测ID
        batch_pred_indices = []
        for factor_logit in pred_logits:
            factor_softmax = torch.softmax(factor_logit, dim=1)
            _, factor_pred_idx = torch.max(factor_softmax, dim=1)
            batch_pred_indices.append(factor_pred_idx.cpu())
        batch_pred_indices = torch.stack(batch_pred_indices, dim=0).T.numpy()

        # 3.4.2 获取最终预测类别
        batch_pred_labels = maper.get_labels_from_indices_batch(batch_pred_indices)

        # 3.5 提取特征
        # 工况特征
        batch_condition_feat = features[0].detach().cpu().numpy()
        # 故障类型特征
        batch_fault_feat = features[1].detach().cpu().numpy()
        # 故障程度特征
        batch_severity_feat = features[2].detach().cpu().numpy()
        # 合并特征
        batch_merge_feat = merge_to_192d(features).detach().cpu().numpy()

        # 3.6 存储结果（按顺序添加）
        pred_labels_list.extend(batch_pred_labels)
        pred_condition_ids_list.extend(batch_pred_indices[:, 0])
        pred_fault_type_ids_list.extend(batch_pred_indices[:, 1])
        pred_severity_ids_list.extend(batch_pred_indices[:, 2])

        condition_features.extend(batch_condition_feat)
        fault_type_features.extend(batch_fault_feat)
        severity_features.extend(batch_severity_feat)
        img_features.extend(batch_merge_feat)

    # 4. 构建结果DataFrame
    pred_df = pd.DataFrame({
        "类别预测ID": pred_labels_list,
        "工况预测ID": pred_condition_ids_list,
        "故障类型预测ID": pred_fault_type_ids_list,
        "故障程度预测ID": pred_severity_ids_list
    })
    result_df = pd.concat([image_df, pred_df], axis=1)

    return result_df, condition_features, fault_type_features, severity_features, img_features


@torch.no_grad()
def similarity_predict(model,
                       data_path,
                       semantic_path,
                       test_image_class,
                       predict_class_file,
                       # attributes,
                       device: torch.device,
                       transform,
                       batch_size: int = 32):
    # 模型准备
    model = model.to(device)
    model.eval()
    # 将注意力矩阵移至目标设备
    image_df = generate_zsl_image_dataframe(data_path, test_image_class, predict_class_file)
    classes = image_df['标签名称'].values
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
    print(classification_report(image_df['标注类别ID'].values, pred_labels_list,
                                target_names=classes))

    return result_df


@torch.no_grad()
def cls_predict(model,
                data_path,
                test_image_class,
                device: torch.device,
                transform,
                predict_class_file=None,
                batch_size: int = 32):
    # 模型准备
    model = model.to(device)
    model.eval()
    # 将注意力矩阵移至目标设备
    image_df = generate_zsl_image_dataframe(data_path, test_image_class, predict_class_file)

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
    print(classification_report(image_df['标注类别ID'].values, pred_labels_list,
                                digits=4))

    return result_df
