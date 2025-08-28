import pytest
import torch
from swajay_cv_toolkit.losses import FocalLoss, get_loss_function

def test_focal_loss():
    loss_fn = FocalLoss(alpha=1, gamma=2)
    inputs = torch.randn(4, 10)
    targets = torch.randint(0, 10, (4,))
    loss = loss_fn(inputs, targets)
    assert loss.item() > 0

def test_get_loss_function():
    loss_fn = get_loss_function('focal')
    assert loss_fn is not None
    
    loss_fn = get_loss_function('mixed')
    assert loss_fn is not None