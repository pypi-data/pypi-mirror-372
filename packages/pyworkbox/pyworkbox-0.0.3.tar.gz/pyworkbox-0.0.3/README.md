# PyWorkBox

[![PyPI Version](https://img.shields.io/pypi/v/pyworkbox.svg)](https://pypi.org/project/pyworkbox/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyworkbox.svg)](https://pypi.org/project/pyworkbox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

这是一个包含常用功能的 Python 工具函数库，涵盖装饰器、数据库操作、数据可视化、模型评估、降维可视化、节假日处理等多个方面。

## Installation

```bash
pip install pyworkbox
```

### database parameter setup

在使用数据库功能前，请设置以下环境变量：

```bash
# Linux/macOS
echo 'export DB_HOST="your_database_host"' >> ~/.bashrc
echo 'export DB_PORT=5432' >> ~/.bashrc
echo 'export DB_NAME="your_database_name"' >> ~/.bashrc
echo 'export DB_USER="your_username"' >> ~/.bashrc
echo 'export DB_PASSWORD="your_password"' >> ~/.bashrc
source ~/.bashrc

# Windows (Command Prompt)
setx DB_HOST "your_database_host"
setx DB_PORT 5432
setx DB_NAME "your_database_name"
setx DB_USER "your_username"
setx DB_PASSWORD "your_password"

# Windows (PowerShell)
[Environment]::SetEnvironmentVariable("DB_HOST", "your_database_host", "User")
[Environment]::SetEnvironmentVariable("DB_PORT", 5432, "User")
[Environment]::SetEnvironmentVariable("DB_NAME", "your_database_name", "User")
[Environment]::SetEnvironmentVariable("DB_USER", "your_username", "User")
[Environment]::SetEnvironmentVariable("DB_PASSWORD", "your_password", "User")
## Window设置完环境变量以后需要重启电脑
```

## Quick Start

```python
from pyworkbox import fetch_dataframe

# 使用主要功能
sql = 'select * from table limit 10;'

df = fetch_dataframe(sql)
```

## 功能模块说明

### 1. 装饰器（Decorators）

#### `timer`
用于测量函数执行时间的装饰器。

```python
@timer
def my_function():
    time.sleep(1)
```

#### `memoize`
缓存函数结果的装饰器，避免重复计算。

```python
@memoize
def expensive_function(x):
    return x * x
```

---

### 2. 数据库操作（Database）

#### `fetch_data_from_db`
从 MySQL 数据库分批次读取数据并保存为 Parquet 文件。

```python
rounds = fetch_data_from_db(
    tbl_name='my_table',
    order_sql='id',
    db_name='my_db',
    batch_size=10000
)
```

#### `concat_tbl_data`
合并多个 Parquet 文件为一个 DataFrame。

```python
concat_tbl_data('my_table', rounds)
```

#### `fetch_dataframe`
执行 SQL 查询并返回 DataFrame。

```python
df = fetch_dataframe('SELECT * FROM my_table', db_name='my_db')
```

#### `df2db`
将 DataFrame 写入数据库（支持覆盖或追加模式）。

```python
df2db(df, db_name='my_db', tbl_name='my_table', mode='replace')
```

---

### 3. 数据分布可视化（Distribution Plot）

#### `draw_distribute`
绘制数据的分布图（支持 KDE、直方图、混合图）。

```python
draw_distribute(
    df, 
    column='age', 
    v_min=0, 
    v_max=100, 
    hue='gender',
    plot_type="kde+histogram"
)
```

---

### 4. 模型评估（Evaluation）

#### `draw_best_f1_score`
绘制 F1 分数随阈值变化图，返回最佳 F1 分数。

```python
best_f1 = draw_best_f1_score(oof_xgb, 'class_1')
```

#### `draw_best_accuracy`
绘制准确率随阈值变化图，返回最佳准确率。

```python
best_acc = draw_best_accuracy(oof_xgb, 'class_1')
```

#### `draw_auc_curve`
绘制 ROC 曲线并计算 AUC。

```python
auc_score = draw_auc_curve(oof_xgb, 'class_1')
```

#### `plot_importance_meng`
绘制特征重要性图（适用于 XGBoost 模型）。

```python
top_features = plot_importance_meng(clf, importance_type='weight', num_feats=10)
```

---

### 5. t-SNE 可视化

#### `tSNE_cal_plot`
计算并绘制 t-SNE 降维结果。

```python
X_tsne, idx = tSNE_cal_plot(
    df, 
    x_name=['feature1', 'feature2'], 
    y_name='label',
    n=5000,
    perplexity=50
)
```

#### `split_patient_from_tsne`
根据矩形区域从 t-SNE 图中提取样本。

```python
rect_lim = {
    'group1': {'x_lim': [-10, 10], 'y_lim': [-10, 10]}
}
points = split_patient_from_tsne(X_tsne, rect_lim, df, 'label')
```

---

### 6. 节假日处理（Holidays）

#### `in_easter_holiday`
判断日期是否在复活节假期内。

```python
is_easter = in_easter_holiday(datetime(2023, 4, 9))
```

#### `in_christmas_holiday`
判断日期是否在圣诞节假期内。

```python
is_christmas = in_christmas_holiday(datetime(2023, 12, 25))
```

#### `get_period_of_month`
判断日期属于上旬、中旬还是下旬。

```python
period = get_period_of_month(datetime(2023, 7, 15))  # 返回 2
```

#### `get_holiday_workday`
从 GitHub 获取节假日和调休信息。

```python
holidays, workdays = get_holiday_workday('https://raw.githubusercontent.com/xxx/holidays.js')
```

---

### 7. 模型工具（Models）

#### `ridge_regression`
岭回归闭式解实现。

```python
coef = ridge_regression(X, y, lambda_param=0.1)
```

---

### 8. 时间处理（Time Processing）

#### `get_last_day_of_previous_month`
获取上个月的最后一天。

```python
last_day = get_last_day_of_previous_month()
# 或指定日期
last_day = get_last_day_of_previous_month('2024-07-01')
```

---

## 使用示例

```python
from my_utils import timer, fetch_dataframe, draw_distribute

@timer
def process_data():
    df = fetch_dataframe('SELECT * FROM users', db_name='test_db')
    draw_distribute(df, 'age', v_min=0, v_max=100)

process_data()
```

---

## 注意事项

- 数据库连接参数已硬编码，请根据需要修改 `host`、`user`、`passwd` 等字段。
- 部分函数依赖外部库，请确保已安装所需依赖。
- 可视化函数默认使用中文字体（Microsoft YaHei），请确保系统中已安装该字体或替换为其他支持中文的字体。

---

如果有任何问题或建议，欢迎联系维护者：mengvision