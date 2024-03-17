import numpy as np
import torch

# Calculate MAPE
def mean_absolute_percentage_error_np(y_true, y_pred, threshold = 0.1) :
    y_true_floor = np.maximum(y_true, threshold)
    mape = np.mean(np.abs(y_true_floor - y_pred) / y_true_floor)
    return mape

def mean_absolute_percentage_error(y_true: torch.Tensor, y_pred: torch.Tensor, threshold = 0.1):
    y_true_floor = torch.maximum(y_true, torch.tensor(threshold))
    mape = torch.mean(torch.abs(y_true_floor - y_pred) / y_true_floor)
    return mape
