"""
Utility functions for the calibre package.
"""
import numpy as np
from sklearn.utils import check_array
from typing import Tuple, Union, Optional, List, Any
import warnings

def check_arrays(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Check and validate input arrays.
    
    Parameters
    ----------
    X : array-like of shape (n_samples,)
        Input features.
    y : array-like of shape (n_samples,)
        Target values.
        
    Returns
    -------
    X : ndarray of shape (n_samples,)
        Validated input features as a 1D numpy array.
    y : ndarray of shape (n_samples,)
        Validated target values as a 1D numpy array.
        
    Raises
    ------
    ValueError
        If X and y have different lengths or are empty.
        
    Examples
    --------
    >>> import numpy as np
    >>> X = [0.1, 0.3, 0.5, 0.7, 0.9]
    >>> y = [0, 0, 1, 1, 1]
    >>> X_valid, y_valid = check_arrays(X, y)
    """
    # Convert inputs to numpy arrays and validate dimensions.
    X = check_array(X, ensure_2d=False)
    y = check_array(y, ensure_2d=False)
    
    # Flatten to 1D arrays.
    X = X.ravel()
    y = y.ravel()
    
    # Check for empty arrays
    if len(X) == 0:
        raise ValueError("Input arrays cannot be empty")
    
    # Verify that the arrays have the same length.
    if len(X) != len(y):
        raise ValueError(f"Input arrays X and y must have the same length. Got len(X)={len(X)} and len(y)={len(y)}")
    
    return X, y


def sort_by_x(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Sort arrays by X values.
    
    Parameters
    ----------
    X : array-like of shape (n_samples,)
        Input features.
    y : array-like of shape (n_samples,)
        Target values.
        
    Returns
    -------
    sort_idx : ndarray of shape (n_samples,)
        Indices that would sort X.
    X_sorted : ndarray of shape (n_samples,)
        Sorted X values.
    y_sorted : ndarray of shape (n_samples,)
        y values sorted by X.
        
    Examples
    --------
    >>> import numpy as np
    >>> X = np.array([0.5, 0.3, 0.7, 0.1, 0.9])
    >>> y = np.array([1, 0, 1, 0, 1])
    >>> idx, X_sorted, y_sorted = sort_by_x(X, y)
    >>> print(X_sorted)
    [0.1 0.3 0.5 0.7 0.9]
    >>> print(y_sorted)
    [0 0 1 1 1]
    """
    # Ensure inputs are numpy arrays
    X = np.asarray(X)
    y = np.asarray(y)
    
    # Get sorting indices
    sort_idx = np.argsort(X)
    X_sorted = X[sort_idx]
    y_sorted = y[sort_idx]
    
    return sort_idx, X_sorted, y_sorted

def create_bins(X: np.ndarray, n_bins: int = 10, 
                strategy: str = 'uniform') -> np.ndarray:
    """
    Create bin edges for discretizing continuous values.
    
    Parameters
    ----------
    X : array-like of shape (n_samples,)
        Values to be binned.
    n_bins : int, default=10
        Number of bins.
    strategy : {'uniform', 'quantile'}, default='uniform'
        Strategy for binning:
        - 'uniform': Bins with uniform widths.
        - 'quantile': Bins with approximately equal counts.
        
    Returns
    -------
    bins : ndarray of shape (n_bins+1,)
        Bin edges.
        
    Examples
    --------
    >>> import numpy as np
    >>> X = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    >>> create_bins(X, n_bins=3, strategy='uniform')
    array([0.1, 0.367, 0.633, 0.9])
    """
    X = np.asarray(X)
    
    if strategy == 'uniform':
        # Create bins with uniform widths
        bins = np.linspace(np.min(X), np.max(X), n_bins + 1)
    elif strategy == 'quantile':
        # Create bins with approximately equal counts
        bins = np.percentile(X, np.linspace(0, 100, n_bins + 1))
    else:
        raise ValueError(f"Unknown binning strategy: {strategy}. "
                         f"Use 'uniform' or 'quantile'.")
    
    return bins


def bin_data(X: np.ndarray, bins: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Assign data points to bins and compute bin centers.
    
    Parameters
    ----------
    X : array-like of shape (n_samples,)
        Values to be binned.
    bins : array-like of shape (n_bins+1,)
        Bin edges.
        
    Returns
    -------
    bin_indices : ndarray of shape (n_samples,)
        Bin indices for each data point.
    bin_centers : ndarray of shape (n_bins,)
        Centers of each bin.
        
    Examples
    --------
    >>> import numpy as np
    >>> X = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    >>> bins = np.array([0.0, 0.33, 0.67, 1.0])
    >>> bin_indices, bin_centers = bin_data(X, bins)
    >>> print(bin_indices)
    [0 0 1 2 2]
    >>> print(bin_centers)
    [0.165 0.5   0.835]
    """
    X = np.asarray(X)
    bins = np.asarray(bins)
    
    # Assign data points to bins
    bin_indices = np.digitize(X, bins) - 1
    
    # Clip bin indices to valid range
    bin_indices = np.clip(bin_indices, 0, len(bins) - 2)
    
    # Compute bin centers
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    return bin_indices, bin_centers
