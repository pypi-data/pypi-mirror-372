"""
Advanced Model Architectures for Computer Vision
Support for multiple state-of-the-art architectures

Sources:
- ConvNeXt: Liu et al., 2022 - https://arxiv.org/abs/2201.03545
- ResNet: He et al., 2015 - https://arxiv.org/abs/1512.03385
- EfficientNet: Tan & Le, 2019 - https://arxiv.org/abs/1905.11946
- Vision Transformer: Dosovitskiy et al., 2020 - https://arxiv.org/abs/2010.11929
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
import torchvision.models as models
from typing import Optional, List


class AdaptiveClassifier(nn.Module):
    """
    Adaptive classifier head that automatically adjusts to backbone feature dimensions
    """
    def __init__(self, feature_dim: int, num_classes: int, 
                 hidden_dims: Optional[List[int]] = None,
                 dropout_rates: Optional[List[float]] = None,
                 activation: str = 'silu'):
        super(AdaptiveClassifier, self).__init__()
        
        if hidden_dims is None:
            hidden_dims = [feature_dim // 2, feature_dim // 4, feature_dim // 8]
        
        if dropout_rates is None:
            dropout_rates = [0.35, 0.25, 0.15]
        
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
        return self.classifier(x)


class UniversalImageModel(nn.Module):
    """
    Universal image classification model supporting multiple architectures
    """
    def __init__(self, model_name: str = 'convnext_large', 
                 num_classes: int = 1000,
                 pretrained: bool = True,
                 classifier_config: Optional[dict] = None):
        super(UniversalImageModel, self).__init__()
        
        self.model_name = model_name
        self.num_classes = num_classes
        
        # Default classifier configuration
        if classifier_config is None:
            classifier_config = {
                'hidden_dims': None,  # Auto-calculate
                'dropout_rates': [0.35, 0.25, 0.15],
                'activation': 'silu'
            }
        
        # Create backbone
        if 'timm_' in model_name:
            actual_name = model_name.replace('timm_', '')
            self.backbone = timm.create_model(actual_name, pretrained=pretrained, 
                                            num_classes=0, drop_rate=0.25)
        else:
            self.backbone = self._create_torchvision_model(model_name, pretrained)
        
        # Get feature dimension
        feature_dim = self._get_feature_dim()
        
        # Create adaptive classifier
        self.classifier = AdaptiveClassifier(
            feature_dim=feature_dim,
            num_classes=num_classes,
            **classifier_config
        )
        
    def _create_torchvision_model(self, model_name: str, pretrained: bool):
        """Create model from torchvision"""
        if model_name.startswith('resnet'):
            model = getattr(models, model_name)(pretrained=pretrained)
            model.fc = nn.Identity()
            return model
        elif model_name.startswith('efficientnet'):
            model = getattr(models, model_name)(pretrained=pretrained)
            model.classifier = nn.Identity()
            return model
        else:
            raise ValueError(f"Unsupported torchvision model: {model_name}")
    
    def _get_feature_dim(self):
        """Automatically determine feature dimension"""
        with torch.no_grad():
            dummy_input = torch.randn(1, 3, 224, 224)
            features = self.backbone(dummy_input)
            if len(features.shape) > 2:
                features = F.adaptive_avg_pool2d(features, 1).flatten(1)
            return features.shape[1]
    
    def forward(self, x):
        features = self.backbone(x)
        
        # Handle different output formats
        if len(features.shape) > 2:
            features = F.adaptive_avg_pool2d(features, 1).flatten(1)
        
        return self.classifier(features)


class EnsembleModel(nn.Module):
    """
    Ensemble of multiple models for improved performance
    """
    def __init__(self, models: List[nn.Module], 
                 weights: Optional[List[float]] = None,
                 ensemble_method: str = 'average'):
        super(EnsembleModel, self).__init__()
        
        self.models = nn.ModuleList(models)
        
        if weights is None:
            weights = [1.0 / len(models)] * len(models)
        self.weights = weights
        self.ensemble_method = ensemble_method
        
    def forward(self, x):
        outputs = []
        
        for model in self.models:
            output = model(x)
            if self.ensemble_method == 'average':
                outputs.append(F.softmax(output, dim=1))
            else:
                outputs.append(output)
        
        if self.ensemble_method == 'average':
            # Weighted average of probabilities
            ensemble_output = sum(w * out for w, out in zip(self.weights, outputs))
            return torch.log(ensemble_output + 1e-8)  # Convert back to logits
        elif self.ensemble_method == 'voting':
            # Hard voting
            predictions = [torch.argmax(out, dim=1) for out in outputs]
            # Simple implementation - just return first model's output format
            return outputs[0]
        
        return ensemble_output


class AdversarialModel(nn.Module):
    """
    Model wrapper for adversarial training and attacks
    Supports FGSM, PGD attacks
    """
    def __init__(self, base_model: nn.Module):
        super(AdversarialModel, self).__init__()
        self.base_model = base_model
        
    def forward(self, x):
        return self.base_model(x)
    
    def fgsm_attack(self, x, target, epsilon=0.03):
        """Fast Gradient Sign Method attack"""
        x.requires_grad = True
        output = self.forward(x)
        loss = F.cross_entropy(output, target)
        
        self.zero_grad()
        loss.backward()
        
        # Generate adversarial example
        x_adv = x + epsilon * x.grad.sign()
        x_adv = torch.clamp(x_adv, 0, 1)
        
        return x_adv.detach()
    
    def pgd_attack(self, x, target, epsilon=0.03, alpha=0.01, iterations=10):
        """Projected Gradient Descent attack"""
        x_adv = x.clone().detach()
        
        for _ in range(iterations):
            x_adv.requires_grad = True
            output = self.forward(x_adv)
            loss = F.cross_entropy(output, target)
            
            self.zero_grad()
            loss.backward()
            
            # Update adversarial example
            x_adv = x_adv + alpha * x_adv.grad.sign()
            
            # Project to epsilon ball
            perturbation = torch.clamp(x_adv - x, -epsilon, epsilon)
            x_adv = torch.clamp(x + perturbation, 0, 1).detach()
        
        return x_adv


# Factory function for easy model creation
def create_model(model_name: str, num_classes: int, 
                 pretrained: bool = True, **kwargs):
    """
    Factory function to create models
    
    Supported models:
    - ConvNeXt: convnext_tiny, convnext_small, convnext_base, convnext_large
    - ResNet: resnet18, resnet34, resnet50, resnet101, resnet152
    - EfficientNet: efficientnet_b0 through efficientnet_b7
    - Vision Transformer: vit_base_patch16_224, vit_large_patch16_224
    """
    
    # TIMM models (prefix with timm_)
    timm_models = [
        'convnext_tiny', 'convnext_small', 'convnext_base', 'convnext_large',
        'efficientnet_b0', 'efficientnet_b1', 'efficientnet_b2', 'efficientnet_b3',
        'efficientnet_b4', 'efficientnet_b5', 'efficientnet_b6', 'efficientnet_b7',
        'vit_base_patch16_224', 'vit_large_patch16_224', 'vit_huge_patch14_224',
        'swin_base_patch4_window7_224', 'swin_large_patch4_window7_224'
    ]
    
    if model_name in timm_models:
        model_name = f'timm_{model_name}'
    
    return UniversalImageModel(
        model_name=model_name,
        num_classes=num_classes,
        pretrained=pretrained,
        **kwargs
    )


# Model configuration presets
MODEL_CONFIGS = {
    'lightweight': {
        'model_name': 'timm_efficientnet_b0',
        'classifier_config': {
            'hidden_dims': [512, 128],
            'dropout_rates': [0.2, 0.1],
            'activation': 'relu'
        }
    },
    'balanced': {
        'model_name': 'timm_convnext_base',
        'classifier_config': {
            'hidden_dims': [1024, 512, 256],
            'dropout_rates': [0.3, 0.2, 0.1],
            'activation': 'silu'
        }
    },
    'high_performance': {
        'model_name': 'timm_convnext_large',
        'classifier_config': {
            'hidden_dims': [1536, 768, 384],
            'dropout_rates': [0.35, 0.25, 0.15],
            'activation': 'silu'
        }
    },
    'transformer': {
        'model_name': 'timm_vit_base_patch16_224',
        'classifier_config': {
            'hidden_dims': [512, 256],
            'dropout_rates': [0.1, 0.05],
            'activation': 'gelu'
        }
    }
}


def get_model_config(config_name: str):
    """Get predefined model configuration"""
    return MODEL_CONFIGS.get(config_name, MODEL_CONFIGS['balanced'])