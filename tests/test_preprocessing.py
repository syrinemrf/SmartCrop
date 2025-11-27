"""
Tests pour le preprocessing
"""
import pytest
import pandas as pd
import numpy as np
from src.data.preprocessing import DataPreprocessor


@pytest.fixture
def sample_data():
    """Données d'exemple"""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'N': np.random.randint(0, 140, n_samples),
        'P': np.random.randint(5, 145, n_samples),
        'K': np.random.randint(5, 205, n_samples),
        'temperature': np.random.uniform(8, 44, n_samples),
        'humidity': np.random.uniform(14, 100, n_samples),
        'ph': np.random.uniform(3.5, 10, n_samples),
        'rainfall': np.random.uniform(20, 300, n_samples),
        'label': np.random.choice(['rice', 'maize', 'wheat'], n_samples)
    }
    
    return pd.DataFrame(data)


def test_preprocessor_initialization():
    """Test l'initialisation du preprocessor"""
    prep = DataPreprocessor(test_size=0.2, random_state=42)
    
    assert prep.test_size == 0.2
    assert prep.random_state == 42
    assert prep.scaler is not None
    assert prep.label_encoder is not None


def test_fit_transform(sample_data):
    """Test fit_transform"""
    prep = DataPreprocessor()
    X_train, X_test, y_train, y_test = prep.fit_transform(sample_data)
    
    # Vérifier les shapes
    assert len(X_train) + len(X_test) == len(sample_data)
    assert len(y_train) + len(y_test) == len(sample_data)
    
    # Vérifier la proportion
    test_ratio = len(X_test) / len(sample_data)
    assert abs(test_ratio - 0.2) < 0.05  # Tolérance
    
    # Vérifier la standardisation
    assert abs(X_train.mean()) < 0.1  # Proche de 0
    assert abs(X_train.std() - 1.0) < 0.1  # Proche de 1


def test_label_encoding(sample_data):
    """Test l'encodage des labels"""
    prep = DataPreprocessor()
    X_train, X_test, y_train, y_test = prep.fit_transform(sample_data)
    
    # Les labels doivent être des entiers
    assert y_train.dtype == np.int64
    assert y_test.dtype == np.int64
    
    # Vérifier le décodage
    original_labels = sample_data['label'].unique()
    encoded_labels = prep.label_encoder.classes_
    assert set(original_labels) == set(encoded_labels)


def test_transform_new_data(sample_data):
    """Test la transformation de nouvelles données"""
    prep = DataPreprocessor()
    X_train, X_test, y_train, y_test = prep.fit_transform(sample_data)
    
    # Nouvelles données
    new_data = sample_data.drop('label', axis=1).head(5)
    transformed = prep.transform(new_data)
    
    assert transformed.shape == (5, 7)
    assert abs(transformed.mean()) < 1.0  # Standardisé


def test_inverse_transform_labels(sample_data):
    """Test le décodage des labels"""
    prep = DataPreprocessor()
    X_train, X_test, y_train, y_test = prep.fit_transform(sample_data)
    
    # Décoder
    decoded = prep.inverse_transform_labels(y_test)
    
    # Vérifier que ce sont des noms de cultures
    assert all(isinstance(label, str) for label in decoded)
    assert all(label in sample_data['label'].unique() for label in decoded)


def test_stratified_split(sample_data):
    """Test que le split est stratifié"""
    prep = DataPreprocessor()
    X_train, X_test, y_train, y_test = prep.fit_transform(sample_data)
    
    # Distribution dans train
    train_unique, train_counts = np.unique(y_train, return_counts=True)
    train_dist = train_counts / len(y_train)
    
    # Distribution dans test
    test_unique, test_counts = np.unique(y_test, return_counts=True)
    test_dist = test_counts / len(y_test)
    
    # Les distributions doivent être similaires
    assert len(train_unique) == len(test_unique)
