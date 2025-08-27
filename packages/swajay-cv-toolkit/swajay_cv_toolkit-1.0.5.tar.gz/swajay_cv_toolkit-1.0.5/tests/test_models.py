import pytest
import torch
from swajay_cv_toolkit.models import create_model

def test_create_model():
    model = create_model('timm_efficientnet_b0', num_classes=10)
    assert model is not None
    
    # Test forward pass
    x = torch.randn(1, 3, 224, 224)
    output = model(x)
    assert output.shape == (1, 10)