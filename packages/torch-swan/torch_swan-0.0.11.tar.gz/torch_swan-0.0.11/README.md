<file name=README.md># SWAN: Switchable Activation Networks

## Overview
<img src="https://raw.githubusercontent.com/ainilaha/swan/HEAD/logo.png" alt="SWAN logo" width="300"/>

Swan is fun
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

```</file>

<file name=pyproject.toml>[tool.hatch.build.targets.wheel]
packages = ["src/torch_swan"]
include = ["logo.png"]

[tool.hatch.build.targets.sdist]
include = [
  "src/torch_swan",
  "README.md",
  "LICENSE",
  
]
</file>