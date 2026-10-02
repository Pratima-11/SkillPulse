"""Load and serve the trained SkillPulse reliability model."""
import math, os, pickle
from app.config import Config
_model = None

def _sigmoid(z):
    z=max(-30.0,min(30.0,z)); return 1.0/(1.0+math.exp(-z))

def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(Config.ML_MODEL_PATH):
            raise FileNotFoundError("Reliability model not found. Run ml/training/train_model.py.")
        with open(Config.ML_MODEL_PATH,"rb") as f: _model=pickle.load(f)
    return _model

def predict_reliability(features: dict) -> float:
    model=_load_model(); values=[float(features[name]) for name in model["features"]]
    z=0.0
    for value,mean,std,weight in zip(values,model["means"],model["stds"],model["weights"]):
        z += ((value-mean)/(std or 1.0))*weight
    return max(0.0,min(1.0,_sigmoid(z)))
