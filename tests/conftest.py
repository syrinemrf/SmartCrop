"""
Configuration pytest
"""
import sys
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))
