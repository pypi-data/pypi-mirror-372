# =============================================================================
# 1. swajay_cv_toolkit/__init__.py
# =============================================================================

"""
swajay-cv-toolkit: Advanced Computer Vision Toolkit
==================================================

A comprehensive toolkit for state-of-the-art image classification,
featuring advanced loss functions, model architectures, augmentations,
and training pipelines.

Author: Swajay
License: MIT
Version: 1.0.0

Quick Start:
    >>> from swajay_cv_toolkit import create_model, get_loss_function, AdvancedTrainer
    >>> model = create_model('convnext_large', num_classes=10)
    >>> criterion = get_loss_function('mixed')
    >>> trainer = AdvancedTrainer(model, criterion, optimizer)
"""

from .version import __version__

# Core modules
from .losses import (
    FocalLoss,
    LabelSmoothingCrossEntropy, 
    PolyLoss,
    MixedLoss,
    get_loss_function,
    compute_class_weights
)

from .models import (
    UniversalImageModel,
    AdaptiveClassifier,
    EnsembleModel,
    AdversarialModel,
    create_model,
    get_model_config,
    MODEL_CONFIGS
)

from .augmentations import (
    AdvancedAugmentations,
    MixupCutmix,
    AdvancedDataset,
    get_augmentation_preset,
    AUGMENTATION_PRESETS
)

from .training import (
    AdvancedTrainer,
    TTAPredictor,
    ModelEvaluator,
    create_optimizer,
    create_scheduler,
    TRAINING_PRESETS
)

from .utils import (
    seed_everything,
    setup_device,
    count_parameters,
    save_experiment,
    load_experiment
)

__all__ = [
    # Version
    '__version__',
    
    # Loss Functions
    'FocalLoss',
    'LabelSmoothingCrossEntropy',
    'PolyLoss', 
    'MixedLoss',
    'get_loss_function',
    'compute_class_weights',
    
    # Models
    'UniversalImageModel',
    'AdaptiveClassifier',
    'EnsembleModel',
    'AdversarialModel',
    'create_model',
    'get_model_config',
    'MODEL_CONFIGS',
    
    # Augmentations
    'AdvancedAugmentations',
    'MixupCutmix',
    'AdvancedDataset', 
    'get_augmentation_preset',
    'AUGMENTATION_PRESETS',
    
    # Training
    'AdvancedTrainer',
    'TTAPredictor',
    'ModelEvaluator',
    'create_optimizer',
    'create_scheduler',
    'TRAINING_PRESETS',
    
    # Utils
    'seed_everything',
    'setup_device',
    'count_parameters',
    'save_experiment',
    'load_experiment'
]