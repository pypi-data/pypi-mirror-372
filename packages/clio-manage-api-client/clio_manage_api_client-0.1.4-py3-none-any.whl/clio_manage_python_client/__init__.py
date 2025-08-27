from pathlib import Path

pkg_dir = Path(__file__).resolve().parent
models_dir = pkg_dir / "models"

if not models_dir.exists():
    from clio_api_model_generator import clio_manage
    print("'models/' directory not found. Generating models...")
    clio_manage.generate_models(output_dir=models_dir, overwrite=False)

from .client import Client as Manage
from . import utils
Manage.utils = utils

__all__ = ["Manage"]
