"""
ML Trainer Library

Exposes:
- UnifiedTrainer: Single entry point for training models by task
"""

from .auto_trainer import AutoTrainer

__all__ = ["AutoTrainer"]
