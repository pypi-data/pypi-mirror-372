# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 18:11:31 2025

@author: mengshiquan
"""

#%% Decorators
## timer 执行时间
import time

def timer(fun):
    def wrapper(*args, **kwargs):
        st = time.time()
        res = fun(*args, **kwargs)
        ed = time.time()
        print(f'{fun.__name__} took {ed-st:.1f} sec')
        return res
    return wrapper

## 缓存结果, 避免了相同输入的冗余计算，显著加快工作流程
def momoize(func):
    cache = {}
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper


#%% data base
import pymysql
import pandas as pd
import os

def fetch_data_from_db(tbl_name, order_sql, db_name, batch_size=20000, batch_no=0):
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_database = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    conn=pymysql.connect(host = db_host,
                         user = db_user,
                         passwd=db_password,
                         port= db_port,
                         db=db_database,
                         charset='utf8'
    )
    cur = conn.cursor() # 生成游标对象
    offset = batch_no*batch_size #初始偏移量为0 
    cur.execute(f'SELECT COUNT(*) FROM `{tbl_name}`')
    total_records = cur.fetchone()[0]
    spend = 0
    
    rounds = int(total_records/batch_size)+1
    print(f'start to fetch {total_records} rows data...')
    print(f'An estimated {rounds} iterations will be performed.')
    round_time = []
    st = time.time()
    while offset < total_records:
        sql=f"SELECT * FROM `{tbl_name}` ORDER BY {order_sql} LIMIT {batch_size} OFFSET {offset}" # SQL语句
        cur.execute(sql)
        res = cur.fetchall()
    
        df = pd.DataFrame(res, columns=[i[0] for i in cur.description])
        df.to_parquet(f'{tbl_name}_{batch_no}.pqt')
    
        batch_no += 1
        ed = time.time()
        round_time.append(ed-st)
        spend += ed-st
        remain_rounds = rounds - batch_no
        remain_time = remain_rounds*(sum(round_time)/len(round_time))
        print(f'[{batch_no}/{rounds}]: takes {ed-st:.1f} sec, estimated to be completed in {remain_time} seconds. ')
        st = ed
        offset += len(res)
    
    ed = time.time()
    
    print(f'takes total {spend + ed-st:.1f} sec to fetch all data')
    
    cur.close() # 关闭游标
    conn.close() # 关闭连接
    return rounds

def concat_tbl_data(tbl_name, rounds):
    st = time.time()
    df_list = []
    whole_tm = 0
    for i in range(rounds):
        df = pd.read_parquet(f'{tbl_name}_{i}.pqt')
        ed = time.time()
        print(f'[{i}/{rounds}]: {ed-st:.1f} sec to read')
        whole_tm += ed-st
        st = ed
        df_list.append(df)
    
    df_all = pd.concat(df_list,axis=0)
    print(df_all.shape)
    
    df_all.to_parquet(f'{tbl_name}.pqt')
    
    ed = time.time()
    whole_tm += ed-st
    print(f'takes {whole_tm:.1f} sec to do all thing!')


def fetch_dataframe(sql, db_name='rpt'):
    db_host = os.getenv('DB_HOST','localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_database = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    conn=pymysql.connect(host = db_host,
                         user = db_user,
                         passwd=db_password,
                         port= db_port,
                         db=db_database,
                         charset='utf8'
    )
    cur = conn.cursor() # 生成游标对象
    cur.execute(sql)
    res = cur.fetchall()
    
    df = pd.DataFrame(res, columns=[i[0] for i in cur.description])
    return df

from datetime import datetime, timedelta
from tqdm import tqdm
# from joblib import Parallel, delayed

## 将dataframe插入到数据库 insert data into db from df
def df2db(df_input, db_name, tbl_name, mode='replace'):
    """
    将DataFrame插入到数据库中。

    :param df: 要插入的DataFrame
    :param db_name: 数据库名称
    :param tbl_name: 表名称
    :param mode: 'replace' 表示删除原有表并重建；'append' 表示在原表基础上追加数据
    """
    df = df_input.copy()
    def check_type(x):
        type_map = {int: 'INT', str: 'VARCHAR', float: 'FLOAT', list: 'VARCHAR', pd.Timestamp: 'DATETIME', datetime: 'DATETIME'}
        return type_map.get(type(x), 'VARCHAR')

    def table_exists_and_has_column(connection, tbl_name, column_name):
        """检查表是否存在以及是否包含指定列"""
        query = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{tbl_name}' AND column_name = '{column_name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0] > 0
    
    # 在DataFrame中新增 `insert_time` 列
    df['insert_time'] = datetime.now()

    col_names = df.columns.to_list()

    db_host = os.getenv('DB_HOST','localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_database = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    connection = pymysql.connect(host = db_host,
                         user = db_user,
                         passwd=db_password,
                         port= db_port,
                         db=db_database,
                         charset='utf8'
    )

    try:
        with connection.cursor() as cursor:
            if mode == 'replace':
                cursor.execute(f"DROP TABLE IF EXISTS {tbl_name}")

                # 生成表结构的SQL语句
                str_col_sql = ""
                for i, col in enumerate(tqdm(df.columns)):
                    typelist = df[df[col].notna()][col].apply(check_type).unique()
                    if len(typelist) != 1:
                        str_col_sql += f"    {col_names[i]} VARCHAR,\n"
                    else:
                        str_col_sql += f"    {col_names[i]} {typelist[0]},\n"
                    if i == len(df.columns) - 1:
                        str_col_sql = str_col_sql[:-2]

                # # 添加 `insert_time` 列的定义
                # str_col_sql += ",\n    insert_time DATETIME"

                create_table_query = f"""
                CREATE TABLE {tbl_name} (
                {str_col_sql});
                """
                print(create_table_query)
                cursor.execute(create_table_query)

            elif mode == 'append':
                # 检查表是否存在
                if not table_exists_and_has_column(connection, tbl_name, 'insert_time'):
                    raise ValueError(f"表 {tbl_name} 不存在，或表中缺少 'insert_time' 列，请使用 mode='replace' 创建新表。")

            cols = "`, `".join([str(i) for i in df.columns.tolist()])
            insert_sql = f"INSERT INTO `{tbl_name}` (`{cols}`) VALUES (" + "%s," * (len(df.columns) - 1) + "%s)"

            df.replace(np.nan, None, inplace=True)
            data_tuples = [tuple(x) for x in df.to_numpy()]

            cursor.executemany(insert_sql, data_tuples)

            connection.commit()

            print("DataFrame successfully written to the database.")

    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    finally:
        connection.close()

#%% distribution draw

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"] 
plt.rcParams['axes.unicode_minus']=False

# 数据处理函数
def preprocess_data(df, column, hue=None,v_min=None, v_max=None):
    """
    预处理数据：处理时间类型、过滤空值和无限值，并应用范围裁剪。
    """
    df = df.copy()
    data = df[column]
    if pd.api.types.is_datetime64_any_dtype(data):
        data = data.astype('int64') / 1000  # 转换时间为秒级别
        is_time = True
    else:
        data = data.values
        is_time = False

    # 过滤空值和无限值
    valid_mask = ~np.isnan(data) & ~np.isinf(data)
    data = data[valid_mask]
    hue_col = None
    if hue is not None:
        hue_col = df[hue][valid_mask]

    # 应用范围裁剪
    if v_min is not None and v_max is not None:
        if is_time:
            v_min = np.datetime64(pd.to_datetime(v_min)).astype('int64') / 1000
            v_max = np.datetime64(pd.to_datetime(v_max)).astype('int64') / 1000
        data = data[(data >= v_min) & (data <= v_max)]
        if hue is not None:
            hue_col = hue_col[(data >= v_min) & (data <= v_max)]

    return data, is_time, hue_col

# 统计信息计算函数
def calculate_statistics(data):
    """
    计算数据的统计信息。
    """
    stats = {
        'count': len(data),
        'max': np.max(data),
        'min': np.min(data),
        'mean': np.mean(data),
        'median': np.median(data),
        'std': np.std(data),
        'iqr_25': np.quantile(data, 0.25),
        'iqr_50': np.quantile(data, 0.5),
        'iqr_75': np.quantile(data, 0.75),
    }
    return stats

# 绘图函数
def plot_distribution(data, stats, is_time, plot_type="kde", hue_name=None, hue_col=None, title=None, colors=None):
    """
    绘制分布图，包括核密度曲线或直方图，以及统计标记。
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    if plot_type == "kde":
        if hue_col is None:
            # 计算密度
            density = scipy.stats.gaussian_kde(data)
            x = np.linspace(data.min(), data.max(), 100)
            y = density(x)

            # 绘图
            ax1.plot(x, y, label='Density Curve', color='#1F77B4')
            ax1.fill_between(x, y, alpha=0.3, color='#1F77B4')
            ax1.vlines(x[np.argmax(y)], 0, y.max(), linestyles='dashed', color='#1F77B4')

            # 时间轴处理
            if is_time:
                x_ticks = pd.to_datetime(x, unit='s').strftime('%Y-%m-%d')
                plt.xticks(x, x_ticks, rotation=90)

        else:
            # 多分类绘图
            unique_hues = np.unique(hue_col)
            colors = colors or ['#1F77B4', '#FF7F0E', '#39A639', '#D62728', '#9467BD']
            for i, h in enumerate(unique_hues):
                hue_data = data[hue_col == h]
                density = scipy.stats.gaussian_kde(hue_data)
                x = np.linspace(hue_data.min(), hue_data.max(), 100)
                y = density(x)

                ax1.plot(x, y, label=f'{hue_name}: {h}', color=colors[i])
                ax1.fill_between(x, y, alpha=0.3, color=colors[i])
                ax1.vlines(x[np.argmax(y)], 0, y.max(), linestyles='dashed', color=colors[i])

    elif plot_type == "histogram":
        bins = 30  # 默认30个分箱
        ax1.hist(data, bins=bins, color='#1F77B4', alpha=0.7, edgecolor='black', label='Histogram')

        # 时间轴处理
        if is_time:
            bin_edges = np.histogram_bin_edges(data, bins=bins)
            x_ticks = pd.to_datetime(bin_edges, unit='s').strftime('%Y-%m-%d')
            plt.xticks(bin_edges, x_ticks, rotation=90)

    elif plot_type == "kde+histogram":
        if hue_col is None:
            # 绘制直方图
            bins = 30
            ax2 = ax1.twinx()  # 添加第二y轴
            counts, bin_edges, _ = ax1.hist(data, bins=bins, color='#1F77B4', alpha=0.3, edgecolor='black', label='Histogram')
    
            # 绘制核密度曲线
            density = scipy.stats.gaussian_kde(data)
            x = np.linspace(data.min(), data.max(), 100)
            y = density(x)
            ax2.plot(x, y, label='Density Curve', color='#FF7F0E')
    
            # 设置y轴标签和比例
            ax1.set_ylabel('Frequency')
            ax2.set_ylabel('Density')
            ax2.set_ylim(0, max(y) * 1.2)
    
            # 时间轴处理
            if is_time:
                x_ticks = pd.to_datetime(bin_edges, unit='s').strftime('%Y-%m-%d')
                plt.xticks(bin_edges, x_ticks, rotation=90)
        else:
            # 多分类绘图
            unique_hues = np.unique(hue_col)
            colors = colors or ['#1F77B4', '#FF7F0E', '#39A639', '#D62728', '#9467BD']
            for i, h in enumerate(unique_hues):
                hue_data = data[hue_col == h]

                # 绘制直方图
                bins = 30
                ax2 = ax1.twinx()  # 添加第二y轴
                counts, bin_edges, _ = ax1.hist(hue_data, bins=bins, color=colors[i], alpha=0.3, edgecolor='black', label=f'{hue_name}: {h}')
                
                density = scipy.stats.gaussian_kde(hue_data)
                x = np.linspace(hue_data.min(), hue_data.max(), 100)
                y = density(x)
                ax2.plot(x, y, label=f'{hue_name}: {h}', color=colors[i])

                # 设置y轴标签和比例
                ax1.set_ylabel('Frequency')
                ax2.set_ylabel('Density')
                ax2.set_ylim(0, max(y) * 1.2)
                
                # ax1.fill_between(x, y, alpha=0.3, color=colors[i])
                # ax1.vlines(x[np.argmax(y)], 0, y.max(), linestyles='dashed', color=colors[i])

    ax1.set_title(title or "Distribution Plot")
    fig.legend(loc='upper right')
    plt.show()

