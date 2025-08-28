# =============================================================================
# Updated __init__.py for v1.1.0 
# =============================================================================

"""
swajay-cv-toolkit v1.1.0: Advanced Computer Vision Toolkit
=========================================================

🆕 NEW in v1.1.0:
- ConvNeXt V2 support (convnextv2_huge, convnextv2_large, etc.)
- Stochastic Weight Averaging (SWA)
- SAM optimizer support  
- Learnable loss ensembles with dynamic weighting
- Progressive resizing training
- Advanced TTA with 10+ transforms
- Temperature scaling for model calibration

A comprehensive toolkit for state-of-the-art image classification,
featuring the latest architectures and training techniques.

Author: Swajay
License: MIT
Version: 1.1.0

Quick Start:
    >>> from swajay_cv_toolkit import create_model, get_loss_function, AdvancedTrainer
    >>> 
    >>> # Use the latest ConvNeXt V2 Huge model
    >>> model = create_model('convnextv2_huge', num_classes=10, use_ema=True)
    >>> 
    >>> # Use ultimate loss ensemble with learnable weights  
    >>> criterion = get_loss_function('ultimate')
    >>> 
    >>> # Train with SWA and advanced techniques
    >>> trainer = AdvancedTrainer(model, criterion, optimizer, use_swa=True)
    >>> history = trainer.fit(train_loader, val_loader, epochs=45)
"""

from .version import __version__

# Core modules (existing)
from .losses import (
    FocalLoss,
    LabelSmoothingCrossEntropy, 
    PolyLoss,
    MixedLoss,
    get_loss_function,
    compute_class_weights,
    # NEW in v1.1.0
    BiTemperedLoss,
    TaylorCrossEntropy,
    AsymmetricLoss,
    LearnableLossEnsemble,
    DynamicLossScaling,
    list_available_losses,
    AVAILABLE_LOSSES
)

from .models import (
    UniversalImageModel,
    AdaptiveClassifier,
    EnsembleModel,
    AdversarialModel,
    create_model,
    get_model_config,
    MODEL_CONFIGS,
    # NEW in v1.1.0
    EMAModel,
    TemperatureScaling,
    AdvancedEnsembleModel,
    list_available_models,
    SUPPORTED_MODELS
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
    TRAINING_PRESETS,
    # NEW in v1.1.0
    SAM,
    ProgressiveTrainer
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
    
    # Loss Functions (Enhanced)
    'FocalLoss',
    'LabelSmoothingCrossEntropy',
    'PolyLoss', 
    'MixedLoss',
    'BiTemperedLoss',          # NEW
    'TaylorCrossEntropy',      # NEW
    'AsymmetricLoss',          # NEW
    'LearnableLossEnsemble',   # NEW
    'DynamicLossScaling',      # NEW
    'get_loss_function',
    'compute_class_weights',
    'list_available_losses',   # NEW
    'AVAILABLE_LOSSES',        # NEW
    
    # Models (Enhanced)
    'UniversalImageModel',
    'AdaptiveClassifier',
    'EnsembleModel',
    'AdversarialModel',
    'EMAModel',                # NEW
    'TemperatureScaling',      # NEW
    'AdvancedEnsembleModel',   # NEW
    'create_model',
    'get_model_config',
    'MODEL_CONFIGS',
    'list_available_models',   # NEW
    'SUPPORTED_MODELS',        # NEW
    
    # Augmentations
    'AdvancedAugmentations',
    'MixupCutmix',
    'AdvancedDataset', 
    'get_augmentation_preset',
    'AUGMENTATION_PRESETS',
    
    # Training (Enhanced)
    'AdvancedTrainer',
    'TTAPredictor',
    'ModelEvaluator',
    'SAM',                     # NEW
    'ProgressiveTrainer',      # NEW
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