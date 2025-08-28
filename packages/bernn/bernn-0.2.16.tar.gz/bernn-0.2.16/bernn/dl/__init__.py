"""Deep Learning modules for BERNN.

This subpackage contains the deep learning models and training code.
"""

# Model definitions
from .models.pytorch import (
    AutoEncoder2,
    SHAPAutoEncoder2,
    KANAutoEncoder2,
    SHAPKANAutoEncoder2,
    AutoEncoder3,
    SHAPAutoEncoder3,
)

# Training modules
from .train import (
    TrainAE,
    TrainAEClassifierHoldout,
    TrainAEThenClassifierHoldout,
)

# KAN modules
from .models.pytorch.ekan import KANLinear, KAN

__all__ = [
    # Models
    "AutoEncoder2",
    "SHAPAutoEncoder2",
    "KANAutoEncoder2",
    "SHAPKANAutoEncoder2",
    "AutoEncoder3",
    "SHAPAutoEncoder3",
    "KANAutoEncoder3",
    "SHAPKANAutoEncoder3",

    # Training
    "TrainAE",
    "TrainAEClassifierHoldout",
    "TrainAEThenClassifierHoldout",

    # KAN
    "KANLinear",
    "KAN"
]
