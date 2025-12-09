# AgriPrime+ (SmartCrop)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-4285F4?logo=google-cloud)](https://agriprime-829483620630.europe-west1.run.app)

**AI-powered crop recommendation system with 99.5% accuracy**. Deployed on Google Cloud Run with PostgreSQL (Neon), featuring multilingual support (EN/FR/AR), real-time weather data, and explainable AI predictions.

🌐 **Live Demo**: [agriprime-829483620630.europe-west1.run.app](https://agriprime-829483620630.europe-west1.run.app)

---

## 📋 Overview

AgriPrime+ is a production-ready web application that recommends optimal crops based on soil nutrients (N, P, K, pH) and climate conditions (temperature, humidity, rainfall). Built with Flask, Random Forest ML model, and deployed on Google Cloud Platform.

### Key Metrics

| Metric | Value |
|--------|-------|
| **Accuracy** | 99.55% |
| **Model** | Random Forest (500 trees, max_depth=10) |
| **Crops Supported** | 22 (rice, wheat, maize, coffee, etc.) |
| **Languages** | English, French, Arabic (RTL) |
| **Response Time** | < 100ms |
| **Deployment** | Cloud Run (Docker, auto-scaling) |

---

## ✨ Features

### 🤖 Machine Learning
- **Random Forest Classifier** with optimized hyperparameters
- **Explainable AI (XAI)** using LIME for prediction transparency
- **Feature importance** analysis (rainfall: 22%, humidity: 21%, K: 18%)
- Real-time predictions with confidence scores

### 🌍 Smart Climate Integration
- **Automatic weather data** via Open-Meteo API (free, no API key)
- Seasonal climate averages (spring/summer/autumn/winter)
- Global coverage with historical climate data
- Monthly rainfall calculation for agriculture

### 🗺️ Interactive Mapping
- **Leaflet.js** map for location selection
- **Geolocation** auto-detection
- **Address search** with Nominatim (OpenStreetMap)
- Auto-fill temperature/humidity/rainfall based on location + season

### 👤 User Management
- Secure authentication (bcrypt password hashing)
- User profiles with prediction history
- Dashboard with statistics and charts (Chart.js)
- PDF export of prediction history

### 🌐 Internationalization
- **3 languages**: English, French, Arabic
- RTL (right-to-left) support for Arabic
- Language switcher in navbar
- Localized UI and notifications

### 📱 Modern UI/UX
- Responsive design (Bootstrap 5.3)
- Mobile-first approach
- Dark mode compatible
- Real-time notifications system

---

## 🏗️ Architecture

```
CropRecommendation/
├── app/                         # Flask application
│   ├── app.py                   # Main application (1023 lines)
│   ├── translations.py          # i18n support (EN/FR/AR)
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html           # Base template with Leaflet map
│   │   ├── predict.html        # ML prediction form
│   │   ├── dashboard.html      # User statistics + charts
│   │   ├── weather.html        # Open-Meteo integration
│   │   ├── chatbot.html        # Agricultural assistant
│   │   └── ...
│   └── static/
│       ├── css/style.css       # Custom styles
│       └── js/main.js          # Client-side logic
│
├── src/                         # Core ML modules
│   ├── models/predictor.py     # Random Forest predictor + LIME
│   ├── data/preprocessing.py   # StandardScaler pipeline
│   └── utils/logger.py         # Logging configuration
│
├── models/tuned/
│   └── random_forest_best.pkl  # Trained model (363 KB)
│
├── config/config.yaml           # Application configuration
├── Dockerfile                   # Multi-stage build for Cloud Run
├── docker-compose.yml           # Local development
└── requirements.txt             # Python dependencies
```

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/syrinemrf/SmartCrop.git
cd SmartCrop

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.app import app, db; app.app_context().push(); db.create_all()"

# Run application
python app/app.py
# Visit: http://localhost:5000
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Access at http://localhost:5000
```

### Google Cloud Run Deployment

```bash
# Prerequisites: gcloud CLI authenticated
gcloud run deploy agriprime \
  --source . \
  --region=europe-west1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://...
```

---

## 🔧 Configuration

**Environment Variables** (`.env`):

```bash
# Flask
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=0

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Optional: Individual DB variables
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smartcrop
DB_USER=postgres
DB_PASSWORD=your-password
```

**Model Configuration** (`config/config.yaml`):

```yaml
model:
  path: "models/tuned/random_forest_best.pkl"
  algorithm: "Random Forest"
  
app:
  languages: ["en", "fr", "ar"]
  port: 5000
```

---

## 🛠️ Tech Stack

**Backend**
- Python 3.10, Flask 3.0, SQLAlchemy (ORM)
- Random Forest (scikit-learn), LIME (explainability)
- PostgreSQL (Neon cloud), Gunicorn (WSGI server)

**Frontend**
- Bootstrap 5.3 (responsive UI), Chart.js (visualizations)
- Leaflet.js (interactive maps), Font Awesome (icons)

**APIs & Services**
- Open-Meteo (climate data - free, no API key)
- Nominatim OSM (geocoding)
- Geolocation API (browser native)

**DevOps**
- Docker (multi-stage builds), Google Cloud Run
- GitHub (version control), Neon (serverless PostgreSQL)

---

## 📊 ML Model Details

### Algorithm: Random Forest Classifier

**Hyperparameters**:
```python
RandomForestClassifier(
    n_estimators=500,
    max_depth=10,
    max_features='sqrt',
    min_samples_split=5,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)
```

**Training Pipeline**:
1. Data loading (2200 samples, 7 features)
2. Train/test split (80/20 stratified)
3. StandardScaler normalization
4. Random Forest training
5. 10-fold cross-validation
6. Model serialization (joblib)

**Feature Importance**:
- Rainfall: 22.3%
- Humidity: 21.7%
- Potassium (K): 18.3%
- Temperature: 14.2%
- Nitrogen (N): 10.8%
- Phosphorus (P): 8.9%
- pH: 3.8%

**Explainability**: LIME (Local Interpretable Model-agnostic Explanations) provides per-prediction feature contributions.

---

## 🌐 API Reference

### Authentication
All endpoints require user login (session-based authentication).

### Endpoints

**POST `/api/predict`** - Crop prediction
```bash
curl -X POST https://agriprime-829483620630.europe-west1.run.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90, "P": 42, "K": 43,
    "temperature": 20.8, "humidity": 82,
    "ph": 6.5, "rainfall": 202.9
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "crop": "rice",
    "confidence": 0.87,
    "top_3": [
      {"crop": "rice", "probability": 0.87},
      {"crop": "wheat", "probability": 0.08},
      {"crop": "maize", "probability": 0.03}
    ]
  }
}
```

**GET `/api/history`** - User prediction history
```bash
curl https://agriprime-829483620630.europe-west1.run.app/api/history
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 🤝 Contributors

- **Syrine Maaref** - Developer ([GitHub](https://github.com/syrinemrf))
- **Ibtissem Moussa** - Developer ([GitHub](https://github.com/ibtissemitbs))

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Dataset**: Crop Recommendation Dataset (Kaggle)
- **APIs**: Open-Meteo (climate), Nominatim OSM (geocoding)
- **Cloud**: Google Cloud Run, Neon PostgreSQL
- **Libraries**: scikit-learn, Flask, Leaflet.js, Bootstrap

---

## 📬 Contact

- **GitHub**: [@syrinemrf](https://github.com/syrinemrf)
- **Email**: syrine.maaref@itbs.tn
- **Live App**: [agriprime-829483620630.europe-west1.run.app](https://agriprime-829483620630.europe-west1.run.app)

---

<div align="center">

**⭐ Star this project if you find it useful! ⭐**

Made with ❤️ for sustainable agriculture

</div>
