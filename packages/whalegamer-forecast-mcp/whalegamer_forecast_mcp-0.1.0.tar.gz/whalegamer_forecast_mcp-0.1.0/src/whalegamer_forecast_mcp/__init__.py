"""FastMCP sales forecast tool.

A tool for forecasting sales data using Prophet model.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import json
from datetime import datetime
import os
import warnings
from mcp.server.fastmcp import FastMCP

# 忽略警告
warnings.filterwarnings('ignore')

# Create an MCP server
mcp = FastMCP("SalesForecast")


class ProphetSalesForecast:
    """基于Prophet的销量预测系统（专为少量数据优化）"""
    
    def __init__(self):
        """初始化系统"""
        self.time_series = None
        self.prophet_model = None
        self.prophet_forecast = None
        self.report = {
            'data_exploration': {},
            'prophet': {},
            'best_model': {'name': 'Prophet', 'reason': '专为少量数据设计'}
        }
    
    def load_data_from_list(self, sales_data, start_date):
        """
        从列表加载销售数据
        
        参数:
            sales_data: 销量数据列表
            start_date: 起始日期字符串 (YYYY-MM-DD)
        """
        try:
            # 创建日期范围
            start_date = pd.to_datetime(start_date)
            date_range = pd.date_range(start=start_date, periods=len(sales_data), freq='MS')
            
            # 创建时间序列
            self.time_series = pd.Series(sales_data, index=date_range)
            
            # print(f"数据加载成功，共 {len(self.time_series)} 个数据点")
            # print(f"日期范围: {self.time_series.index.min()} 至 {self.time_series.index.max()}")
            
            return self.time_series
            
        except Exception as e:
            # print(f"数据加载错误: {str(e)}")
            raise
    
    def quick_data_exploration(self, plot=True):
        """
        快速数据探索与分析
        
        参数:
            plot: 是否绘制数据图表
        """
        if self.time_series is None:
            raise ValueError("请先加载数据")
            
        time_series = self.time_series
        # print("\n正在进行快速数据探索...")
            
        # 基本统计信息
        stats = time_series.describe()
        # print("\n数据基本统计信息:")
        # print(stats)
        
        # 缺失值检查
        missing_values = time_series.isnull().sum()
        # print(f"\n缺失值数量: {missing_values}")
        
        # 保存数据探索结果
        self.report['data_exploration'] = {
            'stats': stats.to_dict(),
            'missing_values': int(missing_values),
            'data_points': len(time_series)
        }
        
        # 数据图表绘制已移除
        
        return self.report['data_exploration']
    
    def preprocess_data(self, transform_method='log'):
        """
        数据预处理（转换）
        
        参数:
            transform_method: 转换方法，可选 'log' 或 'sqrt'
        """
        if self.time_series is None:
            raise ValueError("请先加载数据")
            
        time_series = self.time_series
        # print("\n正在进行数据预处理...")
            
        # 数据转换（Prophet对转换不敏感，但可以尝试）
        if transform_method == 'log':
            # 对数转换（添加小常数避免log(0)）
            transformed_data = np.log1p(time_series)
            # print(f"使用对数转换处理数据（log(1+x)）")
        elif transform_method == 'sqrt':
            # 平方根转换
            transformed_data = np.sqrt(time_series)
            # print(f"使用平方根转换处理数据")
        else:
            # 不进行转换
            transformed_data = time_series
            # print(f"不进行数据转换")
        
        return transformed_data
    
    def run_prophet_model(self, forecast_steps=12, growth='linear', seasonality_mode='additive'):
        """
        运行 Prophet 模型进行预测（专为少量数据优化）
        
        参数:
            forecast_steps: 预测未来的步数
            growth: 增长模型 ('linear', 'flat')
            seasonality_mode: 季节性模式 ('additive', 'multiplicative')
        """
        if self.time_series is None:
            raise ValueError("请先加载数据")
            
        time_series = self.time_series
            
        try:
            # print("准备 Prophet 模型数据...")
            
            # 准备 Prophet 格式的数据
            df_prophet = pd.DataFrame({
                'ds': time_series.index,
                'y': time_series.values
            })
            
            # 创建并训练模型（专为少量数据优化）
            # print("训练 Prophet 模型中...")
            self.prophet_model = Prophet(
                growth=growth,
                seasonality_mode=seasonality_mode,
                yearly_seasonality='auto',
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,  # 减少突变点影响
                seasonality_prior_scale=10.0,  # 增加季节性强度
                holidays_prior_scale=10.0,
                mcmc_samples=0,  # 不使用MCMC（小数据更快）
                interval_width=0.95  # 95%置信区间
            )
            
            # 添加自定义季节性（如果有足够数据）
            if len(time_series) > 12:
                self.prophet_model.add_seasonality(
                    name='monthly',
                    period=30.5,
                    fourier_order=3  # 减少参数数量
                )
            
            self.prophet_model.fit(df_prophet)
            
            # 创建预测数据框
            freq = pd.infer_freq(time_series.index) or 'MS'
            future = self.prophet_model.make_future_dataframe(
                periods=forecast_steps, 
                freq=freq,
                include_history=True
            )
            
            # 预测
            self.prophet_forecast = self.prophet_model.predict(future)
            
            # Prophet模型组件分解图已移除
            # print("\nProphet 模型组件分解已完成")
            
            # 计算评估指标（使用历史数据）
            historical = self.prophet_forecast[self.prophet_forecast['ds'] <= time_series.index.max()]
            mae = mean_absolute_error(time_series, historical['yhat'])
            rmse = np.sqrt(mean_squared_error(time_series, historical['yhat']))
            
            # 保存模型结果
            self.report['prophet'] = {
                'forecast_steps': int(forecast_steps),
                'forecast_mean': self.prophet_forecast['yhat'][-forecast_steps:].tolist(),
                'lower_95': self.prophet_forecast['yhat_lower'][-forecast_steps:].tolist(),
                'upper_95': self.prophet_forecast['yhat_upper'][-forecast_steps:].tolist(),
                'mae': float(mae),
                'rmse': float(rmse),
                'growth_model': growth,
                'seasonality_mode': seasonality_mode
            }
            
            # print(f"Prophet 模型预测完成，预测未来 {forecast_steps} 个周期")
            # print(f"历史数据MAE: {mae:.2f}, RMSE: {rmse:.2f}")
            
            return self.prophet_forecast
            
        except Exception as e:
            # print(f"Prophet 模型错误: {str(e)}")
            raise
    
    def plot_forecast(self, title=None, figsize=(12, 6)):
        """
        生成绘制预测结果的Python代码并返回
        
        参数:
            title: 图表标题
            figsize: 图表大小
        返回:
            str: 用于绘制预测图表的Python代码
        """
        if self.time_series is None:
            raise ValueError("请先加载数据")
            
        time_series = self.time_series
            
        try:
            # 准备数据
            forecast_dates = self.prophet_forecast['ds']
            forecast_values = self.prophet_forecast['yhat']
            lower_bound = self.prophet_forecast['yhat_lower']
            upper_bound = self.prophet_forecast['yhat_upper']
            
            # 分离历史和预测
            history_mask = forecast_dates <= time_series.index.max()
            future_mask = forecast_dates > time_series.index.max()
            
            # 将数据转换为可序列化的格式
            historical_dates = time_series.index.strftime('%Y-%m-%d').tolist()
            historical_values = time_series.values.tolist()
            
            forecast_dates_str = forecast_dates.dt.strftime('%Y-%m-%d').tolist()
            forecast_values_list = forecast_values.tolist()
            lower_bound_list = lower_bound.tolist()
            upper_bound_list = upper_bound.tolist()
            
            # 生成Python绘图代码
            plot_code = f'''
# 预测图表绘制代码
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 历史数据
historical_dates = {historical_dates}
historical_values = {historical_values}

# 预测数据
forecast_dates = {forecast_dates_str}
forecast_values = {forecast_values_list}
lower_bound = {lower_bound_list}
upper_bound = {upper_bound_list}

# 转换日期格式
historical_dates = [datetime.strptime(date, "%Y-%m-%d") for date in historical_dates]
forecast_dates = [datetime.strptime(date, "%Y-%m-%d") for date in forecast_dates]

# 分离历史和预测
history_mask = [date <= max(historical_dates) for date in forecast_dates]
future_mask = [date > max(historical_dates) for date in forecast_dates]

# 创建历史和预测数据列表
history_dates = [forecast_dates[i] for i in range(len(forecast_dates)) if history_mask[i]]
history_values = [forecast_values[i] for i in range(len(forecast_values)) if history_mask[i]]
future_dates = [forecast_dates[i] for i in range(len(forecast_dates)) if future_mask[i]]
future_values = [forecast_values[i] for i in range(len(forecast_values)) if future_mask[i]]

# 绘制图表
plt.figure(figsize={figsize})

# 绘制历史数据
plt.plot(historical_dates, historical_values, 'b-', label='Historical Sales')

# 绘制历史拟合
plt.plot(history_dates, history_values, 'g--', label='Model Fit')

# 绘制预测
plt.plot(future_dates, future_values, 'r--', label='Forecasted Sales')

# 绘制置信区间
plt.fill_between(forecast_dates, lower_bound, upper_bound, color='gray', alpha=0.2, label='95% Confidence Interval')

# 设置标题和标签
plt.title('{title or "Sales Forecast"}')
plt.xlabel('Date')
plt.ylabel('Sales Volume')
plt.legend()
plt.grid(True)

# 禁用科学计数法，使用常规数字格式
from matplotlib.ticker import ScalarFormatter
ax = plt.gca()
ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.ticklabel_format(style='plain', axis='y')

# 显示图表
plt.tight_layout()
plt.show()
'''
            
            return plot_code
            
        except Exception as e:
            # print(f"生成绘图代码错误: {str(e)}")
            raise
    
    # JSON格式报告生成功能已移除

@mcp.tool()
def sales_forecast(input_str: str) -> str:
    """Generate sales forecast plot code based on input data
    
    Args:
        input_str: Input string in format [[sales_data],start_date,forecast_steps,growth_model]
                   Example: "[[300,320,350,330,310],2023-08-01,12,linear]"
    
    Returns:
        Python code string for plotting the forecast
    """
    try:
        forecast_system = ProphetSalesForecast()
        
        # 去除字符串两端的引号（如果有）
        if input_str.startswith('"') and input_str.endswith('"'):
            input_str = input_str[1:-1]
        elif input_str.startswith('\'') and input_str.endswith('\''):
            input_str = input_str[1:-1]
        
        # 手动解析输入字符串
        # 首先检查字符串格式是否正确
        if not (input_str.startswith('[') and input_str.endswith(']')):
            raise ValueError("输入必须是列表格式，以[开始，以]结束")
        
        # 去除最外层的方括号
        content = input_str[1:-1].strip()
        
        # 查找第一个逗号的位置（在第一个列表之后）
        # 首先找到第一个列表的结束位置
        bracket_count = 0
        first_list_end = -1
        for i, char in enumerate(content):
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and first_list_end == -1:
                    first_list_end = i
                    break
        
        if first_list_end == -1:
            raise ValueError("无法解析销量数据列表")
        
        # 提取销量数据列表字符串
        sales_data_str = content[:first_list_end+1]
        
        # 解析销量数据列表
        sales_data = eval(sales_data_str)
        
        # 分割剩余部分
        remaining = content[first_list_end+1:].strip()
        if remaining.startswith(','):
            remaining = remaining[1:].strip()
        
        # 分割剩余的三个元素
        parts = remaining.split(',')
        if len(parts) != 3:
            raise ValueError(f"格式错误，预期3个额外元素，但找到{len(parts)}个")
        
        # 提取起始日期、预测周期数和增长模型
        start_date = parts[0].strip().strip('"\'')
        forecast_steps = int(parts[1].strip())
        growth_model = parts[2].strip().strip('"\'')
        
        # 验证数据格式
        if not isinstance(sales_data, list):
            raise ValueError("销量数据必须是列表格式")
        if not all(isinstance(x, (int, float)) for x in sales_data):
            raise ValueError("销量列表中所有元素必须是数字")
        
        # 验证日期格式
        try:
            pd.to_datetime(start_date)
        except:
            raise ValueError("日期格式错误，请使用YYYY-MM-DD格式")
            
        # 验证增长模型
        if growth_model not in ['linear', 'flat']:
            growth_model = 'linear'
            
        # 加载数据
        forecast_system.load_data_from_list(sales_data, start_date)
        
        # 自动数据探索
        forecast_system.quick_data_exploration()
        
        # 运行Prophet模型
        forecast_system.run_prophet_model(forecast_steps, growth=growth_model)
        
        # 获取预测图表代码
        plot_code = forecast_system.plot_forecast()
        
        return plot_code
        
    except Exception as e:
        raise ValueError(f"销量预测错误: {str(e)}")


def main() -> None:
    mcp.run(transport='stdio')

