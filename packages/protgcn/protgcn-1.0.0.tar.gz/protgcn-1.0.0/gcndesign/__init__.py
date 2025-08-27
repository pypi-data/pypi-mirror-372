"""
ProtGCN: Graph Convolutional Networks for Protein Sequence Design

This package provides state-of-the-art protein sequence prediction from backbone structures
using Graph Convolutional Networks.
"""

__version__ = "1.0.0"
__author__ = "Mahatir Ahmed Tusher, Anik Saha, Md. Shakil Ahmed"
__email__ = "protgcn@example.com"

# Import main classes for easy access
from .predictor import Predictor
from .models import GCNdesign
from .dataset import pdb2input, BBGDataset
from .hypara import HyperParam, InputSource

# Package metadata
__all__ = [
    'Predictor',
    'GCNdesign',
    'pdb2input',
    'BBGDataset',
    'HyperParam',
    'InputSource'
]
