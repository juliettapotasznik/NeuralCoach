import pandas as pd 
import numpy as np
from dtaidistance import dtw as dtaidistance_dtw
from sklearn.manifold import TSNE
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
import seaborn as sns

def correlation_matrix(joints_mse):
    """
    Correlation coefficient measures how MSE errors between joints are related to each other.
    """
    df = pd.DataFrame(joints_mse)
    return df.corr()

def mae(windows, reconstructed):
    """
    Calculates the mean absolute difference between predicted and actual values, providing a linear measure of average error.
    """
    return np.mean(np.abs(windows - reconstructed))

def cosine_similarity(windows, reconstructed):
    """
    Measures directional similarity (not magnitude) between two vectors by calculating the cosine of the angle between them.
    Flattens sequences and calculates similarity per window.
    """
    num_windows = windows.shape[0]
    similarities = []
    
    for i in range(num_windows):
        real_flat = windows[i].flatten()
        recon_flat = reconstructed[i].flatten()
        dot_product = np.dot(real_flat, recon_flat)
        norm_real = np.linalg.norm(real_flat)
        norm_recon = np.linalg.norm(recon_flat)
        if norm_real > 0 and norm_recon > 0:
            similarities.append(dot_product / (norm_real * norm_recon))
    
    return np.mean(similarities) if similarities else 0.0

def dtw(windows, reconstructed):
    """
    Algorithm measuring similarity between two time sequences that can find optimal alignment even if sequences are phase-shifted or differ in speed.
    """
    
    num_windows = windows.shape[0]
    dtw_distances = []
    
    for i in range(num_windows):
        real_seq = np.linalg.norm(windows[i], axis=1)  
        recon_seq = np.linalg.norm(reconstructed[i], axis=1)
        
        distance = dtaidistance_dtw.distance(real_seq, recon_seq)
        dtw_distances.append(distance)
    
    return np.mean(dtw_distances)

def tsne(windows, reconstructed, n_components=2, perplexity=30.0, random_state=42):
    """
    Dimensionality reduction technique used primarily for visualizing high-dimensional data (e.g., in 2D or 3D) by clustering similar points close together.
    """
    num_windows = windows.shape[0]
    
    real_flat = windows.reshape(num_windows, -1)
    recon_flat = reconstructed.reshape(num_windows, -1)
    
    combined = np.vstack([real_flat, recon_flat])
    
    tsne_model = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state)
    combined_embedding = tsne_model.fit_transform(combined)
    
    real_embedding = combined_embedding[:num_windows]
    recon_embedding = combined_embedding[num_windows:]
    
    return real_embedding, recon_embedding

def skewness_and_kurtosis(errors):
    """
    Calculates skewness and kurtosis of error distribution.
    
    Skewness:
    - > 0: distribution skewed to the right (more small errors, few large ones)
    - = 0: symmetric distribution
    - < 0: distribution skewed to the left (more large errors)
    
    Kurtosis:
    - > 3: high (more extremes than a normal distribution)
    - = 3: normal kurtosis (normal distribution)
    - < 3: low (fewer extremes, flatter distribution)
    """
    errors_array = np.array(errors).flatten()
    
    errors_array = errors_array[errors_array > 0]
    errors_array = errors_array[~np.isnan(errors_array)]
    
    if len(errors_array) == 0:
        return {'skewness': 0.0, 'kurtosis': 0.0}
    
    skewness_value = float(skew(errors_array))
    kurtosis_value = float(kurtosis(errors_array, fisher=False))
    
    return {
        'skewness': skewness_value,
        'kurtosis': kurtosis_value
    }

def anomaly_heatmap(per_frame_joint_mse, save_path=None, figsize=(14, 8)):
    """
    Creates an anomaly heatmap showing MSE errors per frame and per joint.
    
    X-axis: frames (time)
    Y-axis: joints
    Colors: error intensity (red = high errors, green = low errors)
    """
    df = pd.DataFrame(per_frame_joint_mse)
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.heatmap(
        df,
        cmap='RdYlGn_r',  
        annot=False,  
        fmt='.2f',
        cbar_kws={'label': 'MSE Error'},
        ax=ax,
        linewidths=0.5,
        linecolor='gray'
    )
    
    ax.set_xlabel('Frame (Time)', fontsize=12)
    ax.set_ylabel('Joint', fontsize=12)
    ax.set_title('Anomaly Heatmap - MSE Errors per Joint and Frame', fontsize=14, fontweight='bold')
    
    plt.setp(ax.get_yticklabels(), rotation=0)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap saved to: {save_path}")
    
    return fig