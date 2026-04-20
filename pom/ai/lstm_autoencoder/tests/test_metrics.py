import sys
from unittest.mock import MagicMock

# Mock matplotlib and seaborn BEFORE importing metrics
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['matplotlib.image'] = MagicMock()
sys.modules['matplotlib.backend_bases'] = MagicMock()
sys.modules['matplotlib.colors'] = MagicMock()
sys.modules['seaborn'] = MagicMock()

import pytest
import numpy as np
import pandas as pd
from metrics import mae, cosine_similarity, skewness_and_kurtosis, correlation_matrix

def test_mae():
    # Case 1: Identical arrays -> MAE should be 0
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[1, 2], [3, 4]])
    assert mae(a, b) == 0.0

    # Case 2: Known difference
    # |1-2| + |2-3| + |3-4| + |4-5| = 1 + 1 + 1 + 1 = 4
    # Mean = 4 / 4 = 1.0
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[2, 3], [4, 5]])
    assert mae(a, b) == 1.0

def test_cosine_similarity():
    # Case 1: Identical vectors -> Similarity 1.0
    # Shape: (num_windows, features)
    a = np.array([[1, 0]])
    b = np.array([[1, 0]])
    assert np.isclose(cosine_similarity(a, b), 1.0)

    # Case 2: Orthogonal vectors -> Similarity 0.0
    a = np.array([[1, 0]])
    b = np.array([[0, 1]])
    assert np.isclose(cosine_similarity(a, b), 0.0)

    # Case 3: Opposite vectors -> Similarity -1.0
    a = np.array([[1, 0]])
    b = np.array([[-1, 0]])
    assert np.isclose(cosine_similarity(a, b), -1.0)

def test_skewness_and_kurtosis():
    # Case 1: Normal distribution (approx)
    # Skewness should be near 0
    np.random.seed(42)
    data = np.random.normal(0, 1, 1000)
    # Shift to be positive as the function filters > 0
    data = np.abs(data) + 0.1 
    
    result = skewness_and_kurtosis(data)
    assert "skewness" in result
    assert "kurtosis" in result
    assert isinstance(result["skewness"], float)
    assert isinstance(result["kurtosis"], float)

    # Case 2: Empty or all zeros
    result_empty = skewness_and_kurtosis([])
    assert result_empty["skewness"] == 0.0
    assert result_empty["kurtosis"] == 0.0

def test_correlation_matrix():
    # 2 joints, 3 frames
    # Joint 0: [0.1, 0.2, 0.3]
    # Joint 1: [0.2, 0.4, 0.6] -> Perfect correlation (1.0)
    joints_mse = {
        "joint_0": [0.1, 0.2, 0.3],
        "joint_1": [0.2, 0.4, 0.6]
    }
    corr = correlation_matrix(joints_mse)
    
    assert corr.shape == (2, 2)
    assert np.isclose(corr.loc["joint_0", "joint_1"], 1.0)
