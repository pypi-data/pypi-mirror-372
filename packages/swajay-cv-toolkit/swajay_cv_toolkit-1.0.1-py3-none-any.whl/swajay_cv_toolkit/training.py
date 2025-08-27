"""
Complete Training Pipeline for Computer Vision
Modular training system with advanced features

Sources:
- AdamW: Loshchilov & Hutter, 2017 - https://arxiv.org/abs/1711.05101
- Cosine Annealing: Loshchilov & Hutter, 2016 - https://arxiv.org/abs/1608.03983
- Early Stopping: Prechelt, 1998 - Neural Networks: Tricks of the trade
- Gradient Clipping: Pascanu et al., 2013 - https://arxiv.org/abs/1211.5063
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, WeightedRandomSampler
import numpy as np
import time
import math
from typing import Dict, List, Optional, Tuple, Callable
from collections import defaultdict
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')


class AdvancedTrainer:
    """
    Advanced training pipeline with comprehensive features
    """
    
    def __init__(self, 
                 model: nn.Module,
                 criterion: nn.Module,
                 optimizer: optim.Optimizer,
                 scheduler: Optional[optim.lr_scheduler._LRScheduler] = None,
                 device: str = 'cuda',
                 mixed_precision: bool = True,
                 gradient_clip_norm: float = 1.0):
        
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.mixed_precision = mixed_precision
        self.gradient_clip_norm = gradient_clip_norm
        
        # Mixed precision setup
        if mixed_precision:
            self.scaler = torch.cuda.amp.GradScaler()
        
        # Training history
        self.history = defaultdict(list)
        
        # Best model tracking
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        self.best_epoch = 0
        
    def train_epoch(self, 
                   train_loader: DataLoader,
                   epoch: int,
                   mixup_cutmix: Optional[Callable] = None,
                   verbose: bool = True) -> Dict[str, float]:
        """Train for one epoch"""
        
        self.model.train()
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device, non_blocking=True), target.to(self.device, non_blocking=True)
            
            # Apply mixup/cutmix if provided
            if mixup_cutmix is not None:
                data, target_a, target_b, lam = mixup_cutmix(data, target)
                mixed_target = True
            else:
                target_a, target_b, lam = target, target, 1.0
                mixed_target = False
            
            self.optimizer.zero_grad()
            
            if self.mixed_precision:
                with torch.cuda.amp.autocast():
                    outputs = self.model(data)
                    if mixed_target:
                        loss = lam * self.criterion(outputs, target_a) + (1 - lam) * self.criterion(outputs, target_b)
                    else:
                        loss = self.criterion(outputs, target)
                
                self.scaler.scale(loss).backward()
                
                if self.gradient_clip_norm > 0:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip_norm)
                
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(data)
                if mixed_target:
                    loss = lam * self.criterion(outputs, target_a) + (1 - lam) * self.criterion(outputs, target_b)
                else:
                    loss = self.criterion(outputs, target)
                
                loss.backward()
                
                if self.gradient_clip_norm > 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip_norm)
                
                self.optimizer.step()
            
            if self.scheduler is not None:
                self.scheduler.step()
            
            # Statistics
            running_loss += loss.item()
            
            # Calculate accuracy
            _, preds = torch.max(outputs, 1)
            if mixed_target:
                running_corrects += (lam * preds.eq(target_a).float() + 
                                   (1 - lam) * preds.eq(target_b).float()).sum().item()
            else:
                running_corrects += torch.sum(preds == target.data)
            
            total_samples += target.size(0)
            
            # Verbose logging
            if verbose and batch_idx % 50 == 0:
                current_lr = self.optimizer.param_groups[0]['lr']
                print(f'Epoch: {epoch}, Batch: {batch_idx}/{len(train_loader)}, '
                      f'Loss: {loss.item():.6f}, Acc: {100.*running_corrects/total_samples:.2f}%, '
                      f'LR: {current_lr:.8f}')
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = running_corrects / total_samples
        
        return {'loss': epoch_loss, 'accuracy': epoch_acc}
    
    def validate_epoch(self, val_loader: DataLoader, verbose: bool = True) -> Dict[str, float]:
        """Validate for one epoch"""
        
        self.model.eval()
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0
        
        all_preds = []
        all_targets = []
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device, non_blocking=True), target.to(self.device, non_blocking=True)
                
                if self.mixed_precision:
                    with torch.cuda.amp.autocast():
                        outputs = self.model(data)
                else:
                    outputs = self.model(data)
                
                loss = F.cross_entropy(outputs, target)
                
                running_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                running_corrects += torch.sum(preds == target.data)
                total_samples += target.size(0)
                
                all_preds.extend(preds.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = running_corrects / total_samples
        
        if verbose:
            print(f'Validation Loss: {epoch_loss:.6f}, Validation Acc: {epoch_acc*100:.2f}%')
        
        return {
            'loss': epoch_loss, 
            'accuracy': epoch_acc,
            'predictions': all_preds,
            'targets': all_targets
        }
    
    def fit(self,
            train_loader: DataLoader,
            val_loader: DataLoader,
            epochs: int,
            mixup_cutmix: Optional[Callable] = None,
            early_stopping_patience: int = 10,
            save_path: str = 'best_model.pth',
            verbose: bool = True) -> Dict[str, List]:
        """
        Complete training loop with early stopping
        """
        
        patience_counter = 0
        start_time = time.time()
        
        for epoch in range(epochs):
            if verbose:
                print(f'\nEpoch {epoch+1}/{epochs}')
                print('-' * 60)
            
            epoch_start = time.time()
            
            # Training
            train_metrics = self.train_epoch(
                train_loader, epoch, mixup_cutmix, verbose
            )
            
            # Validation
            val_metrics = self.validate_epoch(val_loader, verbose)
            
            # Update history
            self.history['train_loss'].append(train_metrics['loss'])
            self.history['train_accuracy'].append(train_metrics['accuracy'])
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_accuracy'].append(val_metrics['accuracy'])
            
            epoch_time = time.time() - epoch_start
            
            if verbose:
                print(f'Epoch time: {epoch_time:.2f}s')
            
            # Early stopping check
            if val_metrics['loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['loss']
                self.best_val_acc = val_metrics['accuracy']
                self.best_epoch = epoch
                patience_counter = 0
                
                # Save best model
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_loss': val_metrics['loss'],
                    'val_accuracy': val_metrics['accuracy'],
                }, save_path)
                
                if verbose:
                    print(f'New best model saved! Val Loss: {self.best_val_loss:.6f}, '
                          f'Val Acc: {self.best_val_acc*100:.2f}%')
            else:
                patience_counter += 1
                
            # Early stopping
            if patience_counter >= early_stopping_patience and epoch > 10:
                print(f'Early stopping triggered after {epoch+1} epochs')
                break
        
        total_time = time.time() - start_time
        print(f'\nTraining completed in {total_time/60:.2f} minutes')
        print(f'Best validation loss: {self.best_val_loss:.6f}')
        print(f'Best validation accuracy: {self.best_val_acc*100:.2f}%')
        
        return dict(self.history)
    
    def load_best_model(self, save_path: str = 'best_model.pth'):
        """Load the best saved model"""
        checkpoint = torch.load(save_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded best model from epoch {checkpoint['epoch']} "
              f"with val_acc: {checkpoint['val_accuracy']*100:.2f}%")


class TTAPredictor:
    """
    Test-Time Augmentation predictor
    """
    
    def __init__(self, model: nn.Module, device: str = 'cuda'):
        self.model = model
        self.device = device
        self.model.eval()
    
    def predict_with_tta(self,
                        test_dataset,
                        tta_transforms: List,
                        weights: Optional[List[float]] = None,
                        batch_size: int = 32) -> np.ndarray:
        """
        Predict using Test-Time Augmentation
        """
        if weights is None:
            weights = [1.0 / len(tta_transforms)] * len(tta_transforms)
        
        all_predictions = []
        
        with torch.no_grad():
            for idx in range(len(test_dataset)):
                if idx % 500 == 0:
                    print(f"Processing image {idx}/{len(test_dataset)}")
                
                image, _ = test_dataset[idx]
                
                # Convert PIL to numpy if needed
                if hasattr(image, 'mode'):
                    image = np.array(image)
                
                tta_preds = []
                
                # Apply each TTA transform
                for transform in tta_transforms:
                    augmented = transform(image=image)
                    img_tensor = augmented['image'].unsqueeze(0).to(self.device)
                    
                    output = self.model(img_tensor)
                    prob = torch.softmax(output, dim=1)
                    tta_preds.append(prob.cpu().numpy())
                
                # Weighted average of predictions
                weighted_pred = np.average(tta_preds, axis=0, weights=weights)
                final_pred = np.argmax(weighted_pred)
                all_predictions.append(final_pred)
        
        return np.array(all_predictions)


class ModelEvaluator:
    """
    Comprehensive model evaluation tools
    """
    
    @staticmethod
    def evaluate_model(model: nn.Module,
                      test_loader: DataLoader,
                      class_names: List[str],
                      device: str = 'cuda') -> Dict:
        """
        Comprehensive model evaluation
        """
        model.eval()
        all_preds = []
        all_targets = []
        all_probs = []
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                outputs = model(data)
                probs = torch.softmax(outputs, dim=1)
                _, preds = torch.max(outputs, 1)
                
                all_preds.extend(preds.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(all_targets, all_preds)
        
        # Classification report
        report = classification_report(
            all_targets, all_preds, 
            target_names=class_names, 
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(all_targets, all_preds)
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm,
            'predictions': all_preds,
            'targets': all_targets,
            'probabilities': all_probs
        }
    
    @staticmethod
    def create_submission(predictions: np.ndarray,
                         class_names: List[str],
                         filename: str = 'submission.csv'):
        """Create submission file"""
        pred_labels = [class_names[pred] for pred in predictions]
        
        submission_df = pd.DataFrame({
            'ID': range(len(predictions)),
            'Label': pred_labels
        })
        
        submission_df.to_csv(filename, index=False)
        print(f"Submission saved as '{filename}'")
        print(f"Total predictions: {len(predictions)}")
        print(f"Class distribution:")
        print(submission_df['Label'].value_counts())
        
        return submission_df


# Utility functions for optimizer and scheduler creation
def create_optimizer(model: nn.Module,
                    optimizer_name: str = 'adamw',
                    learning_rate: float = 1e-3,
                    weight_decay: float = 1e-4,
                    differential_lr: bool = True) -> optim.Optimizer:
    """
    Create optimizer with differential learning rates
    """
    
    if differential_lr:
        # Separate backbone and classifier parameters
        backbone_params = []
        classifier_params = []
        
        for name, param in model.named_parameters():
            if 'classifier' in name or 'head' in name or 'fc' in name:
                classifier_params.append(param)
            else:
                backbone_params.append(param)
        
        param_groups = [
            {'params': backbone_params, 'lr': learning_rate * 0.1, 'weight_decay': weight_decay},
            {'params': classifier_params, 'lr': learning_rate, 'weight_decay': weight_decay * 10}
        ]
    else:
        param_groups = model.parameters()
    
    if optimizer_name.lower() == 'adamw':
        return optim.AdamW(param_groups, lr=learning_rate, weight_decay=weight_decay, eps=1e-8)
    elif optimizer_name.lower() == 'adam':
        return optim.Adam(param_groups, lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_name.lower() == 'sgd':
        return optim.SGD(param_groups, lr=learning_rate, weight_decay=weight_decay, momentum=0.9)
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")


def create_scheduler(optimizer: optim.Optimizer,
                    scheduler_name: str = 'cosine',
                    total_steps: int = None,
                    warmup_steps: int = None,
                    **kwargs) -> optim.lr_scheduler._LRScheduler:
    """
    Create learning rate scheduler
    """
    
    if scheduler_name.lower() == 'cosine':
        if total_steps is None:
            raise ValueError("total_steps required for cosine scheduler")
        
        def lr_lambda(current_step):
            if warmup_steps and current_step < warmup_steps:
                return float(current_step) / float(max(1, warmup_steps))
            progress = float(current_step - (warmup_steps or 0)) / float(max(1, total_steps - (warmup_steps or 0)))
            return max(0.0, 0.5 * (1.0 + math.cos(math.pi * progress)))
        
        return optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
        
    elif scheduler_name.lower() == 'step':
        step_size = kwargs.get('step_size', 10)
        gamma = kwargs.get('gamma', 0.1)
        return optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
        
    elif scheduler_name.lower() == 'plateau':
        return optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5)
        
    else:
        raise ValueError(f"Unknown scheduler: {scheduler_name}")


# Training configuration presets
TRAINING_PRESETS = {
    'lightweight': {
        'optimizer': 'adamw',
        'learning_rate': 3e-4,
        'weight_decay': 1e-4,
        'scheduler': 'cosine',
        'epochs': 20,
        'batch_size': 64,
        'mixed_precision': True
    },
    'standard': {
        'optimizer': 'adamw',
        'learning_rate': 1e-3,
        'weight_decay': 1e-4,
        'scheduler': 'cosine',
        'epochs': 30,
        'batch_size': 32,
        'mixed_precision': True
    },
    'competition': {
        'optimizer': 'adamw',
        'learning_rate': 8e-4,
        'weight_decay': 1e-3,
        'scheduler': 'cosine',
        'epochs': 40,
        'batch_size': 32,
        'mixed_precision': True,
        'differential_lr': True,
        'gradient_clip_norm': 0.8
    }
}