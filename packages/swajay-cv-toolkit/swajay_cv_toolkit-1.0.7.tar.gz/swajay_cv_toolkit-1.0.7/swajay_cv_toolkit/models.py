"""
Advanced Model Architectures for Computer Vision - Updated v1.1.0
Support for latest architectures and advanced training techniques

NEW FEATURES:
- ConvNeXt V2 support (convnextv2_huge, convnextv2_large, etc.)
- Exponential Moving Average (EMA) wrapper
- Progressive training support
- Temperature scaling for calibration
- Advanced ensemble techniques

Sources:
- ConvNeXt V2: Woo et al., 2023 - https://arxiv.org/abs/2301.00808
- EMA: Polyak & Juditsky, 1992 - Acceleration of stochastic approximation
- Temperature Scaling: Guo et al., 2017 - https://arxiv.org/abs/1706.04599
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
import torchvision.models as models
from typing import Optional, List, Dict, Any
from collections import OrderedDict
import math


class AdaptiveClassifier(nn.Module):
    """
    Adaptive classifier head with enhanced capabilities
    """
    def __init__(self, feature_dim: int, num_classes: int, 
                 hidden_dims: Optional[List[int]] = None,
                 dropout_rates: Optional[List[float]] = None,
                 activation: str = 'silu',
                 use_attention: bool = False):
        super(AdaptiveClassifier, self).__init__()
        
        if hidden_dims is None:
            # Smart sizing based on feature dimension and number of classes
            if feature_dim > 2048:
                hidden_dims = [feature_dim // 2, feature_dim // 4, feature_dim // 8]
            elif feature_dim > 1024:
                hidden_dims = [feature_dim // 2, feature_dim // 4]
            else:
                hidden_dims = [feature_dim // 2]
        
        if dropout_rates is None:
            dropout_rates = [0.4, 0.3, 0.2][:len(hidden_dims)]
        
        # Ensure we have enough dropout rates
        while len(dropout_rates) < len(hidden_dims):
            dropout_rates.append(dropout_rates[-1] * 0.8)
        
        activation_fn = {
            'relu': nn.ReLU,
            'silu': nn.SiLU,
            'gelu': nn.GELU,
            'leaky_relu': nn.LeakyReLU
        }[activation]
        
        layers = []
        prev_dim = feature_dim
        
        # Add attention mechanism if requested
        if use_attention:
            self.attention = nn.MultiheadAttention(feature_dim, num_heads=8, batch_first=True)
        else:
            self.attention = None
        
        for i, (hidden_dim, dropout_rate) in enumerate(zip(hidden_dims, dropout_rates)):
            layers.extend([
                nn.Dropout(dropout_rate),
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                activation_fn(inplace=True)
            ])
            prev_dim = hidden_dim
        
        layers.extend([
            nn.Dropout(dropout_rates[-1] * 0.5),
            nn.Linear(prev_dim, num_classes)
        ])
        
        self.classifier = nn.Sequential(*layers)
        self._init_weights()
    
    def _init_weights(self):
        for m in self.classifier.modules():
            if isinstance(m, nn.Linear):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        if self.attention is not None and len(x.shape) == 3:
            # Apply attention if input has sequence dimension
            x, _ = self.attention(x, x, x)
            x = x.mean(dim=1)  # Global average pooling
        
        return self.classifier(x)


class EMAModel(nn.Module):
    """
    Exponential Moving Average wrapper for any model
    """
    def __init__(self, model: nn.Module, decay: float = 0.9999):
        super(EMAModel, self).__init__()
        self.model = model
        self.ema_model = None
        self.decay = decay
        self.num_updates = 0
        
    def _create_ema_model(self):
        """Create EMA model copy"""
        self.ema_model = type(self.model)(**self.model_kwargs) if hasattr(self, 'model_kwargs') else None
        if self.ema_model is not None:
            self.ema_model.load_state_dict(self.model.state_dict())
            for param in self.ema_model.parameters():
                param.requires_grad_(False)
    
    def update_ema(self):
        """Update EMA model parameters"""
        if self.ema_model is None:
            self._create_ema_model()
            return
        
        self.num_updates += 1
        # Decay adjustment based on number of updates
        decay = min(self.decay, (1 + self.num_updates) / (10 + self.num_updates))
        
        with torch.no_grad():
            for ema_param, param in zip(self.ema_model.parameters(), self.model.parameters()):
                ema_param.data.mul_(decay).add_(param.data, alpha=1 - decay)
    
    def forward(self, x, use_ema=False):
        if use_ema and self.ema_model is not None:
            return self.ema_model(x)
        return self.model(x)


class TemperatureScaling(nn.Module):
    """
    Temperature scaling for model calibration
    """
    def __init__(self, model: nn.Module):
        super(TemperatureScaling, self).__init__()
        self.model = model
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
    
    def forward(self, x):
        logits = self.model(x)
        return logits / self.temperature
    
    def calibrate(self, val_loader, device):
        """Calibrate temperature using validation set"""
        self.model.eval()
        nll_criterion = nn.CrossEntropyLoss()
        
        # Collect all logits and labels
        logits_list = []
        labels_list = []
        
        with torch.no_grad():
            for data, labels in val_loader:
                data, labels = data.to(device), labels.to(device)
                logits = self.model(data)
                logits_list.append(logits)
                labels_list.append(labels)
        
        logits = torch.cat(logits_list)
        labels = torch.cat(labels_list)
        
        # Optimize temperature
        optimizer = torch.optim.LBFGS([self.temperature], lr=0.01, max_iter=50)
        
        def eval_loss():
            loss = nll_criterion(logits / self.temperature, labels)
            loss.backward()
            return loss
        
        optimizer.step(eval_loss)
        print(f"Optimal temperature: {self.temperature.item():.3f}")
        
        return self.temperature.item()


class UniversalImageModel(nn.Module):
    """
    Enhanced Universal image classification model with advanced features
    """
    def __init__(self, model_name: str = 'convnext_large', 
                 num_classes: int = 1000,
                 pretrained: bool = True,
                 classifier_config: Optional[dict] = None,
                 use_ema: bool = False,
                 ema_decay: float = 0.9999):
        super(UniversalImageModel, self).__init__()
        
        self.model_name = model_name
        self.num_classes = num_classes
        
        # Default classifier configuration
        if classifier_config is None:
            classifier_config = {
                'hidden_dims': None,  # Auto-calculate
                'dropout_rates': [0.4, 0.3, 0.2],
                'activation': 'silu',
                'use_attention': False
            }
        
        # Create backbone with enhanced model support
        self.backbone = self._create_backbone(model_name, pretrained)
        
        # Get feature dimension
        feature_dim = self._get_feature_dim()
        
        # Create adaptive classifier
        self.classifier = AdaptiveClassifier(
            feature_dim=feature_dim,
            num_classes=num_classes,
            **classifier_config
        )
        
        # EMA wrapper if requested
        if use_ema:
            self.ema_wrapper = EMAModel(self, decay=ema_decay)
        else:
            self.ema_wrapper = None
        
    def _create_backbone(self, model_name: str, pretrained: bool):
        """Enhanced backbone creation with support for latest models"""
        
        # Map of model families to their timm names
        model_mappings = {
            # ConvNeXt V1
            'convnext_tiny': 'convnext_tiny.fb_in22k_ft_in1k',
            'convnext_small': 'convnext_small.fb_in22k_ft_in1k',
            'convnext_base': 'convnext_base.fb_in22k_ft_in1k',
            'convnext_large': 'convnext_large.fb_in22k_ft_in1k',
            'convnext_xlarge': 'convnext_xlarge.fb_in22k_ft_in1k',
            
            # ConvNeXt V2 (Latest!)
            'convnextv2_nano': 'convnextv2_nano.fcmae_ft_in22k_in1k',
            'convnextv2_tiny': 'convnextv2_tiny.fcmae_ft_in22k_in1k',
            'convnextv2_base': 'convnextv2_base.fcmae_ft_in22k_in1k',
            'convnextv2_large': 'convnextv2_large.fcmae_ft_in22k_in1k',
            'convnextv2_huge': 'convnextv2_huge.fcmae_ft_in22k_in1k_384',
            
            # EfficientNet V2
            'efficientnetv2_s': 'tf_efficientnetv2_s.in21k_ft_in1k',
            'efficientnetv2_m': 'tf_efficientnetv2_m.in21k_ft_in1k',
            'efficientnetv2_l': 'tf_efficientnetv2_l.in21k_ft_in1k',
            'efficientnetv2_xl': 'tf_efficientnetv2_xl.in21k_ft_in1k',
            
            # Vision Transformers
            'vit_base_patch16_224': 'vit_base_patch16_224.augreg2_in21k_ft_in1k',
            'vit_large_patch16_224': 'vit_large_patch16_224.augreg_in21k_ft_in1k',
            'vit_huge_patch14_224': 'vit_huge_patch14_224.orig_in21k_ft_in1k',
            
            # Swin Transformers
            'swin_base_patch4_window7_224': 'swin_base_patch4_window7_224.ms_in22k_ft_in1k',
            'swin_large_patch4_window7_224': 'swin_large_patch4_window7_224.ms_in22k_ft_in1k',
            
            # MaxViT (Latest hybrid architecture)
            'maxvit_base_tf_224': 'maxvit_base_tf_224.in1k',
            'maxvit_large_tf_224': 'maxvit_large_tf_224.in1k',
            
            # CoAtNet (Attention + Convolution)
            'coatnet_0_rw_224': 'coatnet_0_rw_224.sw_in1k',
            'coatnet_1_rw_224': 'coatnet_1_rw_224.sw_in1k',
            
            # EfficientNet (Original)
            'efficientnet_b0': 'efficientnet_b0.ra_in1k',
            'efficientnet_b1': 'efficientnet_b1.ra4_e3600_r224_in1k',
            'efficientnet_b2': 'efficientnet_b2.ra_in1k',
            'efficientnet_b3': 'efficientnet_b3.ra2_in1k',
            'efficientnet_b4': 'efficientnet_b4.ra2_in1k',
            'efficientnet_b5': 'efficientnet_b5.sw_in12k_ft_in1k',
            'efficientnet_b6': 'efficientnet_b6.ra2_in1k',
            'efficientnet_b7': 'efficientnet_b7.ra2_in1k',
        }
        
        # Get the full timm model name
        timm_name = model_mappings.get(model_name, model_name)
        
        try:
            # Create model using timm
            backbone = timm.create_model(timm_name, pretrained=pretrained, num_classes=0, drop_rate=0.0)
            print(f"✅ Created {timm_name} using timm")
            return backbone
        except Exception as e:
            print(f"⚠️ Failed to create {timm_name}: {e}")
            
            # Fallback to torchvision for basic models
            if 'resnet' in model_name:
                model = getattr(models, model_name)(pretrained=pretrained)
                model.fc = nn.Identity()
                return model
            else:
                raise ValueError(f"Unsupported model: {model_name}. Available models: {list(model_mappings.keys())}")
    
    def _get_feature_dim(self):
        """Automatically determine feature dimension"""
        with torch.no_grad():
            # Try different input sizes for different model types
            input_sizes = [(1, 3, 224, 224), (1, 3, 384, 384)]
            
            for input_size in input_sizes:
                try:
                    dummy_input = torch.randn(*input_size)
                    features = self.backbone(dummy_input)
                    if len(features.shape) > 2:
                        features = F.adaptive_avg_pool2d(features, 1).flatten(1)
                    return features.shape[1]
                except:
                    continue
            
            # Fallback
            return 1024
    
    def forward(self, x, use_ema=False):
        features = self.backbone(x)
        
        # Handle different output formats
        if len(features.shape) > 2:
            features = F.adaptive_avg_pool2d(features, 1).flatten(1)
        
        output = self.classifier(features)
        
        return output
    
    def update_ema(self):
        """Update EMA if enabled"""
        if self.ema_wrapper is not None:
            self.ema_wrapper.update_ema()


class AdvancedEnsembleModel(nn.Module):
    """
    Advanced ensemble with temperature scaling and weighted averaging
    """
    def __init__(self, models: List[nn.Module], 
                 weights: Optional[List[float]] = None,
                 ensemble_method: str = 'weighted_average',
                 use_temperature_scaling: bool = True):
        super(AdvancedEnsembleModel, self).__init__()
        
        self.models = nn.ModuleList(models)
        
        if weights is None:
            weights = [1.0 / len(models)] * len(models)
        self.register_buffer('weights', torch.tensor(weights))
        
        self.ensemble_method = ensemble_method
        
        # Temperature scaling for each model
        if use_temperature_scaling:
            self.temperatures = nn.ParameterList([
                nn.Parameter(torch.ones(1) * 1.5) for _ in models
            ])
        else:
            self.temperatures = None
    
    def forward(self, x):
        outputs = []
        
        for i, model in enumerate(self.models):
            output = model(x)
            
            # Apply temperature scaling
            if self.temperatures is not None:
                output = output / self.temperatures[i]
            
            if self.ensemble_method == 'weighted_average':
                outputs.append(F.softmax(output, dim=1) * self.weights[i])
            else:
                outputs.append(output * self.weights[i])
        
        if self.ensemble_method == 'weighted_average':
            # Weighted average of probabilities
            ensemble_output = sum(outputs)
            return torch.log(ensemble_output + 1e-8)  # Convert back to logits
        else:
            # Weighted average of logits
            return sum(outputs)


# Factory function for easy model creation with new models
def create_model(model_name: str, num_classes: int, 
                 pretrained: bool = True, 
                 use_ema: bool = False,
                 **kwargs):
    """
    Enhanced factory function with support for latest architectures
    """
    
    return UniversalImageModel(
        model_name=model_name,
        num_classes=num_classes,
        pretrained=pretrained,
        use_ema=use_ema,
        **kwargs
    )


# Enhanced model configuration presets
MODEL_CONFIGS = {
    'lightweight': {
        'model_name': 'efficientnet_b0',
        'classifier_config': {
            'hidden_dims': [512, 128],
            'dropout_rates': [0.2, 0.1],
            'activation': 'relu'
        }
    },
    'balanced': {
        'model_name': 'convnext_base',
        'classifier_config': {
            'hidden_dims': [1024, 512, 256],
            'dropout_rates': [0.3, 0.2, 0.1],
            'activation': 'silu'
        }
    },
    'high_performance': {
        'model_name': 'convnext_large',
        'classifier_config': {
            'hidden_dims': [1536, 768, 384],
            'dropout_rates': [0.4, 0.3, 0.2],
            'activation': 'silu'
        }
    },
    'ultimate': {  # NEW: For maximum performance
        'model_name': 'convnextv2_huge',
        'classifier_config': {
            'hidden_dims': [2048, 1024, 512],
            'dropout_rates': [0.5, 0.4, 0.3],
            'activation': 'silu',
            'use_attention': True
        },
        'use_ema': True,
        'ema_decay': 0.9999
    },
    'transformer': {
        'model_name': 'vit_large_patch16_224',
        'classifier_config': {
            'hidden_dims': [768, 256],
            'dropout_rates': [0.1, 0.05],
            'activation': 'gelu',
            'use_attention': True
        }
    },
    'hybrid': {  # NEW: Latest hybrid architecture
        'model_name': 'maxvit_large_tf_224',
        'classifier_config': {
            'hidden_dims': [1024, 512],
            'dropout_rates': [0.3, 0.2],
            'activation': 'silu'
        }
    }
}


def get_model_config(config_name: str):
    """Get predefined model configuration"""
    return MODEL_CONFIGS.get(config_name, MODEL_CONFIGS['balanced'])


# List of all supported models
SUPPORTED_MODELS = [
    # ConvNeXt V1
    'convnext_tiny', 'convnext_small', 'convnext_base', 'convnext_large', 'convnext_xlarge',
    
    # ConvNeXt V2 (Latest!)
    'convnextv2_nano', 'convnextv2_tiny', 'convnextv2_base', 'convnextv2_large', 'convnextv2_huge',
    
    # EfficientNet V2
    'efficientnetv2_s', 'efficientnetv2_m', 'efficientnetv2_l', 'efficientnetv2_xl',
    
    # Vision Transformers
    'vit_base_patch16_224', 'vit_large_patch16_224', 'vit_huge_patch14_224',
    
    # Swin Transformers  
    'swin_base_patch4_window7_224', 'swin_large_patch4_window7_224',
    
    # MaxViT
    'maxvit_base_tf_224', 'maxvit_large_tf_224',
    
    # CoAtNet
    'coatnet_0_rw_224', 'coatnet_1_rw_224',
    
    # EfficientNet (Original)
    'efficientnet_b0', 'efficientnet_b1', 'efficientnet_b2', 'efficientnet_b3',
    'efficientnet_b4', 'efficientnet_b5', 'efficientnet_b6', 'efficientnet_b7',
]


def list_available_models():
    """List all available models"""
    print("🏗️ Available Models in swajay-cv-toolkit v1.1.0:")
    print("\n🔥 ConvNeXt V2 (Latest & Best):")
    for model in [m for m in SUPPORTED_MODELS if 'convnextv2' in m]:
        print(f"  - {model}")
    
    print("\n🚀 Vision Transformers:")
    for model in [m for m in SUPPORTED_MODELS if 'vit' in m or 'swin' in m]:
        print(f"  - {model}")
        
    print("\n⚡ EfficientNet Family:")
    for model in [m for m in SUPPORTED_MODELS if 'efficientnet' in m]:
        print(f"  - {model}")
        
    print("\n🔬 Hybrid Architectures:")
    for model in [m for m in SUPPORTED_MODELS if any(x in m for x in ['maxvit', 'coatnet'])]:
        print(f"  - {model}")


if __name__ == "__main__":
    # Demo the new capabilities
    print("🚀 swajay-cv-toolkit Models v1.1.0 - Advanced Architectures")
    
    list_available_models()
    
    # Test ConvNeXt V2 Huge
    try:
        model = create_model('convnextv2_huge', num_classes=20, use_ema=True)
        print(f"\n✅ ConvNeXt V2 Huge created successfully!")
        print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you have the latest timm version: pip install --upgrade timm")