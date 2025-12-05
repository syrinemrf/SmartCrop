"""
Flask Application - SmartCrop
===============================================
Complete web application with authentication and ML predictions
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
from pathlib import Path
import pandas as pd

# Ajouter le chemin src et app au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from src.models.predictor import CropPredictor
from src.utils.logger import setup_logger
from translations import translations, get_translation, get_all_translations

# Configuration
app = Flask(__name__)
import os
from dotenv import load_dotenv
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-2024')

# Database configuration - supports DATABASE_URL (Neon/Heroku) or individual vars
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Neon/Heroku style URL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local PostgreSQL with individual variables
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql+psycopg2://{os.environ.get('DB_USER', 'postgres')}:{os.environ.get('DB_PASSWORD', '')}"
        f"@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'smartcrop')}"
    )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Better for cloud databases
}
app.config['LANGUAGES'] = ['en', 'fr', 'ar']

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
# LANGUAGE HANDLING
# ============================================================================

@app.before_request
def before_request():
    """Set language before each request"""
    lang = session.get('lang', 'en')
    if lang not in app.config['LANGUAGES']:
        lang = 'en'
    g.lang = lang
    g.translations = get_all_translations(lang)
    g.is_rtl = (lang == 'ar')

@app.context_processor
def inject_translations():
    """Inject translations into all templates"""
    return {
        't': g.translations,
        'current_lang': g.lang,
        'is_rtl': g.is_rtl,
        'languages': [
            {'code': 'en', 'name': 'English', 'flag': '🇬🇧'},
            {'code': 'fr', 'name': 'Français', 'flag': '🇫🇷'},
            {'code': 'ar', 'name': 'العربية', 'flag': '🇹🇳'}
        ]
    }

@app.route('/set-language/<lang>')
def set_language(lang):
    """Set the user's preferred language"""
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


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
    profile_image = db.Column(db.String(255), nullable=True)  # Chemin de la photo de profil
    # Nouveaux champs profil
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(50), nullable=True)
    
    def set_password(self, password):
        """Hash the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def get_profile_image(self):
        from flask import url_for
        if self.profile_image:
            return url_for('static', filename=f'images/profiles/{self.profile_image}')
        # Fallback to UI Avatars with user's initials
        return f"https://ui-avatars.com/api/?name={self.username}&background=2E7D32&color=fff&size=150&bold=true"


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


class Notification(db.Model):
    """Notification model for smart alerts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, success, warning, danger
    icon = db.Column(db.String(50), default='fa-bell')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(255), nullable=True)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'icon': self.icon,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'link': self.link,
            'time_ago': self.time_ago()
        }
    
    def time_ago(self):
        now = datetime.utcnow()
        diff = now - self.created_at
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"


