# utils.py
import numpy as np
import pandas as pd
from typing import Union

def extract_vector_values(vector: pd.DataFrame) -> np.ndarray:
    """Pure function: extract numeric values from vector DataFrame"""
    if vector.shape[1] == 1:  # Column vector
        return vector.iloc[:, 0].values
    elif vector.shape[0] == 1:  # Row vector
        return vector.iloc[0, :].values
    else:
        raise ValueError("Input must be a vector (single row or column)")

def validate_vector_dimensions(v1: pd.DataFrame, v2: pd.DataFrame) -> None:
    """Pure function: validate that two vectors have compatible dimensions"""
    if not (isinstance(v1, pd.DataFrame) and isinstance(v2, pd.DataFrame)):
        raise TypeError("Both inputs must be DataFrames")
    
    if v1.shape != v2.shape:
        raise ValueError(f"Vector dimensions don't match: {v1.shape} vs {v2.shape}")

def normalize_vector(vector: pd.DataFrame) -> pd.DataFrame:
    """Pure function: normalize vector by its sum"""
    if vector.shape[1] == 1:  # Column vector
        return vector.div(vector.iloc[:, 0].sum())
    else:  # Row vector
        return vector.div(vector.iloc[0, :].sum())

def compute_inner_product(v1: pd.DataFrame, v2: pd.DataFrame) -> float:
    """Pure function: compute inner product of two vectors"""
    validate_vector_dimensions(v1, v2)
    values1 = extract_vector_values(v1)
    values2 = extract_vector_values(v2)
    return np.dot(values1, values2)

def compute_outer_product(v1: pd.DataFrame, v2: pd.DataFrame) -> np.ndarray:
    """Pure function: compute outer product of two vectors"""
    validate_vector_dimensions(v1, v2)
    values1 = extract_vector_values(v1)
    values2 = extract_vector_values(v2)
    return np.outer(values1, values2)

# matrix.py
import numpy as np
import pandas as pd
from typing import Union, Tuple
from functools import reduce
from . import utils  # assuming utils is in same package

class Matrix:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._basis = None
        
    @property
    def basis(self) -> np.ndarray:
        """Column space basis vectors"""
        if self._basis is None:
            self._basis = np.array(self.df.index)
        return self._basis
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Matrix dimensions"""
        return self.df.shape
    
    def row_vector(self, i: Union[int, str], normalized: bool = False) -> pd.DataFrame:
        """Extract row vector by index (int) or name (str)"""
        if isinstance(i, str):
            vector = self.df.loc[[i], :]
        else:
            vector = self.df.iloc[[i], :]
        
        return utils.normalize_vector(vector) if normalized else vector
       
    def column_vector(self, j: Union[int, str], normalized: bool = False) -> pd.DataFrame:
        """Extract column vector by index (int) or name (str)"""
        if isinstance(j, str):
            vector = self.df.loc[:, [j]]
        else:
            vector = self.df.iloc[:, [j]]
            
        return utils.normalize_vector(vector) if normalized else vector
   
    def component(self, i: Union[int, str], j: Union[int, str]) -> Union[int, float]:
        """Get component value by index or name"""
        if isinstance(i, str) or isinstance(j, str):
            return self.df.loc[i, j]
        else:
            return self.df.iloc[i, j]

    def inner_product(self, 
                     v1: Union[pd.DataFrame, int, str], 
                     v2: Union[pd.DataFrame, int, str], 
                     normalized: bool = False,
                     vector_type: str = 'column') -> float:
        """
        Compute inner product of two vectors
        Args:
            v1, v2: Either DataFrames or indices/names for extraction
            normalized: Whether to normalize vectors before computation
            vector_type: 'column' or 'row' when using indices/names
        """
        # Convert indices/names to DataFrames if needed
        if not isinstance(v1, pd.DataFrame):
            v1 = self.column_vector(v1, normalized) if vector_type == 'column' else self.row_vector(v1, normalized)
        if not isinstance(v2, pd.DataFrame):
            v2 = self.column_vector(v2, normalized) if vector_type == 'column' else self.row_vector(v2, normalized)
            
        return utils.compute_inner_product(v1, v2)

    def outer_product(self, 
                     v1: Union[pd.DataFrame, int, str], 
                     v2: Union[pd.DataFrame, int, str],
                     vector_type: str = 'column') -> np.ndarray:
        """
        Compute outer product of two vectors
        Args:
            v1, v2: Either DataFrames or indices/names for extraction
            vector_type: 'column' or 'row' when using indices/names
        """
        # Convert indices/names to DataFrames if needed
        if not isinstance(v1, pd.DataFrame):
            v1 = self.column_vector(v1) if vector_type == 'column' else self.row_vector(v1)
        if not isinstance(v2, pd.DataFrame):
            v2 = self.column_vector(v2) if vector_type == 'column' else self.row_vector(v2)
            
        return utils.compute_outer_product(v1, v2)
       
    def trace(self) -> float:
        """Compute trace (only for square matrices)"""
        if self.df.shape[0] != self.df.shape[1]:
            raise ValueError(f"Trace is only defined for square matrices. Current shape: {self.df.shape}")
        return np.trace(self.df.values)
   
    def to_numpy(self) -> np.ndarray:
        """Convert entire matrix to numpy array"""
        return self.df.values

    @staticmethod
    def compose_inner_products(*vectors: pd.DataFrame) -> float:
        """Compose multiple inner products: v1·v2, then result·v3, etc."""
        if len(vectors) < 2:
            raise ValueError("At least two vectors required for inner product composition")
       
        return reduce(utils.compute_inner_product, vectors)

# Example usage:
# Now you can use utils functions independently:
# from utils import compute_inner_product, extract_vector_values
# 
# v1 = pd.DataFrame({'a': [1, 2, 3]})
# v2 = pd.DataFrame({'b': [4, 5, 6]})
# result = compute_inner_product(v1, v2)  # Works without Matrix class
# 
# values = extract_vector_values(v1)  # [1, 2, 3]