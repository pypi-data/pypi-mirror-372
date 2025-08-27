## Installation

**1. Install PyTorch**

First, you must install PyTorch separately. Please visit the [official PyTorch website](https://pytorch.org/get-started/locally/) and select the correct options for your system (OS, package manager, compute platform like CUDA or CPU).

For example, a common command is:
```bash
pip3 install torch 
```
**2. Optional: Install requirements for speedup**
You may also wish to install accelerate, triton >=3.4 and kernels to speed up inference if using with transformers models to generate. this package mainly relies on transformers for tokenizing, not inference, so these are not direct dependencies.

**3. Install Spaim**
Once PyTorch is installed, you can install `spaim` using pip:
```bash
pip install spaim
```