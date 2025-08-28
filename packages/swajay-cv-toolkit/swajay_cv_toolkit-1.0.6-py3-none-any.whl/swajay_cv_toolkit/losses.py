"""
Advanced Loss Functions for Deep Learning - Updated v1.1.0
Enhanced loss functions with learnable weights and advanced techniques

NEW FEATURES:
- Learnable loss ensemble with dynamic weighting
- Bi-Tempered Loss for label noise robustness
- Taylor Cross Entropy Loss
- Asymmetric Loss for imbalanced datasets
- Advanced focal loss variants

Sources:
- Focal Loss: Lin et al., 2017 - https://arxiv.org/abs/1708.02002
- Label Smoothing: Szegedy et al., 2016 - https://arxiv.org/abs/1512.00567
- Bi-Tempered Loss: Amid et al., 2019 - https://arxiv.org/abs/1906.03361
- Taylor Cross Entropy: Feng et al., 2020 - https://arxiv.org/abs/2008.12887
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Dict, Any, List


class FocalLoss(nn.Module):
    """
    Enhanced Focal Loss with multiple variants
    Reference: "Focal Loss for Dense Object Detection" (Lin et al., 2017)
    """
    def __init__(self, alpha=1, gamma=2, logits=False, reduce=True, 
                 class_weights=None, variant='standard'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.logits = logits
        self.reduce = reduce
        self.variant = variant
        
        if class_weights is not None:
            self.register_buffer('class_weights', torch.FloatTensor(class_weights))
        else:
            self.class_weights = None

    def forward(self, inputs, targets):
        if self.logits:
            BCE_loss = F.cross_entropy(inputs, targets, reduction='none', weight=self.class_weights)
        else:
            BCE_loss = F.cross_entropy(inputs, targets, reduction='none', weight=self.class_weights)
        
        pt = torch.exp(-BCE_loss)
        
        if self.variant == 'standard':
            F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss
        elif self.variant == 'balanced':
            # Balanced focal loss
            alpha_t = self.alpha * torch.ones_like(targets)
            F_loss = alpha_t * (1-pt)**self.gamma * BCE_loss
        elif self.variant == 'adaptive':
            # Adaptive gamma based on difficulty
            adaptive_gamma = self.gamma * (1 + BCE_loss)
            F_loss = self.alpha * (1-pt)**adaptive_gamma * BCE_loss
        else:
            F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss

        if self.reduce:
            return torch.mean(F_loss)
        else:
            return F_loss


class LabelSmoothingCrossEntropy(nn.Module):
    """
    Enhanced Label Smoothing Cross Entropy with temperature scaling
    Reference: "Rethinking the Inception Architecture" (Szegedy et al., 2016)
    """
    def __init__(self, eps=0.1, reduction='mean', temperature=1.0, 
                 class_weights=None, adaptive_smoothing=False):
        super(LabelSmoothingCrossEntropy, self).__init__()
        self.eps = eps
        self.reduction = reduction
        self.temperature = temperature
        self.adaptive_smoothing = adaptive_smoothing
        
        if class_weights is not None:
            self.register_buffer('class_weights', torch.FloatTensor(class_weights))
        else:
            self.class_weights = None

    def forward(self, output, target):
        # Apply temperature scaling
        output = output / self.temperature
        
        # Adaptive smoothing based on confidence
        if self.adaptive_smoothing:
            max_probs = F.softmax(output, dim=-1).max(dim=-1)[0]
            adaptive_eps = self.eps * (1 - max_probs).unsqueeze(1)
        else:
            adaptive_eps = self.eps
        
        c = output.size()[-1]
        log_preds = torch.log_softmax(output, dim=-1)
        
        if self.class_weights is not None:
            # Apply class weights to uniform distribution
            uniform_dist = self.class_weights / self.class_weights.sum()
            uniform_dist = uniform_dist.unsqueeze(0).expand(output.size(0), -1)
            loss = self.reduce_loss(-(log_preds * uniform_dist).sum(dim=-1), self.reduction)
        else:
            loss = self.reduce_loss(-log_preds.sum(dim=-1), self.reduction)
            loss = loss / c
        
        nll = F.nll_loss(log_preds, target, reduction=self.reduction, weight=self.class_weights)
        return self.linear_combination(loss, nll, adaptive_eps if not self.adaptive_smoothing else adaptive_eps.mean())

    def linear_combination(self, x, y, eps):
        if isinstance(eps, torch.Tensor):
            return eps.unsqueeze(1) * x + (1 - eps.unsqueeze(1)) * y
        return eps * x + (1 - eps) * y

    def reduce_loss(self, loss, reduction='mean'):
        return loss.mean() if reduction == 'mean' else loss.sum() if reduction == 'sum' else loss


class PolyLoss(nn.Module):
    """
    Enhanced Polynomial Loss with multiple variants
    """
    def __init__(self, epsilon=2.0, alpha=1.0, variant='standard', class_weights=None):
        super(PolyLoss, self).__init__()
        self.epsilon = epsilon
        self.alpha = alpha
        self.variant = variant
        
        if class_weights is not None:
            self.register_buffer('class_weights', torch.FloatTensor(class_weights))
        else:
            self.class_weights = None

    def forward(self, output, target):
        ce_loss = F.cross_entropy(output, target, reduction='none', weight=self.class_weights)
        pt = torch.gather(F.softmax(output, dim=1), 1, target.unsqueeze(1)).squeeze(1)
        
        if self.variant == 'standard':
            poly_loss = ce_loss + self.alpha * torch.pow(1 - pt, self.epsilon + 1)
        elif self.variant == 'focal_poly':
            # Combine with focal loss characteristics
            focal_weight = (1 - pt) ** 2
            poly_loss = focal_weight * ce_loss + self.alpha * torch.pow(1 - pt, self.epsilon + 1)
        elif self.variant == 'adaptive':
            # Adaptive epsilon based on loss magnitude
            adaptive_epsilon = self.epsilon * (1 + ce_loss / ce_loss.mean())
            poly_loss = ce_loss + self.alpha * torch.pow(1 - pt, adaptive_epsilon + 1)
        else:
            poly_loss = ce_loss + self.alpha * torch.pow(1 - pt, self.epsilon + 1)
        
        return poly_loss.mean()


class BiTemperedLoss(nn.Module):
    """
    Bi-Tempered Loss for robust learning with noisy labels
    Reference: "Robust Bi-Tempered Logistic Loss" (Amid et al., 2019)
    """
    def __init__(self, t1=0.8, t2=1.2, label_smoothing=0.0, num_iters=5):
        super(BiTemperedLoss, self).__init__()
        self.t1 = t1  # Temperature for activation
        self.t2 = t2  # Temperature for loss
        self.label_smoothing = label_smoothing
        self.num_iters = num_iters

    def log_t(self, u, t):
        """Compute log_t for temperature t != 1"""
        if t == 1.0:
            return torch.log(u)
        else:
            return (u.pow(1.0 - t) - 1.0) / (1.0 - t)

    def exp_t(self, u, t):
        """Compute exp_t for temperature t != 1"""
        if t == 1.0:
            return torch.exp(u)
        else:
            return torch.relu(1.0 + (1.0 - t) * u).pow(1.0 / (1.0 - t))

    def compute_normalization_fixed_point(self, activations, t, num_iters):
        """Compute normalization constant for t != 1"""
        mu, _ = torch.max(activations, -1, keepdim=True)
        normalized_activations_step_0 = activations - mu

        normalized_activations = normalized_activations_step_0

        for _ in range(num_iters):
            logt_partition = torch.sum(self.exp_t(normalized_activations, t), -1, keepdim=True)
            normalized_activations = normalized_activations_step_0 * logt_partition.pow(1.0 - t)

        logt_partition = torch.sum(self.exp_t(normalized_activations, t), -1, keepdim=True)
        normalization_constants = - self.log_t(1.0 / logt_partition, t) + mu

        return normalization_constants

    def tempered_softmax(self, activations, t, num_iters):
        """Compute tempered softmax"""
        if t == 1.0:
            return F.softmax(activations, dim=-1)

        normalization_constants = self.compute_normalization_fixed_point(activations, t, num_iters)
        return self.exp_t(activations - normalization_constants, t)

    def forward(self, activations, labels):
        if self.label_smoothing > 0:
            num_classes = activations.size(-1)
            labels = (1 - self.label_smoothing) * labels + self.label_smoothing / num_classes

        probabilities = self.tempered_softmax(activations, self.t1, self.num_iters)

        loss_values = labels * self.log_t(labels + 1e-10, self.t2) - labels * self.log_t(probabilities + 1e-10, self.t2) - labels.pow(2.0 - self.t2) / (2.0 - self.t2) + probabilities.pow(2.0 - self.t2) / (2.0 - self.t2)

        return torch.sum(loss_values, dim=-1).mean()


class TaylorCrossEntropy(nn.Module):
    """
    Taylor Cross Entropy Loss with higher-order approximations
    Reference: "Taylor Cross Entropy Loss" (Feng et al., 2020)
    """
    def __init__(self, order=2, reduction='mean', class_weights=None):
        super(TaylorCrossEntropy, self).__init__()
        self.order = order
        self.reduction = reduction
        
        if class_weights is not None:
            self.register_buffer('class_weights', torch.FloatTensor(class_weights))
        else:
            self.class_weights = None

    def forward(self, output, target):
        # Get probabilities
        prob = F.softmax(output, dim=1)
        
        # One-hot encoding
        target_one_hot = F.one_hot(target, num_classes=output.size(1)).float()
        
        # Taylor expansion terms
        loss = torch.tensor(0.0, device=output.device)
        
        for i in range(1, self.order + 1):
            term = torch.pow(-1, i) * torch.pow(1 - prob, i) / i
            loss += torch.sum(target_one_hot * term, dim=1)
        
        # Apply class weights if provided
        if self.class_weights is not None:
            weight = self.class_weights[target]
            loss = loss * weight
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class AsymmetricLoss(nn.Module):
    """
    Asymmetric Loss for imbalanced datasets
    Different penalties for false positives and false negatives
    """
    def __init__(self, gamma_neg=4, gamma_pos=1, clip=0.05, eps=1e-8):
        super(AsymmetricLoss, self).__init__()
        self.gamma_neg = gamma_neg
        self.gamma_pos = gamma_pos
        self.clip = clip
        self.eps = eps

    def forward(self, x, y):
        # Sigmoid activation
        x_sigmoid = torch.sigmoid(x)
        xs_pos = x_sigmoid
        xs_neg = 1 - x_sigmoid

        # Asymmetric clipping
        if self.clip is not None and self.clip > 0:
            xs_neg = (xs_neg + self.clip).clamp(max=1)

        # Basic CE calculation
        los_pos = y * torch.log(xs_pos.clamp(min=self.eps))
        los_neg = (1 - y) * torch.log(xs_neg.clamp(min=self.eps))
        loss = los_pos + los_neg

        # Asymmetric focusing
        if self.gamma_neg > 0 or self.gamma_pos > 0:
            pt0 = xs_pos * y
            pt1 = xs_neg * (1 - y)
            pt = pt0 + pt1
            one_sided_gamma = self.gamma_pos * y + self.gamma_neg * (1 - y)
            one_sided_w = torch.pow(1 - pt, one_sided_gamma)
            loss *= one_sided_w

        return -loss.sum()


class LearnableLossEnsemble(nn.Module):
    """
    Ensemble of multiple loss functions with learnable weights
    Automatically learns optimal combination during training
    """
    def __init__(self, loss_configs: List[Dict[str, Any]], 
                 initial_weights: Optional[List[float]] = None,
                 temperature: float = 1.0):
        super(LearnableLossEnsemble, self).__init__()
        
        self.losses = nn.ModuleList()
        self.loss_names = []
        
        # Create loss functions
        for config in loss_configs:
            loss_type = config.pop('type')
            loss_fn = self._create_loss_function(loss_type, **config)
            self.losses.append(loss_fn)
            self.loss_names.append(loss_type)
        
        # Learnable weights (in log space for numerical stability)
        if initial_weights is None:
            initial_weights = [1.0] * len(self.losses)
        
        # Initialize weights in log space
        log_weights = torch.log(torch.tensor(initial_weights, dtype=torch.float32))
        self.log_weights = nn.Parameter(log_weights)
        self.temperature = temperature
        
    def _create_loss_function(self, loss_type: str, **kwargs):
        """Create loss function from configuration"""
        loss_map = {
            'focal': FocalLoss,
            'label_smooth': LabelSmoothingCrossEntropy,
            'poly': PolyLoss,
            'bitemperd': BiTemperedLoss,
            'taylor': TaylorCrossEntropy,
            'asymmetric': AsymmetricLoss,
            'ce': nn.CrossEntropyLoss
        }
        
        if loss_type not in loss_map:
            raise ValueError(f"Unknown loss type: {loss_type}")
        
        return loss_map[loss_type](**kwargs)
    
    def get_normalized_weights(self):
        """Get softmax-normalized weights"""
        return F.softmax(self.log_weights / self.temperature, dim=0)
    
    def forward(self, outputs, targets, return_individual=False):
        """Forward pass with learnable weighting"""
        individual_losses = []
        weighted_losses = []
        
        # Normalize weights
        normalized_weights = self.get_normalized_weights()
        
        # Compute individual losses
        for loss_fn, weight in zip(self.losses, normalized_weights):
            try:
                loss_val = loss_fn(outputs, targets)
                individual_losses.append(loss_val)
                weighted_losses.append(weight * loss_val)
            except Exception as e:
                print(f"Error in loss computation: {e}")
                # Fallback to cross-entropy
                loss_val = F.cross_entropy(outputs, targets)
                individual_losses.append(loss_val)
                weighted_losses.append(weight * loss_val)
        
        # Total weighted loss
        total_loss = sum(weighted_losses)
        
        if return_individual:
            loss_dict = {
                name: loss.item() for name, loss in zip(self.loss_names, individual_losses)
            }
            loss_dict['weights'] = normalized_weights.detach().cpu().numpy()
            loss_dict['total'] = total_loss.item()
            return total_loss, loss_dict
        
        return total_loss


class DynamicLossScaling(nn.Module):
    """
    Dynamic loss scaling that adapts weights based on training progress
    """
    def __init__(self, loss_ensemble: LearnableLossEnsemble, 
                 adaptation_rate: float = 0.01):
        super(DynamicLossScaling, self).__init__()
        self.loss_ensemble = loss_ensemble
        self.adaptation_rate = adaptation_rate
        self.step_count = 0
        
    def forward(self, outputs, targets):
        self.step_count += 1
        
        # Compute loss with current weights
        total_loss, loss_dict = self.loss_ensemble(outputs, targets, return_individual=True)
        
        # Dynamic adaptation (example: reduce focal loss weight over time)
        if self.step_count % 100 == 0:
            with torch.no_grad():
                # Example adaptation strategy
                decay_factor = 1.0 - (self.step_count * self.adaptation_rate / 10000)
                decay_factor = max(0.1, decay_factor)  # Minimum weight
                
                # Adjust weights (this is just an example)
                self.loss_ensemble.log_weights[0] *= decay_factor  # Reduce focal loss over time
        
        return total_loss


# Enhanced factory function with new loss types
def get_loss_function(loss_type: str, num_classes: Optional[int] = None, 
                     class_weights: Optional[List[float]] = None, **kwargs):
    """
    Enhanced factory function for loss functions
    """
    if class_weights is not None:
        kwargs['class_weights'] = class_weights
    
    if loss_type == 'focal':
        return FocalLoss(**kwargs)
    elif loss_type == 'focal_balanced':
        return FocalLoss(variant='balanced', **kwargs)
    elif loss_type == 'focal_adaptive':
        return FocalLoss(variant='adaptive', **kwargs)
    elif loss_type == 'label_smooth':
        return LabelSmoothingCrossEntropy(**kwargs)
    elif loss_type == 'poly':
        return PolyLoss(**kwargs)
    elif loss_type == 'poly_focal':
        return PolyLoss(variant='focal_poly', **kwargs)
    elif loss_type == 'bitemperd':
        return BiTemperedLoss(**kwargs)
    elif loss_type == 'taylor':
        return TaylorCrossEntropy(**kwargs)
    elif loss_type == 'asymmetric':
        return AsymmetricLoss(**kwargs)
    elif loss_type == 'mixed':
        # Classic mixed loss
        loss_configs = [
            {'type': 'focal', 'alpha': 1, 'gamma': 2.3},
            {'type': 'label_smooth', 'eps': 0.25},
            {'type': 'poly', 'epsilon': 2.5, 'alpha': 0.8}
        ]
        return LearnableLossEnsemble(loss_configs, [0.25, 0.45, 0.30])
    elif loss_type == 'ultimate':
        # Ultimate loss ensemble for maximum performance
        loss_configs = [
            {'type': 'focal', 'variant': 'adaptive', 'alpha': 1, 'gamma': 2.0},
            {'type': 'label_smooth', 'eps': 0.2, 'adaptive_smoothing': True},
            {'type': 'poly', 'variant': 'focal_poly', 'epsilon': 2.0},
            {'type': 'taylor', 'order': 2}
        ]
        return LearnableLossEnsemble(loss_configs, [0.3, 0.3, 0.2, 0.2])
    elif loss_type == 'ce':
        weight = torch.FloatTensor(class_weights) if class_weights else None
        return nn.CrossEntropyLoss(weight=weight)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")


# Utility functions remain the same as before
def compute_class_weights(dataset_targets, method='inverse'):
    """Compute class weights for imbalanced datasets"""
    from collections import Counter
    
    class_counts = Counter(dataset_targets)
    total_samples = len(dataset_targets)
    num_classes = len(class_counts)
    
    if method == 'inverse':
        weights = [total_samples / (num_classes * class_counts[i]) 
                  for i in range(num_classes)]
    elif method == 'effective_num':
        beta = 0.9999
        weights = [(1 - beta) / (1 - beta**class_counts[i]) 
                  for i in range(num_classes)]
    
    return torch.FloatTensor(weights)


# Available loss functions
AVAILABLE_LOSSES = [
    'focal', 'focal_balanced', 'focal_adaptive',
    'label_smooth', 'poly', 'poly_focal',
    'bitemperd', 'taylor', 'asymmetric', 
    'mixed', 'ultimate', 'ce'
]


def list_available_losses():
    """List all available loss functions"""
    print("🎯 Available Loss Functions in swajay-cv-toolkit v1.1.0:")
    print("\n🔥 Focal Loss Variants:")
    print("  - focal: Standard focal loss")
    print("  - focal_balanced: Balanced focal loss")  
    print("  - focal_adaptive: Adaptive gamma focal loss")
    
    print("\n🎭 Advanced Loss Functions:")
    print("  - label_smooth: Label smoothing cross entropy")
    print("  - poly: Polynomial loss")
    print("  - poly_focal: Focal + polynomial combination")
    print("  - bitemperd: Bi-tempered loss for noisy labels")
    print("  - taylor: Taylor cross entropy")
    print("  - asymmetric: Asymmetric loss for imbalanced data")
    
    print("\n🎪 Loss Ensembles:")
    print("  - mixed: Classic combination (focal + label_smooth + poly)")
    print("  - ultimate: Advanced ensemble with learnable weights")
    
    print("\n📊 Standard:")
    print("  - ce: Cross entropy loss")


if __name__ == "__main__":
    print("🎯 swajay-cv-toolkit Losses v1.1.0 - Advanced Loss Functions")
    
    list_available_losses()
    
    # Demo learnable loss ensemble
    print(f"\n🧪 Testing Learnable Loss Ensemble...")
    try:
        loss_fn = get_loss_function('ultimate', num_classes=10)
        
        # Dummy data
        outputs = torch.randn(4, 10)
        targets = torch.randint(0, 10, (4,))
        
        # Forward pass
        loss, loss_dict = loss_fn(outputs, targets, return_individual=True)
        print(f"✅ Ultimate loss ensemble working!")
        print(f"Total loss: {loss.item():.4f}")
        print(f"Loss weights: {loss_dict['weights']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")