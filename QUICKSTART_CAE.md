# Quick Start: CAE to Point-E Conversion

快速开始：CAE文件转Point-E格式

## Installation / 安装

```bash
cd point-e
pip install -e .
```

## Quick Usage / 快速使用

### 1. Command Line / 命令行

```bash
# Convert CAE to Point-E NPZ format
# 转换CAE文件为Point-E的NPZ格式
python -m point_e.util.convert_cae your_file.cae output.npz --max-points 4096

# Convert to PLY for visualization
# 转换为PLY格式用于可视化
python -m point_e.util.convert_cae your_file.cae output.ply --max-points 4096
```

### 2. Python API / Python接口

```python
from point_e.util import load_cae_file

# Load and convert CAE file
# 加载并转换CAE文件
point_cloud = load_cae_file(
    'your_file.cae',
    max_points=4096,      # Downsample to 4096 points / 下采样到4096个点
    normalize=True        # Normalize coords / 归一化坐标
)

# Save in Point-E format
# 保存为Point-E格式
point_cloud.save('output.npz')
```

### 3. With Custom Colors / 自定义颜色

```python
from point_e.util.cae_parser import CAEParser

parser = CAEParser()
parser.parse_file('your_file.cae')

# Define custom colors by property ID
# 根据属性ID定义自定义颜色
custom_colors = {
    885657: (1.0, 0.0, 0.0),  # Red / 红色
    885658: (0.0, 1.0, 0.0),  # Green / 绿色
    885659: (0.0, 0.0, 1.0),  # Blue / 蓝色
}

point_cloud = parser.to_point_cloud(
    max_points=4096,
    color_map=custom_colors
)
point_cloud.save('output.npz')
```

## Input Format / 输入格式

Your CAE file should contain / 你的CAE文件应包含：

```
GRID        4649        2661.937-433.604113.7815
GRID        4650        2662.825-436.489116.7319
...
CQUAD4   1111017  885657    4651    4650    4653    4649
CTRIA3   1111015  885657    4653    4650    4652
...
PSHELL    885657       1      2.       1               1              0.
```

## Output Format / 输出格式

NPZ file contains / NPZ文件包含：
- `coords`: Point coordinates (N, 3) / 点坐标
- `R`, `G`, `B`: Color channels (N,) / 颜色通道

Compatible with Point-E models / 与Point-E模型兼容 ✓

## Full Documentation / 完整文档

- English: [CAE_CONVERSION_README.md](point_e/examples/CAE_CONVERSION_README.md)
- 中文: [CAE_使用指南.md](CAE_使用指南.md)
- Summary: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## Examples / 示例

```bash
# Run examples / 运行示例
python point_e/examples/cae_conversion_example.py
python point_e/examples/cae_to_pointe_integration.py
```

## Support / 支持

For questions, check the documentation or create an issue.
如有问题，请查看文档或提交Issue。
