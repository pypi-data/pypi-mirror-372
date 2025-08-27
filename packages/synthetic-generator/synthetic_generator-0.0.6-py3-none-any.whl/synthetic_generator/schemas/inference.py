"""
Schema inference for SynGen.

This module provides functionality to automatically infer
data schemas from existing data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from .base import DataSchema, ColumnSchema, DataType, DistributionType


class SchemaInferrer:
    """Class for inferring data schemas from existing data."""
    
    @staticmethod
    def infer(
        data: pd.DataFrame, 
        sample_size: Optional[int] = None
    ) -> DataSchema:
        """
        Infer schema from existing data.
        
        Args:
            data: Input DataFrame
            sample_size: Number of samples to use for inference
            
        Returns:
            Inferred data schema
        """
        # Sample data if specified
        if sample_size and sample_size < len(data):
            data = data.sample(n=sample_size, random_state=42)
        
        columns = []
        
        for col_name in data.columns:
            col_data = data[col_name]
            column_schema = SchemaInferrer._infer_column_schema(col_name, col_data)
            columns.append(column_schema)
        
        return DataSchema(columns=columns)
    
    @staticmethod
    def _infer_column_schema(column_name: str, column_data: pd.Series) -> ColumnSchema:
        """Infer schema for a single column."""
        
        # Determine data type
        data_type = SchemaInferrer._infer_data_type(column_data)
        
        # Determine distribution
        distribution, parameters = SchemaInferrer._infer_distribution(column_data, data_type)
        
        # Determine constraints
        constraints = SchemaInferrer._infer_constraints(column_data, data_type)
        
        return ColumnSchema(
            name=column_name,
            data_type=data_type,
            distribution=distribution,
            parameters=parameters,
            **constraints
        )
    
    @staticmethod
    def _infer_data_type(column_data: pd.Series) -> DataType:
        """Infer data type from column data."""
        
        # Handle missing values
        non_null_data = column_data.dropna()
        
        if len(non_null_data) == 0:
            return DataType.STRING
        
        # Check for boolean first (before numeric)
        if pd.api.types.is_bool_dtype(column_data):
            return DataType.BOOLEAN
        
        # Check for numeric types
        if pd.api.types.is_numeric_dtype(column_data):
            if pd.api.types.is_integer_dtype(column_data):
                return DataType.INTEGER
            else:
                return DataType.FLOAT
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(column_data):
            return DataType.DATETIME
        
        # Check for date (simplified check)
        try:
            # Try to convert to datetime to see if it's a date
            pd.to_datetime(column_data.iloc[0])
            return DataType.DATE
        except:
            pass
        
        # Check for specific text patterns
        sample_values = non_null_data.head(100).astype(str)
        
        # Check for email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if sample_values.str.match(email_pattern).mean() > 0.8:
            return DataType.EMAIL
        
        # Check for phone pattern
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        if sample_values.str.replace(r'[^\d+]', '', regex=True).str.match(phone_pattern).mean() > 0.8:
            return DataType.PHONE
        
        # Check for address pattern (contains street, city, state, zip)
        address_indicators = ['street', 'avenue', 'road', 'drive', 'lane', 'court']
        if any(indicator in ' '.join(sample_values).lower() for indicator in address_indicators):
            return DataType.ADDRESS
        
        # Check for name pattern (first last format)
        name_pattern = r'^[A-Z][a-z]+ [A-Z][a-z]+$'
        if sample_values.str.match(name_pattern).mean() > 0.7:
            return DataType.NAME
        
        # Check for categorical
        unique_ratio = len(non_null_data.unique()) / len(non_null_data)
        if unique_ratio < 0.1:  # Less than 10% unique values
            return DataType.CATEGORICAL
        
        return DataType.STRING
    
    @staticmethod
    def _infer_distribution(
        column_data: pd.Series, 
        data_type: DataType
    ) -> tuple[DistributionType, Dict[str, Any]]:
        """Infer distribution and parameters from column data."""
        
        non_null_data = column_data.dropna()
        
        if len(non_null_data) == 0:
            return DistributionType.CONSTANT, {'value': None}
        
        if data_type in [DataType.INTEGER, DataType.FLOAT]:
            return SchemaInferrer._infer_numeric_distribution(non_null_data)
        elif data_type == DataType.CATEGORICAL:
            return SchemaInferrer._infer_categorical_distribution(non_null_data)
        elif data_type == DataType.BOOLEAN:
            return DistributionType.CATEGORICAL, {
                'categories': [True, False],
                'probabilities': [
                    (non_null_data == True).mean(),
                    (non_null_data == False).mean()
                ]
            }
        else:
            # For text data, use categorical distribution
            unique_values = non_null_data.unique()
            if len(unique_values) <= 20:  # Small number of unique values
                return DistributionType.CATEGORICAL, {
                    'categories': unique_values.tolist()
                }
            else:
                return DistributionType.UNIFORM, {}  # Default for text
    
    @staticmethod
    def _infer_numeric_distribution(column_data: pd.Series) -> tuple[DistributionType, Dict[str, Any]]:
        """Infer distribution for numeric data."""
        
        # Check if it's constant
        if column_data.nunique() == 1:
            return DistributionType.CONSTANT, {'value': column_data.iloc[0]}
        
        # Check if it's discrete (integer-like)
        if column_data.dtype in ['int64', 'int32'] or column_data.apply(lambda x: x.is_integer()).all():
            # Check for Poisson-like distribution (count data)
            if column_data.min() >= 0 and column_data.mean() > 0:
                return DistributionType.POISSON, {'lambda': column_data.mean()}
            else:
                return DistributionType.UNIFORM, {
                    'min': column_data.min(),
                    'max': column_data.max()
                }
        
        # For continuous data, try to fit distributions
        try:
            # Check for normal distribution
            from scipy import stats
            _, p_value = stats.normaltest(column_data)
            if p_value > 0.05:  # Not significantly different from normal
                return DistributionType.NORMAL, {
                    'mean': column_data.mean(),
                    'std': column_data.std()
                }
        except ImportError:
            pass
        
        # Check for exponential-like distribution
        if column_data.min() >= 0:
            # Check if it's roughly exponential
            sorted_data = np.sort(column_data)
            if len(sorted_data) > 10:
                # Simple check: if log of sorted data is roughly linear
                log_data = np.log(sorted_data + 1e-10)
                if np.corrcoef(np.arange(len(log_data)), log_data)[0, 1] > 0.8:
                    return DistributionType.EXPONENTIAL, {'lambda': 1 / column_data.mean()}
        
        # Default to uniform
        return DistributionType.UNIFORM, {
            'min': column_data.min(),
            'max': column_data.max()
        }
    
    @staticmethod
    def _infer_categorical_distribution(column_data: pd.Series) -> tuple[DistributionType, Dict[str, Any]]:
        """Infer distribution for categorical data."""
        
        value_counts = column_data.value_counts()
        total = len(column_data)
        
        if len(value_counts) == 1:
            return DistributionType.CONSTANT, {'value': value_counts.index[0]}
        
        # Calculate probabilities
        probabilities = (value_counts / total).tolist()
        categories = value_counts.index.tolist()
        
        return DistributionType.CATEGORICAL, {
            'categories': categories,
            'probabilities': probabilities
        }
    
    @staticmethod
    def _infer_constraints(column_data: pd.Series, data_type: DataType) -> Dict[str, Any]:
        """Infer constraints for a column."""
        constraints = {}
        
        non_null_data = column_data.dropna()
        
        if len(non_null_data) == 0:
            return constraints
        
        # Nullability
        null_count = column_data.isna().sum()
        constraints['nullable'] = bool(null_count > 0)
        if null_count > 0:
            constraints['null_probability'] = float(null_count / len(column_data))
        
        # Uniqueness
        constraints['unique'] = bool(len(non_null_data.unique()) == len(non_null_data))
        
        # Value constraints for numeric data
        if data_type in [DataType.INTEGER, DataType.FLOAT]:
            constraints['min_value'] = non_null_data.min()
            constraints['max_value'] = non_null_data.max()
        
        # Pattern constraints for text data
        if data_type in [DataType.STRING, DataType.EMAIL, DataType.PHONE, DataType.NAME, DataType.ADDRESS]:
            # Check for common patterns
            sample_values = non_null_data.head(100).astype(str)
            
            # Check if all values follow a pattern
            if data_type == DataType.EMAIL:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if sample_values.str.match(email_pattern).all():
                    constraints['pattern'] = email_pattern
            
            elif data_type == DataType.PHONE:
                phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
                if sample_values.str.replace(r'[^\d+]', '', regex=True).str.match(phone_pattern).all():
                    constraints['pattern'] = phone_pattern
        
        return constraints


def infer_schema_from_data(data: pd.DataFrame, sample_size: Optional[int] = None) -> DataSchema:
    """Convenience function to infer schema from data."""
    return SchemaInferrer.infer(data, sample_size) 