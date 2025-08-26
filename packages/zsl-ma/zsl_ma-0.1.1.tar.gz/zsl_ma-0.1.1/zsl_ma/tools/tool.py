import os
import re
from datetime import datetime
from typing import List, Dict, Any
# from zsl_ma.dataset_utils.dataset import FactorLabelMapper
from typing import Tuple, Optional

import numpy as np
import pandas as pd
import pytz
import seaborn as sns
import torch
import wandb
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
from sklearn.metrics import ConfusionMatrixDisplay, classification_report

from zsl_ma.dataset_utils.FactorLabelMapper import FactorLabelMapper, load_class_list


def setup_save_dirs(parent_dir: str, prefix: Optional[str]) -> Tuple[str, str, str]:
    """
    目录创建函数：若目录创建失败，直接抛出异常终止程序，而非返回None。
    功能：
    1. 若prefix不为None：在parent_dir下创建「前缀-数字」格式的编号文件夹（如"exp-1"）。
    2. 若prefix为None：直接使用parent_dir作为根保存目录。
    3. 统一创建子目录：images、checkpoints、attributes（含三级子目录：avg_disent_feats、semantic_attribute、semantic_embed）。

    参数:
        parent_dir: 父目录路径（对应configs.save_dir）
        prefix: 文件夹前缀（对应configs.prefix，可为None）

    返回:
        Tuple[save_dir, img_dir, model_dir]: 成功创建的根目录、图像目录、模型目录路径。
        （若失败，会直接抛出异常，不会返回）
    """
    # ------------------------------
    # 1. 确保父目录存在（不存在则创建，失败则抛异常）
    # ------------------------------
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)  # 失败时抛出 OSError（如权限不足、路径无效）

    # ------------------------------
    # 2. 确定根保存目录 save_dir
    # ------------------------------
    if prefix is None:
        save_dir = parent_dir
    else:
        # 正则匹配现有编号文件夹（如"exp-1"）
        escaped_prefix = re.escape(prefix)
        pattern = re.compile(f'^{escaped_prefix}-(\\d+)$')
        existing_numbers = []

        # 收集现有有效编号
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isdir(item_path):
                match = pattern.match(item)
                if match:
                    try:
                        existing_numbers.append(int(match.group(1)))
                    except ValueError:
                        continue  # 忽略数字部分无效的文件夹（如"exp-abc"）

        # 计算下一个可用编号
        if not existing_numbers:
            next_number = 1
        else:
            existing_numbers.sort()
            next_number = 1
            for num in existing_numbers:
                if num > next_number:
                    break
                next_number = num + 1

        # 创建编号文件夹（若已存在，抛 FileExistsError）
        new_folder_name = f"{prefix}-{next_number}"
        save_dir = os.path.join(parent_dir, new_folder_name)
        os.makedirs(save_dir, exist_ok=False)  # exist_ok=False 确保文件夹不存在时才创建

    # ------------------------------
    # 3. 创建子目录（images、checkpoints、attributes及其三级子目录）
    # ------------------------------
    img_dir = os.path.join(save_dir, "images")
    model_dir = os.path.join(save_dir, "checkpoints")
    attr_dir = os.path.join(save_dir, "attributes")
    sub_attr_dirs = [
        os.path.join(attr_dir, "avg_disent_feats"),
        os.path.join(attr_dir, "semantic_attribute"),
        os.path.join(attr_dir, "semantic_embed")
    ]

    # 允许子目录已存在（exist_ok=True），但其他错误（如权限不足）仍抛异常
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(attr_dir, exist_ok=True)
    for sub_dir in sub_attr_dirs:
        os.makedirs(sub_dir, exist_ok=True)

    return save_dir, img_dir, model_dir


def make_save_dirs(root_dir):
    img_dir = os.path.join(root_dir, 'images')
    model_dir = os.path.join(root_dir, 'checkpoints')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    print(f'The output folder:{img_dir},{model_dir} has been created.')
    return img_dir, model_dir


def get_device():
    return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


def calculate_metric(all_labels, all_predictions, classes, class_metric=False, average='macro avg'):
    metric = classification_report(y_true=all_labels, y_pred=all_predictions, target_names=classes
                                   , digits=4, output_dict=True)
    if not class_metric:
        metric = {
            'accuracy': metric.get('accuracy'),
            'precision': metric.get(average).get('precision'),
            'recall': metric.get(average).get('recall'),
            'f1-score': metric.get(average).get('f1-score'),
        }
        return metric
    else:
        return metric


def plot_confusion_matrix(all_labels,
                          all_predictions,
                          classes,
                          name='confusion_matrix.png',
                          normalize=None,
                          cmap=plt.cm.Blues,
                          ):
    ConfusionMatrixDisplay.from_predictions(all_labels,
                                            all_predictions,
                                            display_labels=classes,
                                            cmap=cmap,
                                            normalize=normalize,
                                            xticks_rotation=45
                                            )
    plt.savefig(name, dpi=500)
    plt.close()