# 主函数
def draw_distribute(
    df, column, v_min=None, v_max=None, hue=None, path=None, file_name=None, show_title=True, plot_type="kde"
):
    """
    绘制数据分布图，并保存到指定路径。

    参数:
        df (pd.DataFrame): 数据集，包含需要分析的列。
        column (str): 要分析的列的名称。
        v_min (str | float, optional): 数据筛选的最小值，支持时间字符串或数值。
        v_max (str | float, optional): 数据筛选的最大值，支持时间字符串或数值。
        hue (array-like, optional): 分类变量，指定不同类别数据以不同颜色显示。
        path (str, optional): 保存图像的路径。
        file_name (str, optional): 保存图像的文件名（不含扩展名）。
        show_title (bool, optional): 是否显示图表标题，默认为True。
        plot_type (str, optional): 绘图类型，可选 "kde" (核密度估计), "histogram" (直方图), "kde+histogram" (核密度+直方图)。
    
    注意:
        - 如果 `path` 和 `file_name` 均为空，则图像仅在屏幕显示，不会保存。
        - 当绘制时间类型数据时，`v_min` 和 `v_max` 应为有效的时间字符串格式，如 "2023-01-01"。
    """
    data, is_time, hue_col = preprocess_data(df, column, hue, v_min, v_max)
    stats = calculate_statistics(data)
    title = (
        f"{column} Distribution\n"
        f"Count: {stats['count']}, Max: {stats['max']}, Min: {stats['min']}\n"
        f"Mean: {stats['mean']}, Median: {stats['median']}, Std: {stats['std']}\n"
        f"IQR25: {stats['iqr_25']}, IQR50: {stats['iqr_50']}, IQR75: {stats['iqr_75']}"
    ) if show_title else None

    plot_distribution(data, stats, is_time, plot_type=plot_type, hue_name=hue, hue_col=hue_col, title=title)

    if path and file_name:
        plt.savefig(f"{path}/{file_name}.png", dpi=300, bbox_inches="tight", pad_inches=0.5)


