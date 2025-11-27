"""
Configuration du logging
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "CropRecommendation",
    log_dir: str = "logs",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure et retourne un logger
    
    Args:
        name: Nom du logger
        log_dir: Répertoire pour les logs
        level: Niveau de logging
    
    Returns:
        Logger configuré
    """
    # Créer le répertoire de logs
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Éviter les handlers dupliqués
    if logger.handlers:
        return logger
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier
    log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
