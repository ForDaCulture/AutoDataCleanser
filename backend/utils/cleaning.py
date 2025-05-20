import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Tuple, Dict, Any, List, Optional
from schemas.clean import CleanRequest
import logging

logger = logging.getLogger(__name__)

class CleaningError(Exception):
    """Custom exception for data cleaning errors"""
    pass

def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate the input DataFrame.
    Raises CleaningError if validation fails.
    """
    if df is None:
        raise CleaningError("DataFrame is None")
    
    if df.empty:
        raise CleaningError("DataFrame is empty")
    
    if not isinstance(df, pd.DataFrame):
        raise CleaningError("Input must be a pandas DataFrame")

def profile_data(df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate a detailed profile of the DataFrame.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary containing column statistics
    """
    try:
        validate_dataframe(df)
        
        stats = []
        for col in df.columns:
            col_data = df[col]
            col_stats = {
                "column": col,
                "type": str(col_data.dtype),
                "missing_pct": float(col_data.isnull().mean()) * 100,
                "unique_count": int(col_data.nunique())
            }
            
            # Add type-specific statistics
            if pd.api.types.is_numeric_dtype(col_data):
                col_stats.update({
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean()),
                    "std": float(col_data.std())
                })
            elif pd.api.types.is_string_dtype(col_data):
                col_stats.update({
                    "min_length": int(col_data.str.len().min()),
                    "max_length": int(col_data.str.len().max()),
                    "avg_length": float(col_data.str.len().mean())
                })
            
            stats.append(col_stats)
            
        return {"profile": stats}
    except Exception as e:
        logger.error(f"Error profiling data: {str(e)}")
        raise CleaningError(f"Failed to profile data: {str(e)}")

def auto_clean(
    df: pd.DataFrame,
    req: CleanRequest
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
    """
    Automatically clean the DataFrame based on the provided request.
    
    Args:
        df: Input DataFrame
        req: Cleaning request parameters
    
    Returns:
        Tuple of (cleaned DataFrame, summary statistics, audit log)
    """
    try:
        validate_dataframe(df)
        
        before = df.copy()
        audit = {"steps": []}
        summary = {
            "imputation": {},
            "outliers_removed": 0,
            "duplicates_removed": 0,
            "rows_before": len(df),
            "rows_after": len(df)
        }
        
        # Imputation
        if req.impute:
            for col in df.select_dtypes(include=["number", "object"]):
                if df[col].isnull().any():
                    try:
                        if req.impute == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                            df[col].fillna(df[col].mean(), inplace=True)
                            audit["steps"].append({"action": "impute_mean", "column": col})
                            summary["imputation"][col] = "mean"
                        elif req.impute == "median" and pd.api.types.is_numeric_dtype(df[col]):
                            df[col].fillna(df[col].median(), inplace=True)
                            audit["steps"].append({"action": "impute_median", "column": col})
                            summary["imputation"][col] = "median"
                        else:
                            mode_value = df[col].mode().iloc[0]
                            df[col].fillna(mode_value, inplace=True)
                            audit["steps"].append({"action": "impute_mode", "column": col})
                            summary["imputation"][col] = "mode"
                    except Exception as e:
                        logger.warning(f"Failed to impute column {col}: {str(e)}")
                        continue
        
        # Outlier removal
        if req.outlier:
            try:
                num_cols = df.select_dtypes(include=["number"]).columns
                if len(num_cols) > 0:
                    # Handle missing values before outlier detection
                    X = df[num_cols].fillna(df[num_cols].mean())
                    iso = IsolationForest(contamination=0.05, random_state=42)
                    preds = iso.fit_predict(X)
                    outlier_rows = df.index[preds == -1].tolist()
                    df = df[preds != -1]
                    audit["steps"].append({
                        "action": "remove_outliers",
                        "rows": outlier_rows,
                        "columns": list(num_cols)
                    })
                    summary["outliers_removed"] = len(outlier_rows)
            except Exception as e:
                logger.warning(f"Failed to remove outliers: {str(e)}")
        
        # Duplicates
        if req.dedupe:
            try:
                dup_rows = df[df.duplicated()].index.tolist()
                df = df.drop_duplicates()
                audit["steps"].append({
                    "action": "remove_duplicates",
                    "rows": dup_rows
                })
                summary["duplicates_removed"] = len(dup_rows)
            except Exception as e:
                logger.warning(f"Failed to remove duplicates: {str(e)}")
        
        summary["rows_after"] = len(df)
        return df, summary, audit
        
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        raise CleaningError(f"Failed to clean data: {str(e)}")

def suggest_features(df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    """
    Suggest feature engineering operations for the DataFrame.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary containing feature suggestions
    """
    try:
        validate_dataframe(df)
        
        suggestions = []
        
        # Date parsing
        for col in df.select_dtypes(include=["datetime", "object"]):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notnull().any():
                    suggestions.append({
                        "column": col,
                        "type": "date_parting",
                        "parts": ["year", "month", "day", "weekday"],
                        "reason": "Column contains date-like values."
                    })
            except Exception:
                continue
        
        # Ratios
        num_cols = df.select_dtypes(include=["number"]).columns
        if len(num_cols) >= 2:
            for i, col1 in enumerate(num_cols):
                for col2 in num_cols[i+1:]:
                    # Check if ratio would be meaningful
                    if df[col2].abs().min() > 0:  # Avoid division by zero
                        suggestions.append({
                            "type": "ratio",
                            "columns": [col1, col2],
                            "reason": f"Ratio of {col1}/{col2} may be meaningful."
                        })
        
        # One-hot encoding
        for col in df.select_dtypes(include=["object", "category"]):
            if df[col].nunique() < 20:
                suggestions.append({
                    "column": col,
                    "type": "one_hot",
                    "reason": "Low cardinality categorical column."
                })
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error suggesting features: {str(e)}")
        raise CleaningError(f"Failed to suggest features: {str(e)}") 