#%% evalutate
from sklearn.metrics import f1_score, accuracy_score,roc_curve, auc
import matplotlib.pyplot as plt

def draw_best_f1_score(oof_xgb, class_of_interest, low_thres=0.2, high_thres=0.8):
    ### F1-score -------------------------------------------------------------------
    scores = []; thresholds = []
    best_score_xgb = 0; best_threshold_xgb = 0
    
    for threshold in np.arange(low_thres,high_thres,0.005):
        preds = (oof_xgb['predict'].values.reshape((-1))>threshold).astype('int')
        m = f1_score(oof_xgb['target'].values.reshape((-1)), preds, average='macro')   
        scores.append(m)
        thresholds.append(threshold)
        if m>best_score_xgb:
            best_score_xgb = m
            best_threshold_xgb = threshold
    
    # PLOT THRESHOLD VS. F1_SCORE
    plt.figure(figsize=(20,5))
    plt.plot(thresholds,scores,'-o',color='blue')
    plt.scatter([best_threshold_xgb], [best_score_xgb], color='blue', s=300, alpha=1)
    plt.xlabel('Threshold',size=14)
    plt.ylabel('Validation F1 Score',size=14)
    plt.title(f'Threshold vs. F1_Score with Best F1_Score = {best_score_xgb:.5f} at Best Threshold = {best_threshold_xgb:.4} \n{class_of_interest}',size=18)
    plt.show()
    
    print(f'F1_Score = {best_score_xgb:.5f}')
    return best_score_xgb

