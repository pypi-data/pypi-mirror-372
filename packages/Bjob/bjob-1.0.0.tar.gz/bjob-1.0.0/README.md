# Bjob - 工作性价比计算器

一个基于MCP的工作性价比计算工具，帮助用户综合评估薪资、工时、通勤等多维度因素。

## 安装

```bash
pip install Bjob
```

## 使用

### 作为MCP工具使用

在Trae中配置：

```json
{
  "mcpServers": {
    "Bjob": {
      "command": "uvx",
      "args": ["Bjob"]
    }
  }
}
```

### 直接运行

```bash
python -m Bjob
```

## 功能

- 计算工作性价比综合评分
- 考虑PPP转换因子
- 包含学历、经验、城市等个人因素
- 提供改进建议

## 支持的参数

- 年薪总包
- 每周工作天数
- 居家办公天数
- 年假天数
- 通勤时间
- 学历、工作经验、城市等级等

## 示例

```python
from Bjob import calculate_job_worth

result = calculate_job_worth(
    annual_salary=300000,
    work_days_per_week=5,
    daily_work_hours=8,
    commute_hours=1.5,
    education="本科",
    city_level="二线城市"
)
print(result)
```