import os
import joblib


def load_model(model_name: str):
    dir_name = os.path.dirname(__file__)
    all_model_files = [f for f in os.listdir(dir_name) if f.endswith(".model")]
    model_names = [f.split(".")[0] for f in all_model_files]
    if model_name not in model_names:
        raise ValueError(f"Model {model_name} not found in {dir_name}")

    model_file = f"{model_name}.model"
    model = joblib.load(os.path.join(dir_name, model_file))
    return model