def draw_best_accuracy(oof_xgb, class_of_interest, low_thres=0.2, high_thres=0.8):
    ### Accuracy -------------------------------------------------------------------
    scores = []; thresholds = []
    best_score_xgb = 0; best_threshold_xgb = 0
    
    for threshold in np.arange(0.3,0.7,0.005):
        preds = (oof_xgb['predict'].values.reshape((-1))>threshold).astype('int')
        m = accuracy_score(oof_xgb['target'].values.reshape((-1)), preds)
        # target = oof_xgb['target'].values.reshape((-1))
        # res = preds+target
        # m = (len(res)-sum(res==1))/len(res)
        scores.append(m)
        thresholds.append(threshold)
        if m>best_score_xgb:
            best_score_xgb = m
            best_threshold_xgb = threshold
    
    # PLOT THRESHOLD VS. F1_SCORE
    plt.figure(figsize=(20,5))
    plt.plot(thresholds,scores,'-o',color='blue')
    plt.scatter([best_threshold_xgb], [best_score_xgb], color='blue', s=300, alpha=1)
    plt.xlabel('Threshold',size=14)
    plt.ylabel('Validation Accuracy Score',size=14)
    plt.title(f'Threshold vs. Accuracy with Best Accuracy = {best_score_xgb:.5f} at Best Threshold = {best_threshold_xgb:.4} \n{class_of_interest}',size=18)
    plt.show()
    
    print(f'Accuracy_Score = {best_score_xgb:.5f}')
    return best_score_xgb

