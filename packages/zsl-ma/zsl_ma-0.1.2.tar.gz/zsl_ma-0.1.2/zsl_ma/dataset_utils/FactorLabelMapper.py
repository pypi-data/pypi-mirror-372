import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import torch


def load_class_list(txt_path: Path) -> Tuple[List[Tuple[str, Optional[int]]], bool]:
    """从txt文件加载原始类别列表，支持两种格式：
    - 纯类别（如"0-B-007"）
    - 类别+索引（如"0-B-007：0"或"0-B-014:1"）
    返回：(类别-索引列表, 是否包含索引)
    """
    classes_with_indices: List[Tuple[str, Optional[int]]] = []
    has_indices = False  # 是否包含索引映射
    seen_classes = set()  # 用于去重

    with open(txt_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # 跳过空行

            # 尝试解析索引（支持中文冒号“：”和英文冒号“:”）
            idx: Optional[int] = None
            if '：' in line:
                parts = [p.strip() for p in line.split('：', 1)]
                has_indices = True
            elif ':' in line:
                parts = [p.strip() for p in line.split(':', 1)]
                has_indices = True
            else:
                parts = [line]  # 纯类别格式

            # 校验解析结果
            if len(parts) == 2:
                cls_name, idx_str = parts
                if not cls_name:
                    raise ValueError(f"行{line_num}：类别名称为空")
                if cls_name in seen_classes:
                    continue  # 去重
                # 解析索引为整数
                try:
                    idx = int(idx_str)
                    if idx < 0:
                        raise ValueError(f"行{line_num}：索引不能为负数")
                except ValueError as e:
                    raise ValueError(f"行{line_num}：索引格式错误（{str(e)}）") from e
                classes_with_indices.append((cls_name, idx))
                seen_classes.add(cls_name)
            else:
                # 纯类别格式
                cls_name = parts[0]
                if cls_name not in seen_classes:
                    classes_with_indices.append((cls_name, None))
                    seen_classes.add(cls_name)

    # 无索引时按类别名称排序（保持原逻辑）
    if not has_indices:
        classes_with_indices.sort(key=lambda x: x[0])

    return classes_with_indices, has_indices


class FactorLabelMapper:
    """类别-因子-标签映射管理器（支持因子解析和基础映射两种模式）"""

    def __init__(self,
                 data_dir=None,
                 class_list_path: Optional[str] = None,
                 factor_index_map_path: Optional[str] = None,
                 ignore_factors: Optional[List[str]] = None):  # 忽略因子：仅接收纯因子名（如["故障程度"]）
        """初始化映射管理器
        参数说明:
            data_dir: 数据目录，当class_list_path不存在时从该目录子文件夹获取类别
            class_list_path: 类别列表txt文件路径，优先于data_dir
            factor_index_map_path: 因子索引映射文件路径（开启因子解析模式）
                                   注意：该文件中**一定不存在IGNORE行**，无需处理此类行
            ignore_factors: 可选，用户指定的忽略因子列表（纯因子名，不含单位和()）
                            仅从该参数获取需要忽略的因子，与factor_index_map_path文件无关
        """
        # 1. 基础参数验证：必须提供类别来源
        if data_dir is None and class_list_path is None:
            raise ValueError("必须提供data_dir或class_list_path参数之一")

        # 存储用户指定的忽略因子（纯因子名）
        self.user_ignore_factors = ignore_factors  # 例如：["故障程度"]

        # 2. 加载原始类别
        self.raw_classes: List[str] = []  # 原始类别列表（如0-B-007、No-A-001等）
        self.classes_with_indices: List[Tuple[str, Optional[int]]] = []  # 类别-索引列表
        self.has_indices: bool = False  # 是否包含索引映射

        if class_list_path is not None:
            class_list_path = Path(class_list_path)
            if class_list_path.exists():
                self.classes_with_indices, self.has_indices = load_class_list(class_list_path)
                self.raw_classes = [cls for cls, idx in self.classes_with_indices]

        if not self.raw_classes and data_dir is not None:
            data_dir = Path(data_dir)
            if not data_dir.exists():
                raise ValueError(f"数据目录不存在:{data_dir}")
            # 从数据目录加载时默认无索引，按文件夹名生成类别
            self.raw_classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
            self.classes_with_indices = [(cls, None) for cls in self.raw_classes]
            self.has_indices = False

        if not self.raw_classes:
            raise ValueError("未找到任何原始类别！请检查txt文件或数据目录子文件夹")

        # 3. 初始化核心属性
        self.factor_index_map_path = Path(factor_index_map_path) if factor_index_map_path else None
        self.parse_factors: bool = self.factor_index_map_path is not None  # 是否开启因子解析
        self.classes: List[str] = []  # 最终类别列表
        self.class_to_idx: Dict[str, int] = {}  # 类别→标签映射
        self.idx_to_class: Dict[int, str] = {}  # 标签→类别反向映射

        # 4. 因子解析模式专属属性
        self.factor_names: List[str] = []  # 原始因子名（含单位，如['工况(HP)','故障类型','故障程度(英寸)']）
        self.factor_base_names: List[str] = []  # 纯因子名（不含单位，如['工况','故障类型','故障程度']）
        self.factor_units: List[str] = []  # 因子单位（如['HP','','英寸']）
        self.ignore_factors: List[str] = []  # 最终生效的忽略因子（纯因子名）
        self.class_to_factors: Dict[str, Tuple[str, ...]] = {}  # 原类别→处理后因子
        self.factor_maps: List[Dict[str, int]] = []  # 因子取值→索引
        self.factor_inv_maps: List[Dict[int, str]] = []  # 因子索引→取值
        self.num_factors: int = 0  # 处理后因子数量
        self.default_no_label: int = -1  # 默认无效标签（含No类别中的最小标签）
        self.lookup_table: Dict[Tuple[int, ...], int] = {}  # 因子索引组合→标签

        # 5. 分支初始化逻辑
        if self.parse_factors:
            # 因子解析模式：先完成所有映射构建，再获取默认标签
            self._load_factor_names()  # 加载因子名（文件中无IGNORE行）
            self._parse_class_factors()
            self._build_factor_maps()
            self.num_factors = len(self.factor_maps)

            # 构建类别映射
            self.classes = self._get_unique_merged_classes()
            self.class_to_idx = self._build_class_to_idx()
            self.idx_to_class = {v: k for k, v in self.class_to_idx.items() if k in self.classes}

            # 获取默认标签
            self._get_default_no_label()
            self._build_batch_lookup_table()
        else:
            # 基础映射模式：处理索引映射
            if self.has_indices:
                # 校验索引有效性
                indices = [idx for _, idx in self.classes_with_indices]
                if any(idx is None for idx in indices):
                    raise ValueError("基础模式下不能混合使用带索引和不带索引的行")
                if len(set(indices)) != len(indices):
                    raise ValueError("基础模式下存在重复的类别索引")
                if any(idx < 0 for idx in indices if idx is not None):
                    raise ValueError("基础模式下索引不能为负数")

                # 构建类别-索引映射（按索引排序类别）
                self.class_to_idx = {cls: idx for cls, idx in self.classes_with_indices}
                self.classes = sorted(self.class_to_idx.keys(), key=lambda x: self.class_to_idx[x])
                self.idx_to_class = {idx: cls for cls, idx in self.class_to_idx.items()}
            else:
                # 无索引时自动生成（保持原逻辑）
                self.classes = self.raw_classes.copy()
                self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
                self.idx_to_class = {idx: cls for cls, idx in self.class_to_idx.items()}

            # 基础模式获取默认标签
            self._get_default_no_label()

    def _load_factor_names(self) -> None:
        """从factor_index_map.txt加载因子名称和单位
        注意：该文件中**不存在IGNORE行**，无需处理此类行
        仅解析因子名（含单位），并提取纯因子名和单位
        """
        if not self.factor_index_map_path or not self.factor_index_map_path.exists():
            raise FileNotFoundError(f"因子索引映射文件不存在:{self.factor_index_map_path}")

        with open(self.factor_index_map_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]  # 仅保留非空行

        # 解析因子名称+单位（用正则提取()内的单位）
        i = 0
        while i < len(lines):
            line = lines[i]
            # 正则匹配格式：因子名(单位)，如“工况(HP)”→分组1=工况，分组2=HP；无单位则匹配原始字符串
            match = re.match(r'^(.+?)\((.+?)\)$', line)
            if match:
                raw_factor_name = line  # 保留原始含单位的因子名（用于后续因子块匹配）
                factor_base_name = match.group(1).strip()  # 纯因子名（不含单位）
                factor_unit = match.group(2).strip()  # 提取的单位
            else:
                raw_factor_name = line  # 无单位的原始因子名（如“故障类型”）
                factor_base_name = line.strip()  # 纯因子名=原始名
                factor_unit = ""  # 无单位

            # 存储因子相关信息（确保顺序一致）
            self.factor_names.append(raw_factor_name)
            self.factor_base_names.append(factor_base_name)
            self.factor_units.append(factor_unit)

            # 跳过当前因子的映射行（直到下一个因子名或文件结束）
            i += 1
            while i < len(lines) and ":" in lines[i]:  # 映射行含":"，因子名行不含
                i += 1

        # 解析忽略因子：仅使用用户指定的ignore_factors（纯因子名）
        if self.user_ignore_factors is not None:
            # 校验用户输入的纯因子名是否存在
            invalid_factors = [f for f in self.user_ignore_factors if f not in self.factor_base_names]
            if invalid_factors:
                raise ValueError(
                    f"用户指定的忽略因子不存在（纯因子名）：{invalid_factors}\n可用纯因子名：{self.factor_base_names}")
            self.ignore_factors = list(dict.fromkeys(self.user_ignore_factors))  # 去重
        else:
            # 未指定忽略因子时为空列表
            self.ignore_factors = []

    def _parse_class_factors(self) -> None:
        """解析所有原始类别的因子（统一数量、移除忽略因子）"""
        raw_factors_dict: Dict[str, List[str]] = {}
        for cls in self.raw_classes:
            raw_factors = cls.split("-")
            raw_factors_dict[cls] = raw_factors

        # 确定基准因子数量（所有类别必须一致）
        all_factor_counts = {len(raw_factors_dict[cls]) for cls in self.raw_classes}
        if len(all_factor_counts) > 1:
            raise ValueError(f"类别的因子数量不一致:存在{all_factor_counts}种格式")
        base_factor_count = all_factor_counts.pop()

        # 处理所有类别的因子（统一校验数量）
        temp_class_factors: Dict[str, List[str]] = {}
        for cls in self.raw_classes:
            raw_factors = raw_factors_dict[cls]
            if len(raw_factors) != base_factor_count:
                raise ValueError(f"类别'{cls}'因子数({len(raw_factors)})与基准({base_factor_count})不匹配")
            temp_class_factors[cls] = raw_factors.copy()

        # 移除忽略因子（基于纯因子名匹配计算索引）
        if self.ignore_factors and self.factor_base_names:
            # 找到需要忽略的因子索引（基于纯因子名匹配）
            ignore_indices = [i for i, base_name in enumerate(self.factor_base_names) if
                              base_name in self.ignore_factors]
            # 过滤类别因子
            for cls, factors in temp_class_factors.items():
                filtered_factors = [f for i, f in enumerate(factors) if i not in ignore_indices]
                self.class_to_factors[cls] = tuple(filtered_factors)
            # 同步删除忽略的因子名、纯因子名、单位（保持索引一致）
            self.factor_names = [name for i, name in enumerate(self.factor_names) if i not in ignore_indices]
            self.factor_base_names = [name for i, name in enumerate(self.factor_base_names) if i not in ignore_indices]
            self.factor_units = [unit for i, unit in enumerate(self.factor_units) if i not in ignore_indices]
        else:
            for cls, factors in temp_class_factors.items():
                self.class_to_factors[cls] = tuple(factors)

        # 校验处理后因子数量一致
        final_factor_counts = {len(factors) for factors in self.class_to_factors.values()}
        if len(final_factor_counts) > 1:
            raise RuntimeError(f"类别因子处理后数量不一致:{final_factor_counts}")

    def _get_unique_merged_classes(self) -> List[str]:
        """生成唯一的合并类别列表（因子拼接+去重排序）"""
        merged_classes = set()
        for factors in self.class_to_factors.values():
            merged_cls = "-".join(factors)
            merged_classes.add(merged_cls)
        return sorted(merged_classes)

    def _build_class_to_idx(self) -> Dict[str, int]:
        """构建类别→标签映射（合并类别+原始类别）"""
        merged_cls_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        class_to_idx = {}
        # 映射原始类别到合并类别的标签
        for raw_cls in self.raw_classes:
            factors = self.class_to_factors[raw_cls]
            merged_cls = "-".join(factors)
            class_to_idx[raw_cls] = merged_cls_to_idx[merged_cls]
        # 加入合并类别的映射
        class_to_idx.update(merged_cls_to_idx)
        return class_to_idx

    def _build_factor_maps(self) -> None:
        """从factor_index_map.txt加载因子-索引映射
        注意：该文件中**不存在IGNORE行**，无需过滤此类行
        """
        if not self.factor_index_map_path or not self.factor_index_map_path.exists():
            raise FileNotFoundError(f"因子索引映射文件不存在:{self.factor_index_map_path}")

        with open(self.factor_index_map_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]  # 仅保留非空行

        # 分割因子块（每个因子块以因子名行开始，后跟映射行）
        factor_blocks: List[List[str]] = []
        current_block: List[str] = []
        for line in lines:
            if ":" in line:
                current_block.append(line)  # 映射行（含":"）
            else:
                if current_block:
                    factor_blocks.append(current_block)
                current_block = [line]  # 因子名行（不含":"）
        if current_block:
            factor_blocks.append(current_block)

        # 过滤掉被忽略的因子块（基于原始因子名匹配）
        filtered_blocks = []
        for block in factor_blocks:
            factor_name = block[0]
            # 找到原始因子名对应的纯因子名，判断是否被忽略
            factor_idx = self.factor_names.index(factor_name) if factor_name in self.factor_names else -1
            if factor_idx != -1 and self.factor_base_names[factor_idx] not in self.ignore_factors:
                filtered_blocks.append(block)

        # 校验因子块数量（与过滤后的因子名数量一致）
        expected_num = len(self.factor_names)
        if len(filtered_blocks) != expected_num:
            raise ValueError(f"因子映射文件错误:过滤后有{len(filtered_blocks)}个因子块，需{expected_num}个")

        # 解析每个因子块的映射关系
        for block in filtered_blocks:
            factor_name = block[0]
            value_to_idx: Dict[str, int] = {}

            for line in block[1:]:
                if ":" not in line:
                    raise ValueError(f"{factor_name}映射格式错误:无':'，内容'{line}'")
                val, idx_str = line.split(":", 1)
                val = val.strip()
                idx_str = idx_str.strip()

                try:
                    idx = int(idx_str)
                    if idx < 0:
                        raise ValueError(f"索引需非负，实际{idx}")
                except ValueError as e:
                    raise ValueError(f"{factor_name}映射错误:{str(e)}") from e

                if val in value_to_idx:
                    raise ValueError(f"{factor_name}映射重复:取值'{val}'已定义")
                value_to_idx[val] = idx

            # 校验映射完整性：确保所有类别中该因子的取值都有对应的索引
            actual_values = set()
            for factors in self.class_to_factors.values():
                factor_idx = self.factor_names.index(factor_name)
                if factor_idx < len(factors):
                    actual_values.add(factors[factor_idx])
            missing_values = actual_values - set(value_to_idx.keys())
            if missing_values:
                raise ValueError(f"{factor_name}映射不完整:缺少{sorted(missing_values)}")

            # 构建反向映射并校验索引唯一
            idx_to_value = {idx: val for val, idx in value_to_idx.items()}
            if len(idx_to_value) != len(value_to_idx):
                raise ValueError(f"{factor_name}映射错误:存在重复索引")

            self.factor_maps.append(value_to_idx)
            self.factor_inv_maps.append(idx_to_value)

    def _get_default_no_label(self) -> None:
        """获取默认无效标签（含No类别中的最小标签）"""
        if not self.class_to_idx:
            raise RuntimeError("需先构建class_to_idx映射，才能计算默认标签")

        # 筛选包含"No"的原始类别
        no_classes = [cls for cls in self.raw_classes if "No" in cls]
        if not no_classes:
            raise ValueError("未找到含'No'的类别，无法确定默认无效标签")

        # 获取这些类别的标签并取最小值
        no_labels = [self.class_to_idx[cls] for cls in no_classes]
        self.default_no_label = min(no_labels)

    def _build_batch_lookup_table(self) -> None:
        """构建因子索引组合→标签的查询表，用于批量转换"""

        def generate_combinations(index: int, current_indices: List[int]) -> None:
            if index == self.num_factors:
                try:
                    factors = self.get_factors_from_indices(tuple(current_indices))
                    merged_cls = self.get_class_from_factors(factors)
                    self.lookup_table[tuple(current_indices)] = self.class_to_idx[merged_cls]
                except ValueError:
                    pass  # 跳过无效组合
                return
            # 遍历当前因子的所有可能索引
            for idx in self.factor_inv_maps[index].keys():
                generate_combinations(index + 1, current_indices + [idx])

        generate_combinations(0, [])

    # 基础功能：类别↔标签转换
    def get_idx_from_class(self, cls: str) -> int:
        """通过类别名称获取对应的标签索引"""
        if cls not in self.class_to_idx:
            raise ValueError(f"未知类别:{cls}，可选类别示例:{self.classes[:3]}...")
        return self.class_to_idx[cls]

    def get_class_from_idx(self, idx: int) -> str:
        """通过标签索引获取对应的类别名称"""
        if idx not in self.idx_to_class:
            raise ValueError(f"未知标签:{idx}，有效范围:0~{len(self.classes) - 1}")
        return self.idx_to_class[idx]

    def get_label_from_class(self, cls: str) -> int:
        """通过类别名称获取对应的标签（同get_idx_from_class）"""
        return self.get_idx_from_class(cls)

    def get_class_from_label(self, label: int) -> str:
        """通过标签获取对应的类别名称（同get_class_from_idx）"""
        return self.get_class_from_idx(label)

    # 因子相关功能（仅解析模式可用）
    def get_factors_from_class(self, cls: str) -> Tuple[str, ...]:
        """从类别名称解析出因子组合"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法获取因子")
        if cls in self.class_to_factors:
            return self.class_to_factors[cls]
        if cls in self.classes:
            return tuple(cls.split("-"))
        raise ValueError(f"未知类别:{cls}，无法获取因子")

    def get_class_from_factors(self, factors: Tuple[str, ...]) -> str:
        """通过因子组合获取对应的类别名称"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法通过因子获取类别")
        merged_cls = "-".join(factors)
        if merged_cls not in self.classes:
            raise ValueError(f"因子组合{factors}对应的合并类别不存在")
        return merged_cls

    def get_indices_from_factors(self, factors: Tuple[str, ...]) -> Tuple[int, ...]:
        """将因子组合转换为对应的索引组合"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法转换因子索引")
        if len(factors) != self.num_factors:
            raise ValueError(f"因子数量不匹配:输入{len(factors)}个，需{self.num_factors}个")

        indices = []
        for i, (factor_val, factor_map) in enumerate(zip(factors, self.factor_maps)):
            factor_name = self.factor_names[i]
            if factor_val not in factor_map:
                raise ValueError(f"未知{factor_name}取值:{factor_val}，可选取值:{sorted(factor_map.keys())}")
            indices.append(factor_map[factor_val])
        return tuple(indices)

    def get_factors_from_indices(self, indices: Tuple[int, ...]) -> Tuple[str, ...]:
        """将索引组合转换为对应的因子组合"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法转换因子")
        if len(indices) != self.num_factors:
            raise ValueError(f"索引数量不匹配:输入{len(indices)}个，需{self.num_factors}个")

        factors = []
        for i, (idx, inv_map) in enumerate(zip(indices, self.factor_inv_maps)):
            factor_name = self.factor_names[i]
            if idx not in inv_map:
                raise ValueError(f"未知{factor_name}索引:{idx}，有效范围:0~{len(inv_map) - 1}")
            factors.append(inv_map[idx])
        return tuple(factors)

    def get_label_from_factors(self, factors: Tuple[str, ...]) -> int:
        """通过因子组合获取对应的标签"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法通过因子获取标签")
        merged_cls = self.get_class_from_factors(factors)
        return self.get_label_from_class(merged_cls)

    def get_label_from_indices(self, indices: Tuple[int, ...]) -> int:
        """通过索引组合获取对应的标签"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法通过索引获取标签")
        factors = self.get_factors_from_indices(indices)
        return self.get_label_from_factors(factors)

    def get_labels_from_indices_batch(self, indices_tensor) -> List[int]:
        """批量通过索引组合获取对应的标签"""
        if not self.parse_factors:
            raise RuntimeError("未开启因子解析，无法批量获取标签")
        if isinstance(indices_tensor, torch.Tensor):
            indices_tensor = indices_tensor.cpu().numpy()

        labels = []
        for idx in indices_tensor:
            idx_tuple = tuple(map(int, idx))
            if len(idx_tuple) != self.num_factors:
                labels.append(self.default_no_label)
                continue
            labels.append(self.lookup_table.get(idx_tuple, self.default_no_label))
        return labels

    # 调试功能：打印映射信息
    def print_mappings(self) -> None:
        """打印关键映射信息，用于调试和验证"""
        print("=" * 50)
        print(f"1. 基础配置信息")
        print(f"   模式: {'因子解析模式' if self.parse_factors else '基础映射模式'}")
        print(f"   原始类别总数:{len(self.raw_classes)}")
        print(f"   最终类别总数:{len(self.classes)}")
        if self.parse_factors:
            # 显示“原始因子名→纯因子名→单位”对应关系
            print(f"   因子信息（原始名→纯名→单位）:")
            for i in range(len(self.factor_names)):
                unit_info = self.factor_units[i] if self.factor_units[i] else "无"
                print(f"     - {self.factor_names[i]} → {self.factor_base_names[i]} → 单位:{unit_info}")
            # 显示忽略的纯因子名（仅来自用户指定）
            print(f"   忽略因子(纯因子名，仅来自用户指定):{self.ignore_factors}")
            print(f"   处理后因子数量:{self.num_factors}")
            print(f"   默认无效标签(含No类别最小标签):{self.default_no_label}")
            print(f"   默认无效标签对应类别:{self.get_class_from_label(self.default_no_label)}")
        else:
            print(f"   是否使用自定义索引: {self.has_indices}")

        print("\n2. 最终类别→标签映射")
        for cls in self.classes:
            print(f"   {cls}: {self.class_to_idx[cls]}")

        if self.parse_factors:
            print("\n3. 因子→索引映射")
            for i, (factor_name, factor_map) in enumerate(zip(self.factor_names, self.factor_maps)):
                print(f"   {factor_name}: {factor_map}")

            print("\n4. 原始类别→合并类别→因子→标签 示例")
            for raw_cls in self.raw_classes:  # 只显示前3个避免过长
                factors = self.get_factors_from_class(raw_cls)
                merged_cls = self.get_class_from_factors(factors)
                indices = self.get_indices_from_factors(factors)  # 获取因子索引组合
                label = self.get_label_from_class(raw_cls)
                print(f"   原始:{raw_cls} → 合并:{merged_cls} → 因子:{factors} → 因子索引组合:{indices} → 标签:{label}")

            print("\n5. 因子索引组合→标签 示例")
            for idx_comb, label in list(self.lookup_table.items()):  # 只显示前3个避免过长
                factors = self.get_factors_from_indices(idx_comb)
                print(f"   索引组合:{idx_comb} → 因子:{factors} → 标签:{label}")
        else:
            print("\n3. 原始类别→标签 示例")
            for raw_cls in self.raw_classes:  # 只显示前3个避免过长
                print(f"   {raw_cls}: {self.class_to_idx[raw_cls]}")
        print("=" * 50)


# 使用示例
if __name__ == "__main__":
    print("=== 测试：因子解析模式（用户指定忽略因子） ===")
    mapper_parse_user_ignore = FactorLabelMapper(
        class_list_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\seen_classes.txt',
        factor_index_map_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\factor_index_map.txt',
        ignore_factors=["工况"]  # 用户指定忽略因子
    )
    mapper_parse_user_ignore.print_mappings()

    print("\n\n=== 测试：因子解析模式（不指定忽略因子） ===")
    mapper_parse_no_ignore = FactorLabelMapper(
        class_list_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\seen_classes.txt',
        factor_index_map_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\factor_index_map.txt'
        # 不指定ignore_factors，即不忽略任何因子
    )
    mapper_parse_no_ignore.print_mappings()

    print("\n\n=== 测试：基础映射模式（带自定义索引） ===")
    mapper_basic_custom = FactorLabelMapper(
        class_list_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\custom_index_classes.txt'
    )
    mapper_basic_custom.print_mappings()
