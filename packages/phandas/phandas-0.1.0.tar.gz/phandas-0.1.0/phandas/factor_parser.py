import ast
import operator
import pandas as pd
import numpy as np
from typing import Any, Dict, Callable
import warnings

class FactorExpressionParser:
    """
    因子表達式解析器
    
    支持解析和計算因子表達式，如：-1 * ts_rank(rank(low), 9)
    
    支持的操作：
    - 基本數學運算：+, -, *, /, **
    - 函數調用：rank, ts_rank, ts_sum, ts_mean, delta, delay 等
    - 數據列引用：open, high, low, close, volume
    - 數值常量：整數和浮點數
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化解析器
        
        Args:
            data: MultiIndex DataFrame，包含 OHLCV 數據
        """
        self.data = data
        self.functions = self._get_available_functions()
        self.variables = self._get_available_variables()
        
        # 支持的運算符
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
    
    def _get_available_functions(self) -> Dict[str, Callable]:
        """獲取可用的函數"""
        from . import factors
        
        return {
            # 時間序列函數
            'ts_sum': factors.ts_sum,
            'ts_mean': factors.ts_mean,
            'ts_std': factors.ts_std,
            'ts_min': factors.ts_min,
            'ts_max': factors.ts_max,
            'ts_rank': factors.ts_rank,
            'ts_argmax': factors.ts_argmax,
            'ts_argmin': factors.ts_argmin,
            
            # 其他函數
            'rank': self._rank_func,  # 使用修正的 rank 函數
            'delta': factors.delta,
            'delay': factors.delay,
            'scale': factors.scale,
            'returns': factors.returns,
            'correlation': factors.correlation,
            'decay_linear': factors.decay_linear,
            
            # 數學函數
            'abs': np.abs,
            'log': np.log,
            'sqrt': np.sqrt,
            'sign': np.sign,
            'max': np.maximum,
            'min': np.minimum,
        }
    
    def _get_available_variables(self) -> Dict[str, pd.Series]:
        """獲取可用的變量（數據列）"""
        variables = {}
        for col in self.data.columns:
            variables[col] = self.data[col]
        return variables
    
    def _rank_func(self, df: pd.Series) -> pd.Series:
        """截面排名函數 - 最高值=1，最低值=0"""
        def simple_rank(group):
            ranks = group.rank(method='min', ascending=True)
            return (ranks - 1) / (len(group) - 1) if len(group) > 1 else pd.Series([1.0], index=group.index)
        
        if isinstance(df.index, pd.MultiIndex):
            return df.groupby('timestamp').apply(simple_rank).droplevel(0)
        else:
            return simple_rank(df)
    
    def parse_expression(self, expression: str) -> pd.Series:
        """
        解析並計算因子表達式
        
        Args:
            expression: 因子表達式字符串
            
        Returns:
            pd.Series: 計算結果，錯誤時填入 NaN
        """
        try:
            # 解析表達式為 AST
            tree = ast.parse(expression, mode='eval')
            
            # 計算表達式
            result = self._eval_node(tree.body)
            
            # 確保返回 Series
            if not isinstance(result, pd.Series):
                if isinstance(result, (int, float)):
                    # 如果是標量，創建與數據同樣索引的 Series
                    result = pd.Series(result, index=self.data.index)
                else:
                    result = pd.Series(result, index=self.data.index)
            
            # 清理無效值：將 inf/-inf 轉換為 NaN
            result = result.replace([np.inf, -np.inf], np.nan)
            
            return result
            
        except Exception as e:
            # 任何錯誤都返回全 NaN 的 Series
            warnings.warn(f"因子表達式 '{expression}' 計算失敗: {str(e)}，返回 NaN")
            return pd.Series(np.nan, index=self.data.index)
    
    def _eval_node(self, node: ast.AST) -> Any:
        """遞歸計算 AST 節點"""
        
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Name):
            # 變量引用
            if node.id in self.variables:
                return self.variables[node.id]
            else:
                # 未定義變量時返回 NaN Series 而不是拋出異常
                warnings.warn(f"未定義的變量: {node.id}，將填入 NaN")
                return pd.Series(np.nan, index=self.data.index)
        
        elif isinstance(node, ast.BinOp):
            # 二元運算
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.operators[type(node.op)]
            return op(left, right)
        
        elif isinstance(node, ast.UnaryOp):
            # 一元運算
            operand = self._eval_node(node.operand)
            op = self.operators[type(node.op)]
            return op(operand)
        
        elif isinstance(node, ast.Call):
            # 函數調用
            func_name = node.func.id
            if func_name not in self.functions:
                # 未定義函數時返回 NaN Series 而不是拋出異常
                warnings.warn(f"未定義的函數: {func_name}，將填入 NaN")
                return pd.Series(np.nan, index=self.data.index)
            
            try:
                # 計算參數
                args = [self._eval_node(arg) for arg in node.args]
                kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
                
                # 調用函數
                func = self.functions[func_name]
                result = func(*args, **kwargs)
                
                # 如果結果包含無效值，清理它們
                if isinstance(result, pd.Series):
                    result = result.replace([np.inf, -np.inf], np.nan)
                
                return result
                
            except Exception as e:
                # 函數執行錯誤時返回 NaN
                warnings.warn(f"函數 {func_name} 執行失敗: {str(e)}，將填入 NaN")
                return pd.Series(np.nan, index=self.data.index)
        
        else:
            raise TypeError(f"不支持的節點類型: {type(node)}")

