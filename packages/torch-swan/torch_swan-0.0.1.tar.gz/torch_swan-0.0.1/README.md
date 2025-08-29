# SWAN: Switchable Activation Networks

## Overview
<img src="logo.png" alt="drawing" width="300"/>

SWAN (Switchable Activation Networks) is a Python-based framework for training and optimizing neural networks with switchable activation units. It provides tools for pruning and exporting dense models, as well as benchmarking latency for efficient deployment.

## Features
- **Trainable Switchable Activation Units**: Dynamically adjust activation units during training for optimal performance.
- **Model Pruning**: Export pruned dense models based on gate probabilities to reduce model size and complexity.
- **Latency Measurement**: Benchmark model inference latency for deployment on various devices.
- **MNIST Example**: Includes a minimal example for training on the MNIST dataset.

## Requirements
- Python 3.8+
- PyTorch
- Torchvision
- NumPy

## Installation
Clone the repository and install the required dependencies:
```bash
git clone <repository-url>
cd SWAN

python -m pip uninstall -y torch-swan torch_swan
python -m pip install -e .
```

Or install via pip:
```bash
pip install torch_swan
```

```Python
import torch_swan as swan


```


Examples
```bash
python main.py mnist --device mps --epochs 5

nohup python main.py vgg16 --epochs 50 --device npu  --threshold 0.6 --resize 224 --batch_size 200  > train.log 2>&1 &

nohup python main.py vgg16 --epochs 50 --device gpu  --threshold 0.6 --resize 224 --batch_size 256 --pretrained False > train.log 2>&1 &

```