def draw_auc_curve(oof_xgb, class_of_interest):
    ### AUC -----------------------------------------------------------------------
    pred = oof_xgb['predict'].values.reshape(-1)
    y=oof_xgb['target'].values.reshape((-1))
    
    fpr, tpr, thresholds = roc_curve(y, pred, pos_label=1)
    auc_score = auc(fpr, tpr)
    print('AUC: ', auc_score )
    
    from sklearn.metrics import RocCurveDisplay
    display = RocCurveDisplay.from_predictions(
        y,
        pred,
        name=f"{class_of_interest} vs the rest",
        color="darkorange",
        # plot_chance_level=True,
    )
    _ = display.ax_.set(
        xlabel="False Positive Rate",
        ylabel="True Positive Rate",
        title="One-vs-Rest ROC curves",
    )
    return auc_score 

def plot_importance_meng(clf, importance_type='weight', num_feats=10, percent=False):
    trees_info = clf.get_booster().trees_to_dataframe()
    ## 去掉叶子节点
    trees_info = trees_info[trees_info['Feature']!='Leaf'][['Feature', 'Split','Gain','Cover']]
    ## groupby 统计节点基本importance 值
    trees_imp = trees_info.groupby('Feature').agg({'Feature':'count', 'Gain':['sum','mean'], 'Cover':['sum', 'mean']})
    if percent:
        trees_imp['weight'] = trees_imp[trees_imp.columns[0]]/trees_imp[trees_imp.columns[0]].sum()
        trees_imp['total_gain'] = trees_imp[trees_imp.columns[1]]/trees_imp[trees_imp.columns[1]].sum()
        trees_imp['gain'] = trees_imp[trees_imp.columns[2]]/trees_imp[trees_imp.columns[2]].sum()
        trees_imp['total_cover'] = trees_imp[trees_imp.columns[3]]/trees_imp[trees_imp.columns[3]].sum()
        trees_imp['cover'] = trees_imp[trees_imp.columns[4]]/trees_imp[trees_imp.columns[4]].sum()
    else:
        trees_imp.columns = ['weight','total_gain','gain', 'total_cover', 'cover']
    
    feature_imp_df = trees_imp.sort_values(by=importance_type)[-num_feats:][importance_type]
    feature_imp = feature_imp_df.values
    # print(feature_imp)
    features = feature_imp_df.index.to_list()
    plt.barh(range(num_feats), feature_imp, align='center')
    plt.yticks(range(num_feats), features)
    for x,y in zip(feature_imp, range(num_feats)):
        plt.text(x, y, f"{x:.0f}")
    plt.title('Feature Importance')
    plt.xlabel(importance_type)
    plt.show()
    return features

#%% TSNE_plot
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

@timer
def tSNE_cal(df, x_name, perplexity=50, n=5000, random_state=42):
    np.random.seed(random_state)
    if n!=0:
        idx = np.random.choice(len(df), n, replace=False) # 不重复抽样 / 不放回
        df_sub = df.iloc[idx]
        df_sub = df_sub[x_name]
        df_sub = df_sub.fillna(0) # tsne不能含nan
        X = df_sub.values
    else:
        df_sub = df[x_name].copy()
        df_sub = df_sub.fillna(0) # tsne不能含nan
        X = df_sub.values
    tsne = TSNE(n_components=2, perplexity=perplexity, init='pca', random_state=random_state)
    X_tsne = tsne.fit_transform(X)
    return X_tsne, idx

from typing import Optional, List, Any, Dict
import warnings

