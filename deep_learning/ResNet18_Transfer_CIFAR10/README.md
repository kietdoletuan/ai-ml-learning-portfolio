# ResNet18 Transfer Learning — 5-Class CIFAR-10

## What It Does
Uses a pretrained ResNet18 (ImageNet) as a frozen feature extractor. Only the final FC layer was retrained on 5 CIFAR-10 classes (airplane, automobile, bird, cat, deer).

## How It Was Built
All layers frozen via `requires_grad=False`. FC layer replaced with `nn.Linear(512, 5)`. Images resized to 224×224 and normalized with ImageNet mean/std. Trained 5 epochs with Adam, CrossEntropyLoss, MLFlow logging.

## Result
87.12% val accuracy in 5 epochs with only the FC layer training. No overfitting observed.

## What I Learned
Transfer learning works because ImageNet features (edges, textures, shapes) generalize across vision tasks. Freezing the backbone is feature extraction — unfreezing it is fine-tuning, which would push accuracy higher but requires more careful learning rate tuning to avoid destroying pretrained weights.