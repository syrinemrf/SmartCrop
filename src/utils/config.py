"""
Gestion de la configuration
"""
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Classe de configuration centralisée"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Charge la configuration depuis un fichier YAML
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge le fichier YAML"""
        if not self.config_path.exists():
            return self._default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'data': {
                'path': 'data/Crop_recommendation.csv',
                'test_size': 0.2,
                'random_state': 42
            },
            'model': {
                'name': 'Naive Bayes',
                'path': 'models/tuned/naive_bayes_best.pkl'
            },
            'training': {
                'cv_folds': 10,
                'scoring': 'accuracy'
            },
            'app': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'secret_key': 'your-secret-key-change-this'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration
        
        Args:
            key: Clé de configuration (utiliser '.' pour nested, ex: 'data.path')
            default: Valeur par défaut si la clé n'existe pas
        
        Returns:
            Valeur de configuration
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def save(self):
        """Sauvegarde la configuration"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False)
