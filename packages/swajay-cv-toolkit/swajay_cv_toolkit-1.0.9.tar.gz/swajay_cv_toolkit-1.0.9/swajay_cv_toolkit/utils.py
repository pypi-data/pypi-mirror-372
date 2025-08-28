# =============================================================================
# 3. swajay_cv_toolkit/utils.py
# =============================================================================

"""
Utility functions for the CV toolkit
"""

import os
import random
import torch
import numpy as np
import json
from typing import Dict, Any, Optional
from pathlib import Path


def seed_everything(seed: int = 42) -> None:
    """
    Set random seeds for reproducibility
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def setup_device(device: Optional[str] = None) -> torch.device:
    """
    Setup and return appropriate device
    
    Args:
        device: Device string ('cuda', 'cpu', or None for auto)
        
    Returns:
        torch.device: Configured device
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    device = torch.device(device)
    
    if device.type == 'cuda':
        print(f"Using GPU: {torch.cuda.get_device_name()}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("Using CPU")
    
    return device


def count_parameters(model: torch.nn.Module) -> Dict[str, int]:
    """
    Count model parameters
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with parameter counts
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'non_trainable_parameters': total_params - trainable_params
    }


def save_experiment(experiment_data: Dict[str, Any], 
                   save_path: str = 'experiment.json') -> None:
    """
    Save experiment configuration and results
    
    Args:
        experiment_data: Dictionary containing experiment info
        save_path: Path to save the experiment data
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert non-serializable objects to strings
    serializable_data = {}
    for key, value in experiment_data.items():
        try:
            json.dumps(value)
            serializable_data[key] = value
        except (TypeError, ValueError):
            serializable_data[key] = str(value)
    
    with open(save_path, 'w') as f:
        json.dump(serializable_data, f, indent=2, default=str)
    
    print(f"Experiment saved to {save_path}")


def load_experiment(load_path: str = 'experiment.json') -> Dict[str, Any]:
    """
    Load experiment configuration and results
    
    Args:
        load_path: Path to load the experiment data
        
    Returns:
        Dictionary containing experiment info
    """
    with open(load_path, 'r') as f:
        experiment_data = json.load(f)
    
    print(f"Experiment loaded from {load_path}")
    return experiment_data


def get_model_size_mb(model: torch.nn.Module) -> float:
    """
    Calculate model size in MB
    
    Args:
        model: PyTorch model
        
    Returns:
        Model size in MB
    """
    param_size = 0
    buffer_size = 0
    
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_mb = (param_size + buffer_size) / 1024 / 1024
    return size_mb


def check_dependencies() -> Dict[str, str]:
    """
    Check installed versions of key dependencies
    
    Returns:
        Dictionary with package versions
    """
    import sys
    packages = {}
    
    try:
        import torch
        packages['torch'] = torch.__version__
    except ImportError:
        packages['torch'] = 'Not installed'
    
    try:
        import torchvision
        packages['torchvision'] = torchvision.__version__
    except ImportError:
        packages['torchvision'] = 'Not installed'
    
    try:
        import timm
        packages['timm'] = timm.__version__
    except ImportError:
        packages['timm'] = 'Not installed'
    
    try:
        import albumentations
        packages['albumentations'] = albumentations.__version__
    except ImportError:
        packages['albumentations'] = 'Not installed'
    
    packages['python'] = sys.version.split()[0]
    
    return packages