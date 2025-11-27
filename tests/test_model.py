"""
Tests pour le module de prédiction
"""
import pytest
import numpy as np
import pandas as pd
from src.models.predictor import CropPredictor


@pytest.fixture
def predictor():
    """Fixture pour le prédicteur"""
    pred = CropPredictor()
    pred.load_model()
    return pred


@pytest.fixture
def sample_features():
    """Features d'exemple"""
    return [90, 42, 43, 20.8, 82, 6.5, 202.9]


def test_predictor_initialization():
    """Test l'initialisation du prédicteur"""
    pred = CropPredictor()
    assert pred.model is None
    assert pred.scaler is None
    assert pred.label_encoder is None
    assert len(pred.feature_names) == 7


def test_model_loading(predictor):
    """Test le chargement du modèle"""
    assert predictor.model is not None
    assert predictor.scaler is not None
    assert predictor.label_encoder is not None


def test_prediction_with_list(predictor, sample_features):
    """Test prédiction avec une liste"""
    result = predictor.predict(sample_features)
    
    assert 'crop' in result
    assert 'confidence' in result
    assert 'top_3' in result
    assert 0 <= result['confidence'] <= 1
    assert len(result['top_3']) == 3


def test_prediction_with_array(predictor, sample_features):
    """Test prédiction avec un array"""
    features_array = np.array(sample_features)
    result = predictor.predict(features_array)
    
    assert 'crop' in result
    assert isinstance(result['crop'], str)


def test_prediction_with_dataframe(predictor, sample_features):
    """Test prédiction avec un DataFrame"""
    df = pd.DataFrame([sample_features], 
                     columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    result = predictor.predict(df)
    
    assert 'crop' in result
    assert result['confidence'] > 0


def test_prediction_invalid_features(predictor):
    """Test prédiction avec mauvais nombre de features"""
    invalid_features = [90, 42, 43]  # Seulement 3 au lieu de 7
    
    with pytest.raises(ValueError):
        predictor.predict(invalid_features)


def test_top_3_predictions(predictor, sample_features):
    """Test que top_3 est trié par probabilité"""
    result = predictor.predict(sample_features)
    top_3 = result['top_3']
    
    # Vérifier que c'est trié décroissant
    for i in range(len(top_3) - 1):
        assert top_3[i]['probability'] >= top_3[i+1]['probability']


def test_prediction_consistency(predictor, sample_features):
    """Test la consistance des prédictions"""
    result1 = predictor.predict(sample_features)
    result2 = predictor.predict(sample_features)
    
    # Les prédictions doivent être identiques
    assert result1['crop'] == result2['crop']
    assert abs(result1['confidence'] - result2['confidence']) < 1e-10


def test_all_probabilities_sum(predictor, sample_features):
    """Test que les probabilités somment à 1"""
    result = predictor.predict(sample_features)
    total_prob = sum(result['all_probabilities'].values())
    
    assert abs(total_prob - 1.0) < 1e-5  # Tolérance pour erreurs float


def test_batch_prediction(predictor):
    """Test prédictions par batch"""
    data = pd.DataFrame([
        [90, 42, 43, 20.8, 82, 6.5, 202.9],
        [20, 10, 15, 25.5, 70, 5.8, 150.0]
    ], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    results = predictor.predict_batch(data)
    
    assert len(results) == 2
    assert all('crop' in r for r in results)
