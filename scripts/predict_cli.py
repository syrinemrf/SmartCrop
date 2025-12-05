#!/usr/bin/env python
"""
Script CLI pour faire des prédictions de cultures
Usage: python scripts/predict_cli.py --N 90 --P 42 --K 43 --temperature 20.8 --humidity 82 --ph 6.5 --rainfall 202.9
"""
import sys
from pathlib import Path
import argparse
import json

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.predictor import CropPredictor
from src.utils.logger import setup_logger

logger = setup_logger('PredictCLI')


def print_result(result: dict, verbose: bool = False):
    """Affiche les résultats de prédiction"""
    print("\n" + "="*60)
    print("🌾 RÉSULTAT DE PRÉDICTION")
    print("="*60)
    
    print(f"\n✅ Culture recommandée: {result['crop'].upper()}")
    print(f"📊 Confiance: {result['confidence']*100:.2f}%")
    
    print(f"\n🏆 Top 3 Cultures:")
    for i, crop_info in enumerate(result['top_3'], 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"   {emoji} {crop_info['crop']:<15} {crop_info['probability']*100:>6.2f}%")
    
    if verbose:
        print(f"\n📈 Toutes les probabilités:")
        sorted_probs = sorted(
            result['all_probabilities'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for crop, prob in sorted_probs:
            bar = "█" * int(prob * 50)
            print(f"   {crop:<15} {prob*100:>6.2f}% {bar}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='🌾 Crop Recommendation CLI - Prédiction de cultures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s --N 90 --P 42 --K 43 --temperature 20.8 --humidity 82 --ph 6.5 --rainfall 202.9
  %(prog)s --N 20 --P 10 --K 15 --temperature 25.5 --humidity 70 --ph 5.8 --rainfall 150 --verbose
        """
    )
    
    # Arguments de features
    parser.add_argument('--N', type=float, required=True,
                       help='Azote (N) - Range: 0-140')
    parser.add_argument('--P', type=float, required=True,
                       help='Phosphore (P) - Range: 5-145')
    parser.add_argument('--K', type=float, required=True,
                       help='Potassium (K) - Range: 5-205')
    parser.add_argument('--temperature', type=float, required=True,
                       help='Température (°C) - Range: 8-44')
    parser.add_argument('--humidity', type=float, required=True,
                       help='Humidité (%) - Range: 14-100')
    parser.add_argument('--ph', type=float, required=True,
                       help='pH du sol - Range: 3.5-10')
    parser.add_argument('--rainfall', type=float, required=True,
                       help='Précipitations (mm) - Range: 20-300')
    
    # Options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Afficher toutes les probabilités')
    parser.add_argument('--json', action='store_true',
                       help='Sortie en format JSON')
    parser.add_argument('--model-path', type=str,
                       default='models/tuned/random_forest_best.pkl',
                       help='Chemin vers le modèle')
    
    args = parser.parse_args()
    
    try:
        # Créer les features
        features = [
            args.N,
            args.P,
            args.K,
            args.temperature,
            args.humidity,
            args.ph,
            args.rainfall
        ]
        
        logger.info("Chargement du modèle...")
        predictor = CropPredictor(model_path=args.model_path)
        predictor.load_model()
        
        logger.info("Prédiction en cours...")
        result = predictor.predict(features)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(result, verbose=args.verbose)
        
        logger.info("Prédiction terminée avec succès")
        return 0
    
    except FileNotFoundError as e:
        logger.error(f"Fichier non trouvé: {e}")
        print(f"\n❌ Erreur: Modèle non trouvé. Vérifiez que le modèle existe à: {args.model_path}")
        return 1
    
    except ValueError as e:
        logger.error(f"Valeur invalide: {e}")
        print(f"\n❌ Erreur: {e}")
        return 1
    
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        print(f"\n❌ Erreur inattendue: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