class LoginAttempt(db.Model):
    """Track login attempts for security"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), nullable=True)
    success = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Helper function to create notifications
def create_notification(user_id, title, message, notif_type='info', icon='fa-bell', link=None):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        icon=icon,
        link=link
    )
    db.session.add(notif)
    db.session.commit()
    return notif


def cleanup_old_notifications():
    """Delete notifications older than 1 day"""
    from datetime import timedelta
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    old_notifications = Notification.query.filter(Notification.created_at < one_day_ago).all()
    for notif in old_notifications:
        db.session.delete(notif)
    if old_notifications:
        db.session.commit()
    return len(old_notifications)


def generate_seasonal_notifications(user_id):
    """Generate seasonal tips and recommendations"""
    import random
    from datetime import timedelta
    
    # Check if user already received a tip today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    recent_tip = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.created_at >= today_start,
        Notification.title.like('%Tip%')
    ).first()
    
    if recent_tip:
        return  # Already sent tip today
    
    # Get current month for seasonal tips
    month = datetime.utcnow().month
    
    seasonal_tips = {
        # Winter (Dec-Feb)
        12: [("Winter Prep 🌨️", "Perfect time to prepare soil for spring planting. Consider soil testing!", "fa-snowflake")],
        1: [("New Year, New Crops! 🎊", "Start planning your crop rotation for the year. Check our Crop Guide!", "fa-calendar", "/crop-guide")],
        2: [("Spring is Coming 🌸", "Begin preparing seedbeds. Early spring crops can be started indoors.", "fa-seedling")],
        # Spring (Mar-May)
        3: [("Spring Planting 🌱", "Optimal time to plant wheat, barley, and early vegetables.", "fa-leaf", "/predict")],
        4: [("Soil Testing Time 🔬", "April is perfect for soil analysis. Check our Lab locations!", "fa-flask", "/soil-labs")],
        5: [("Peak Growing Season 🌿", "Monitor your crops closely. Perfect weather for growth!", "fa-sun")],
        # Summer (Jun-Aug)
        6: [("Summer Heat ☀️", "Ensure adequate irrigation during hot months.", "fa-water")],
        7: [("Mid-Summer Check 🌾", "Time to assess crop health and plan harvests.", "fa-tasks")],
        8: [("Harvest Prep 🌽", "Some crops are ready for harvest. Plan your next rotation!", "fa-tractor")],
        # Fall (Sep-Nov)
        9: [("Autumn Planting 🍂", "Great time for fall crops and cover crops.", "fa-leaf")],
        10: [("Soil Enrichment 🪴", "Add organic matter to prepare for next season.", "fa-recycle")],
        11: [("Season Wrap-up 📊", "Review your predictions and plan for next year.", "fa-chart-line", "/dashboard")],
    }
    
    if month in seasonal_tips:
        tip = random.choice(seasonal_tips[month])
        title, message, icon = tip[0], tip[1], tip[2]
        link = tip[3] if len(tip) > 3 else None
        
        create_notification(
            user_id,
            title,
            message,
            notif_type='info',
            icon=icon,
            link=link
        )


# Security: Rate limiting for login attempts
def check_login_attempts(ip_address):
    """Check if IP has too many failed login attempts"""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(minutes=15)
    attempts = LoginAttempt.query.filter(
        LoginAttempt.ip_address == ip_address,
        LoginAttempt.success == False,
        LoginAttempt.created_at > cutoff
    ).count()
    return attempts < 5  # Max 5 attempts per 15 minutes


def log_login_attempt(ip_address, username, success):
    """Log a login attempt"""
    attempt = LoginAttempt(ip_address=ip_address, username=username, success=success)
    db.session.add(attempt)
    db.session.commit()


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


@app.route('/soil-labs')
def soil_labs():
    """Soil analysis laboratories in Tunisia"""
    return render_template('soil_labs.html')


@app.route('/crop-guide')
def crop_guide():
    """Complete crop guide with calendar and tips"""
    return render_template('crop_guide.html')


@app.route('/weather')
def weather():
    """Weather dashboard - accessible without login"""
    return render_template('weather.html')


@app.route('/marketplace')
def marketplace():
    """Seed marketplace"""
    return render_template('marketplace.html')


@app.route('/chatbot')
def chatbot():
    """Agricultural chatbot assistant"""
    return render_template('chatbot.html')


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
        
        # Create welcome notification
        create_notification(
            user.id,
            "Welcome to SmartCrop! 🌱",
            "Your account has been created successfully. Start by making your first crop prediction!",
            notif_type='success',
            icon='fa-seedling',
            link='/predict'
        )
        
        logger.info(f"New user created: {username}")
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login with enhanced security"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        ip_address = request.remote_addr
        
        # Check rate limiting
        if not check_login_attempts(ip_address):
            flash('Too many failed login attempts. Please try again in 15 minutes.', 'danger')
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            log_login_attempt(ip_address, username, True)
            login_user(user, remember=remember)
            logger.info(f"User logged in: {username}")
            
            # Check for inactivity and create notification
            last_prediction = Prediction.query.filter_by(user_id=user.id)\
                .order_by(Prediction.created_at.desc()).first()
            if last_prediction:
                days_since = (datetime.utcnow() - last_prediction.created_at).days
                if days_since >= 7:
                    create_notification(
                        user.id,
                        "Welcome Back! 🌾",
                        f"It's been {days_since} days since your last prediction. Your crops miss you!",
                        notif_type='info',
                        icon='fa-calendar-alt',
                        link='/predict'
                    )
            
            # Generate seasonal tips
            generate_seasonal_notifications(user.id)
            
            flash(f'Welcome {username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            log_login_attempt(ip_address, username, False)
            logger.warning(f"Failed login attempt for username: {username} from IP: {ip_address}")
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

# =========================
# ROUTES - PROFILE
# =========================

from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
PROFILE_IMG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'profiles')
os.makedirs(PROFILE_IMG_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Changement email
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Cet email est déjà utilisé.', 'danger')
            else:
                current_user.email = email
                flash('Email mis à jour.', 'success')
        
        # Mise à jour des autres champs
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone
        current_user.location = location
        
        # Upload photo de profil
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                file.save(os.path.join(PROFILE_IMG_FOLDER, filename))
                current_user.profile_image = filename
                flash('Photo de profil mise à jour.', 'success')
        
        db.session.commit()
        
        # Notification for profile update
        create_notification(
            current_user.id,
            "Profile Updated ✅",
            "Your profile information has been successfully updated.",
            notif_type='info',
            icon='fa-user-edit'
        )
        
        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('profile'))
    
    # Récupérer les statistiques pour le profil
    predictions_count = Prediction.query.filter_by(user_id=current_user.id).count()
    
    # Prédictions ce mois
    from datetime import timedelta
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    predictions_this_month = Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.created_at >= start_of_month
    ).count()
    
    # Confiance moyenne
    avg_confidence = db.session.query(db.func.avg(Prediction.confidence)).filter(
        Prediction.user_id == current_user.id
    ).scalar() or 0
    
    # Dernières prédictions
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(
        Prediction.created_at.desc()
    ).limit(5).all()
    
    return render_template('profile.html', 
                           user=current_user,
                           predictions_count=predictions_count,
                           predictions_this_month=predictions_this_month,
                           avg_confidence=avg_confidence,
                           recent_predictions=recent_predictions)

@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if not current_user.check_password(old_password):
        flash('Ancien mot de passe incorrect.', 'danger')
    elif new_password != confirm_password:
        flash('Les mots de passe ne correspondent pas.', 'danger')
    elif len(new_password) < 6:
        flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        create_notification(
            current_user.id,
            "Password Changed 🔐",
            "Your password has been successfully updated.",
            notif_type='success',
            icon='fa-lock'
        )
        flash('Mot de passe mis à jour.', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    logout_user()
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Compte supprimé avec succès.', 'info')
    return redirect(url_for('index'))


# ============================================================================
# ROUTES - NOTIFICATIONS
# ============================================================================

@app.route('/notifications')
@login_required
def notifications():
    """View all notifications"""
    # Cleanup old notifications (older than 1 day)
    cleanup_old_notifications()
    
    user_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    return render_template('notifications.html', notifications=user_notifications)


@app.route('/api/notifications')
@login_required
def api_notifications():
    """API to get notifications"""
    user_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(20).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in user_notifications],
        'unread_count': unread_count
    })


@app.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    """Mark a notification as read"""
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


# ============================================================================
# ROUTES - DASHBOARD (ENHANCED)
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Enhanced user dashboard"""
    from datetime import timedelta
    
    # Statistics
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).limit(5).all()
    
    # Predictions this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    predictions_this_week = Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.created_at >= week_ago
    ).count()
    
    # Most predicted crops
    predictions_all = Prediction.query.filter_by(user_id=current_user.id).all()
    crop_counts = {}
    for pred in predictions_all:
        crop_counts[pred.predicted_crop] = crop_counts.get(pred.predicted_crop, 0) + 1
    
    # Average confidence
    avg_confidence = 0
    if predictions_all:
        avg_confidence = sum(p.confidence for p in predictions_all) / len(predictions_all)
    
    # Top crop
    top_crop = max(crop_counts, key=crop_counts.get) if crop_counts else None
    
    # Unread notifications count
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()
    
    # Recent notifications (for sidebar)
    recent_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(5).all()
    
    # Generate smart tips based on user activity
    tips = generate_smart_tips(current_user.id, predictions_all, crop_counts)
    
    return render_template('dashboard.html',
                         total_predictions=total_predictions,
                         recent_predictions=recent_predictions,
                         predictions_this_week=predictions_this_week,
                         crop_counts=crop_counts,
                         avg_confidence=avg_confidence,
                         top_crop=top_crop,
                         unread_notifications=unread_notifications,
                         recent_notifications=recent_notifications,
                         tips=tips)


