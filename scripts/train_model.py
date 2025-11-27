#!/usr/bin/env python
"""
Script pour entraîner le modèle
"""
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loader import DataLoader
from src.data.preprocessing import DataPreprocessor
from src.utils.logger import setup_logger
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score, StratifiedKFold
import joblib
import json

logger = setup_logger('Training')


def train_model(data_path: str = "data/Crop_recommendation.csv",
                model_path: str = "models/tuned/naive_bayes_best.pkl",
                cv_folds: int = 10):
    """
    Entraîne le modèle Naive Bayes
    
    Args:
        data_path: Chemin vers les données
        model_path: Chemin de sauvegarde du modèle
        cv_folds: Nombre de folds pour la validation croisée
    """
    logger.info("="*60)
    logger.info("ENTRAÎNEMENT DU MODÈLE")
    logger.info("="*60)
    
    # Charger les données
    logger.info(f"Chargement des données depuis {data_path}")
    loader = DataLoader(data_path)
    df = loader.load_data()
    
    # Preprocessing
    logger.info("Preprocessing des données...")
    preprocessor = DataPreprocessor(test_size=0.2, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.fit_transform(df)
    
    # Entraînement
    logger.info("Entraînement du modèle Naive Bayes...")
    model = GaussianNB()
    model.fit(X_train, y_train)
    
    # Validation croisée
    logger.info(f"Validation croisée ({cv_folds}-fold)...")
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
    
    # Évaluation
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    # Résultats
    logger.info("\n" + "="*60)
    logger.info("RÉSULTATS")
    logger.info("="*60)
    logger.info(f"Train Accuracy:    {train_score:.4f}")
    logger.info(f"Test Accuracy:     {test_score:.4f}")
    logger.info(f"CV Score (mean):   {cv_scores.mean():.4f}")
    logger.info(f"CV Score (std):    {cv_scores.std():.4f}")
    
    # Sauvegarde
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\nSauvegarde du modèle: {model_path}")
    joblib.dump(model, model_path)
    
    logger.info("Sauvegarde du preprocessor...")
    preprocessor.save("models")
    
    # Sauvegarder les métriques
    metrics = {
        'model_name': 'Naive Bayes',
        'train_score': float(train_score),
        'test_score': float(test_score),
        'cv_score': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std())
    }
    
    metrics_path = Path("results/tuning/best_model_info.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"Métriques sauvegardées: {metrics_path}")
    logger.info("\n✅ Entraînement terminé avec succès!")
    
    return model, preprocessor


def main():
    parser = argparse.ArgumentParser(description='Entraîner le modèle de recommandation')
    parser.add_argument('--data', type=str, default='data/Crop_recommendation.csv',
                       help='Chemin vers les données')
    parser.add_argument('--model', type=str, default='models/tuned/naive_bayes_best.pkl',
                       help='Chemin de sauvegarde du modèle')
    parser.add_argument('--cv-folds', type=int, default=10,
                       help='Nombre de folds pour CV')
    
    args = parser.parse_args()
    
    try:
        train_model(args.data, args.model, args.cv_folds)
        return 0
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
