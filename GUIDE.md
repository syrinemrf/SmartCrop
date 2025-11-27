# 📚 Guide d'Utilisation - Crop Recommendation System

## 🚀 Démarrage Rapide (5 minutes)

### 1️⃣ Installation

```powershell
# Cloner le projet (ou extraire le ZIP)
cd C:\Users\Syrin\CropRecommendation

# Créer environnement virtuel
python -m venv venv

# Activer (Windows PowerShell)
venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt
```

### 2️⃣ Initialiser la Base de Données

```powershell
python -c "from app.app import app, db; app.app_context().push(); db.create_all(); print('✅ DB initialisée')"
```

### 3️⃣ Lancer l'Application

```powershell
python app/app.py
```

📍 **Accès**: http://localhost:5000

---

## 📖 Utilisation Complète

### Interface Web

#### 🏠 Page d'Accueil
- Présentation du système
- Fonctionnalités clés
- Cultures supportées
- Boutons "Commencer" et "Se Connecter"

#### 📝 Inscription
1. Cliquer sur **"S'inscrire"**
2. Remplir le formulaire:
   - Nom d'utilisateur (min. 3 caractères)
   - Email valide
   - Mot de passe (min. 6 caractères)
   - Confirmer mot de passe
3. Cliquer sur **"S'inscrire"**
4. Redirection automatique vers la page de connexion

#### 🔐 Connexion
1. Cliquer sur **"Se Connecter"**
2. Entrer identifiants (username + password)
3. ✅ Cocher "Se souvenir de moi" (optionnel)
4. Cliquer sur **"Se Connecter"**

#### 📊 Dashboard
Une fois connecté, accédez au **Dashboard** qui affiche:

**Statistiques**:
- 📈 Total de prédictions
- 🌾 Nombre de cultures uniques prédites
- 📅 Date d'inscription

**Graphiques Interactifs**:
- 🥧 Distribution des cultures (pie chart)
- 📊 Top 5 cultures (bar chart)

**Prédictions Récentes**:
- Tableau des 5 dernières prédictions
- Date, culture, confiance, paramètres

#### 🔮 Faire une Prédiction

1. Cliquer sur **"Prédire"** dans la navbar
2. Remplir le formulaire avec vos paramètres:

   **Paramètres du Sol (NPK)**:
   - **N (Azote)**: 0-140 (ex: 90)
   - **P (Phosphore)**: 5-145 (ex: 42)
   - **K (Potassium)**: 5-205 (ex: 43)

   **Paramètres Climatiques**:
   - **Température**: 8-44°C (ex: 20.8)
   - **Humidité**: 14-100% (ex: 82)
   - **pH du Sol**: 3.5-10 (ex: 6.5)
   - **Précipitations**: 20-300mm (ex: 202.9)

3. Cliquer sur **"Prédire la Culture"**

**Résultat Affiché**:
- ✅ Culture recommandée (en gros)
- 📊 Barre de confiance (pourcentage)
- 🏆 Top 3 cultures alternatives
- ℹ️ Message informatif

La prédiction est **automatiquement sauvegardée** dans votre historique.

#### 📜 Historique

1. Cliquer sur **"Historique"**
2. Voir toutes vos prédictions:
   - ID, Date/Heure
   - Culture prédite
   - Confiance
   - Tous les paramètres (N, P, K, Temp, Humidité, pH, Pluie)
3. **Pagination** : 10 résultats par page

#### ℹ️ À Propos

Page d'information sur:
- Technologie utilisée
- Stack technique
- Performances du modèle
- Architecture

---

## 🖥️ Ligne de Commande (CLI)

### Prédiction CLI

Faire des prédictions sans interface web:

```powershell
# Prédiction simple
python scripts/predict_cli.py --N 90 --P 42 --K 43 --temperature 20.8 --humidity 82 --ph 6.5 --rainfall 202.9

# Prédiction verbose (toutes les probabilités)
python scripts/predict_cli.py --N 90 --P 42 --K 43 --temperature 20.8 --humidity 82 --ph 6.5 --rainfall 202.9 --verbose

# Sortie JSON
python scripts/predict_cli.py --N 90 --P 42 --K 43 --temperature 20.8 --humidity 82 --ph 6.5 --rainfall 202.9 --json
```

### Entraîner le Modèle

Ré-entraîner le modèle avec de nouvelles données:

```powershell
# Entraînement par défaut
python scripts/train_model.py

# Avec options personnalisées
python scripts/train_model.py --data data/Crop_recommendation.csv --model models/my_model.pkl --cv-folds 5
```

---

## 🔌 API REST

### Authentification

L'API nécessite une **session authentifiée**. Vous devez d'abord vous connecter via l'interface web ou programmatiquement.

### Endpoints

#### POST /api/predict

**Description**: Faire une prédiction

**Headers**:
```
Content-Type: application/json
Cookie: session=<your-session-cookie>
```

**Body (JSON)**:
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "temperature": 20.8,
  "humidity": 82,
  "ph": 6.5,
  "rainfall": 202.9
}
```

**Réponse**:
```json
{
  "success": true,
  "data": {
    "crop": "rice",
    "confidence": 0.9955,
    "top_3": [
      {"crop": "rice", "probability": 0.9955},
      {"crop": "wheat", "probability": 0.0030},
      {"crop": "maize", "probability": 0.0015}
    ],
    "all_probabilities": {
      "rice": 0.9955,
      "wheat": 0.0030,
      ...
    }
  }
}
```

#### GET /api/history

**Description**: Récupérer l'historique des prédictions

**Réponse**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "N": 90,
      "P": 42,
      ...
      "predicted_crop": "rice",
      "confidence": 0.9955,
      "created_at": "2024-11-24 10:30:00"
    }
  ]
}
```

