from pathlib import Path
from clio_api_model_generator import clio_manage

def update_models():
    client_dir = Path(__file__).resolve().parent
    models_dir = client_dir / "models"

    # This already generates and exports to models_dir
    clio_manage.generate_models(output_dir=models_dir, overwrite=False)

if __name__ == "__main__":
    update_models()
