# bigquant 数据SDK

bigquant 数据SDK 是专为金融数据查询和操作设计的强大工具，提供与 bigquant 数据服务的无缝集成。该 SDK 适用于需要高效、可靠地访问高质量金融数据集的金融分析师、量化研究员和数据科学家。

## 特性

- **认证**: 使用您的访问密钥和秘密密钥安全地认证您的 bigquant 账户。
- **配额管理**: 轻松检索当前配额信息，监控数据使用情况。
- **数据读取**: 轻松从 bigquant 数据库（BDB）读取金融数据到不同的格式，如 Apache Arrow 表或 Pandas DataFrame，支持分区过滤和列选择。
- **数据写入**: （尚不支持）未来将具有分区、索引、处理重复数据、排序和文档支持等高级功能将数据写回 BDB。
- **数据删除**: （尚不支持）未来将可以安全删除不再需要的数据。

## 快速开始

要开始使用 bigquant 数据SDK，首先使用 pip 安装包：

```shell
pip3 install bigquantdai
```

然后，您可以认证并开始查询金融数据：

```python
from bigquantdai import dai

# 使用 bigquant 认证
dai.login('您的访问密钥', '您的秘密密钥')

# 创建 DataSource 实例
data_source = dai.DataSource('您的数据源ID')

# 读取数据为 Apache Arrow 表
arrow_table = data_source.read_bdb()

# 或者将数据读取为 Pandas DataFrame
pandas_df = data_source.read_bdb(as_type=pd.DataFrame)

# 注意: 数据写入和数据删除功能目前尚不支持。
```

## 文档

有关使用 bigquant 数据SDK 的更多信息，请参考我们的[文档](https://bigquant.com/wiki/doc/sdk-gMEOV2bGYi)。

## 支持

如果您需要帮助或有任何问题，请通过我们的[官方网站](https://bigquant.com)联系我们。

---

今天就开始您的数据驱动投资之旅吧，使用 bigquant 数据SDK！