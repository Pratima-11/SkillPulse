
from unittest.mock import Mock, patch

from services.matching_service import _get_reliability_score


def make_worker():
    return Mock(
        jobs_accepted=20,
        jobs_completed=18,
        jobs_cancelled=1,
        average_rating=4.5,
        experience_years=5,
    )


def test_cold_start_worker_returns_neutral_score():
    worker = Mock(
        jobs_accepted=0,
        jobs_completed=0,
        jobs_cancelled=0,
        average_rating=0,
        experience_years=0,
    )

    score = _get_reliability_score(worker)

    assert score == 0.5


@patch("ml.predict.predict_reliability")
def test_existing_worker_uses_ml_prediction(mock_predict):
    worker = make_worker()
    mock_predict.return_value = 0.85

    score = _get_reliability_score(worker)

    assert score == 0.85
    mock_predict.assert_called_once()


@patch("ml.predict.predict_reliability")
@patch(
    "services.reliability_service.compute_rule_based_reliability"
)
def test_ml_failure_uses_rule_based_fallback(
    mock_rule_based,
    mock_predict,
):
    worker = make_worker()
    mock_predict.side_effect = RuntimeError("Simulated ML failure")
    mock_rule_based.return_value = 0.75

    score = _get_reliability_score(worker)

    assert score == 0.75
    mock_predict.assert_called_once()
    mock_rule_based.assert_called_once_with(worker)
