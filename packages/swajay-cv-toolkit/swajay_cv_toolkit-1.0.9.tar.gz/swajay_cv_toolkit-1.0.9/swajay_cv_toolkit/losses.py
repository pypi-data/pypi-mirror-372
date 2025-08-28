"""
Advanced Loss Functions for Deep Learning
Modular implementation of state-of-the-art loss functions

Sources:
- Focal Loss: Lin et al., 2017 - https://arxiv.org/abs/1708.02002
- Label Smoothing: Szegedy et al., 2016 - https://arxiv.org/abs/1512.00567
- PolyLoss: Kaggle competition implementations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance
    Reference: "Focal Loss for Dense Object Detection" (Lin et al., 2017)
    """
    def __init__(self, alpha=1, gamma=2, logits=False, reduce=True):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.logits = logits
        self.reduce = reduce

    def forward(self, inputs, targets):
        if self.logits:
            BCE_loss = F.cross_entropy(inputs, targets, reduction='none')
        else:
            BCE_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss

        if self.reduce:
            return torch.mean(F_loss)
        else:
            return F_loss


class LabelSmoothingCrossEntropy(nn.Module):
    """
    Label Smoothing Cross Entropy Loss
    Reference: "Rethinking the Inception Architecture" (Szegedy et al., 2016)
    """
    def __init__(self, eps=0.1, reduction='mean'):
        super(LabelSmoothingCrossEntropy, self).__init__()
        self.eps = eps
        self.reduction = reduction

    def forward(self, output, target):
        c = output.size()[-1]
        log_preds = torch.log_softmax(output, dim=-1)
        loss = self.reduce_loss(-log_preds.sum(dim=-1), self.reduction)
        nll = F.nll_loss(log_preds, target, reduction=self.reduction)
        return self.linear_combination(loss/c, nll, self.eps)

    def linear_combination(self, x, y, eps):
        return eps*x + (1-eps)*y

    def reduce_loss(self, loss, reduction='mean'):
        return loss.mean() if reduction == 'mean' else loss.sum() if reduction == 'sum' else loss


class PolyLoss(nn.Module):
    """
    Polynomial Loss - Extension of cross-entropy with polynomial weighting
    Commonly used in Kaggle competitions
    """
    def __init__(self, epsilon=2.0, alpha=1.0):
        super(PolyLoss, self).__init__()
        self.epsilon = epsilon
        self.alpha = alpha

    def forward(self, output, target):
        ce_loss = F.cross_entropy(output, target, reduction='none')
        pt = torch.gather(F.softmax(output, dim=1), 1, target.unsqueeze(1)).squeeze(1)
        poly_loss = ce_loss + self.alpha * torch.pow(1 - pt, self.epsilon + 1)
        return poly_loss.mean()


class MixedLoss(nn.Module):
    """
    Combination of multiple loss functions for improved training
    Weights can be tuned based on problem characteristics
    """
    def __init__(self, focal_weight=0.25, label_smooth_weight=0.45, poly_weight=0.30,
                 focal_alpha=1, focal_gamma=2.3, label_smooth_eps=0.25,
                 poly_epsilon=2.5, poly_alpha=0.8):
        super(MixedLoss, self).__init__()
        self.focal_weight = focal_weight
        self.label_smooth_weight = label_smooth_weight
        self.poly_weight = poly_weight

        self.focal_loss = FocalLoss(alpha=focal_alpha, gamma=focal_gamma, logits=True)
        self.label_smooth_loss = LabelSmoothingCrossEntropy(eps=label_smooth_eps)
        self.poly_loss = PolyLoss(epsilon=poly_epsilon, alpha=poly_alpha)

    def forward(self, output, target):
        focal = self.focal_loss(output, target)
        label_smooth = self.label_smooth_loss(output, target)
        poly = self.poly_loss(output, target)

        total_loss = (self.focal_weight * focal +
                     self.label_smooth_weight * label_smooth +
                     self.poly_weight * poly)
        return total_loss


class AdversarialLoss(nn.Module):
    """
    Adversarial training loss combining clean and adversarial examples
    Useful for robust model training
    """
    def __init__(self, base_criterion, adv_weight=0.3):
        super(AdversarialLoss, self).__init__()
        self.base_criterion = base_criterion
        self.adv_weight = adv_weight

    def forward(self, clean_output, adv_output, target):
        clean_loss = self.base_criterion(clean_output, target)
        adv_loss = self.base_criterion(adv_output, target)
        return (1 - self.adv_weight) * clean_loss + self.adv_weight * adv_loss


# Factory function for easy loss selection
def get_loss_function(loss_type='mixed', num_classes=None, **kwargs):
    """
    Factory function to get loss functions
    
    Args:
        loss_type: 'focal', 'label_smooth', 'poly', 'mixed', 'ce', 'adversarial'
        num_classes: Number of classes (for class weights if needed)
        **kwargs: Additional parameters for specific losses
    """
    if loss_type == 'focal':
        return FocalLoss(**kwargs)
    elif loss_type == 'label_smooth':
        return LabelSmoothingCrossEntropy(**kwargs)
    elif loss_type == 'poly':
        return PolyLoss(**kwargs)
    elif loss_type == 'mixed':
        return MixedLoss(**kwargs)
    elif loss_type == 'ce':
        return nn.CrossEntropyLoss()
    elif loss_type == 'adversarial':
        base_loss = kwargs.get('base_loss', nn.CrossEntropyLoss())
        return AdversarialLoss(base_loss, **kwargs)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")


# Utility functions for loss analysis
def compute_class_weights(dataset_targets, method='inverse'):
    """
    Compute class weights for imbalanced datasets
    
    Args:
        dataset_targets: List of target labels
        method: 'inverse' or 'effective_num'
    """
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