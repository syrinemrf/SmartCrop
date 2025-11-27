"""
Flask Application - SmartCrop
===============================================
Complete web application with authentication and ML predictions
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
from pathlib import Path
import pandas as pd

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.predictor import CropPredictor
from src.utils.logger import setup_logger

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crop_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Logger
logger = setup_logger('FlaskApp')

 # ML Model
predictor = CropPredictor()


 # ============================================================================
 # DATABASE MODELS
 # ============================================================================

class User(UserMixin, db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Prediction model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    N = db.Column(db.Float, nullable=False)
    P = db.Column(db.Float, nullable=False)
    K = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    prediction_name = db.Column(db.String(255), nullable=True)
    predicted_crop = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'N': self.N,
            'P': self.P,
            'K': self.K,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'ph': self.ph,
            'rainfall': self.rainfall,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'prediction_name': self.prediction_name,
            'predicted_crop': self.predicted_crop,
            'confidence': self.confidence,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


@login_manager.user_loader
def load_user(user_id):
    """Load a user"""
    return User.query.get(int(user_id))


 # ============================================================================
 # ROUTES - PUBLIC PAGES
 # ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


 # ============================================================================
 # ROUTES - AUTHENTICATION
 # ============================================================================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('signup'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('This username already exists.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('This email is already in use.', 'danger')
            return redirect(url_for('signup'))
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user created: {username}")
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            logger.info(f"User logged in: {username}")
            flash(f'Welcome {username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logger.info(f"User logged out: {current_user.username}")
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


 # ============================================================================
 # ROUTES - APPLICATION (PROTECTED)
 # ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Statistics
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).limit(5).all()
    
    # Most predicted crops
    predictions_all = Prediction.query.filter_by(user_id=current_user.id).all()
    crop_counts = {}
    for pred in predictions_all:
        crop_counts[pred.predicted_crop] = crop_counts.get(pred.predicted_crop, 0) + 1
    
    return render_template('dashboard.html',
                         total_predictions=total_predictions,
                         recent_predictions=recent_predictions,
                         crop_counts=crop_counts)


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Prediction page"""
    if request.method == 'POST':
        try:
            # Get form data
            features = [
                float(request.form.get('N')),
                float(request.form.get('P')),
                float(request.form.get('K')),
                float(request.form.get('temperature')),
                float(request.form.get('humidity')),
                float(request.form.get('ph')),
                float(request.form.get('rainfall'))
            ]
            
            # Prediction
            result = predictor.predict(features)
            
            # Save to database
            # Ensure prediction_name is a string and not None
            pred_name = request.form.get('prediction_name', type=str)
            if not pred_name or pred_name == 'None':
                lat = request.form.get('latitude', type=float)
                lng = request.form.get('longitude', type=float)
                if lat and lng:
                    pred_name = f"{lat}, {lng}"
                else:
                    pred_name = "Unnamed"
            prediction = Prediction(
                user_id=current_user.id,
                N=features[0],
                P=features[1],
                K=features[2],
                temperature=features[3],
                humidity=features[4],
                ph=features[5],
                rainfall=features[6],
                latitude=request.form.get('latitude', type=float),
                longitude=request.form.get('longitude', type=float),
                prediction_name=pred_name,
                predicted_crop=result['crop'],
                confidence=result['confidence']
            )
            db.session.add(prediction)
            db.session.commit()
            
            logger.info(f"Prediction made by {current_user.username}: {result['crop']}")
            
            return render_template('predict.html', result=result, features=features)
        
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            flash(f'Error during prediction: {str(e)}', 'danger')
    
    return render_template('predict.html')


@app.route('/history')
@login_required
def history():
    """Prediction history"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html', predictions=predictions)


 # ============================================================================
 # API ENDPOINTS
 # ============================================================================

@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """Prediction API"""
    try:
        data = request.get_json()
        
        features = [
            float(data['N']),
            float(data['P']),
            float(data['K']),
            float(data['temperature']),
            float(data['humidity']),
            float(data['ph']),
            float(data['rainfall'])
        ]
        
        result = predictor.predict(features)
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/history')
@login_required
def api_history():
    """History API"""
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).limit(50).all()
    
    return jsonify({
        'success': True,
        'data': [pred.to_dict() for pred in predictions]
    })


 # ============================================================================
 # ERROR HANDLING
 # ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """404 Page"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 Page"""
    db.session.rollback()
    return render_template('500.html'), 500

# PDF download route (must be before app.run)
from flask import make_response
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.route('/download_history_pdf')
@login_required
def download_history_pdf():
    """Download prediction history as PDF"""
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "Prediction History - SmartCrop")
    y -= 30
    p.setFont("Helvetica", 10)
    for pred in predictions:
        line = f"{pred.created_at.strftime('%d/%m/%Y %H:%M')} | Crop: {pred.predicted_crop} | Confidence: {round(pred.confidence*100,1)}% | N: {pred.N} | P: {pred.P} | K: {pred.K} | Temp: {pred.temperature}°C | Humidity: {pred.humidity}% | pH: {pred.ph} | Rainfall: {pred.rainfall}mm"
        p.drawString(40, y, line)
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica", 10)
    p.save()
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=prediction_history.pdf'
    return response


 # ============================================================================
 # INITIALIZATION
 # ============================================================================

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")


def init_ml():
    """Initialize the ML model"""
    try:
        predictor.load_model()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")


if __name__ == '__main__':
    init_db()
    init_ml()
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import make_response
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.route('/download_history_pdf')
@login_required
def download_history_pdf():
    """Download prediction history as PDF"""
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "Prediction History - SmartCrop")
    y -= 30
    p.setFont("Helvetica", 10)
    for pred in predictions:
        line = f"{pred.created_at.strftime('%d/%m/%Y %H:%M')} | Crop: {pred.predicted_crop} | Confidence: {round(pred.confidence*100,1)}% | N: {pred.N} | P: {pred.P} | K: {pred.K} | Temp: {pred.temperature}°C | Humidity: {pred.humidity}% | pH: {pred.ph} | Rainfall: {pred.rainfall}mm"
        p.drawString(40, y, line)
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica", 10)
    p.save()
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=prediction_history.pdf'
    return response
