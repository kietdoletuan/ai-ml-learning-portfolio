# PyTorch CNN — MNIST

## What it does

- Trains a two-block convolutional neural network on the MNIST handwritten digit 
dataset and compares test accuracy against the best MLP baseline (98.29%) from 
the same experiment. The goal is to demonstrate what spatial feature learning 
adds over a fully-connected approach on the same data.

## How it was built

- Model: two convolutional blocks followed by a linear output layer. Each block 
follows Conv2d > BatchNorm2d > ReLU > MaxPool2d. BatchNorm is placed after the 
convolution and before the activation. This is deliberate, normalizing the 
pre-activation distribution stabilizes gradient flow and allows faster convergence.

-Shape trace through the network:
(batch, 1, 28, 28) → Conv2d(1,32,3) → (batch, 32, 26, 26) → MaxPool2d(2) → 
(batch, 32, 13, 13) → Conv2d(32,64,3) → (batch, 64, 11, 11) → MaxPool2d(2) → 
(batch, 64, 5, 5) → Flatten → (batch, 1600) → Linear(1600, 10)

- Tech stack: PyTorch, torchvision, MLFlow (experiment: mnist-mlp, run: cnn-2layers), 
scikit-learn for confusion matrix. Training: Adam lr=0.001, CrossEntropyLoss, 20 epochs.

## The result

- Test accuracy: 99.11% vs MLP baseline 98.29%, a gain of 0.82%.

- Loss converged smoothly with no oscillation, dropping from 0.117 at epoch 0 to 
0.003 by epoch