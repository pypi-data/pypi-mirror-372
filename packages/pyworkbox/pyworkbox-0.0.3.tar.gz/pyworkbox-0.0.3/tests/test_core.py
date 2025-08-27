# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 18:11:58 2025

@author: mengshiquan
"""

# test_core.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from unittest.mock import patch, MagicMock

# 导入要测试的模块
from your_package_name.core import (
    timer,
    momoize,
    fetch_data_from_db,
    concat_tbl_data,
    fetch_dataframe,
    df2db,
    preprocess_data,
    calculate_statistics,
    plot_distribution,
    draw_distribute,
    draw_best_f1_score,
    draw_best_accuracy,
    draw_auc_curve,
    plot_importance_meng,
    tSNE_cal,
    plot_tsne,
    tSNE_cal_plot,
    split_patient_from_tsne,
    calculate_easter_date,
    in_easter_holiday,
    in_christmas_holiday,
    get_period_of_month,
    fetch_file_from_github,
    get_holidays_info,
    get_workdays_info,
    get_holiday_workday,
    ridge_regression,
    get_last_day_of_previous_month
)

# 替换为你的包名
your_package_name = "your_package_name"

class TestDecorators:
    """测试装饰器函数"""
    
    def test_timer_decorator(self, capsys):
        """测试timer装饰器"""
        
        @timer
        def test_function():
            return "test_result"
        
        result = test_function()
        
        # 检查函数返回值
        assert result == "test_result"
        
        # 检查输出内容
        captured = capsys.readouterr()
        assert "test_function took" in captured.out
    
    def test_momoize_decorator(self):
        """测试momoize装饰器"""
        
        call_count = 0
        
        @momoize
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次相同参数调用，应该使用缓存
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 1  # 调用次数不应增加
        
        # 不同参数调用
        result3 = test_function(3)
        assert result3 == 6
        assert call_count == 2

class TestDatabaseFunctions:
    """测试数据库相关函数"""
    
    @patch('your_package_name.core.pymysql.connect')
    def test_fetch_dataframe(self, mock_connect):
        """测试fetch_dataframe函数"""
        # 创建mock对象
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # 模拟数据库返回结果
        mock_cursor.description = [('col1',), ('col2',)]
        mock_cursor.fetchall.return_value = [(1, 'a'), (2, 'b')]
        
        # 执行函数
        df = fetch_dataframe("SELECT * FROM test_table")
        
        # 验证结果
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 2)
        assert list(df.columns) == ['col1', 'col2']
        
        # 验证数据库连接和查询被调用
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_with("SELECT * FROM test_table")

class TestDistributionFunctions:
    """测试分布绘图函数"""
    
    def test_preprocess_data_numeric(self):
        """测试数值数据预处理"""
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        data, is_time, hue_col = preprocess_data(df, 'value')
        
        assert isinstance(data, np.ndarray)
        assert not is_time
        assert hue_col is None
        assert len(data) == 5
    
    def test_preprocess_data_datetime(self):
        """测试时间数据预处理"""
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5),
            'category': ['A', 'B', 'A', 'B', 'A']
        })
        data, is_time, hue_col = preprocess_data(df, 'date', hue='category')
        
        assert is_time
        assert hue_col is not None
        assert len(hue_col) == 5
    
    def test_calculate_statistics(self):
        """测试统计计算"""
        data = np.array([1, 2, 3, 4, 5])
        stats = calculate_statistics(data)
        
        assert stats['count'] == 5
        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['std'] == pytest.approx(1.414, 0.001)

class TestEvaluationFunctions:
    """测试评估函数"""
    
    def test_draw_best_f1_score(self):
        """测试F1分数计算"""
        oof_data = pd.DataFrame({
            'predict': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'target': [0, 0, 0, 0, 1, 1, 1, 1, 1]
        })
        
        best_score = draw_best_f1_score(oof_data, 'test_class')
        assert 0 <= best_score <= 1
    
    def test_draw_best_accuracy(self):
        """测试准确率计算"""
        oof_data = pd.DataFrame({
            'predict': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            'target': [0, 0, 0, 0, 1, 1, 1, 1, 1]
        })
        
        best_score = draw_best_accuracy(oof_data, 'test_class')
        assert 0 <= best_score <= 1

class TestTSNEFunctions:
    """测试TSNE函数"""
    
    def test_tSNE_cal(self):
        """测试TSNE计算"""
        df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'label': np.random.choice(['A', 'B'], 100)
        })
        
        X_tsne, idx = tSNE_cal(df, ['feature1', 'feature2'], n=50)
        
        assert X_tsne.shape[0] == 50
        assert X_tsne.shape[1] == 2
        assert len(idx) == 50

class TestHolidayFunctions:
    """测试节假日函数"""
    
    def test_calculate_easter_date(self):
        """测试复活节日期计算"""
        easter_2023 = calculate_easter_date(2023)
        assert isinstance(easter_2023, datetime)
        assert easter_2023.year == 2023
    
    def test_in_easter_holiday(self):
        """测试复活节假期判断"""
        # 2023年复活节是4月9日
        easter_day = datetime(2023, 4, 9)
        assert in_easter_holiday(easter_day)
        
        # 非复活节日期
        normal_day = datetime(2023, 6, 15)
        assert not in_easter_holiday(normal_day)
    
    def test_in_christmas_holiday(self):
        """测试圣诞节假期判断"""
        christmas_day = datetime(2023, 12, 25)
        assert in_christmas_holiday(christmas_day)
        
        # 非圣诞节日期
        normal_day = datetime(2023, 6, 15)
        assert not in_christmas_holiday(normal_day)
    
    def test_get_period_of_month(self):
        """测试月份分段"""
        assert get_period_of_month(datetime(2023, 1, 5)) == 1  # 上旬
        assert get_period_of_month(datetime(2023, 1, 15)) == 2  # 中旬
        assert get_period_of_month(datetime(2023, 1, 25)) == 3  # 下旬

class TestModelFunctions:
    """测试模型函数"""
    
    def test_ridge_regression(self):
        """测试岭回归"""
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([3, 7, 11])
        
        coefficients = ridge_regression(X, y, lambda_param=0.1)
        
        assert isinstance(coefficients, np.ndarray)
        assert len(coefficients) == 3  # 包括截距项

class TestTimeFunctions:
    """测试时间处理函数"""
    
    def test_get_last_day_of_previous_month(self):
        """测试获取上个月最后一天"""
        # 测试指定日期
        result = get_last_day_of_previous_month('2024-07-01')
        assert result == datetime(2024, 6, 30)
        
        # 测试当前日期（需要mock当前时间）
        with patch('your_package_name.core.datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2024, 7, 15)
            mock_datetime.strptime = datetime.strptime
            result = get_last_day_of_previous_month()
            assert result == datetime(2024, 6, 30)

class TestUtilityFunctions:
    """测试工具函数"""
    
    @patch('your_package_name.core.requests.get')
    def test_fetch_file_from_github(self, mock_get):
        """测试从GitHub获取文件"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        content = fetch_file_from_github("https://github.com/test/test.py")
        assert content == "test content"
        
        mock_response.status_code = 404
        content = fetch_file_from_github("https://github.com/test/test.py")
        assert "文件下载失败" in content

# 运行测试的主函数
if __name__ == "__main__":
    pytest.main([__file__, "-v"])