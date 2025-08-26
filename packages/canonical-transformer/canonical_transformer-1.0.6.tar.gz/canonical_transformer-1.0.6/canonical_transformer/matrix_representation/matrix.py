import numpy as np
import pandas as pd
from typing import Union, Tuple
from functools import reduce

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
   
   def row_vector(self, i: int, option_normalized: bool = False) -> pd.DataFrame:
       """Extract i-th row vector as DataFrame with basis information preserved"""
       if option_normalized:
           return self.df.iloc[[i], :].div(self.df.iloc[i, :].sum())
       return self.df.iloc[[i], :]
       
   def column_vector(self, j: int, option_normalized: bool = False) -> pd.DataFrame:
       """Extract j-th column vector as DataFrame with basis information preserved"""
       if option_normalized:
           return self.df.iloc[:, [j]].div(self.df.iloc[:, j].sum())
       return self.df.iloc[:, [j]]
   
   def component_ij(self, i: int, j: int) -> Union[int, float]:
       """Get (i,j) component value"""
       return self.df.iloc[i, j]
   
   def row_vector_by_name(self, index_name: str, option_normalized: bool = False) -> pd.DataFrame:
       """Extract row vector by index name with basis information preserved"""
       if option_normalized:
           return self.df.loc[[index_name], :].div(self.df.loc[index_name, :].sum())
       return self.df.loc[[index_name], :]

   def column_vector_by_name(self, column_name: str, option_normalized: bool = False) -> pd.DataFrame:
       """Extract column vector by column name with basis information preserved"""
       if option_normalized:
           return self.df.loc[:, [column_name]].div(self.df.loc[:, column_name].sum())
       return self.df.loc[:, [column_name]]

   def component_by_name(self, index_name: str, column_name: str) -> Union[int, float]:
       """Get component value by index and column names"""
       return self.df.loc[index_name, column_name]

   def _validate_vector_dimensions(self, v1: pd.DataFrame, v2: pd.DataFrame) -> None:
       """Pure function: validate that two vectors have compatible dimensions"""
       if not (isinstance(v1, pd.DataFrame) and isinstance(v2, pd.DataFrame)):
           raise TypeError("Both inputs must be DataFrames")
       
       if v1.shape != v2.shape:
           raise ValueError(f"Vector dimensions don't match: {v1.shape} vs {v2.shape}")

   def inner_product_by_index(self, j1: int, j2: int, option_normalized: bool = False) -> float:
       """Compute inner product of two column vectors by index"""
       return self._compute_inner_product(
           self.column_vector(j1, option_normalized), 
           self.column_vector(j2, option_normalized)
       )

   def inner_product_by_name(self, col1: str, col2: str, option_normalized: bool = False) -> float:
       """Compute inner product of two column vectors by name"""
       return self._compute_inner_product(
           self.column_vector_by_name(col1, option_normalized), 
           self.column_vector_by_name(col2, option_normalized)
       )
   
   def inner_product(self, vector1: pd.DataFrame, vector2: pd.DataFrame) -> float:
       """Compute inner product of two vector DataFrames"""
       return self._compute_inner_product(vector1, vector2)

   def _compute_inner_product(self, v1: pd.DataFrame, v2: pd.DataFrame) -> float:
       """Pure function: compute inner product of two vectors"""
       self._validate_vector_dimensions(v1, v2)
       values1 = self._extract_vector_values(v1)
       values2 = self._extract_vector_values(v2)
       return np.dot(values1, values2)

   def outer_product_by_index(self, j1: int, j2: int) -> np.ndarray:
       """Compute outer product of two column vectors by index"""
       return self._compute_outer_product(
           self.column_vector(j1), 
           self.column_vector(j2)
       )

   def _compute_outer_product(self, v1: pd.DataFrame, v2: pd.DataFrame) -> np.ndarray:
       """Pure function: compute outer product of two vectors"""
       self._validate_vector_dimensions(v1, v2)
       values1 = self._extract_vector_values(v1)
       values2 = self._extract_vector_values(v2)
       return np.outer(values1, values2)
       
   def trace(self) -> float:
       """Compute trace (only for square matrices)"""
       if self.df.shape[0] != self.df.shape[1]:
           raise ValueError(f"Trace is only defined for square matrices. Current shape: {self.df.shape}")
       return np.trace(self.df.values)
   
   def to_numpy(self) -> np.ndarray:
       """Convert entire matrix to numpy array"""
       return self.df.values

   # Functional programming utilities
   @staticmethod
   def compose_inner_products(*vectors: pd.DataFrame) -> float:
       """Compose multiple inner products: v1·v2·v3·... (left-associative)"""
       if len(vectors) < 2:
           raise ValueError("At least two vectors required for inner product composition")
       
       def pairwise_inner_product(acc: float, vector_pair: Tuple[pd.DataFrame, pd.DataFrame]) -> float:
           return Matrix._compute_inner_product_static(vector_pair[0], vector_pair[1])
       
       pairs = [(vectors[i], vectors[i+1]) for i in range(len(vectors)-1)]
       return reduce(lambda acc, pair: Matrix._compute_inner_product_static(pair[0], pair[1]), pairs)

   @staticmethod
   def _compute_inner_product_static(v1: pd.DataFrame, v2: pd.DataFrame) -> float:
       """Static pure function for inner product computation"""
       if not (isinstance(v1, pd.DataFrame) and isinstance(v2, pd.DataFrame)):
           raise TypeError("Both inputs must be DataFrames")
       
       if v1.shape != v2.shape:
           raise ValueError(f"Vector dimensions don't match: {v1.shape} vs {v2.shape}")
       
       # Extract values
       if v1.shape[1] == 1:  # Column vectors
           values1 = v1.iloc[:, 0].values
           values2 = v2.iloc[:, 0].values
       elif v1.shape[0] == 1:  # Row vectors
           values1 = v1.iloc[0, :].values
           values2 = v2.iloc[0, :].values
       else:
           raise ValueError("Input must be vectors (single row or column)")
           
       return np.dot(values1, values2)