### Exemple Python avec Requests

```python
import requests

# Session
session = requests.Session()

# 1. Login
login_data = {
    'username': 'johndoe',
    'password': 'password123'
}
session.post('http://localhost:5000/login', data=login_data)

# 2. Prédiction
predict_data = {
    'N': 90,
    'P': 42,
    'K': 43,
    'temperature': 20.8,
    'humidity': 82,
    'ph': 6.5,
    'rainfall': 202.9
}
response = session.post('http://localhost:5000/api/predict', json=predict_data)
result = response.json()
print(f"Culture: {result['data']['crop']}")

# 3. Historique
history = session.get('http://localhost:5000/api/history')
print(history.json())
```

---

## 🐳 Docker

### Démarrage avec Docker Compose

```powershell
# Construire et démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

**Accès**:
- Application: http://localhost:5000
- Nginx: http://localhost

### Commandes Docker Utiles

```powershell
# Rebuild après modifications
docker-compose up -d --build

# Entrer dans le container
docker exec -it crop-recommender-web bash

# Voir l'état
docker-compose ps

# Supprimer tout (volumes inclus)
docker-compose down -v
```

---

## 🎯 Cas d'Usage

### Exemple 1: Culture de Riz

```
N: 90
P: 42
K: 43
Température: 20.8°C
Humidité: 82%
pH: 6.5
Précipitations: 202.9mm

➡️ Résultat: Rice (99.55% confiance)
```

### Exemple 2: Culture de Maïs

```
N: 75
P: 50
K: 60
Température: 25°C
Humidité: 65%
pH: 6.0
Précipitations: 100mm

➡️ Résultat: Maize
```

### Exemple 3: Culture de Café

```
N: 100
P: 25
K: 30
Température: 23°C
Humidité: 70%
pH: 6.2
Précipitations: 150mm

➡️ Résultat: Coffee
```

---

## ⚙️ Configuration Avancée

### Modifier le Port

**Fichier**: `app/app.py` (dernière ligne)

```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Changer 5000 → 8080
```

### Changer la Clé Secrète

**Fichier**: `config/config.yaml`

```yaml
app:
  secret_key: "votre-nouvelle-cle-ultra-secrete-2024"
```

### Base de Données Externe (PostgreSQL)

**requirements.txt**: Ajouter
```
psycopg2-binary==2.9.9
```

**config.yaml**:
```yaml
database:
  uri: "postgresql://user:password@localhost/cropdb"
```

---

## 🔧 Dépannage

### Problème: "Port déjà utilisé"

**Solution**:
```powershell
# Trouver le processus sur le port 5000
netstat -ano | findstr :5000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Problème: "Module non trouvé"

**Solution**:
```powershell
# Vérifier l'environnement virtuel activé
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Problème: "Modèle non trouvé"

**Solution**:
```powershell
# Vérifier que les modèles existent
ls models/tuned/

# Si absent, copier depuis models/ ou ré-entraîner
python scripts/train_model.py
```

### Problème: "Database error"

**Solution**:
```powershell
# Supprimer l'ancienne DB
rm crop_recommendation.db

# Recréer
python -c "from app.app import app, db; app.app_context().push(); db.create_all()"
```

---

## 📱 Conseils d'Utilisation

### Pour Agriculteurs

1. **Analyser votre sol**: Faire un test NPK chez un laboratoire agricole
2. **Relevés climatiques**: Utiliser les moyennes annuelles de votre région
3. **Précipitations**: Moyennes mensuelles ou saisonnières
4. **Interpréter**: Le top 3 vous donne des alternatives viables
5. **Historique**: Comparer avec vos cultures précédentes

### Pour Développeurs

1. **API**: Intégrer dans vos applications avec l'API REST
2. **CLI**: Automatiser avec des scripts batch
3. **Tests**: Lancer `pytest` avant modifications
4. **Logs**: Consulter `logs/` pour déboguer
5. **Contribution**: Fork → Modify → Pull Request

### Pour Étudiants

1. **Notebooks**: Étudier le processus ML dans `notebooks/`
2. **Code**: Analyser `src/` pour comprendre l'architecture
3. **Expérimenter**: Modifier les hyperparamètres
4. **Comparer**: Tester d'autres algorithmes (Random Forest, SVM)
5. **Documenter**: Ajouter vos propres analyses

---

## 🎓 Ressources Supplémentaires

- **Documentation Flask**: https://flask.palletsprojects.com/
- **Scikit-learn**: https://scikit-learn.org/
- **Bootstrap 5**: https://getbootstrap.com/
- **Chart.js**: https://www.chartjs.org/

---

## 💡 Prochaines Étapes

1. ✅ Utiliser l'application
2. 📊 Analyser vos résultats
3. 🔧 Personnaliser si nécessaire
4. 🚀 Déployer en production
5. 🌍 Partager avec la communauté

---

**Besoin d'aide ?** Consultez le README.md ou ouvrez une issue sur GitHub.
