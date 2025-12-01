"""
Système de prédiction pour les cultures
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Union
from lime.lime_tabular import LimeTabularExplainer

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
        self.lime_explainer = None
        self.training_data = None
        
    def load_model(self):
        """Charge le modèle et les preprocesseurs"""
        try:
            logger.info(f"Chargement du modèle depuis {self.model_path}")
            self.model = joblib.load(self.model_path)
            
            model_dir = self.model_path.parent.parent
            self.scaler = joblib.load(model_dir / "scaler.pkl")
            self.label_encoder = joblib.load(model_dir / "label_encoder.pkl")
            
            # Charger les données d'entraînement pour LIME
            try:
                self.training_data = np.load(model_dir / "X_train_scaled.npy")
            except:
                # Fallback: charger depuis data/
                self.training_data = np.load("data/X_train_scaled.npy")
            
            # Initialiser LIME explainer
            self._init_lime_explainer()
            
            logger.info("Modèle chargé avec succès")
        except FileNotFoundError as e:
            logger.error(f"Fichier non trouvé: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            raise
    
    def _init_lime_explainer(self):
        """Initialise l'explainer LIME"""
        if self.training_data is not None:
            self.lime_explainer = LimeTabularExplainer(
                training_data=self.training_data,
                feature_names=self.feature_names,
                class_names=list(self.label_encoder.classes_),
                mode='classification',
                discretize_continuous=True
            )
            logger.info("LIME explainer initialisé")
    
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
    
    def explain_prediction(self, features: Union[List, np.ndarray], num_features: int = 7) -> Dict:
        """
        Explique une prédiction avec LIME
        
        Args:
            features: Les features de l'échantillon à expliquer
            num_features: Nombre de features à inclure dans l'explication
        
        Returns:
            Dictionnaire avec l'explication LIME
        """
        if self.model is None:
            self.load_model()
        
        if self.lime_explainer is None:
            logger.warning("LIME explainer non disponible")
            return {'error': 'Explainer not available'}
        
        # Convertir en array si nécessaire
        if isinstance(features, list):
            features = np.array(features)
        
        # Standardiser les features
        features_scaled = self.scaler.transform(features.reshape(1, -1))[0]
        
        # Fonction de prédiction pour LIME (sur données scalées)
        def predict_fn(X):
            return self.model.predict_proba(X)
        
        try:
            # Générer l'explication
            explanation = self.lime_explainer.explain_instance(
                features_scaled,
                predict_fn,
                num_features=num_features,
                top_labels=1
            )
            
            # Récupérer la classe prédite
            predicted_label = self.model.predict(features_scaled.reshape(1, -1))[0]
            
            # Extraire les contributions des features
            exp_list = explanation.as_list(label=predicted_label)
            
            # Formater les résultats
            feature_contributions = []
            for feature_desc, weight in exp_list:
                # Extraire le nom de la feature depuis la description LIME
                feature_name = feature_desc
                for fn in self.feature_names:
                    if fn in feature_desc:
                        feature_name = fn
                        break
                
                feature_contributions.append({
                    'feature': feature_name,
                    'description': feature_desc,
                    'weight': float(weight),
                    'impact': 'positive' if weight > 0 else 'negative'
                })
            
            # Trier par importance absolue
            feature_contributions.sort(key=lambda x: abs(x['weight']), reverse=True)
            
            return {
                'contributions': feature_contributions,
                'predicted_class': self.label_encoder.inverse_transform([predicted_label])[0],
                'intercept': float(explanation.intercept[predicted_label]) if hasattr(explanation, 'intercept') else 0
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'explication LIME: {e}")
            return {'error': str(e)}
