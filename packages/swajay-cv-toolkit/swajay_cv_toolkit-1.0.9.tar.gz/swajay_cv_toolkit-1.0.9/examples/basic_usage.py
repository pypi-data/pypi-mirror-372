"""
Basic usage example for swajay-cv-toolkit
"""
import torch
from swajay_cv_toolkit import create_model, get_loss_function

def main():
    # Create a model
    model = create_model('timm_efficientnet_b0', num_classes=10)
    print(f"Created model with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Create loss function
    criterion = get_loss_function('mixed')
    print("Created mixed loss function")
    
    # Test forward pass
    x = torch.randn(4, 3, 224, 224)
    y = torch.randint(0, 10, (4,))
    
    output = model(x)
    loss = criterion(output, y)
    
    print(f"Output shape: {output.shape}")
    print(f"Loss value: {loss.item():.4f}")

if __name__ == "__main__":
    main()