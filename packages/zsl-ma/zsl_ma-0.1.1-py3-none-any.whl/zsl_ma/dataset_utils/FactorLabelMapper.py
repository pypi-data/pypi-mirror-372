from pathlib import Path
from typing import Dict, List, Tuple, Optional

import torch


def load_class_list(txt_path: Path) -> List[str]:
    """
    私有方法：从txt文件加载类别列表

    处理逻辑：
    1. 跳过空行（避免无效类别）
    2. 去重（保留txt中首次出现的顺序，避免重复类别）
    3. sorted排序（按字符串自然顺序排序，与文件夹提取类别逻辑保持一致）
    4. 返回排序后的类别列表

    参数：
        txt_path: 类别txt文件路径（Path对象）
    返回：
        List[str]: 去重、去空、排序后的类别列表
    """
    classes = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            classes.append(line)

    classes = sorted(list(dict.fromkeys(classes)))
    return classes


class FactorLabelMapper:
    """
    类别-因子-标签映射管理器

    核心功能：
    1. 双来源加载类别（txt文件优先，无则从数据目录子文件夹提取）
    2. 动态解析类别中的因子（按'-'分割，支持任意数量因子）
    3. 特殊处理含"No"的类别（默认将故障程度设为"0"，通常表示正常状态）
    4. 批量处理因子索引→标签（无效组合自动映射到"标签最小的No类别"）
    5. 提供类别、因子、标签间的双向转换接口
    6. 支持从外部txt文件加载因子索引映射（新增功能）
    """

    def __init__(self,
                 data_dir,
                 class_list_path=None,
                 parse_factors: bool = False,
                 build_lookup_table: bool = False,
                 factor_names: Optional[List[str]] = ["工况", "故障类型",'故障程度'],
                 factor_index_map_path: Optional[str] = None  # 新增参数：因子索引映射文件路径
                 ):
        """
        初始化映射管理器

        参数说明：
            data_dir: 必传，数据目录路径（用于文件夹提取类别备份）
            class_list_path: 可选，类别txt文件路径（优先级高于文件夹提取）
            parse_factors: 可选，是否开启因子解析（默认关闭）
            build_lookup_table: 可选，是否构建批量查询表（需先开启parse_factors，默认关闭）
            factor_names: 可选，因子名称列表（需与解析出的因子数量一致）
            factor_index_map_path: 可选，因子索引映射txt文件路径（若提供则从文件加载索引，否则自动生成）
        """
        self.data_dir = Path(data_dir)
        self.classes: List[str] = []

        # 加载类别（原有逻辑）
        if class_list_path is not None:
            class_list_path = Path(class_list_path)
            if class_list_path.exists():
                self.classes = load_class_list(class_list_path)

        if not self.classes:
            if not self.data_dir.exists():
                raise ValueError(f"数据目录不存在：{self.data_dir}")
            self.classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])

        if not self.classes:
            raise ValueError("未找到任何类别！请检查txt文件或数据目录子文件夹")

        # 基础映射（原有逻辑）
        self.class_to_idx: Dict[str, int] = {cls: idx for idx, cls in enumerate(self.classes)}
        self.idx_to_class: Dict[int, str] = {idx: cls for cls, idx in self.class_to_idx.items()}

        # 因子解析相关属性（新增factor_index_map_path）
        self.parse_factors = parse_factors
        self.factor_names = factor_names
        self.class_to_factors: Optional[Dict[str, Tuple[str, ...]]] = None
        self.factor_maps: Optional[List[Dict[str, int]]] = None
        self.factor_inv_maps: Optional[List[Dict[int, str]]] = None
        self.num_factors: Optional[int] = None
        self.lookup_table: Optional[Dict[Tuple[int, ...], int]] = None
        self.default_no_label: Optional[int] = None
        self.factor_index_map_path = Path(factor_index_map_path) if factor_index_map_path else None  # 存储因子索引映射路径

        # 开启因子解析时的初始化（原有逻辑扩展）
        if self.parse_factors:
            if factor_names is None:
                raise ValueError("解析因子时必须指定factor_names参数")
            self.class_to_factors = self._parse_class_factors()
            self.factor_maps, self.factor_inv_maps = self._build_factor_maps()  # 此处会根据新参数选择加载方式
            self.num_factors = len(self.factor_maps) if self.factor_maps else 0
            self.default_no_label = self._get_default_no_label()

            if self.factor_names and len(self.factor_names) != self.num_factors:
                raise ValueError(
                    f"因子名称数量不匹配：指定{len(self.factor_names)}个，实际解析出{self.num_factors}个因子"
                )

            if build_lookup_table:
                self._build_batch_lookup_table()

    def _get_default_no_label(self) -> int:
        if not self.class_to_factors:
            raise RuntimeError("需先开启parse_factors=True解析因子，才能计算默认No类别")

        no_class_labels = []
        for cls, factors in self.class_to_factors.items():
            if "No" in factors:
                no_class_labels.append(self.class_to_idx[cls])

        if not no_class_labels:
            raise ValueError("数据集中未找到包含'No'的类别，无法设置无效组合的默认映射目标")

        return min(no_class_labels)

    def _parse_class_factors(self) -> Dict[str, Tuple[str, ...]]:
        class_to_factors = {}
        raw_factors_dict = {}

        for cls in self.classes:
            raw_factors = cls.split('-')
            raw_factors_dict[cls] = raw_factors

        non_no_classes = [cls for cls in self.classes if "No" not in raw_factors_dict[cls]]
        if non_no_classes:
            non_no_factor_counts = {len(raw_factors_dict[cls]) for cls in non_no_classes}
            if len(non_no_factor_counts) > 1:
                raise ValueError(
                    f"非'No'类别的因子数量不一致：存在{non_no_factor_counts}种格式"
                )
            base_factor_count = non_no_factor_counts.pop()
        else:
            base_factor_count = 2
            print(f"警告：所有类别均为'No'类，默认基准因子数量设为2（格式：(No, 程度)）")

        for cls in self.classes:
            raw_factors = raw_factors_dict[cls]
            raw_count = len(raw_factors)
            processed_factors = raw_factors.copy()

            if "No" in raw_factors:
                if raw_count > base_factor_count:
                    raise ValueError(
                        f"含'No'类别'{cls}'的原始因子数量({raw_count})超过基准数量({base_factor_count})"
                    )

                if raw_count < base_factor_count:
                    supplement_count = base_factor_count - raw_count
                    processed_factors += [""] * supplement_count

                processed_factors[-1] = "0"
                processed_factors = [f if f else "No" for f in processed_factors]

            else:
                if len(processed_factors) != base_factor_count:
                    raise ValueError(
                        f"非'No'类别'{cls}'的因子数量({len(processed_factors)})与基准数量({base_factor_count})不匹配"
                    )

            factors_tuple = tuple(processed_factors)
            class_to_factors[cls] = factors_tuple

        final_factor_counts = {len(factors) for factors in class_to_factors.values()}
        if len(final_factor_counts) > 1:
            raise RuntimeError(
                f"类别因子处理后数量不一致：{final_factor_counts}"
            )

        return class_to_factors

    def _build_factor_maps(self) -> Tuple[List[Dict[str, int]], List[Dict[int, str]]]:
        """
        构建因子映射（扩展逻辑：优先从文件加载，否则自动生成）
        """
        if not self.class_to_factors:
            raise RuntimeError("需先开启parse_factors=True解析因子，才能构建因子映射")

        factors_list = list(self.class_to_factors.values())
        num_factors = len(factors_list[0])

        # 新增逻辑：如果指定了因子索引映射文件且文件存在，则从文件加载
        if self.factor_index_map_path and self.factor_index_map_path.exists():
            return self._load_factor_maps_from_file(num_factors)
        # 原有逻辑：自动生成因子索引映射
        else:
            factor_values = [set() for _ in range(num_factors)]
            for factors in factors_list:
                for i in range(num_factors):
                    factor_values[i].add(factors[i])

            factor_maps = []
            factor_inv_maps = []
            for i in range(num_factors):
                sorted_vals = sorted(factor_values[i])
                factor_maps.append({v: idx for idx, v in enumerate(sorted_vals)})
                factor_inv_maps.append({idx: v for idx, v in enumerate(sorted_vals)})

            return factor_maps, factor_inv_maps

    def _load_factor_maps_from_file(self, expected_num_factors: int) -> Tuple[
        List[Dict[str, int]], List[Dict[int, str]]]:
        """
        从txt文件加载因子索引映射（新增方法）

        文件格式规范：
        1. 每个因子的映射块之间用空行分隔
        2. 每个映射块内每行格式为"因子取值:索引"（索引为非负整数）
        3. 因子块顺序必须与解析出的因子顺序一致
        4. 必须包含所有实际出现的因子取值

        示例（2个因子）：
        No:0
        A:1
        B:2

        0:0
        1:1
        2:2
        """
        if not self.factor_index_map_path.exists():
            raise FileNotFoundError(f"因子索引映射文件不存在：{self.factor_index_map_path}")

        # 读取文件并分割为因子块（按空行分割）
        with open(self.factor_index_map_path, 'r', encoding='utf-8') as f:
            raw_lines = [line.rstrip('\n') for line in f]

        factor_blocks = []
        current_block = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped:  # 非空行加入当前块
                current_block.append(stripped)
            else:  # 空行作为块分隔符
                if current_block:
                    factor_blocks.append(current_block)
                    current_block = []
        if current_block:  # 处理最后一个块
            factor_blocks.append(current_block)

        # 校验因子数量匹配
        if len(factor_blocks) != expected_num_factors:
            raise ValueError(
                f"因子索引映射文件错误：文件中包含{len(factor_blocks)}个因子块，"
                f"但实际需要{expected_num_factors}个因子"
            )

        factor_maps = []
        factor_inv_maps = []

        # 解析每个因子块
        for block_idx, block in enumerate(factor_blocks):
            factor_name = self.factor_names[block_idx] if self.factor_names else f"因子{block_idx + 1}"
            value_to_idx = {}

            for line_num, line in enumerate(block, 1):
                if ':' not in line:
                    raise ValueError(
                        f"{factor_name}映射格式错误（第{line_num}行）：缺少分隔符':'，内容为'{line}'"
                    )
                val, idx_str = line.split(':', 1)
                val = val.strip()
                idx_str = idx_str.strip()

                # 校验索引格式
                try:
                    idx = int(idx_str)
                    if idx < 0:
                        raise ValueError(f"索引必须为非负整数，实际为{idx}")
                except ValueError as e:
                    raise ValueError(
                        f"{factor_name}映射格式错误（第{line_num}行）：{str(e)}"
                    ) from e

                # 校验重复定义
                if val in value_to_idx:
                    raise ValueError(
                        f"{factor_name}映射错误（第{line_num}行）：取值'{val}'重复定义"
                    )
                value_to_idx[val] = idx

            # 校验是否包含所有实际出现的因子取值
            actual_values = {factors[block_idx] for factors in self.class_to_factors.values()}
            missing_values = actual_values - set(value_to_idx.keys())
            if missing_values:
                raise ValueError(
                    f"{factor_name}映射不完整：缺少以下取值的索引定义：{sorted(missing_values)}"
                )

            # 构建反向映射并校验索引唯一性
            idx_to_value = {idx: val for val, idx in value_to_idx.items()}
            if len(idx_to_value) != len(value_to_idx):
                raise ValueError(f"{factor_name}映射错误：存在重复索引定义")

            factor_maps.append(value_to_idx)
            factor_inv_maps.append(idx_to_value)

        return factor_maps, factor_inv_maps

    def _build_batch_lookup_table(self) -> None:
        if not self.parse_factors or not self.factor_maps:
            raise RuntimeError("需先开启parse_factors=True并构建因子映射，才能构建批量查询表")

        self.lookup_table = {}

        def generate_combinations(index: int, current: List[int]) -> None:
            if index == self.num_factors:
                try:
                    factors = self.get_factors_from_indices(tuple(current))
                    cls = self.get_class_from_factors(factors)
                    self.lookup_table[tuple(current)] = self.get_label_from_class(cls)
                except ValueError:
                    pass
                return
            for idx in self.factor_inv_maps[index]:
                generate_combinations(index + 1, current + [idx])

        generate_combinations(0, [])

    # 基础功能：类别↔索引/标签 双向转换（原有逻辑不变）
    def get_idx_from_class(self, cls: str) -> int:
        if cls not in self.class_to_idx:
            raise ValueError(f"未知类别：{cls}，可选类别示例：{self.classes[:5]}...")
        return self.class_to_idx[cls]

    def get_class_from_idx(self, idx: int) -> str:
        if idx not in self.idx_to_class:
            raise ValueError(f"未知索引：{idx}，有效索引范围：0~{len(self.classes) - 1}")
        return self.idx_to_class[idx]

    def get_label_from_class(self, cls: str) -> int:
        return self.get_idx_from_class(cls)

    def get_class_from_label(self, label: int) -> str:
        return self.get_class_from_idx(label)

    # 因子相关功能（原有逻辑不变）
    def get_factors_from_class(self, cls: str) -> Tuple[str, ...]:
        if not self.parse_factors:
            raise RuntimeError("需先在初始化时设置parse_factors=True，才能解析类别中的因子")
        if cls not in self.class_to_factors:
            raise ValueError(f"未知类别：{cls}，可选类别示例：{self.classes[:5]}...")
        return self.class_to_factors[cls]

    def get_class_from_factors(self, factors: Tuple[str, ...]) -> str:
        if not self.parse_factors:
            raise RuntimeError("需先在初始化时设置parse_factors=True，才能通过因子构建类别")
        cls = '-'.join(factors)
        if cls not in self.classes:
            raise ValueError(f"因子组合对应的类别不存在：{cls}")
        return cls

    def get_indices_from_factors(self, factors: Tuple[str, ...]) -> Tuple[int, ...]:
        if not self.parse_factors:
            raise RuntimeError("需先在初始化时设置parse_factors=True，才能进行因子→索引转换")
        if len(factors) != self.num_factors:
            raise ValueError(f"因子数量不匹配：输入{len(factors)}个因子，实际需要{self.num_factors}个")

        indices = []
        for i in range(self.num_factors):
            factor_name = self.factor_names[i] if self.factor_names else f"因子{i + 1}"
            if factors[i] not in self.factor_maps[i]:
                raise ValueError(
                    f"未知{factor_name}取值：{factors[i]}，"
                    f"可选取值：{sorted(self.factor_maps[i].keys())}"
                )
            indices.append(self.factor_maps[i][factors[i]])

        return tuple(indices)

    def get_factors_from_indices(self, indices: Tuple[int, ...]) -> Tuple[str, ...]:
        if not self.parse_factors:
            raise RuntimeError("需先在初始化时设置parse_factors=True，才能进行索引→因子转换")
        if len(indices) != self.num_factors:
            raise ValueError(f"索引数量不匹配：输入{len(indices)}个索引，实际需要{self.num_factors}个")

        factors = []
        for i in range(self.num_factors):
            factor_name = self.factor_names[i] if self.factor_names else f"因子{i + 1}"
            if indices[i] not in self.factor_inv_maps[i]:
                raise ValueError(
                    f"未知{factor_name}索引：{indices[i]}，"
                    f"有效索引范围：0~{len(self.factor_inv_maps[i]) - 1}"
                )
            factors.append(self.factor_inv_maps[i][indices[i]])

        return tuple(factors)

    def get_label_from_factors(self, factors: Tuple[str, ...]) -> int:
        cls = self.get_class_from_factors(factors)
        return self.get_label_from_class(cls)

    def get_label_from_indices(self, indices: Tuple[int, ...]) -> int:
        factors = self.get_factors_from_indices(indices)
        return self.get_label_from_factors(factors)

    def get_labels_from_indices_batch(self, indices_tensor) -> List[int]:
        if not self.parse_factors or self.lookup_table is None:
            raise RuntimeError("需在初始化时同时设置parse_factors=True和build_lookup_table=True，才能批量获取标签")
        if isinstance(indices_tensor, torch.Tensor):
            indices_tensor = indices_tensor.cpu().numpy()

        labels = []
        for idx in indices_tensor:
            if len(idx) != self.num_factors:
                labels.append(self.default_no_label)
                continue
            index_tuple = tuple(map(int, idx))
            label = self.lookup_table.get(index_tuple, self.default_no_label)
            labels.append(label)

        return labels

    def print_mappings(self) -> None:
        print("\n=== 核心映射信息 ===")
        print(f"类别总数：{len(self.classes)}")
        print(f"所有类别：{self.classes}")
        print("类别→索引（标签）映射：", self.class_to_idx)

        if self.parse_factors:
            print(f"\n=== 因子解析信息（共{self.num_factors}个因子） ===")
            for i in range(self.num_factors):
                factor_name = self.factor_names[i] if self.factor_names else f"因子{i + 1}"
                print(f"{factor_name}→索引映射：{self.factor_maps[i]}")

            print(f"\n=== 默认No类别信息 ===")
            print(f"标签最小的No类别标签：{self.default_no_label}")
            print(f"对应的类别名称：{self.get_class_from_label(self.default_no_label)}")
            print(f"对应的因子元组：{self.get_factors_from_class(self.get_class_from_label(self.default_no_label))}")

            print("\n=== 所有类别→因子解析结果 ===")
            for cls in self.classes:
                factors = self.get_factors_from_class(cls)
                indices = self.get_indices_from_factors(factors)
                label = self.get_label_from_class(cls)
                print(f"类别：{cls} → 因子：{factors} → 索引：{indices} → 标签：{label}")


if __name__ == "__main__":
    mapper = FactorLabelMapper(
        data_dir=r"D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\train",
        class_list_path=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\seen_classes.txt',
        parse_factors=True,
        factor_names=["工况", "故障类型",'故障程度'],
        factor_index_map_path=r"D:\Code\2-ZSL\Zero-Shot-Learning\data\小波变换后的图片\zsl_crwu\factor_index_map.txt"
    )

    mapper.print_mappings()