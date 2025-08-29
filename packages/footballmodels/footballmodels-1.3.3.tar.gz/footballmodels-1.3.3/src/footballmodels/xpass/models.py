import joblib
import requests
import pickle


def get_model(league: str, use_positions_as_features: bool):
    URL = "http://www.mclachbot.com/site/models"
    pos_str = "pos" if use_positions_as_features else "nopos"
    model_file = f"xpass_v2_{league.lower()}_{pos_str}.model"
    r = requests.get(f"{URL}/{model_file}")
    if r.status_code != 200:
        raise ValueError(f"Model {model_file} not found")

    return pickle.loads(r.content)
