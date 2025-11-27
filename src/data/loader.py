"""
Chargement et validation des données
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Classe pour charger et valider les données de culture"""
    
    REQUIRED_COLUMNS = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
    
    def __init__(self, data_path: str = "data/Crop_recommendation.csv"):
        """
        Initialise le chargeur de données
        
        Args:
            data_path: Chemin vers le fichier CSV
        """
        self.data_path = Path(data_path)
        self.data = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Charge les données depuis le fichier CSV
        
        Returns:
            DataFrame avec les données
        """
        try:
            logger.info(f"Chargement des données depuis {self.data_path}")
            self.data = pd.read_csv(self.data_path)
            self._validate_data()
            logger.info(f"Données chargées avec succès: {self.data.shape}")
            return self.data
        except FileNotFoundError:
            logger.error(f"Fichier non trouvé: {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {str(e)}")
            raise
    
    def _validate_data(self):
        """Valide la structure des données"""
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.data.columns)
        if missing_cols:
            raise ValueError(f"Colonnes manquantes: {missing_cols}")
        
        # Vérifier les valeurs manquantes
        null_counts = self.data.isnull().sum()
        if null_counts.any():
            logger.warning(f"Valeurs manquantes détectées:\n{null_counts[null_counts > 0]}")
        
        # Vérifier les doublons
        duplicates = self.data.duplicated().sum()
        if duplicates > 0:
            logger.warning(f"{duplicates} doublons détectés")
    
    def get_feature_names(self) -> list:
        """Retourne les noms des features"""
        return [col for col in self.REQUIRED_COLUMNS if col != 'label']
    
    def get_stats(self) -> dict:
        """Retourne des statistiques sur les données"""
        if self.data is None:
            self.load_data()
        
        return {
            'n_samples': len(self.data),
            'n_features': len(self.get_feature_names()),
            'n_classes': self.data['label'].nunique(),
            'classes': sorted(self.data['label'].unique().tolist()),
            'class_distribution': self.data['label'].value_counts().to_dict()
        }
