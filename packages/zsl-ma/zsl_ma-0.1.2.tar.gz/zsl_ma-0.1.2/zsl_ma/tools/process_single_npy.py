import os

import numpy as np
import torch
from tqdm import tqdm

from zsl_ma.models.projection import AttributeProjectionModel


def process_single_npy_files(
    source_dir: str,
    target_dir: str,
    model,
    device,
    file_ext: str = '.npy'
) -> None:
    """
    逐个处理文件夹中的npy文件，通过模型处理后保存结果（一次处理一个文件）
    
    参数:
        source_dir: 源文件夹路径，包含需要处理的npy文件
        target_dir: 目标文件夹路径，用于保存处理结果
        model: 深度学习模型，接收numpy数组或tensor并返回处理结果
        device: 模型运行设备，如"cuda"或"cpu"，默认自动选择
        file_ext: 要处理的文件扩展名，默认为'.npy'
    """
    # 设备设置

    model = model.to(device)
    model.eval()
    
    # 获取源文件夹中所有符合条件的文件
    all_files = [
        f for f in os.listdir(source_dir)
        if os.path.isfile(os.path.join(source_dir, f)) and f.lower().endswith(file_ext)
    ]
    
    if not all_files:
        print(f"警告：在源文件夹 {source_dir} 中未找到任何{file_ext}文件")
        return

    # 逐个处理文件
    for file_name in tqdm(all_files, desc="处理进度"):
        file_path = os.path.join(source_dir, file_name)
        target_path = os.path.join(target_dir, file_name)
        
        # 跳过已处理的文件（可选）
        if os.path.exists(target_path):
            # print(f"文件 {file_name} 已处理，跳过")
            continue
        
        try:
            # 1. 读取单个npy文件
            data = np.load(file_path)
            
            # 2. 数据预处理（根据模型需求添加）
            # 示例：确保数据维度正确，如添加批次维度
            if len(data.shape) == 3:  # 假设输入是( height, width, channel )
                data = data.transpose(2, 0, 1)  # 转换为(channel, height, width)
                data = np.expand_dims(data, axis=0)  # 添加批次维度
            
            # 3. 转换为tensor并移动到指定设备
            input_tensor = torch.tensor(data, dtype=torch.float32).to(device)
            
            # 4. 模型推理（关闭梯度计算）
            with torch.no_grad():
                output_tensor = model(input_tensor)
            
            # 5. 转换回numpy数组并去除批次维度（如果需要）
            output_data = output_tensor.cpu().numpy()
            if output_data.shape[0] == 1:  # 如果有批次维度则去除
                output_data = output_data.squeeze(0)
            
            # 6. 保存处理结果
            np.save(target_path, output_data)
            
        except Exception as e:
            print(f"\n处理文件 {file_name} 时出错: {str(e)}")
            continue

# 使用示例
if __name__ == "__main__":
    # 示例配置
    SOURCE_DIR = r"/zsl_ma/train/output/exp-1/attributes/semantic_attribute"  # 源npy文件所在文件夹
    TARGET_DIR = r"/zsl_ma/train/output/exp-1/attributes/semantic_embed"  # 结果保存文件夹
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AttributeProjectionModel()
    model.load_state_dict(torch.load(r"/zsl_ma/train/output/exp-1/checkpoints/attr_proj.pth", weights_only=True, map_location='cpu'))
    # 调用处理函数
    process_single_npy_files(
        source_dir=SOURCE_DIR,
        target_dir=TARGET_DIR,
        model=model
    )
    