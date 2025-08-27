"""
Input validation utilities for CausalLLM core functionality
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Any, Union
import warnings

def validate_dataframe(data: Any, min_rows: int = 10, required_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Validate input DataFrame for causal analysis
    
    Args:
        data: Input data to validate
        min_rows: Minimum number of rows required
        required_cols: List of required column names
        
    Returns:
        Validated DataFrame
        
    Raises:
        ValueError: If validation fails
    """
    # Convert to DataFrame if needed
    if not isinstance(data, pd.DataFrame):
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)
        else:
            raise ValueError("Data must be a pandas DataFrame or numpy array")
    
    # Check minimum rows
    if len(data) < min_rows:
        raise ValueError(f"Data must have at least {min_rows} rows, got {len(data)}")
    
    # Check for required columns
    if required_cols:
        missing_cols = set(required_cols) - set(data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check for empty DataFrame
    if data.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Warn about missing values
    if data.isnull().any().any():
        warnings.warn("DataFrame contains missing values. Consider imputation or removal.")
    
    # Warn about constant columns
    constant_cols = [col for col in data.columns if data[col].nunique() <= 1]
    if constant_cols:
        warnings.warn(f"Found constant columns (no variation): {constant_cols}")
    
    return data

def validate_variables(variables: List[str], data: pd.DataFrame) -> List[str]:
    """
    Validate variable list against DataFrame columns
    
    Args:
        variables: List of variable names
        data: DataFrame to check against
        
    Returns:
        Validated variable list
        
    Raises:
        ValueError: If variables not found in data
    """
    if not isinstance(variables, (list, tuple)):
        raise ValueError("Variables must be a list or tuple of strings")
    
    missing_vars = set(variables) - set(data.columns)
    if missing_vars:
        raise ValueError(f"Variables not found in data: {missing_vars}")
    
    return list(variables)

def validate_treatment_outcome(treatment: str, outcome: str, data: pd.DataFrame) -> tuple:
    """
    Validate treatment and outcome variables
    
    Args:
        treatment: Treatment variable name
        outcome: Outcome variable name  
        data: DataFrame containing variables
        
    Returns:
        (treatment, outcome) tuple
        
    Raises:
        ValueError: If variables invalid
    """
    if not isinstance(treatment, str):
        raise ValueError("Treatment must be a string variable name")
    
    if not isinstance(outcome, str):
        raise ValueError("Outcome must be a string variable name")
    
    if treatment not in data.columns:
        raise ValueError(f"Treatment variable '{treatment}' not found in data")
    
    if outcome not in data.columns:
        raise ValueError(f"Outcome variable '{outcome}' not found in data")
    
    if treatment == outcome:
        raise ValueError("Treatment and outcome cannot be the same variable")
    
    # Check treatment variable characteristics
    treatment_unique = data[treatment].nunique()
    if treatment_unique == 1:
        raise ValueError(f"Treatment variable '{treatment}' has no variation")
    
    # Warn if treatment has many unique values (might not be appropriate)
    if treatment_unique > len(data) * 0.5:
        warnings.warn(f"Treatment variable '{treatment}' has many unique values ({treatment_unique}). "
                     "Consider if this is truly a treatment variable.")
    
    return treatment, outcome

def validate_graph_structure(graph_data: Any) -> dict:
    """
    Validate causal graph structure data
    
    Args:
        graph_data: Graph data in various formats
        
    Returns:
        Validated graph dictionary
        
    Raises:
        ValueError: If graph structure invalid
    """
    if isinstance(graph_data, dict):
        # Validate dictionary format
        if 'nodes' not in graph_data or 'edges' not in graph_data:
            raise ValueError("Graph dictionary must contain 'nodes' and 'edges' keys")
        
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        if not isinstance(nodes, (list, tuple)):
            raise ValueError("Nodes must be a list or tuple")
        
        if not isinstance(edges, (list, tuple)):
            raise ValueError("Edges must be a list or tuple")
        
        # Validate edges reference valid nodes
        node_set = set(nodes)
        for edge in edges:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise ValueError("Each edge must be a tuple/list of 2 nodes")
            
            if edge[0] not in node_set or edge[1] not in node_set:
                raise ValueError(f"Edge {edge} references unknown nodes")
        
        return graph_data
    
    elif isinstance(graph_data, str):
        # Validate string format (e.g., DOT notation)
        # Basic validation - more complex parsing would be in dag_parser
        if not graph_data.strip():
            raise ValueError("Graph string cannot be empty")
        
        return {'format': 'string', 'data': graph_data}
    
    else:
        raise ValueError("Graph data must be a dictionary or string")

def validate_intervention(intervention: dict, data: pd.DataFrame) -> dict:
    """
    Validate intervention specification
    
    Args:
        intervention: Intervention dictionary
        data: DataFrame with variables
        
    Returns:
        Validated intervention dictionary
        
    Raises:
        ValueError: If intervention invalid
    """
    if not isinstance(intervention, dict):
        raise ValueError("Intervention must be a dictionary")
    
    if not intervention:
        raise ValueError("Intervention cannot be empty")
    
    # Validate intervention variables exist
    missing_vars = set(intervention.keys()) - set(data.columns)
    if missing_vars:
        raise ValueError(f"Intervention variables not found in data: {missing_vars}")
    
    # Validate intervention values are reasonable
    for var, value in intervention.items():
        if isinstance(value, (int, float)):
            # Check if value is within reasonable range
            var_data = data[var]
            if np.isfinite(var_data).any():  # Skip if all non-finite
                var_min, var_max = var_data.min(), var_data.max()
                var_range = var_max - var_min
                
                if var_range > 0 and (value < var_min - 2*var_range or value > var_max + 2*var_range):
                    warnings.warn(f"Intervention value for '{var}' ({value}) is far outside observed range "
                                f"[{var_min:.2f}, {var_max:.2f}]")
    
    return intervention

def validate_method(method: str, valid_methods: List[str]) -> str:
    """
    Validate method parameter
    
    Args:
        method: Method name to validate
        valid_methods: List of valid method names
        
    Returns:
        Validated method name
        
    Raises:
        ValueError: If method invalid
    """
    if not isinstance(method, str):
        raise ValueError("Method must be a string")
    
    if method not in valid_methods:
        raise ValueError(f"Method '{method}' not supported. Valid methods: {valid_methods}")
    
    return method

def validate_numeric_parameter(value: Any, name: str, min_val: float = None, max_val: float = None) -> float:
    """
    Validate numeric parameter
    
    Args:
        value: Value to validate
        name: Parameter name for error messages
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated numeric value
        
    Raises:
        ValueError: If value invalid
    """
    try:
        numeric_val = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Parameter '{name}' must be numeric, got {type(value).__name__}")
    
    if not np.isfinite(numeric_val):
        raise ValueError(f"Parameter '{name}' must be finite, got {numeric_val}")
    
    if min_val is not None and numeric_val < min_val:
        raise ValueError(f"Parameter '{name}' must be >= {min_val}, got {numeric_val}")
    
    if max_val is not None and numeric_val > max_val:
        raise ValueError(f"Parameter '{name}' must be <= {max_val}, got {numeric_val}")
    
    return numeric_val

def check_data_quality(data: pd.DataFrame) -> dict:
    """
    Perform comprehensive data quality check
    
    Args:
        data: DataFrame to check
        
    Returns:
        Dictionary with quality metrics and issues
    """
    issues = []
    metrics = {}
    
    # Basic metrics
    metrics['n_rows'] = len(data)
    metrics['n_cols'] = len(data.columns)
    metrics['missing_pct'] = data.isnull().sum().sum() / (len(data) * len(data.columns)) * 100
    
    # Check for issues
    
    # 1. Missing values
    missing_cols = data.columns[data.isnull().any()].tolist()
    if missing_cols:
        issues.append(f"Missing values in columns: {missing_cols}")
    
    # 2. Constant columns
    constant_cols = [col for col in data.columns if data[col].nunique() <= 1]
    if constant_cols:
        issues.append(f"Constant columns: {constant_cols}")
    
    # 3. Near-constant columns (>95% same value)
    near_constant = []
    for col in data.columns:
        if data[col].dtype in ['object', 'category']:
            mode_freq = data[col].value_counts().iloc[0] / len(data)
        else:
            mode_freq = (data[col] == data[col].mode()[0]).sum() / len(data) if not data[col].empty else 0
        
        if mode_freq > 0.95:
            near_constant.append(col)
    
    if near_constant:
        issues.append(f"Near-constant columns (>95% same value): {near_constant}")
    
    # 4. Highly correlated pairs
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        corr_matrix = data[numeric_cols].corr().abs()
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if corr_matrix.iloc[i, j] > 0.95:
                    high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
        
        if high_corr_pairs:
            issues.append(f"Highly correlated pairs (r>0.95): {high_corr_pairs}")
    
    # 5. Outliers (simple IQR method)
    outlier_cols = []
    for col in numeric_cols:
        if data[col].nunique() > 10:  # Skip categorical-like numeric columns
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((data[col] < Q1 - 1.5*IQR) | (data[col] > Q3 + 1.5*IQR)).sum()
            
            if outliers > len(data) * 0.05:  # >5% outliers
                outlier_cols.append(f"{col} ({outliers} outliers)")
    
    if outlier_cols:
        issues.append(f"Columns with many outliers: {outlier_cols}")
    
    return {
        'metrics': metrics,
        'issues': issues,
        'quality_score': max(0, 100 - len(issues) * 10)  # Simple scoring
    }