def calculate_factor_from_expression(data: pd.DataFrame, expression: str, factor_name: str = None) -> pd.Series:
    """
    從表達式計算因子值
    
    Args:
        data: MultiIndex DataFrame，包含 OHLCV 數據
        expression: 因子表達式字符串
        factor_name: 因子名稱，如果未提供則使用表達式
        
    Returns:
        pd.Series: 因子值
    """
    parser = FactorExpressionParser(data)
    factor = parser.parse_expression(expression)
    
    if factor_name:
        factor.name = factor_name
    else:
        # 清理表達式作為名稱
        clean_expr = expression.replace(' ', '').replace('*', 'x').replace('/', 'd')
        factor.name = f'factor_{clean_expr}'
    
    return factor

def add_factor_to_data(data, factor_expression: str, factor_name: str = None, output_csv_path: str = None):
    """
    Generate factor values and optionally save to CSV
    
    Args:
        data: Input data, can be:
              - pd.DataFrame with MultiIndex (timestamp, symbol) 
              - str: CSV file path to load data from
        factor_expression: Factor expression, e.g., "-1 * ts_rank(rank(low), 9)"
        factor_name: Factor name, defaults to expression-based name
        output_csv_path: Output CSV path. If provided, saves to file and returns path.
                        If None, returns DataFrame with factor column.
        
    Returns:
        - pd.DataFrame: If output_csv_path is None
        - str: Output file path if output_csv_path is provided
        
    Examples:
        >>> # Memory version (returns DataFrame)
        >>> data_with_factor = phn.add_factor_to_data(data, 'ts_rank(rank(low), 9)', 'alpha004')
        
        >>> # File version (saves CSV and returns path)
        >>> output_path = phn.add_factor_to_data('data/crypto_data.csv', 'ts_rank(rank(low), 9)', 'alpha004', 'data/output.csv')
    """
    import os
    
    # Handle input data
    if isinstance(data, str):
        # Load from CSV file
        df = pd.read_csv(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index(['timestamp', 'symbol'])
    else:
        # Use provided DataFrame
        df = data
    
    # Calculate factor
    factor = calculate_factor_from_expression(df, factor_expression, factor_name)
    
    # Add factor to data
    result_data = df.copy()
    result_data[factor.name] = factor
    
    print(f"Factor '{factor.name}' generated successfully")
    print(f"Valid factor values: {factor.notna().sum()}/{len(factor)}")
    
    # Return based on output_csv_path
    if output_csv_path is None:
        # Memory version
        return result_data
    else:
        # File version
        if output_csv_path == 'auto':
            # Auto-generate path
            if isinstance(data, str):
                input_dir = os.path.dirname(data)
            else:
                input_dir = './data'
            output_filename = f'{factor.name}_factors.csv'
            output_csv_path = os.path.join(input_dir, output_filename)
        
        # Save to CSV
        output_data = result_data.reset_index()
        output_data.to_csv(output_csv_path, index=False)
        
        print(f"Saved to: {output_csv_path}")
        return output_csv_path

# Backward compatibility alias
def generate_factor_csv(input_csv_path: str, factor_expression: str, factor_name: str = None, output_csv_path: str = None) -> str:
    """
    Backward compatibility function for generate_factor_csv
    """
    if output_csv_path is None:
        output_csv_path = 'auto'
    return add_factor_to_data(input_csv_path, factor_expression, factor_name, output_csv_path)


