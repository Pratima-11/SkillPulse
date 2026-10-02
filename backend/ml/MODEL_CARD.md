# SkillPulse Reliability Model Card

## Purpose
Estimate the probability that a worker meets a synthetic reliability label used by the matching engine.

## Training data
`ml/data/reliability_training.csv` contains 1,800 generated worker-history scenarios. It is synthetic development data, not real SkillPulse user data.

## Features
- jobs_completed
- jobs_accepted
- jobs_cancelled
- average_rating
- experience_years

## Model
A reproducible logistic-regression classifier trained by `ml/training/train_model.py`. Inputs are standardized using training-set statistics. The saved model is `ml/models/reliability_model.pkl`.

## Evaluation
The generated `ml/models/metrics.json` contains test-set accuracy, precision, recall, F1 and confusion-matrix counts. Metrics describe only this synthetic dataset and must not be presented as production performance.

## Integration
`services/matching_service.py` calls `ml.predict.predict_reliability()`. If the model is unavailable, the application falls back to the transparent rule-based reliability calculation.
