"""
Preprocessing et transformation des données
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Classe pour le preprocessing des données"""
    
    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        """
        Initialise le preprocesseur
        
        Args:
            test_size: Proportion du test set
            random_state: Seed pour la reproductibilité
        """
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        
    def fit_transform(self, df: pd.DataFrame, target_col: str = 'label'):
        """
        Prépare les données d'entraînement
        
        Args:
            df: DataFrame avec les données
            target_col: Nom de la colonne cible
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        logger.info("Séparation features/target")
        X = df.drop(target_col, axis=1)
        y = df[target_col]
        
        self.feature_names = X.columns.tolist()
        
        # Encodage du target
        logger.info("Encodage des labels")
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split train/test
        logger.info(f"Split train/test ({(1-self.test_size)*100:.0f}/{self.test_size*100:.0f})")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y_encoded
        )
        
        # Standardisation
        logger.info("Standardisation des features")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Train shape: {X_train_scaled.shape}, Test shape: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transforme de nouvelles données
        
        Args:
            X: DataFrame avec les features
            
        Returns:
            Array transformé
        """
        return self.scaler.transform(X)
    
    def inverse_transform_labels(self, y_encoded: np.ndarray) -> np.ndarray:
        """Décode les labels"""
        return self.label_encoder.inverse_transform(y_encoded)
    
    def save(self, model_dir: str = "models"):
        """Sauvegarde le scaler et label encoder"""
        model_path = Path(model_dir)
        model_path.mkdir(exist_ok=True)
        
        joblib.dump(self.scaler, model_path / "scaler.pkl")
        joblib.dump(self.label_encoder, model_path / "label_encoder.pkl")
        logger.info(f"Preprocessor sauvegardé dans {model_dir}")
    
    @classmethod
    def load(cls, model_dir: str = "models"):
        """Charge un preprocessor sauvegardé"""
        preprocessor = cls()
        model_path = Path(model_dir)
        
        preprocessor.scaler = joblib.load(model_path / "scaler.pkl")
        preprocessor.label_encoder = joblib.load(model_path / "label_encoder.pkl")
        logger.info(f"Preprocessor chargé depuis {model_dir}")
        
        return preprocessor