def generate_smart_tips(user_id, predictions, crop_counts):
    """Generate intelligent tips based on user activity"""
    tips = []
    
    if len(predictions) == 0:
        tips.append({
            'icon': 'fa-lightbulb',
            'type': 'info',
            'message': 'Make your first prediction to get personalized crop recommendations!'
        })
    elif len(predictions) < 5:
        tips.append({
            'icon': 'fa-chart-line',
            'type': 'info',
            'message': f'You have {len(predictions)} predictions. Make more to see detailed analytics!'
        })
    
    if crop_counts:
        top_crop = max(crop_counts, key=crop_counts.get)
        tips.append({
            'icon': 'fa-seedling',
            'type': 'success',
            'message': f'Your most recommended crop is {top_crop}. Consider exploring its cultivation guide!'
        })
    
    # Seasonal tip
    from datetime import datetime
    month = datetime.now().month
    if month in [3, 4, 5]:
        tips.append({
            'icon': 'fa-sun',
            'type': 'warning',
            'message': 'Spring season: Ideal time for planting summer crops like tomatoes, peppers, and corn.'
        })
    elif month in [6, 7, 8]:
        tips.append({
            'icon': 'fa-temperature-high',
            'type': 'warning',
            'message': 'Summer: Ensure adequate irrigation for your crops during hot weather.'
        })
    elif month in [9, 10, 11]:
        tips.append({
            'icon': 'fa-leaf',
            'type': 'info',
            'message': 'Autumn: Good time for harvesting summer crops and planting winter varieties.'
        })
    else:
        tips.append({
            'icon': 'fa-snowflake',
            'type': 'info',
            'message': 'Winter: Plan your spring planting and prepare your soil for the next season.'
        })
    
    return tips[:3]  # Return max 3 tips


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
            
            # Explication LIME (XAI)
            explanation = predictor.explain_prediction(features)
            result['explanation'] = explanation
            
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
            
            # Count total predictions for this user
            total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
            
            # Create notification for the prediction
            create_notification(
                current_user.id,
                f"New Prediction: {result['crop']} 🌱",
                f"Recommended crop with {result['confidence']:.1f}% confidence. Soil: N={features[0]}, P={features[1]}, K={features[2]}",
                notif_type='success',
                icon='fa-leaf',
                link='/history'
            )
            
            # Milestone notifications
            milestones = {1: "First", 10: "10th", 25: "25th", 50: "50th", 100: "100th", 500: "500th"}
            if total_predictions in milestones:
                create_notification(
                    current_user.id,
                    f"🎉 Milestone Reached!",
                    f"Congratulations! You just made your {milestones[total_predictions]} prediction! Keep growing!",
                    notif_type='warning',
                    icon='fa-trophy',
                    link='/dashboard'
                )
            
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
    app.run(port=5000, debug=True)