def get_wandb_runs(
        project_path: str,
        default_name: str = "未命名",
        api_key: Optional[str] = None,
        per_page: int = 1000
) -> List[Dict[str, str]]:
    """
    获取指定 WandB 项目的所有运行信息（ID 和 Name）

    Args:
        project_path (str): 项目路径,格式为 "username/project_name"
        default_name (str): 当运行未命名时的默认显示名称（默认:"未命名"）
        api_key (str, optional): WandB API 密钥,若未设置环境变量则需传入
        per_page (int): 分页查询每页数量（默认1000,用于处理大量运行）

    Returns:
        List[Dict]: 包含运行信息的字典列表,格式 [{"id": "...", "name": "..."}]

    Raises:
        ValueError: 项目路径格式错误
        wandb.errors.UsageError: API 密钥无效或未登录
    """
    # 参数校验
    if "/" not in project_path or len(project_path.split("/")) != 2:
        raise ValueError("项目路径格式应为 'username/project_name'")

    # 登录（仅在需要时）
    if api_key:
        wandb.login(key=api_key)
    elif not wandb.api.api_key:
        raise wandb.errors.UsageError("需要提供API密钥或预先调用wandb.login()")

    # 初始化API
    api = wandb.Api()

    try:
        # 分页获取所有运行（自动处理分页逻辑）
        runs = api.runs(project_path, per_page=per_page)
        print(f'共获取{len(runs)}个run')
        result = [
            {
                "id": run.id,
                "name": run.name or default_name,
                "url": run.url,  # 增加实用字段
                "state": run.state,  # 包含运行状态
                "time": run.metadata['startedAt']
            }
            for run in runs
        ]
        beijing_tz = pytz.timezone('Asia/Shanghai')
        for res in result:
            res["time"] = (
                datetime.strptime(res["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
                .replace(tzinfo=pytz.utc)
                .astimezone(beijing_tz)
                .strftime("%Y-%m-%d %H:%M:%S.%f")
            )
        result.sort(key=lambda x: x["time"], reverse=True)
        return result

    except wandb.errors.CommError as e:
        raise ConnectionError(f"连接失败: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"获取运行数据失败: {str(e)}") from e


def get_id(target_name, res):
    df = pd.DataFrame.from_records(res)
    # 筛选状态既不是 'finished' 也不是 'running' 的记录
    filtered = df[(df['name'] == target_name) & ~df['state'].isin(['finished', 'running'])]['id']

    if not filtered.empty:
        # 存在符合条件的记录,返回第一个 id
        return filtered.iloc[0]
    else:
        # 无符合条件的记录,获取该 name 最新的 id（按 id 降序排列取第一个）
        name_df = df[df['name'] == target_name]
        if name_df.empty:
            return '001'  # 无该 name 的任何记录时返回 None
        latest_id_str = name_df['id'].iloc[0]
        # 转为数值加 1 后再格式化为三位字符串
        new_id_num = int(latest_id_str) + 1
        return f"{new_id_num:03d}"


def get_all_projects(entity: str = None, api_key: str = None, verbose: bool = True) -> List[Dict[str, Any]]:
    """
    获取WandB账户中所有的project

    参数:
        entity: WandB实体名称（团队或用户名）,如果为None则使用默认实体
        api_key: WandB API密钥,如果为None则使用环境变量或配置文件中的密钥
        verbose: 是否打印进度信息

    返回:
        包含所有project信息的字典列表
    """
    # 初始化WandB API
    api = wandb.Api(api_key=api_key)

    # 如果未指定实体,获取默认实体
    if entity is None:
        try:
            entity = api.default_entity
            if verbose:
                print(f"使用默认实体: {entity}")
        except Exception as e:
            raise ValueError("未指定实体且无法获取默认实体,请提供entity参数或配置默认实体") from e

    # 存储所有项目的列表
    all_projects = []

    if verbose:
        print(f"开始获取实体 {entity} 下的所有项目...")

    try:
        # 直接迭代获取所有项目
        projects = api.projects(entity=entity)
        for idx, project in enumerate(projects):
            project_info = {
                "id": project.id,
                "name": project.name,
                "entity": project.entity,
                "created_at": project.created_at,
                "url": project.url,
            }
            all_projects.append(project_info)

            if verbose and (idx + 1) % 10 == 0:
                print(f"已获取 {idx + 1} 个项目")


    except Exception as e:
        print(f"获取项目时出错: {e}")

    if verbose:
        print(f"总共获取了 {len(all_projects)} 个项目")

    return all_projects


def natural_sort_key(s: str) -> list:
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]


def generate_zsl_image_dataframe(root_dir: str,
                                 test_image_class,
                                 predict_class_file=None  # 修改为可选参数，默认None
                                 ):
    image_classes = load_class_list(test_image_class)

    # 处理predict_classes：若predict_class_file为空，则使用image_classes
    if predict_class_file is None or not predict_class_file:
        predict_classes = image_classes
    else:
        predict_classes = load_class_list(predict_class_file)

    class_to_idx = {cls: idx for idx, cls in enumerate(predict_classes)}
    image_root_dir = os.path.join(root_dir, 'val')

    full_image_paths = []  # 图片完整路径
    targets = []  # 标注类别ID（映射器中的索引）
    class_names = []  # 标注类别名称
    label_names = []

    for class_name in image_classes:
        # 构建当前类别的图片文件夹路径（image_root_dir / 类别名）
        class_img_dir = os.path.join(image_root_dir, class_name)
        # 收集该类别下的所有图片（筛选指定后缀）
        image_extensions = ('.bmp', '.jpg', '.jpeg', '.png')  # 支持的图片后缀
        class_images = [
            img for img in os.listdir(class_img_dir)
            if img.lower().endswith(image_extensions)  # 忽略大小写（如.IMG/.JPG）
        ]

        # 对图片按自然排序（保证顺序一致性）
        class_images_sorted = sorted(class_images, key=natural_sort_key)

        # 图片完整路径（类别文件夹路径 + 图片名）
        class_image_paths = [os.path.join(class_img_dir, img) for img in class_images_sorted]

        # 处理class_id：若predict_class_file为空，则class_id=class_name，否则按原逻辑处理
        if predict_class_file is None or not predict_class_file:
            class_id = class_name  # 关键修改：predict_class_file为空时，class_id直接使用class_name
        else:
            prefix_part = class_name.split("_")[0]  # 提取"0-No"或"0-B-007"
            parts = prefix_part.split("-")  # 按"-"分割为列表
            class_id = "-".join(parts[1:])

        class_target = class_to_idx[class_id]

        # 批量添加基础信息到列表
        full_image_paths.extend(class_image_paths)
        targets.extend([class_target] * len(class_images_sorted))
        class_names.extend([class_name] * len(class_images_sorted))
        label_names.extend([class_id] * len(class_images_sorted))

    # 构建基础DataFrame（必选列）
    columns = {
        '图片路径': full_image_paths,
        '标注类别ID': targets,
        '标注类别名称': class_names,
        '标签名称': label_names
    }
    return pd.DataFrame(columns)


def generate_image_dataframe(root_dir: str,
                             image_subdir: str,
                             class_list_path: str = None,
                             parse_factors: bool = True,
                             factor_names: List[str] = None) -> Tuple[pd.DataFrame, 'FactorLabelMapper']:
    """
    生成包含图片完整信息及可选因子数据的数据框（适配图片按类别分文件夹存放的场景）

    参数:
        root_dir: str - FactorLabelMapper所需的根目录（用于加载类别映射）
        image_subdir: str - 存放类别文件夹的父目录（位于root_dir下,如"images"）
        class_list_path: str - 类别列表txt路径（可选,传给FactorLabelMapper）
        parse_factors: bool - 是否解析因子信息,True则包含因子相关列,False则只保留基础信息
        factor_names: List[str] - 因子名称列表（解析因子时必须提供）

    返回:
        Tuple[pd.DataFrame, FactorLabelMapper]:
            - pd.DataFrame: 包含图片路径、标注类别及可选因子信息的数据框
            - FactorLabelMapper: 初始化后的类别-因子映射器
    """

    # 初始化类别-因子映射器（获取所有有效类别）
    # 解析因子时必须提供factor_names
    maper = FactorLabelMapper(
        root_dir,
        class_list_path=class_list_path,
        parse_factors=parse_factors,
        build_lookup_table=True,
        factor_names=factor_names if parse_factors else None
    )
    valid_classes = maper.classes  # 映射器加载的有效类别列表

    # ------------------------------
    # 2. 验证图片根目录（image_subdir）
    # ------------------------------
    # 图片根目录 = root_dir / image_subdir（该目录下存放所有类别文件夹）
    image_root_dir = os.path.join(root_dir, image_subdir)
    if not os.path.exists(image_root_dir):
        raise ValueError(f"❌ 图片根目录不存在:{image_root_dir}\n请检查image_subdir参数是否正确")

    # ------------------------------
    # 3. 按类别遍历,收集图片信息
    # ------------------------------
    # 初始化基础数据收集列表（无论是否解析因子都需要）
    full_image_paths = []  # 图片完整路径
    targets = []  # 标注类别ID（映射器中的索引）
    class_names = []  # 标注类别名称

    # 初始化因子数据收集列表（仅当需要解析因子时使用）
    factor_values_list = [[] for _ in range(maper.num_factors)] if parse_factors else []  # 因子原始值
    factor_indices_list = [[] for _ in range(maper.num_factors)] if parse_factors else []  # 因子编码

    # 遍历每个有效类别,收集该类别下的图片
    for class_name in valid_classes:
        # 构建当前类别的图片文件夹路径（image_root_dir / 类别名）
        class_img_dir = os.path.join(image_root_dir, class_name)

        # 校验类别文件夹是否存在（避免映射器类别与实际文件夹不匹配）
        if not os.path.exists(class_img_dir):
            continue

        # 收集该类别下的所有图片（筛选指定后缀）
        image_extensions = ('.bmp', '.jpg', '.jpeg', '.png')  # 支持的图片后缀
        class_images = [
            img for img in os.listdir(class_img_dir)
            if img.lower().endswith(image_extensions)  # 忽略大小写（如.IMG/.JPG）
        ]

        # 若类别文件夹下无图片,警告并跳过
        if not class_images:
            continue

        # 对图片按自然排序（保证顺序一致性）
        class_images_sorted = sorted(class_images, key=natural_sort_key)

        # ------------------------------
        # 4. 提取基础信息（所有场景都需要）
        # ------------------------------
        # 图片完整路径（类别文件夹路径 + 图片名）
        class_image_paths = [os.path.join(class_img_dir, img) for img in class_images_sorted]
        # 该类别的标注ID（所有图片共享同一类别ID）
        class_target = maper.get_label_from_class(class_name)

        # 批量添加基础信息到列表
        full_image_paths.extend(class_image_paths)
        targets.extend([class_target] * len(class_images_sorted))
        class_names.extend([class_name] * len(class_images_sorted))

        # ------------------------------
        # 5. 按需解析因子信息（仅当parse_factors=True时执行）
        # ------------------------------
        if parse_factors:
            # 获取该类别的因子原始值
            factors = maper.get_factors_from_class(class_name)
            # 获取该类别的因子整数编码
            factor_indices = maper.get_indices_from_factors(factors)

            # 批量添加每个因子的信息到对应列表
            for i in range(maper.num_factors):
                factor_values_list[i].extend([factors[i]] * len(class_images_sorted))
                factor_indices_list[i].extend([factor_indices[i]] * len(class_images_sorted))

    # ------------------------------
    # 6. 校验数据完整性,构建DataFrame
    # ------------------------------
    if not full_image_paths:
        raise RuntimeError("❌ 未收集到任何有效图片！请检查:1.类别文件夹路径 2.图片后缀是否支持")

    # 构建基础DataFrame（必选列）
    base_columns = {
        '图片路径': full_image_paths,
        '标注类别ID': targets,
        '标注类别名称': class_names
    }
    image_df = pd.DataFrame(base_columns)

    # 按需添加因子相关列（使用映射器中的因子名称）
    if parse_factors:
        # 添加因子原始值列
        for i in range(maper.num_factors):
            image_df[f'{maper.factor_names[i]}'] = factor_values_list[i]

        # 添加因子编码列
        for i in range(maper.num_factors):
            image_df[f'{maper.factor_names[i]}编码'] = factor_indices_list[i]

    return image_df, maper


# def generate_image_dataframe(root_dir, image_subdir):
#     """
#     生成包含图片完整信息及三因子数据的数据框
#
#     参数:
#         root_dir: str - FactorLabelMapper所需的根目录
#         image_subdir: str - 存放图片的子文件夹名称（位于root_dir下）
#
#     返回:
#         pd.DataFrame - 包含图片路径、标注类别及三因子信息的数据框
#     """
#
#     # 自然排序函数
#     def natural_sort_key(s):
#         return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]
#
#     # 初始化映射器
#     maper = FactorLabelMapper(root_dir)
#
#     # 构建完整的图片文件夹路径
#     image_dir = os.path.join(root_dir, image_subdir)
#
#     # 验证图片文件夹是否存在
#     if not os.path.exists(image_dir):
#         raise ValueError(f"图片文件夹不存在: {image_dir}")
#
#     # 获取排序后的图像列表
#     images_list = [f for f in os.listdir(image_dir) if f.endswith(('.bmp', '.jpg', '.png'))]
#     images_list = sorted(images_list, key=natural_sort_key)
#
#     # 生成完整图片路径
#     full_image_paths = [os.path.join(image_dir, img) for img in images_list]
#
#     # 提取基础信息
#     targets = [
#         maper.class_to_label[os.path.splitext(each)[0].split('_')[0]]
#         for each in images_list
#     ]
#     class_names = [maper.label_to_class[ID] for ID in targets]
#
#     # 提取三因子及其整数编码
#     conditions = []
#     fault_types = []
#     severities = []
#     cond_indices = []
#     fault_indices = []
#     sev_indices = []
#
#     for cls in class_names:
#         # 获取三因子原始值
#         cond, fault, sev = maper.get_factors_from_class(cls)
#         # 在工况后添加HP后缀
#         conditions.append(f"{cond}HP")
#         fault_types.append(fault)
#         severities.append(f'{sev}英寸')
#
#         # 获取三因子整数编码
#         cond_idx, fault_idx, sev_idx = maper.get_indices_from_factors(cond, fault, sev)
#         cond_indices.append(cond_idx)
#         fault_indices.append(fault_idx)
#         sev_indices.append(sev_idx)
#
#     # 构建并返回DataFrame
#     return pd.DataFrame({
#         '图片路径': full_image_paths,
#         '标注类别ID': targets,
#         '标注类别名称': class_names,
#         '故障工况': conditions,
#         '故障类型': fault_types,
#         '故障程度': severities,
#         '工况编码': cond_indices,
#         '故障类型编码': fault_indices,
#         '故障程度编码': sev_indices
#     }), maper


def create_csv(data, file_path):
    """
    根据给定的字典或列表生成CSV文件

    参数:
        data: 可以是列表（作为表头）或字典（键为表头,值为数据）
        file_path: 字符串,CSV文件的保存路径（包括文件名）
    """
    if isinstance(data, list):
        # 处理列表:仅作为表头创建空文件
        df = pd.DataFrame(columns=data)
    elif isinstance(data, dict):
        # 处理字典:键作为表头,值作为数据
        # 检查是否所有值都是列表且长度一致
        values = list(data.values())
        if all(isinstance(v, list) for v in values):
            # 确保所有列表长度相同
            lengths = set(len(v) for v in values)
            if len(lengths) <= 1:  # 允许所有空列表或长度一致的非空列表
                df = pd.DataFrame(data)
            else:
                raise ValueError("字典中所有值的列表长度必须一致")
        else:
            raise ValueError("字典的值必须是列表类型")
    else:
        raise TypeError("data必须是列表或字典类型")

    # 保存为CSV文件
    df.to_csv(file_path, index=False)
    print(f"已生成CSV文件:{file_path}")


def append_metrics_to_csv(metrics, filename='training_metrics.csv'):
    """
    将一轮训练的指标数据按CSV表头顺序整理后追加到文件

    参数:
        metrics: 字典,包含当前轮次的指标数据
        filename: 保存指标的CSV文件名
    """
    # 检查文件是否存在
    if not os.path.exists(filename):
        raise FileNotFoundError(f"文件 {filename} 不存在,请先创建包含表头的CSV文件")

    # 读取CSV文件的表头（仅读取第一行）
    with open(filename, 'r') as f:
        header = f.readline().strip().split(',')

    # 检查metrics是否包含所有表头字段
    missing_keys = [key for key in header if key not in metrics]
    if missing_keys:
        raise ValueError(f"metrics缺少以下必要字段: {missing_keys}")

    # 按表头顺序重新整理字典
    ordered_metrics = {key: metrics[key] for key in header}

    # 转换为DataFrame并追加到CSV
    df = pd.DataFrame([ordered_metrics])
    df.to_csv(filename, mode='a', header=False, index=False)


def create_next_numbered_folder(parent_dir, prefix):
    """
    检查指定文件夹中以指定前缀+数字命名的子文件夹,创建缺失的最小数字对应的文件夹

    参数:
        parent_dir: 父文件夹路径
        prefix: 子文件夹的前缀（如"exp"、"test"等）

    返回:
        新创建的文件夹路径,如果创建失败则返回None
    """
    # 确保父文件夹存在
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir)
            print(f"已创建父文件夹: {parent_dir}")
        except OSError as e:
            print(f"创建父文件夹失败: {e}")
            return None

    # 构建匹配指定前缀+数字格式的正则表达式
    # 转义前缀中的特殊字符,确保正则表达式正确匹配
    escaped_prefix = re.escape(prefix)
    pattern = re.compile(f'^{escaped_prefix}-(\\d+)$')

    # 收集所有符合条件的文件夹的数字
    numbers = []
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        if os.path.isdir(item_path):
            match = pattern.match(item)
            if match:
                try:
                    number = int(match.group(1))
                    numbers.append(number)
                except ValueError:
                    # 忽略数字部分无法转换为整数的文件夹
                    continue

    # 找到最小的缺失数字
    if not numbers:
        # 没有任何符合条件的文件夹,从1开始
        next_number = 1
    else:
        # 排序现有数字
        numbers.sort()
        # 检查从1开始的序列中第一个缺失的数字
        next_number = 1
        for num in numbers:
            if num > next_number:
                break
            next_number = num + 1

    # 创建新文件夹
    new_folder_name = f"{prefix}-{next_number}"
    new_folder_path = os.path.join(parent_dir, new_folder_name)

    try:
        os.makedirs(new_folder_path, exist_ok=False)  # 不覆盖现有文件夹
        print(f"已创建文件夹: {new_folder_path}")
        return new_folder_path
    except OSError as e:
        print(f"创建文件夹失败: {e}")
        return None


def save_class_mean_features(encoding_path, csv_path, show_feature='故障工况', save_npy_path='.'):
    """
    计算每个类别的特征均值并分别保存为npy文件

    参数:
        encoding_path: 特征数组的npy文件路径（形状为 [样本数, 特征维度]）
        csv_path: 包含标签信息的CSV文件路径
        show_feature: 用于分类的特征列名（如'故障工况'）
        save_npy_path: 保存npy文件的目录路径
    """

    # 1. 加载特征数组和CSV标签数据
    try:
        file_path = os.path.join(encoding_path, f'{show_feature}.npy')
        encoding_array = np.load(file_path, allow_pickle=True)
        print(f"成功加载特征数组,形状: {encoding_array.shape}")
    except Exception as e:
        raise ValueError(f"加载特征文件失败: {str(e)}")

    try:
        df = pd.read_csv(csv_path)
        print(f"成功加载CSV文件,共{len(df)}条记录")
    except Exception as e:
        raise ValueError(f"加载CSV文件失败: {str(e)}")

    # 2. 验证数据有效性
    if len(encoding_array) != len(df):
        raise ValueError(f"特征样本数（{len(encoding_array)}）与CSV行数（{len(df)}）不匹配")

    if show_feature not in df.columns:
        raise ValueError(f"CSV文件中未找到'{show_feature}'列,请检查列名是否正确")

    # 3. 按类别计算特征均值并保存
    class_names = df[show_feature].unique().tolist()
    n_classes = len(class_names)
    print(f"共检测到 {n_classes} 个类别: {class_names}")

    for cls in class_names:
        # 提取该类别的所有样本特征
        cls_mask = df[show_feature] == cls
        cls_feats = encoding_array[cls_mask]

        if len(cls_feats) == 0:
            print(f"警告:类别'{cls}'没有对应的样本,跳过计算")
            continue

        # 计算特征均值（按特征维度求平均）
        cls_mean = np.mean(cls_feats, axis=0)
        # print(f"类别'{cls}':{len(cls_feats)}个样本 → 特征均值形状: {cls_mean.shape}")

        # 生成保存路径（格式:show_feature_类别.npy）
        # 处理类别名中的特殊字符（如斜杠、空格等）
        safe_cls_name = str(cls).replace('/', '_').replace(' ', '_')
        file_name = f"{show_feature}_{safe_cls_name}.npy"
        save_path = os.path.join(save_npy_path, file_name)

        # 保存为npy文件
        np.save(save_path, cls_mean)
        # print(f"已保存: {save_path}")

    print("所有类别特征均值计算与保存完成")


def visualize_mean_features(encoding_path, csv_path, show_feature='标注类别名称',
                            save_fig_path='combined_vis.jpg'):
    """
    修复size_max参数错误,将类别特征平均值作为虚拟样本加入原始特征一起降维可视化
    """
    # 1. 加载数据
    encoding_array = np.load(encoding_path, allow_pickle=True)
    df = pd.read_csv(csv_path)

    # 验证数据有效性
    if len(encoding_array) != len(df):
        raise ValueError("特征样本数与CSV行数不匹配")
    for col in [show_feature, '图片路径']:
        if col not in df.columns:
            raise ValueError(f"CSV缺少必要列:{col}")

    # 2. 计算每个类别的特征平均值（作为"虚拟样本"）
    class_names = df[show_feature].unique().tolist()
    n_classes = len(class_names)
    print(f"计算 {n_classes} 个类别的特征平均值,作为虚拟样本加入原始特征...")

    # 按类别分组求均值
    mean_feats_list = []
    mean_labels = []
    for cls in class_names:
        cls_feats = encoding_array[df[show_feature] == cls]
        cls_mean = np.mean(cls_feats, axis=0)
        mean_feats_list.append(cls_mean)
        mean_labels.append(cls)

    # 转换为数组并合并
    mean_feats_array = np.array(mean_feats_list)
    combined_feats = np.vstack([encoding_array, mean_feats_array])  # 合并原始特征与均值特征

    # 3. 准备合并后的标签数据
    original_labels = df[show_feature].tolist()
    original_types = ['原始样本'] * len(original_labels)
    original_names = df['图片路径'].apply(lambda x: x.split('/')[-1]).tolist()

    mean_types = ['均值样本'] * n_classes
    mean_names = [f"{cls}_均值" for cls in class_names]

    combined_labels = original_labels + mean_labels
    combined_types = original_types + mean_types
    combined_names = original_names + mean_names

    # 4. 对合并后的特征进行TSNE降维
    print("对合并后的特征（原始样本+均值样本）进行TSNE降维...")
    tsne = TSNE(n_components=2, max_iter=20000, random_state=42)  # 注意:sklearn 1.5+用max_iter替代n_iter
    combined_tsne_2d = tsne.fit_transform(combined_feats)

    # 5. 准备可视化数据（新增尺寸数值列）
    vis_df = pd.DataFrame({
        'X': combined_tsne_2d[:, 0],
        'Y': combined_tsne_2d[:, 1],
        show_feature: combined_labels,
        '样本类型': combined_types,
        '名称': combined_names,
        '尺寸数值': [1 if t == '原始样本' else 5 for t in combined_types]  # 原始样本=1,均值样本=5
    })

    # 6. 绘制静态图
    plt.figure(figsize=(14, 12), facecolor='white')
    palette = sns.hls_palette(n_classes)
    cls_color_map = {cls: palette[i] for i, cls in enumerate(class_names)}

    # 绘制原始样本
    original_mask = vis_df['样本类型'] == '原始样本'
    for cls in class_names:
        cls_mask = original_mask & (vis_df[show_feature] == cls)
        plt.scatter(
            vis_df.loc[cls_mask, 'X'],
            vis_df.loc[cls_mask, 'Y'],
            color=cls_color_map[cls],
            alpha=0.4,
            s=30,
            marker='o',
            label=cls
        )

    # 绘制均值样本
    mean_mask = vis_df['样本类型'] == '均值样本'
    for i, cls in enumerate(class_names):
        cls_mean_mask = mean_mask & (vis_df[show_feature] == cls)
        plt.scatter(
            vis_df.loc[cls_mean_mask, 'X'],
            vis_df.loc[cls_mean_mask, 'Y'],
            color=cls_color_map[cls],
            s=400,
            marker='*',
            edgecolors='black',
            linewidths=2,
            zorder=10
        )

        # 在均值样本旁添加类别名称
        plt.text(
            vis_df.loc[cls_mean_mask, 'X'].values[0] + 3.0,  # x轴偏移一点,避免重叠
            vis_df.loc[cls_mean_mask, 'Y'].values[0],  # y轴对齐
            cls,  # 类别名称
            fontsize=12,
            fontweight='bold',
            color=cls_color_map[cls],
            bbox=dict(facecolor='white', edgecolor='gray', pad=3, alpha=0.8)  # 白色背景框增强可读性
        )

    plt.legend(title=show_feature, fontsize=10, title_fontsize=12, bbox_to_anchor=(1.05, 1))
    plt.xticks([])
    plt.yticks([])
    plt.title(f'原始特征与{show_feature}均值特征（合并降维）可视化', fontsize=16)
    plt.tight_layout()
    plt.savefig(save_fig_path, dpi=500, bbox_inches='tight')
    print(f"静态图已保存至: {save_fig_path}")
    plt.close()


# def concat_fault_features(condition_path, type_path, degree_path, output_dir=None):
#     """
#     拼接故障工况、类型、程度特征,生成格式正确的文件名:
#     - 故障工况仅保留数字/核心标识（去除HP等后缀）
#     - 故障程度为0时自动省略
#     - 格式:工况-类型[-(非0程度)]（如0-No.npy、x-B-007.npy）
#     """
#
#     # 1. 提取故障工况标识（仅保留数字或核心字符,去除单位后缀如HP）
#     def extract_condition_key(filename):
#         base_name = os.path.splitext(os.path.basename(filename))[0]
#         if "故障工况" not in base_name:
#             raise ValueError(f"文件需包含'故障工况',输入为:{base_name}")
#         condition_part = base_name.split('_')[-1]
#         # 优先提取数字,若无数字则保留字母（如x）,过滤单位后缀
#         numbers = re.findall(r'\d+', condition_part)
#         if numbers:
#             return numbers[0]  # 只保留数字部分（如从0HP提取0）
#         return re.sub(r'[^A-Za-z]', '', condition_part)  # 无数字则保留字母（如x）
#
#     # 2. 提取故障类型标识（保留完整标识）
#     def extract_type_key(filename):
#         base_name = os.path.splitext(os.path.basename(filename))[0]
#         if "故障类型" not in base_name:
#             raise ValueError(f"文件需包含'故障类型',输入为:{base_name}")
#         return re.sub(r'[^A-Za-z0-9]', '', base_name.split('_')[-1])
#
#     # 3. 提取故障程度标识（仅保留非0数字,0则省略）
#     def extract_degree_key(filename):
#         base_name = os.path.splitext(os.path.basename(filename))[0]
#         if "故障程度" not in base_name:
#             raise ValueError(f"文件需包含'故障程度',输入为:{base_name}")
#         degree_part = base_name.split('_')[-1]
#         numbers = re.findall(r'\d+', degree_part)
#         if numbers and numbers[0] != '0':  # 非0数字才保留
#             return numbers[0]
#         return ''  # 0或无数字则返回空
#
#     # 提取关键标识
#     condition_key = extract_condition_key(condition_path)  # 如从0HP提取0
#     type_key = extract_type_key(type_path)  # 如No、B
#     degree_key = extract_degree_key(degree_path)  # 非0则保留,0则空
#
#     # 生成文件名（过滤空值部分）
#     parts = [condition_key, type_key, degree_key]
#     non_empty_parts = [part for part in parts if part]  # 自动剔除空值
#     output_filename = "-".join(non_empty_parts) + ".npy"
#
#     # 确定输出路径
#     if output_dir is None:
#         condition_dir = os.path.dirname(condition_path)
#         output_dir = os.path.join(condition_dir, "fault_combined")
#     os.makedirs(output_dir, exist_ok=True)
#     output_path = os.path.join(output_dir, output_filename)
#
#     # 拼接特征（工况→类型→程度）
#     try:
#         condition_feat = np.load(condition_path, allow_pickle=True)
#         type_feat = np.load(type_path, allow_pickle=True)
#         degree_feat = np.load(degree_path, allow_pickle=True)
#     except Exception as e:
#         raise FileNotFoundError(f"特征文件加载失败: {str(e)}")
#
#     # 验证维度
#     for feat, name in zip(
#             [condition_feat, type_feat, degree_feat],
#             ["故障工况", "故障类型", "故障程度"]
#     ):
#         if feat.ndim != 1:
#             raise ValueError(f"{name}必须为一维数组,实际维度: {feat.ndim}")
#
#     combined_feat = np.concatenate([condition_feat, type_feat, degree_feat], axis=0)
#     np.save(output_path, combined_feat)
#
#     print(f"拼接完成:\n"
#           f"输入: {os.path.basename(condition_path)} + {os.path.basename(type_path)} + {os.path.basename(degree_path)}\n"
#           f"输出文件: {output_filename}\n"
#           f"保存路径: {output_path}")

def concat_fault_features(type_path, degree_path, output_dir=None):
    """
    拼接故障类型、程度特征,生成格式正确的文件名:
    - 故障程度为0时自动省略
    - 格式:类型[-(非0程度)]（如No.npy、B-007.npy）
    """

    # 1. 提取故障类型标识（保留完整标识,过滤特殊字符）
    def extract_type_key(filename):
        base_name = os.path.splitext(os.path.basename(filename))[0]
        if "故障类型" not in base_name:
            raise ValueError(f"文件需包含'故障类型',输入为:{base_name}")
        # 保留字母/数字,过滤下划线、空格等特殊字符
        return re.sub(r'[^A-Za-z0-9]', '', base_name.split('_')[-1])

    # 2. 提取故障程度标识（仅保留非0数字,0则省略）
    def extract_degree_key(filename):
        base_name = os.path.splitext(os.path.basename(filename))[0]
        if "故障程度" not in base_name:
            raise ValueError(f"文件需包含'故障程度',输入为:{base_name}")
        degree_part = base_name.split('_')[-1]
        numbers = re.findall(r'\d+', degree_part)
        if numbers and numbers[0] != '0':  # 仅保留非0数字（0则省略）
            return numbers[0]
        return ''  # 0或无有效数字时返回空

    # 提取类型、程度关键标识
    type_key = extract_type_key(type_path)
    degree_key = extract_degree_key(degree_path)  # 非0则保留（如"007"）,0则为空

    # 生成输出文件名（自动剔除空值部分,避免多余分隔符）
    parts = [type_key, degree_key]
    non_empty_parts = [part for part in parts if part]  # 过滤空的程度标识
    output_filename = "-".join(non_empty_parts) + ".npy"  # 如"No.npy"、"B-007.npy"

    # 确定输出路径（默认与故障类型文件同目录下的"fault_combined"文件夹）
    if output_dir is None:
        type_dir = os.path.dirname(type_path)  # 取故障类型文件的目录
        output_dir = os.path.join(type_dir, "fault_combined")
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
    output_path = os.path.join(output_dir, output_filename)

    # 加载并拼接特征（类型特征 → 程度特征）
    try:
        # 加载一维特征数组
        type_feat = np.load(type_path, allow_pickle=True)
        degree_feat = np.load(degree_path, allow_pickle=True)
    except Exception as e:
        raise FileNotFoundError(f"特征文件加载失败: {str(e)}")

    # 验证特征维度（必须为一维数组,避免拼接异常）
    for feat, name in zip(
            [type_feat, degree_feat],
            ["故障类型", "故障程度"]
    ):
        if feat.ndim != 1:
            raise ValueError(f"{name}特征必须为一维数组,实际维度: {feat.ndim}")

    # 拼接特征（类型在前,程度在后）
    combined_feat = np.concatenate([type_feat, degree_feat], axis=0)
    np.save(output_path, combined_feat)


def write_list_to_file(str_list, file_path):
    """
    将字符串列表中的每个元素写入到txt文件，每个元素占一行

    参数:
        str_list: 字符串列表
        file_path: 要写入的文件路径
    """
    try:
        # 使用with语句打开文件，自动处理文件关闭
        with open(file_path, 'w', encoding='utf-8') as file:
            for item in str_list:
                # 确保每个元素都是字符串类型并添加换行符
                file.write(str(item) + '\n')
    except Exception as e:
        print(f"写入文件时发生错误: {e}")

