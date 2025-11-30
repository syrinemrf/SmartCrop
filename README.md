# SmartCrop

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/yourusername/crop-recommendation)

Crop recommendation system using statistical modeling with **99.5% accuracy**

![Crop Recommendation](https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800&h=400&fit=crop)

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [API](#-api)
- [Tests](#-tests)
- [Technologies](#-technologies)
- [Contributors](#-contributors)
- [License](#-license)

---

## Overview

The **SmartCrop** app is a complete web application that recommends the most suitable crop based on soil and climate conditions.

### Model Performance

| Metric | Score |
|----------|-------|
| Accuracy | 99.55% |
| Precision | 99.58% |
| Recall | 99.55% |
| F1-Score | 99.54% |
| Training Time | 0.053s |

### Supported Crops (22)

Rice, Maize, Chickpea, Red beans, Pigeon pea, Kidney beans, Mung bean, Black beans, Lentil, Apple, Banana, Mango, Grapes, Watermelon, Muskmelon, Orange, Coconut, Papaya, Coffee, Pomegranate, Cotton, Jute

## Features

### Authentication
- ✅ Secure registration & login
- ✅ User session management
- ✅ Password hashing (bcrypt)

### Interactive Dashboard

 ✅ Print your prediction history (PDF/printable view)

### Crop Predictions
- ✅ Interactive form with validation
- ✅ Instant results (< 0.1s)
- ✅ Top 3 crops with probabilities
- ✅ Prediction confidence
- ✅ Automatic saving

### Modern Interface
- ✅ Responsive design (Bootstrap 5)
- ✅ Smooth animations
- ✅ Dark mode ready
- ✅ Mobile-first

### REST API
- ✅ Documented endpoints
- ✅ Authentication required
- ✅ Rate limiting
- ✅ JSON responses

---

## Architecture

```
CropRecommendation/
├── 📁 app/                      # Flask application
│   ├── app.py                   # Entry point
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── predict.html
│   │   ├── history.html
│   │   └── about.html
│   └── static/                  # Static assets
│       ├── css/style.css
│       └── js/main.js
│
├── 📁 src/                      # Modular source code
│   ├── data/
│   │   ├── loader.py            # Data loading
│   │   └── preprocessing.py     # Preprocessing
│   ├── models/
│   │   └── predictor.py         # ML predictions
│   └── utils/
│       ├── config.py            # Configuration
│       └── logger.py            # Logging
│
├── 📁 notebooks/                # Jupyter notebooks (research)
│   ├── 1-EDA.ipynb
│   ├── 2-preprocessing.ipynb
│   ├── 3-model_training.ipynb
│   └── 4-model_evaluation.ipynb
│
├── 📁 tests/                    # Unit tests
│   ├── test_model.py
│   └── test_preprocessing.py
│
├── 📁 deployment/               # Deployment config
│   ├── deploy.py
│   └── nginx.conf
│
├── 📁 config/                   # Configuration files
│   └── config.yaml
│
├── 📁 data/                     # Data
│   ├── Crop_recommendation.csv
│   └── *.npy (preprocessed)
│
├── 📁 models/                   # Saved ML models
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   └── tuned/
│       └── naive_bayes_best.pkl
│
├── 📁 logs/                     # Logs
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile                # Docker configuration
├── 📄 docker-compose.yml        # Orchestration
├── 📄 .gitignore
└── 📄 README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- pip
- (Optional) Docker

### Option 1: Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/crop-recommendation.git
cd crop-recommendation

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize the database

python -c "from app.app import app, db; app.app_context().push(); db.create_all()"

# 6. Run the application
python app/app.py
```

### Option 2: Docker

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/crop-recommendation.git
cd crop-recommendation

# 2. Build and start
docker-compose up -d

# 3. Access the app
# http://localhost:5000
```

### Option 3: Automatic Deployment Script

```bash
# Full setup
python deployment/deploy.py --mode setup

# Local deployment
python deployment/deploy.py --mode local

# Docker deployment
python deployment/deploy.py --mode docker
```

---

## 💻 Usage

### Web Interface

1. **Create an account**: Click "Sign Up"
2. **Log in**: Use your credentials
3. **Access the Dashboard**: View your statistics
4. **Make a prediction**:
   - Click "Predict"
   - Enter parameters (N, P, K, temperature, humidity, pH, rainfall)
   - Click "Predict Crop"
   - View the result and top 3
5. **View history**: Go to "History" page

### REST API

#### Authentication

All API requests require authentication (session cookie after login).

#### Endpoints

**POST /api/predict** - Make a prediction

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.8,
    "humidity": 82,
    "ph": 6.5,
    "rainfall": 202.9
  }'
```

Response:
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
    ]
  }
}
```

**GET /api/history** - Get prediction history

```bash
curl http://localhost:5000/api/history
```

### Programmatic Usage

```python
from src.models.predictor import CropPredictor

# Initialize
predictor = CropPredictor()
predictor.load_model()

# Predict
features = [90, 42, 43, 20.8, 82, 6.5, 202.9]
result = predictor.predict(features)

print(f"Recommended crop: {result['crop']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

## 🌐 Deployment

### Heroku

```bash
# 1. Create app
heroku create my-crop-app

# 2. Add Python buildpack
heroku buildpacks:set heroku/python

# 3. Deploy
git push heroku main

# 4. Open
heroku open
```

### Render

1. Connect your GitHub repository
2. Create a new Web Service
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn app.app:app`
5. Deploy

### DigitalOcean App Platform

1. Connect GitHub repository
2. Select Dockerfile
3. Configure environment variables
4. Deploy

### AWS/GCP/Azure

Use `docker-compose.yml` and follow the provider's documentation.

---

## 🧪 Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific tests
pytest tests/test_model.py -v
pytest tests/test_preprocessing.py -v
```

### Coverage

The project aims for **>80% coverage**

---

## 🛠️ Technologies

### Backend
- **Python 3.10** - Main language
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Scikit-learn** - Machine Learning
- **Pandas/NumPy** - Data manipulation

### Frontend
- **Bootstrap 5** - UI Framework
- **Chart.js** - Charts
- **Font Awesome** - Icons
- **Vanilla JavaScript** - Interactivity

### DevOps
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **Gunicorn** - WSGI Server
- **Nginx** - Reverse Proxy

### Testing
- **Pytest** - Unit tests
- **Pytest-cov** - Coverage

---

## 📊 ML Model

### Algorithm: Gaussian Naive Bayes

**Why Naive Bayes?**
- ✅ **Fast**: Trains in 0.053s
- ✅ **Accurate**: 99.55% accuracy
- ✅ **Simple**: Interpretable
- ✅ **Efficient**: Low resource usage

### Hyperparameters

No hyperparameters to optimize (default model is optimal).

### Pipeline

1. **Data loading** (2200 samples)
2. **Train/Test split** (80/20 stratified)
3. **Standardization** (StandardScaler)
4. **Training** (Naive Bayes)
5. **Cross-validation** (10-fold)
6. **Evaluation** (Confusion matrix, metrics)

---

## 📝 Configuration

Edit `config/config.yaml`:

```yaml
app:
  host: "0.0.0.0"
  port: 5000
  debug: false
  secret_key: "your-secret-key-here"

model:
  path: "models/tuned/naive_bayes_best.pkl"

database:
  uri: "sqlite:///crop_recommendation.db"
```

Environment variables (`.env`):

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///crop_recommendation.db
```

---

## 🤝 Contributors

- **Syrine Maaref** - ([syrinemrf](https://github.com/syrinemrf), syrine.maaref@itbs.tn)
- **Ibtissem Moussa** - 
- You? - Contributions welcome!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Dataset: Crop Recommendation Dataset
- Inspirations: Machine Learning Community
- Tools: Scikit-learn, Flask, Bootstrap

---

## 📬 Contact

- **GitHub**: [@syrinemrf](https://github.com/syrinemrf)
- **Email**: syrine.maaref@itbs.tn


---

<div align="center">

**⭐ If you like this project, give it a star! ⭐**

Made with ❤️

</div>
