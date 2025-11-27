#!/usr/bin/env python
"""
🌾 CROP RECOMMENDATION SYSTEM - SETUP RAPIDE
===========================================

Ce script configure automatiquement votre environnement.
"""
import os
import sys
import subprocess
from pathlib import Path
import platform


def print_banner():
    """Affiche le banner"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🌾  CROP RECOMMENDATION SYSTEM - SETUP WIZARD  🌾      ║
║                                                           ║
║   Configuration automatique de votre environnement       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def check_python():
    """Vérifie la version Python"""
    print("🔍 Vérification Python...")
    version = sys.version_info
    
    if version < (3, 8):
        print(f"❌ Python 3.8+ requis (vous avez {version.major}.{version.minor})")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")
    return True


def check_pip():
    """Vérifie pip"""
    print("\n🔍 Vérification pip...")
    try:
        import pip
        print(f"✅ pip disponible")
        return True
    except ImportError:
        print("❌ pip non installé")
        return False


def create_venv():
    """Crée l'environnement virtuel"""
    print("\n📦 Création de l'environnement virtuel...")
    
    if Path("venv").exists():
        print("⚠️  Environnement virtuel existe déjà")
        response = input("Recréer? (y/N): ")
        if response.lower() != 'y':
            return True
        
        import shutil
        shutil.rmtree("venv")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Environnement virtuel créé")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def install_dependencies():
    """Installe les dépendances"""
    print("\n📚 Installation des dépendances...")
    
    # Déterminer le chemin python
    if platform.system() == "Windows":
        python_path = Path("venv/Scripts/python.exe")
    else:
        python_path = Path("venv/bin/python")
    
    try:
        # Upgrade pip
        print("  ⬆️  Mise à jour pip...")
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True, text=True)
        
        # Install setuptools and wheel first
        print("  🔧 Installation setuptools et wheel...")
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "setuptools", "wheel"],
                      check=True, capture_output=True, text=True)
        
        # Install requirements
        print("  📥 Installation packages (cela peut prendre quelques minutes)...")
        subprocess.run([str(python_path), "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True, capture_output=True, text=True)
        
        print("✅ Dépendances installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        if e.stderr:
            print(f"   Détails: {e.stderr}")
        return False


def create_directories():
    """Crée les répertoires nécessaires"""
    print("\n📁 Création des répertoires...")
    
    dirs = [
        "data",
        "models/tuned",
        "logs",
        "results/metrics",
        "results/tuning",
        "results/visualizations"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Répertoires créés")
    return True


def init_database():
    """Initialise la base de données"""
    print("\n🗄️  Initialisation de la base de données...")
    
    # Déterminer le chemin python
    if platform.system() == "Windows":
        python_path = Path("venv/Scripts/python.exe")
    else:
        python_path = Path("venv/bin/python")
    
    try:
        code = """
from app.app import app, db
with app.app_context():
    db.create_all()
    print('Base de données initialisée')
"""
        subprocess.run([str(python_path), "-c", code], check=True, capture_output=True, text=True)
        print("✅ Base de données initialisée")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        if e.stderr:
            print(f"   Détails: {e.stderr}")
        print("   Vous pourrez l'initialiser plus tard avec:")
        print('   python -c "from app.app import app, db; app.app_context().push(); db.create_all()"')
        return False


def check_model_files():
    """Vérifie la présence des fichiers modèles"""
    print("\n🤖 Vérification des fichiers modèles...")
    
    required_files = [
        "models/tuned/naive_bayes_best.pkl",
        "models/scaler.pkl",
        "models/label_encoder.pkl"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"⚠️  Fichiers modèles manquants:")
        for f in missing:
            print(f"   - {f}")
        print("\n   Pour entraîner le modèle:")
        print("   python scripts/train_model.py")
        return False
    
    print("✅ Fichiers modèles présents")
    return True


def print_next_steps():
    """Affiche les prochaines étapes"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✅  CONFIGURATION TERMINÉE AVEC SUCCÈS !  ✅           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🎯 PROCHAINES ÉTAPES:

1️⃣  Activer l'environnement virtuel:
   Windows PowerShell:  venv\\Scripts\\activate
   Linux/Mac:           source venv/bin/activate

2️⃣  Lancer l'application:
   python app/app.py

3️⃣  Ouvrir dans votre navigateur:
   http://localhost:5000

📚 DOCUMENTATION:
   - README.md  : Vue d'ensemble
   - GUIDE.md   : Guide détaillé
   - Notebooks  : Recherche ML

🔧 COMMANDES UTILES:
   - Prédiction CLI: python scripts/predict_cli.py --help
   - Entraînement:   python scripts/train_model.py
   - Tests:          pytest tests/
   - Docker:         docker-compose up -d

💡 BESOIN D'AIDE?
   Consultez le GUIDE.md ou ouvrez une issue sur GitHub.

🌟 Bon développement ! 🌟
    """)


def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifications
    if not check_python():
        sys.exit(1)
    
    if not check_pip():
        print("\n💡 Installez pip: https://pip.pypa.io/en/stable/installation/")
        sys.exit(1)
    
    # Changement de répertoire
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"\n📂 Répertoire de travail: {os.getcwd()}")
    
    # Setup
    steps = [
        ("Environnement virtuel", create_venv),
        ("Dépendances", install_dependencies),
        ("Répertoires", create_directories),
        ("Base de données", init_database),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Échec à l'étape: {step_name}")
            print("Veuillez corriger l'erreur et relancer le setup.")
            sys.exit(1)
    
    # Vérifications finales
    check_model_files()
    
    # Succès
    print_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        sys.exit(1)