def plot_tsne(
    df,
    X_tsne: np.ndarray,
    y_name: str,
    idx: Optional[List[int]] = None,
    split_by_category: bool = False,
    figsize: tuple = (12, 10),
    alpha: float = 0.6,
    marker_size: int = 50,
    margin_ratio: float = 0.05
) -> None:
    """
    可视化t-SNE降维结果
    
    Parameters:
    -----------
    df : DataFrame
        包含标签信息的数据框
    X_tsne : np.ndarray
        t-SNE降维后的二维坐标数据，形状为 (n_samples, 2)
    y_name : str
        用于颜色编码的标签列名
    idx : List[int], optional
        数据索引列表，如果为None则使用所有数据
    split_by_category : bool, optional
        是否按类别分开显示多个子图
    figsize : tuple, optional
        图形大小，默认为(12, 10)
    alpha : float, optional
        点透明度，默认为0.6
    marker_size : int, optional
        点大小，默认为50
    margin_ratio : float, optional
        边距比例，默认为0.05
    """
    
    # 数据验证
    if idx is not None:
        if len(idx) != len(X_tsne):
            warnings.warn("idx长度与X_tsne样本数不匹配，使用所有数据")
            y = df[y_name]
        else:
            y = df.iloc[idx][y_name]
    else:
        y = df[y_name]
    
    if len(y) != len(X_tsne):
        raise ValueError("标签数量与t-SNE坐标数量不匹配")
    
    # 创建颜色映射
    color_list = [
        '#1F77B4', '#FF7F0E', '#39A639', '#D62728', 
        '#9467BD', '#FE8004', '#B08838', '#FEFEFC',
        '#7F7F7F', '#BCBD22', '#17BECF', '#8C564B'
    ]
    
    unique_categories = np.unique(y)
    n_categories = len(unique_categories)
    
    if n_categories > len(color_list):
        warnings.warn(f"类别数量({n_categories})超过颜色列表长度，将重复使用颜色")
    
    cat2color = {
        category: color_list[i % len(color_list)] 
        for i, category in enumerate(unique_categories)
    }
    
    # 计算坐标范围（带边距）
    x_coords, y_coords = X_tsne[:, 0], X_tsne[:, 1]
    
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    y_min, y_max = np.min(y_coords), np.max(y_coords)
    
    x_margin = (x_max - x_min) * margin_ratio
    y_margin = (y_max - y_min) * margin_ratio
    
    x_limits = (x_min - x_margin, x_max + x_margin)
    y_limits = (y_min - y_margin, y_max + y_margin)
    
    if split_by_category:
        # 按类别分开显示
        fig, axes = plt.subplots(
            nrows=(n_categories + 1) // 2, 
            ncols=2, 
            figsize=(figsize[0], figsize[1] * ((n_categories + 1) // 2) / 2)
        )
        axes = axes.flatten() if n_categories > 1 else [axes]
        
        for i, category in enumerate(unique_categories):
            if i < len(axes):
                ax = axes[i]
                mask = (y == category)
                
                # 绘制当前类别
                ax.scatter(
                    x_coords[mask], y_coords[mask],
                    c=[cat2color[category]], 
                    label=category, 
                    alpha=alpha, 
                    s=marker_size
                )
                
                # 绘制其他类别（浅色）
                other_mask = ~mask
                if np.any(other_mask):
                    ax.scatter(
                        x_coords[other_mask], y_coords[other_mask],
                        c='lightgray', 
                        alpha=alpha * 0.3, 
                        s=marker_size * 0.5,
                        label='Other'
                    )
                
                ax.set_xlim(x_limits)
                ax.set_ylim(y_limits)
                ax.set_title(f'Category: {category}', fontsize=12)
                ax.set_xlabel('t-SNE Dimension 1')
                ax.set_ylabel('t-SNE Dimension 2')
                ax.legend()
                ax.grid(True, alpha=0.2)
        
        # 隐藏多余的子图
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
            
        plt.tight_layout()
        
    else:
        # 在同一图中显示所有类别
        fig, ax = plt.subplots(figsize=figsize)
        
        for category in unique_categories:
            mask = (y == category)
            ax.scatter(
                x_coords[mask], y_coords[mask],
                c=[cat2color[category]], 
                label=category, 
                alpha=alpha, 
                s=marker_size
            )
        
        ax.set_xlim(x_limits)
        ax.set_ylim(y_limits)
        ax.set_xlabel('t-SNE Dimension 1', fontsize=12)
        ax.set_ylabel('t-SNE Dimension 2', fontsize=12)
        ax.set_title('t-SNE Visualization', fontsize=14)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.2)
        
        plt.tight_layout()
    
    plt.show()
    
    # 输出统计信息
    print("t-SNE可视化统计:")
    print(f"总样本数: {len(X_tsne)}")
    print("各类别样本数量:")
    for category in unique_categories:
        count = np.sum(y == category)
        print(f"  {category}: {count} 个样本")
@timer
def tSNE_cal_plot(df, x_name, y_name, perplexity=50, n=5000, random_state=42, split=False):
    X_tsne, idx = tSNE_cal(df, x_name, perplexity=perplexity, n=n, random_state=random_state)
    plot_tsne(df, X_tsne, idx, y_name, split=split)
    return X_tsne, idx

def split_patient_from_tsne(
    X_tsne: np.ndarray, 
    df, 
    feature: str,
    rect_lim: Dict[str, Dict[str, tuple]],
    patient_id_col: str = 'index'
) -> Dict[str, List[Any]]:
    """
    可视化t-SNE降维结果并通过矩形区域选择患者数据
    
    Parameters:
    -----------
    X_tsne : np.ndarray
        t-SNE降维后的二维坐标数据，形状为 (n_samples, 2)
    df : DataFrame
        包含患者信息的数据框，行数应与X_tsne相同
    feature : str
        用于颜色编码的特征列名
    rect_lim : Dict[str, Dict[str, tuple]]
        矩形区域定义，格式为 {'区域名': {'x_lim': (min, max), 'y_lim': (min, max)}}
    patient_id_col : str, optional
        患者ID所在的列名，默认为'index'
    
    Returns:
    --------
    Dict[str, List[Any]]
        每个区域对应的患者ID列表
    """
    
    # 验证输入数据一致性
    if len(X_tsne) != len(df):
        raise ValueError(f"X_tsne长度({len(X_tsne)})与df行数({len(df)})不匹配")
    
    if feature not in df.columns:
        raise ValueError(f"特征列 '{feature}' 不在数据框中")
    
    if patient_id_col not in df.columns:
        raise ValueError(f"患者ID列 '{patient_id_col}' 不在数据框中")
    
    # 获取特征值
    y = df[feature]
    
    # 设置颜色映射
    color_list = ['#1F77B4', '#FF7F0E', '#39A639', '#D62728', 
                 '#9467BD', '#FE8004', '#B08838', '#FEFEFC']
    unique_categories = y.unique()
    cat2color = {cat: color_list[i % len(color_list)] 
                for i, cat in enumerate(unique_categories)}
    y_colors = y.map(cat2color).values
    
    # 计算画布范围（增加5%边距）
    x_coords = X_tsne[:, 0]
    y_coords = X_tsne[:, 1]
    
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()
    
    x_margin = (x_max - x_min) * 0.05
    y_margin = (y_max - y_min) * 0.05
    
    x_limits = (x_min - x_margin, x_max + x_margin)
    y_limits = (y_min - y_margin, y_max + y_margin)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(16, 16))
    points = {}
    
    # 绘制散点图
    for category in unique_categories:
        mask = (y == category)
        category_tsne = X_tsne[mask]
        category_colors = y_colors[mask]
        
        ax.scatter(category_tsne[:, 0], category_tsne[:, 1], 
                  c=category_colors, label=category, alpha=0.3, s=50)
    
    # 绘制矩形区域并提取点
    for region_name, region_limits in rect_lim.items():
        x_lim = region_limits['x_lim']
        y_lim = region_limits['y_lim']
        
        # 使用向量化操作筛选点
        x_in_range = (x_coords >= x_lim[0]) & (x_coords <= x_lim[1])
        y_in_range = (y_coords >= y_lim[0]) & (y_coords <= y_lim[1])
        in_region_mask = x_in_range & y_in_range
        
        # 获取区域内的患者ID
        case_ids = df.loc[in_region_mask, patient_id_col].tolist()
        points[region_name] = case_ids
        
        # 绘制矩形边界
        ax.hlines(y_lim, x_lim[0], x_lim[1], colors='red', linewidths=2)
        ax.vlines(x_lim, y_lim[0], y_lim[1], colors='red', linewidths=2)
        
        # 添加区域标签
        ax.text(np.mean(x_lim), y_lim[1], region_name, 
               fontsize=20, ha='center', va='bottom', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # 设置图形属性
    ax.set_xlim(x_limits)
    ax.set_ylim(y_limits)
    ax.set_xlabel('t-SNE Dimension 1', fontsize=14)
    ax.set_ylabel('t-SNE Dimension 2', fontsize=14)
    ax.set_title('t-SNE Visualization with Selection Regions', fontsize=16)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 输出统计信息
    print("区域选择统计:")
    for region_name, patient_ids in points.items():
        print(f"  {region_name}: {len(patient_ids)} 个患者")
    
    total_selected = sum(len(ids) for ids in points.values())
    print(f"总共选择了 {total_selected} 个患者")
    
    return points


#%% holidays
def calculate_easter_date(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)

# 定义函数，判断日期是否在复活节假期内
def in_easter_holiday(date):
    easter_date = calculate_easter_date(date.year)
    start_holiday = easter_date - timedelta(days=2)  # 假设复活节假期从复活节前两天开始
    end_holiday = easter_date + timedelta(days=2)  # 假设复活节假期到复活节后两天结束

    if start_holiday <= date <= end_holiday:
        return True
    else:
        return False

# 定义函数，判断日期是否在圣诞节假期内
def in_christmas_holiday(date):
    christmas_date = datetime(date.year, 12, 25)  # 圣诞节日期
    start_holiday = christmas_date.replace(day=21)  # 假设圣诞节假期从12月21日开始
    end_holiday = christmas_date.replace(day=31)  # 假设圣诞节假期到12月31日结束

    if start_holiday <= date <= end_holiday:
        return True
    else:
        return False

# 定义函数，判断日期所在的上旬、中旬或下旬
def get_period_of_month(date):
    day = date.day
    if day <= 10:
        return 1
    elif day <= 20:
        return 2
    else:
        return 3

#%% fetch Chinese holidays info from github
import requests
import re

def fetch_file_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        code = response.content
        # with open('yourfile.txt', 'wb') as file:
        #     file.write(response.content)        
        print("文件下载成功")
    else:
        print(f"文件下载失败，状态码: {response.status_code}")
    text = code.decode('utf-8')
    return text


def get_holidays_info(text):
    match = re.search(r'holidays\s*=\s*{[^}]*}', text)
    hosoliday_txt = match.group()
    result = re.sub(r'Holiday\.(\w+)\.value', r"'\1'", hosoliday_txt)
    return result

def get_workdays_info(text):
    match = re.search(r'workdays\s*=\s*{[^}]*}', text)
    workday_txt = match.group()
    result = re.sub(r'Holiday\.(\w+)\.value', r"'\1'", workday_txt)
    return result

def get_holiday_workday(url):
    text = fetch_file_from_github(url)
    holidays = eval(re.sub(r'holidays\s*=\s*', '', get_holidays_info(text)))
    workdays = eval(re.sub(r'workdays\s*=\s*', '', get_workdays_info(text)))    
    return holidays, workdays

#%% some models
def ridge_regression(X,y, lambda_param=0.1): # 添加正则化参数 lambda
    # 求解岭回归的闭式解
    X = np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)  # 添加常数列
    XTX = np.dot(X.T, X)
    XTy = np.dot(X.T, y)
    coefficients = np.dot(np.linalg.inv(XTX + lambda_param * np.eye(XTX.shape[0])), XTy)
    return coefficients

#%% time process
import calendar

def get_last_day_of_previous_month(date_str=None):
    """
    date_str: '2024-7-1', 默认为None则取当天
    获取上个月最后一天的日期
    :return: 上个月最后一天的日期对象
    """
    if date_str:
        today = datetime.strptime('2024-7-1','%Y-%m-%d')
    else:
        today = datetime.today()
    # 计算上个月的年份和月份
    last_month = today.month - 1 if today.month > 1 else 12
    last_month_year = today.year if today.month > 1 else today.year - 1

    # 获取上个月的最后一天
    _, last_day = calendar.monthrange(last_month_year, last_month)
    # 创建日期对象
    return datetime(last_month_year, last_month, last_day)