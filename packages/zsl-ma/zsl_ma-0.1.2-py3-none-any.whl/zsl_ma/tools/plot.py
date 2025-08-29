import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import seaborn as sns


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



def npy_dim_reduction_visualization(npy_dir, dim_method="pca", save_path=None):
    """
    对文件夹内的任意一维npy文件进行降维可视化（维度不固定，需所有样本维度一致）

    参数:
        npy_dir: npy文件所在文件夹路径
        dim_method: 降维方法，可选"pca"（默认）或"tsne"
        save_path: 图片保存路径（如None则不保存，仅显示）
    """
    # 1. 读取所有npy文件，动态适配维度
    npy_files = [f for f in os.listdir(npy_dir) if f.endswith(".npy")]
    if len(npy_files) == 0:
        raise FileNotFoundError(f"文件夹 {npy_dir} 中未找到npy文件")
    if len(npy_files) < 2:
        raise ValueError(f"至少需要2个npy文件才能进行降维，当前仅找到 {len(npy_files)} 个")

    data_list = []
    file_labels = []
    target_dim = None

    for filename in npy_files:
        file_path = os.path.join(npy_dir, filename)
        try:
            data = np.load(file_path, allow_pickle=True).squeeze()
            if data.ndim != 1:
                raise ValueError(f"非一维数据：{filename} 维度为 {data.shape}（需一维数组）")

            if target_dim is None:
                target_dim = len(data)
                print(f"检测到数据维度：{target_dim} 维（以 {filename} 为基准）")
            else:
                if len(data) != target_dim:
                    raise ValueError(
                        f"维度不一致：{filename} 为 {len(data)} 维，需与基准维度 {target_dim} 一致"
                    )

            data_list.append(data)
            file_labels.append(os.path.splitext(filename)[0])

        except Exception as e:
            raise RuntimeError(f"处理文件 {filename} 失败：{str(e)}")

    data_matrix = np.array(data_list)
    sample_num, feat_dim = data_matrix.shape  # 这里定义了feat_dim（每个样本的维度）
    print(f"数据加载完成：共 {sample_num} 个样本，每个样本 {feat_dim} 维")

    # 2. 降维处理
    if dim_method.lower() == "pca":
        reducer = PCA(n_components=2, random_state=42)
        reduced_data = reducer.fit_transform(data_matrix)
        title_suffix = f"PCA降维可视化（原维度：{feat_dim}）"
        explained_var = reducer.explained_variance_ratio_
        print(
            f"PCA降维结果：维度1解释 {explained_var[0]:.3f} 方差，维度2解释 {explained_var[1]:.3f} 方差（累计：{np.sum(explained_var):.3f}）")

    elif dim_method.lower() == "tsne":
        perplexity = min(max(2, sample_num // 4), sample_num - 1)
        reducer = TSNE(
            n_components=2,
            random_state=42,
            perplexity=perplexity,
            init="pca"
        )
        reduced_data = reducer.fit_transform(data_matrix)
        title_suffix = f"t-SNE降维可视化（原维度：{feat_dim}，perplexity={perplexity}）"
        print(f"t-SNE降维完成（自动设置perplexity={perplexity}，适配 {sample_num} 个样本）")

    else:
        raise ValueError(f"不支持的降维方法 {dim_method}，仅可选'pca'或'tsne'")

    # 3. 可视化（修正变量名错误）
    plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Zen Hei"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(10, 8))

    scatter = ax.scatter(
        reduced_data[:, 0],
        reduced_data[:, 1],
        c=range(sample_num),
        cmap="tab10" if sample_num <= 10 else "viridis",
        s=120 if sample_num <= 15 else 80,
        alpha=0.8,
        edgecolors="black",
        linewidth=1
    )

    for i, (x, y, label) in enumerate(zip(reduced_data[:, 0], reduced_data[:, 1], file_labels)):
        ax.annotate(
            label,
            xy=(x, y),
            xytext=(6, 6) if sample_num <= 10 else (4, 4),
            textcoords="offset points",
            fontsize=10 if sample_num <= 10 else 8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8)
        )

    # 关键修正：将n_dim改为feat_dim（已定义的变量）
    ax.set_title(f"{sample_num}个{feat_dim}维npy文件-{title_suffix}", fontsize=14, fontweight="bold")
    ax.set_xlabel("降维维度1", fontsize=12)
    ax.set_ylabel("降维维度2", fontsize=12)
    ax.grid(True, alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("样本索引", fontsize=10)
    cbar.set_ticks(range(sample_num))

    plt.tight_layout()

    if save_path is not None:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"图片已保存至：{save_path}")
    else:
        plt.show()

