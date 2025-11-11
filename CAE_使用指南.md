# CAE文件转Point-E格式使用指南

## 概述

本功能可以将CAE（Nastran格式）文件转换为Point-E可接受的点云格式。

## 快速开始

### 命令行使用

最简单的方式是使用命令行工具：

```bash
# 将CAE文件转换为NPZ格式（Point-E原生格式）
python -m point_e.util.convert_cae 输入文件.cae 输出文件.npz --max-points 4096

# 转换为PLY格式（用于3D可视化工具）
python -m point_e.util.convert_cae 输入文件.cae 输出文件.ply --max-points 4096

# 不进行坐标归一化
python -m point_e.util.convert_cae 输入文件.cae 输出文件.npz --no-normalize
```

### Python API使用

```python
from point_e.util.cae_parser import load_cae_file

# 简单转换
point_cloud = load_cae_file(
    '输入文件.cae',
    max_points=4096,      # 下采样到4096个点
    normalize=True        # 将坐标归一化到[-1, 1]范围
)

# 保存为Point-E格式
point_cloud.save('输出文件.npz')

# 或保存为PLY格式用于可视化
with open('输出文件.ply', 'wb') as f:
    point_cloud.write_ply(f)
```

## 输入格式说明

### GRID格式（点坐标）
```
GRID        4649        2661.937-433.604113.7815
```
- 固定宽度字段（每个8个字符）
- 字段1: "GRID"
- 字段2: 点ID
- 字段3-5: X, Y, Z坐标（可能连在一起）

### CQUAD4格式（四边形单元）
```
CQUAD4   1111017  885657    4651    4650    4653    4649
```
- 字段1: "CQUAD4"
- 字段2: 单元ID
- 字段3: 属性ID
- 字段4-7: 四个点ID

### CTRIA3格式（三角形单元）
```
CTRIA3   1111015  885657    4653    4650    4652
```
- 字段1: "CTRIA3"
- 字段2: 单元ID
- 字段3: 属性ID
- 字段4-6: 三个点ID

### PSHELL格式（壳属性）
```
PSHELL    885657       1      2.       1               1              0.
```
- 字段1: "PSHELL"
- 字段2: 属性ID（用于颜色分配）

## 输出格式

### NPZ格式（Point-E原生）
```python
{
    'coords': np.ndarray(shape=(N, 3), dtype=float32),  # XYZ坐标
    'R': np.ndarray(shape=(N,), dtype=float32),         # 红色通道 [0, 1]
    'G': np.ndarray(shape=(N,), dtype=float32),         # 绿色通道 [0, 1]
    'B': np.ndarray(shape=(N,), dtype=float32),         # 蓝色通道 [0, 1]
}
```

## 功能特点

### 1. 自动下采样
当点数超过`max-points`时，使用**最远点采样**算法自动下采样，确保点云保持良好的空间分布。

```python
# 从几万个点下采样到4096个点
point_cloud = load_cae_file('大型文件.cae', max_points=4096)
```

### 2. 颜色分配
根据属性ID自动分配颜色：
- 每个点通过其所属单元映射到属性ID
- 每个属性ID获得一个独特的颜色
- 使用HSV色彩空间生成易于区分的颜色

### 3. 自定义颜色

```python
from point_e.util.cae_parser import CAEParser

# 解析CAE文件
parser = CAEParser()
parser.parse_file('输入文件.cae')

# 定义自定义颜色映射（属性ID -> RGB元组）
custom_colors = {
    885657: (1.0, 0.0, 0.0),  # 红色
    885658: (0.0, 1.0, 0.0),  # 绿色
    885659: (0.0, 0.0, 1.0),  # 蓝色
}

# 使用自定义颜色转换
point_cloud = parser.to_point_cloud(
    max_points=4096,
    normalize=True,
    color_map=custom_colors
)
```

### 4. 坐标归一化
默认情况下，坐标会被归一化到大约[-1, 1]范围：
1. 点云居中（减去均值）
2. 按最大绝对值缩放

这有助于Point-E模型更好地处理几何体。

## 完整示例

查看以下示例文件了解更多用法：

1. **基础用法**: `point_e/examples/cae_conversion_example.py`
   - 基本转换
   - 自定义颜色映射
   - 详细数据检查
   - 不同的下采样策略

2. **与Point-E集成**: `point_e/examples/cae_to_pointe_integration.py`
   - 完整的工作流程演示
   - 与Point-E模型的集成
   - 可视化

3. **详细文档**: `point_e/examples/CAE_CONVERSION_README.md`
   - 完整的功能说明
   - 故障排除指南

## 运行示例

```bash
# 运行基础示例
python point_e/examples/cae_conversion_example.py

# 运行集成示例
python point_e/examples/cae_to_pointe_integration.py
```

## 常见问题

### 无法解析坐标
确保CAE文件符合Nastran格式规范。解析器支持：
- 固定宽度格式
- 空格分隔格式
- 连接的坐标值（如`2661.937-433.604113.7815`）

### 点没有颜色或颜色都相同
检查：
1. CQUAD4/CTRIA3单元引用了正确的GRID点ID
2. PSHELL条目存在且属性ID正确
3. 属性ID映射正确

### 点数太多
使用`--max-points`参数限制点数：
```bash
python -m point_e.util.convert_cae input.cae output.npz --max-points 4096
```

## 技术支持

如有问题，请参考：
- [完整文档](point_e/examples/CAE_CONVERSION_README.md)
- [示例代码](point_e/examples/)
- 或提交Issue到GitHub仓库
