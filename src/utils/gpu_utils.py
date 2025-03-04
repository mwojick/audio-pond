"""GPU utilities for Audio Pond."""

import logging
import torch


def check_gpu():
    """Configure and verify GPU setup."""
    try:
        num_gpus = torch.cuda.device_count()
        if not num_gpus:
            logging.warning("No GPU devices found. For now, falling back to CPU.")
            return False

        logging.info(f"GPU setup successful. Found {num_gpus} GPU(s)")
        return True
    except Exception as e:
        logging.warning(f"Failed to configure GPU: {str(e)}")
        return False
