"""
Système de prédiction pour les cultures
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Union

logger = logging.getLogger(__name__)


class CropPredictor:
    """Classe pour effectuer des prédictions de cultures"""
    
    def __init__(self, model_path: str = "models/tuned/naive_bayes_best.pkl"):
        """
        Initialise le prédicteur
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
        """
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
    def load_model(self):
        """Charge le modèle et les preprocesseurs"""
        try:
            logger.info(f"Chargement du modèle depuis {self.model_path}")
            self.model = joblib.load(self.model_path)
            
            model_dir = self.model_path.parent.parent
            self.scaler = joblib.load(model_dir / "scaler.pkl")
            self.label_encoder = joblib.load(model_dir / "label_encoder.pkl")
            
            logger.info("Modèle chargé avec succès")
        except FileNotFoundError as e:
            logger.error(f"Fichier non trouvé: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            raise
    
    def predict(self, features: Union[List, np.ndarray, pd.DataFrame]) -> Dict:
        """
        Effectue une prédiction
        
        Args:
            features: Features pour la prédiction
                     Format: [N, P, K, temperature, humidity, ph, rainfall]
                     ou DataFrame avec les colonnes appropriées
        
        Returns:
            Dictionnaire avec la prédiction et les probabilités
        """
        if self.model is None:
            self.load_model()
        
        # Convertir en array si nécessaire
        if isinstance(features, list):
            features = np.array(features).reshape(1, -1)
        elif isinstance(features, pd.DataFrame):
            features = features[self.feature_names].values
        elif isinstance(features, np.ndarray) and features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Validation
        if features.shape[1] != len(self.feature_names):
            raise ValueError(f"Attendu {len(self.feature_names)} features, reçu {features.shape[1]}")
        
        # Standardisation
        features_scaled = self.scaler.transform(features)
        
        # Prédiction
        prediction = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        # Résultats
        crop = self.label_encoder.inverse_transform(prediction)[0]
        confidence = float(probabilities.max())
        
        # Top 3 prédictions
        top_3_indices = probabilities[0].argsort()[-3:][::-1]
        top_3 = [
            {
                'crop': self.label_encoder.inverse_transform([idx])[0],
                'probability': float(probabilities[0][idx])
            }
            for idx in top_3_indices
        ]
        
        return {
            'crop': crop,
            'confidence': confidence,
            'top_3': top_3,
            'all_probabilities': {
                self.label_encoder.inverse_transform([i])[0]: float(probabilities[0][i])
                for i in range(len(probabilities[0]))
            }
        }
    
    def predict_batch(self, features_df: pd.DataFrame) -> List[Dict]:
        """
        Prédictions par batch
        
        Args:
            features_df: DataFrame avec plusieurs échantillons
            
        Returns:
            Liste de dictionnaires avec les prédictions
        """
        if self.model is None:
            self.load_model()
        
        results = []
        for idx, row in features_df.iterrows():
            try:
                result = self.predict(row.values)
                result['index'] = idx
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur pour l'échantillon {idx}: {e}")
                results.append({'index': idx, 'error': str(e)})
        
        return results
    
    def get_feature_importance(self) -> Dict:
        """Retourne l'importance des features si disponible"""
        if self.model is None:
            self.load_model()
        
        # Naive Bayes n'a pas de feature_importances_ mais on peut utiliser les variances
        if hasattr(self.model, 'var_'):
            importances = np.mean(self.model.var_, axis=0)
            return {
                name: float(imp) 
                for name, imp in zip(self.feature_names, importances)
            }
        return {}
