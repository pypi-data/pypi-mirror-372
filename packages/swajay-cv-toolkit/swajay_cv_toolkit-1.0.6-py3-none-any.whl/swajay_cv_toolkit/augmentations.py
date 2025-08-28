"""
Fixed Advanced Data Augmentation Strategies
Comprehensive augmentation pipeline for computer vision

Sources:
- Albumentations: https://albumentations.ai/docs/
- AutoAugment: Cubuk et al., 2018 - https://arxiv.org/abs/1805.09501
- MixUp: Zhang et al., 2017 - https://arxiv.org/abs/1710.09412
- CutMix: Yun et al., 2019 - https://arxiv.org/abs/1905.04899
- TTA: Krizhevsky et al., 2012 - ImageNet Classification with Deep CNNs
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2
import torch
import torch.nn.functional as F
import numpy as np
import random
from typing import List, Optional, Dict, Any


class AdvancedAugmentations:
    """
    Collection of advanced augmentation strategies
    """
    
    @staticmethod
    def get_training_transforms(image_size: int = 224,
                              intensity: str = 'medium',
                              normalize: bool = True) -> A.Compose:
        """
        Get training augmentation transforms
        
        Args:
            image_size: Target image size
            intensity: 'light', 'medium', 'heavy', 'competition'
            normalize: Whether to apply ImageNet normalization
        """
        
        base_transforms = [
            A.Resize(image_size + 32, image_size + 32),
            A.RandomCrop(image_size, image_size),
        ]
        
        if intensity == 'light':
            aug_transforms = [
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.3),
                A.Rotate(limit=15, p=0.3),
            ]
        
        elif intensity == 'medium':
            aug_transforms = [
                A.HorizontalFlip(p=0.6),
                A.VerticalFlip(p=0.2),
                A.RandomRotate90(p=0.3),
                A.Rotate(limit=25, p=0.5),
                A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),
                
                A.OneOf([
                    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
                    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
                    A.HueSaturationValue(hue_shift_limit=15, sat_shift_limit=25, val_shift_limit=15, p=0.5),
                ], p=0.6),
                
                A.OneOf([
                    A.GaussNoise(var_limit=(10.0, 30.0), p=0.3),
                    A.GaussianBlur(blur_limit=(1, 3), p=0.3),
                ], p=0.3),
                
                A.CoarseDropout(max_holes=8, max_height=16, max_width=16,
                              min_holes=1, min_height=4, min_width=4, p=0.3),
            ]
        
        elif intensity == 'heavy':
            aug_transforms = [
                A.HorizontalFlip(p=0.6),
                A.VerticalFlip(p=0.3),
                A.RandomRotate90(p=0.4),
                A.Rotate(limit=30, p=0.6),
                A.ShiftScaleRotate(shift_limit=0.15, scale_limit=0.2, rotate_limit=20, p=0.7),
                
                A.OneOf([
                    A.ElasticTransform(alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03, p=0.6),
                    A.GridDistortion(num_steps=5, distort_limit=0.3, p=0.6),
                    A.OpticalDistortion(distort_limit=0.2, shift_limit=0.2, p=0.6)
                ], p=0.4),
                
                A.OneOf([
                    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.6),
                    A.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.25, hue=0.15, p=0.6),
                    A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.6),
                ], p=0.7),
                
                A.OneOf([
                    A.GaussNoise(var_limit=(10.0, 50.0), p=0.4),
                    A.GaussianBlur(blur_limit=(1, 5), p=0.4),
                    A.MotionBlur(blur_limit=(3, 7), p=0.3),
                ], p=0.5),
                
                A.OneOf([
                    A.CoarseDropout(max_holes=12, max_height=24, max_width=24,
                                  min_holes=1, min_height=8, min_width=8, p=0.5),
                    A.GridDropout(ratio=0.2, unit_size_min=8, unit_size_max=32, p=0.4),
                ], p=0.4),
                
                A.OneOf([
                    A.CLAHE(clip_limit=2.0, tile_grid_size=(4, 4), p=0.3),
                    A.Posterize(num_bits=4, p=0.2),
                    A.Solarize(threshold=128, p=0.2),
                ], p=0.3),
            ]
        
        elif intensity == 'competition':
            aug_transforms = [
                A.HorizontalFlip(p=0.6),
                A.VerticalFlip(p=0.3),
                A.RandomRotate90(p=0.4),
                A.Rotate(limit=30, p=0.6),
                A.ShiftScaleRotate(shift_limit=0.15, scale_limit=0.2, rotate_limit=20, p=0.7),

                A.OneOf([
                    A.ElasticTransform(alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03, p=0.6),
                    A.GridDistortion(num_steps=5, distort_limit=0.4, p=0.6),
                    A.OpticalDistortion(distort_limit=0.3, shift_limit=0.3, p=0.6)
                ], p=0.5),

                A.OneOf([
                    A.GaussNoise(var_limit=(10.0, 60.0), p=0.4),
                    A.GaussianBlur(blur_limit=(1, 5), p=0.4),
                    A.MotionBlur(blur_limit=(3, 9), p=0.4),
                    A.MedianBlur(blur_limit=5, p=0.3),
                ], p=0.5),

                A.OneOf([
                    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.6),
                    A.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.25, hue=0.15, p=0.6),
                    A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.6),
                    A.RGBShift(r_shift_limit=20, g_shift_limit=20, b_shift_limit=20, p=0.6),
                ], p=0.7),

                A.OneOf([
                    A.CLAHE(clip_limit=3.0, tile_grid_size=(6, 6), p=0.4),
                    A.Equalize(p=0.3),
                    A.Posterize(num_bits=4, p=0.3),
                    A.Solarize(threshold=120, p=0.3),
                ], p=0.4),

                A.OneOf([
                    A.CoarseDropout(max_holes=12, max_height=24, max_width=24,
                                   min_holes=1, min_height=8, min_width=8, p=0.5),
                    A.GridDropout(ratio=0.25, unit_size_min=8, unit_size_max=32,
                                 holes_number_x=6, holes_number_y=6, p=0.4),
                ], p=0.5),
            ]
        else:
            # Default to medium
            aug_transforms = [
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
                A.Rotate(limit=15, p=0.3),
            ]
        
        final_transforms = []
        if normalize:
            final_transforms.append(
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            )
        final_transforms.append(ToTensorV2())
        
        return A.Compose(base_transforms + aug_transforms + final_transforms)
    
    @staticmethod
    def get_validation_transforms(image_size: int = 224,
                                normalize: bool = True) -> A.Compose:
        """Get validation transforms"""
        transforms = [A.Resize(image_size, image_size)]
        
        if normalize:
            transforms.append(
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            )
        transforms.append(ToTensorV2())
        
        return A.Compose(transforms)
    
    @staticmethod
    def get_tta_transforms(image_size: int = 224,
                          normalize: bool = True) -> List[A.Compose]:
        """
        Get Test-Time Augmentation transforms
        Returns list of different augmentation pipelines
        """
        base_norm = []
        if normalize:
            base_norm = [A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]
        
        tta_transforms = [
            # Original
            A.Compose([
                A.Resize(image_size, image_size),
                *base_norm,
                ToTensorV2()
            ]),
            # Horizontal flip
            A.Compose([
                A.Resize(image_size, image_size),
                A.HorizontalFlip(p=1.0),
                *base_norm,
                ToTensorV2()
            ]),
            # Larger resize + center crop
            A.Compose([
                A.Resize(image_size + 16, image_size + 16),
                A.CenterCrop(image_size, image_size),
                *base_norm,
                ToTensorV2()
            ]),
            # Vertical flip
            A.Compose([
                A.Resize(image_size, image_size),
                A.VerticalFlip(p=1.0),
                *base_norm,
                ToTensorV2()
            ]),
            # Small rotation
            A.Compose([
                A.Resize(image_size, image_size),
                A.Rotate(limit=10, p=1.0),
                *base_norm,
                ToTensorV2()
            ]),
            # Random crop
            A.Compose([
                A.Resize(image_size + 32, image_size + 32),
                A.RandomCrop(image_size, image_size),
                *base_norm,
                ToTensorV2()
            ]),
            # Both flips
            A.Compose([
                A.Resize(image_size, image_size),
                A.HorizontalFlip(p=1.0),
                A.VerticalFlip(p=1.0),
                *base_norm,
                ToTensorV2()
            ])
        ]
        
        return tta_transforms


class MixupCutmix:
    """
    Implementation of Mixup and Cutmix augmentations
    """
    
    def __init__(self, mixup_alpha=0.2, cutmix_alpha=1.0, prob=0.5):
        self.mixup_alpha = mixup_alpha
        self.cutmix_alpha = cutmix_alpha
        self.prob = prob
    
    def mixup_data(self, x, y):
        """Mixup augmentation"""
        if self.mixup_alpha > 0:
            lam = np.random.beta(self.mixup_alpha, self.mixup_alpha)
        else:
            lam = 1
        
        batch_size = x.size(0)
        index = torch.randperm(batch_size).to(x.device)
        
        mixed_x = lam * x + (1 - lam) * x[index, :]
        y_a, y_b = y, y[index]
        return mixed_x, y_a, y_b, lam
    
    def cutmix_data(self, x, y):
        """Cutmix augmentation"""
        if self.cutmix_alpha > 0:
            lam = np.random.beta(self.cutmix_alpha, self.cutmix_alpha)
        else:
            lam = 1
        
        batch_size = x.size(0)
        index = torch.randperm(batch_size).to(x.device)
        
        bbx1, bby1, bbx2, bby2 = self.rand_bbox(x.size(), lam)
        x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
        
        # Adjust lambda to exactly match pixel ratio
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size()[-1] * x.size()[-2]))
        y_a, y_b = y, y[index]
        return x, y_a, y_b, lam
    
    def rand_bbox(self, size, lam):
        """Generate random bounding box for cutmix"""
        W = size[2]
        H = size[3]
        cut_rat = np.sqrt(1. - lam)
        cut_w = int(W * cut_rat)
        cut_h = int(H * cut_rat)
        
        # Uniform
        cx = np.random.randint(W)
        cy = np.random.randint(H)
        
        bbx1 = np.clip(cx - cut_w // 2, 0, W)
        bby1 = np.clip(cy - cut_h // 2, 0, H)
        bbx2 = np.clip(cx + cut_w // 2, 0, W)
        bby2 = np.clip(cy + cut_h // 2, 0, H)
        
        return bbx1, bby1, bbx2, bby2
    
    def __call__(self, x, y):
        """Apply mixup or cutmix randomly"""
        if random.random() < self.prob:
            if random.random() < 0.5:
                return self.mixup_data(x, y)
            else:
                return self.cutmix_data(x, y)
        return x, y, y, 1.0


class AdvancedDataset(torch.utils.data.Dataset):
    """
    Advanced dataset wrapper with built-in augmentations
    """
    def __init__(self, dataset, transform=None):
        self.dataset = dataset
        self.transform = transform
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        image, label = self.dataset[idx]
        
        # Convert PIL to numpy if needed
        if hasattr(image, 'mode'):  # PIL Image
            image = np.array(image)
        
        # Apply transforms
        if self.transform:
            if isinstance(self.transform, A.Compose):
                augmented = self.transform(image=image)
                image = augmented['image']
            else:
                image = self.transform(image)
        
        return image, label


# Preset configurations
AUGMENTATION_PRESETS = {
    'minimal': {
        'intensity': 'light',
        'mixup_cutmix': None
    },
    'standard': {
        'intensity': 'medium',
        'mixup_cutmix': {'mixup_alpha': 0.2, 'cutmix_alpha': 1.0, 'prob': 0.3}
    },
    'aggressive': {
        'intensity': 'heavy',
        'mixup_cutmix': {'mixup_alpha': 0.3, 'cutmix_alpha': 1.0, 'prob': 0.5}
    },
    'competition': {
        'intensity': 'competition',
        'mixup_cutmix': {'mixup_alpha': 0.2, 'cutmix_alpha': 1.0, 'prob': 0.4}
    }
}


def get_augmentation_preset(preset_name: str, image_size: int = 224):
    """
    Get predefined augmentation configuration
    
    Args:
        preset_name: 'minimal', 'standard', 'aggressive', 'competition'
        image_size: Target image size
    
    Returns:
        Dictionary with train_transform, val_transform, tta_transforms, mixup_cutmix
    """
    config = AUGMENTATION_PRESETS.get(preset_name, AUGMENTATION_PRESETS['standard'])
    
    train_transform = AdvancedAugmentations.get_training_transforms(
        image_size=image_size,
        intensity=config['intensity']
    )
    
    val_transform = AdvancedAugmentations.get_validation_transforms(
        image_size=image_size
    )
    
    tta_transforms = AdvancedAugmentations.get_tta_transforms(
        image_size=image_size
    )
    
    mixup_cutmix = None
    if config['mixup_cutmix']:
        mixup_cutmix = MixupCutmix(**config['mixup_cutmix'])
    
    return {
        'train_transform': train_transform,
        'val_transform': val_transform,
        'tta_transforms': tta_transforms,
        'mixup_cutmix': mixup_cutmix
    }


# Utility functions
def visualize_augmentations(dataset, transform, num_samples=4):
    """
    Visualize augmentation effects (requires matplotlib)
    """
    try:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, num_samples, figsize=(15, 6))
        
        for i in range(num_samples):
            # Original
            image, _ = dataset[i]
            if hasattr(image, 'mode'):  # PIL Image
                image = np.array(image)
            
            axes[0, i].imshow(image)
            axes[0, i].set_title(f'Original {i}')
            axes[0, i].axis('off')
            
            # Augmented
            if isinstance(transform, A.Compose):
                augmented = transform(image=image)
                aug_image = augmented['image']
                if isinstance(aug_image, torch.Tensor):
                    # Denormalize for visualization
                    aug_image = aug_image.permute(1, 2, 0).numpy()
                    aug_image = (aug_image * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406])
                    aug_image = np.clip(aug_image, 0, 1)
            else:
                aug_image = transform(image)
            
            axes[1, i].imshow(aug_image)
            axes[1, i].set_title(f'Augmented {i}')
            axes[1, i].axis('off')
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Matplotlib not available for visualization")