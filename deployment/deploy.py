#!/usr/bin/env python
"""
Script de déploiement pour SmartCrop
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, check=True):
    """Exécute une commande shell"""
    print(f"Exécution: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0


def check_requirements():
    """Vérifie les prérequis"""
    print("Vérification des prérequis...")
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    
    # Vérifier Docker (optionnel)
    if not run_command("docker --version", check=False):
        print("⚠️  Docker non installé (optionnel pour déploiement local)")
    
    print("✅ Prérequis OK")
    return True


def setup_environment():
    """Configure l'environnement"""
    print("\nConfiguration de l'environnement...")
    
    # Créer l'environnement virtuel
    if not Path("venv").exists():
        print("Création de l'environnement virtuel...")
        run_command(f"{sys.executable} -m venv venv")
    
    # Installer les dépendances
    print("Installation des dépendances...")
    pip_cmd = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    print("✅ Environnement configuré")


def init_database():
    """Initialise la base de données"""
    print("\nInitialisation de la base de données...")
    
    python_cmd = "venv\\Scripts\\python" if os.name == 'nt' else "venv/bin/python"
    
    init_script = """
from app.app import app, db
with app.app_context():
    db.create_all()
    print('✅ Base de données initialisée')
"""
    
    with open("temp_init.py", "w") as f:
        f.write(init_script)
    
    run_command(f"{python_cmd} temp_init.py")
    os.remove("temp_init.py")


def run_tests():
    """Exécute les tests"""
    print("\nExécution des tests...")
    
    python_cmd = "venv\\Scripts\\python" if os.name == 'nt' else "venv/bin/python"
    
    if Path("tests").exists():
        run_command(f"{python_cmd} -m pytest tests/ -v", check=False)
    else:
        print("⚠️  Aucun test trouvé")


def deploy_local():
    """Déploiement local"""
    print("\n🚀 Déploiement local...")
    
    python_cmd = "venv\\Scripts\\python" if os.name == 'nt' else "venv/bin/python"
    
    print("\nDémarrage de l'application...")
    print("📍 Accès: http://localhost:5000")
    print("📍 Pour arrêter: Ctrl+C\n")
    
    run_command(f"{python_cmd} app/app.py", check=False)


def deploy_docker():
    """Déploiement avec Docker"""
    print("\n🐳 Déploiement Docker...")
    
    # Build
    print("Construction de l'image...")
    run_command("docker-compose build")
    
    # Run
    print("Démarrage des containers...")
    run_command("docker-compose up -d")
    
    print("\n✅ Application déployée!")
    print("📍 Accès: http://localhost:5000")
    print("📍 Nginx: http://localhost")
    print("\nCommandes utiles:")
    print("  - Voir les logs: docker-compose logs -f")
    print("  - Arrêter: docker-compose down")
    print("  - Rebuild: docker-compose up -d --build")


def deploy_production():
    """Instructions pour déploiement production"""
    print("\n🌐 Déploiement Production")
    print("="*50)
    
    print("\n1. HEROKU:")
    print("   - heroku create mon-app")
    print("   - git push heroku main")
    
    print("\n2. RENDER:")
    print("   - Connecter repo GitHub")
    print("   - Build: pip install -r requirements.txt")
    print("   - Start: gunicorn app.app:app")
    
    print("\n3. AWS/GCP/AZURE:")
    print("   - Utiliser docker-compose.yml")
    print("   - Configurer variables d'environnement")
    print("   - Ajouter domaine et certificat SSL")
    
    print("\n4. DigitalOcean App Platform:")
    print("   - Connecter repo GitHub")
    print("   - Sélectionner Dockerfile")
    print("   - Déploiement automatique")


def main():
    parser = argparse.ArgumentParser(description='Deploy SmartCrop')
    parser.add_argument('--mode', choices=['local', 'docker', 'production', 'setup'],
                       default='local', help='Mode de déploiement')
    parser.add_argument('--skip-tests', action='store_true', help='Skip tests')
    
    args = parser.parse_args()
    
    print("🌱 SMARTCROP - DEPLOYMENT")
    print("="*50)
    
    if not check_requirements():
        sys.exit(1)
    
    if args.mode in ['local', 'setup']:
        setup_environment()
        init_database()
    
    if not args.skip_tests and args.mode != 'setup':
        run_tests()
    
    if args.mode == 'local':
        deploy_local()
    elif args.mode == 'docker':
        deploy_docker()
    elif args.mode == 'production':
        deploy_production()
    elif args.mode == 'setup':
        print("\n✅ Setup terminé!")
        print("Pour démarrer: python deployment/deploy.py --mode local")


if __name__ == '__main__':
    main()
