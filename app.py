import os
import math
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key is required for session tracking and flash messages
app.secret_key = os.environ.get('SECRET_KEY', 'dev_change_me')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    tuition = db.Column(db.String(50), nullable=False)
    acceptance_rate = db.Column(db.String(50), nullable=False)
    programs = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    distance = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def calculate_distance(lat1, lon1, lat2, lon2):
    # Returns the distance in kilometers between two points
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0 # Radius of the Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def apply_filters(query, search, tuition, program):
    if search:
        query = query.filter(db.or_(
            University.name.ilike(f'%{search}%'),
            University.location.ilike(f'%{search}%'),
            University.programs.ilike(f'%{search}%')
        ))
    if program:
        query = query.filter(University.programs.ilike(f'%{program}%'))
    if tuition:
        if tuition == 'free':
            query = query.filter(University.tuition.ilike('%free%'))
        elif tuition == 'under_30000':
            query = query.filter(University.tuition.ilike('%15,000%'))
    return query

class CustomPagination:
    """A helper class to paginate standard Python lists since SQLAlchemy paginate doesn't work with custom sorting"""
    def __init__(self, current_page, total_pages, items):
        self.page = current_page
        self.pages = total_pages
        self.has_prev = current_page > 1
        self.has_next = current_page < total_pages
        self.prev_num = current_page - 1
        self.next_num = current_page + 1
        self.items = items

# ==========================================
# PUBLIC ROUTES
# ==========================================

@app.route('/')
def home():
    search = request.args.get('search', '')
    tuition = request.args.get('tuition', '')
    program = request.args.get('program', '')
    page = request.args.get('page', 1, type=int)
    
    # Grab user location from the URL
    user_lat = request.args.get('user_lat', type=float)
    user_lng = request.args.get('user_lng', type=float)

    # 1. Start query and apply filters
    query = University.query
    query = apply_filters(query, search, tuition, program)
    all_unis = query.all()

    # 2. Calculate distance and sort if location is provided
    if user_lat is not None and user_lng is not None:
        for uni in all_unis:
            uni.distance = calculate_distance(user_lat, user_lng, uni.latitude, uni.longitude)
        # Sort by distance (closest first)
        all_unis.sort(key=lambda u: u.distance if u.distance is not None else float('inf'))
    else:
        for uni in all_unis:
            uni.distance = None

    # 3. Manually paginate the sorted list
    total = len(all_unis)
    pages = math.ceil(total / 12) if total > 0 else 1
    if page < 1: page = 1
    if page > pages: page = pages
    
    start = (page - 1) * 12
    end = start + 12
    paged_universities = all_unis[start:end]
    pagination = CustomPagination(page, pages, paged_universities)

    # 4. Only grab map markers for the visible universities
    map_markers = [
        {'name': uni.name, 'lat': uni.latitude, 'lng': uni.longitude} 
        for uni in paged_universities if uni.latitude and uni.longitude
    ]

    return render_template('Homepage.html', 
                           universities=paged_universities, 
                           pagination=pagination,
                           map_markers=map_markers,
                           search=search,
                           tuition=tuition,
                           program=program,
                           user_lat=user_lat if user_lat else '',
                           user_lng=user_lng if user_lng else '')

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('Loginpage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or Email already exists.")
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            email=email,
            age=int(age),
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('Registerpage.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ==========================================
# LOGGED IN / ADMIN ROUTES
# ==========================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    tuition = request.args.get('tuition', '')
    program = request.args.get('program', '')
    page = request.args.get('page', 1, type=int)
    
    # Grab user location from the URL
    user_lat = request.args.get('user_lat', type=float)
    user_lng = request.args.get('user_lng', type=float)

    # 1. Start query and apply filters
    query = University.query
    query = apply_filters(query, search, tuition, program)
    all_unis = query.all()

    # 2. Calculate distance and sort if location is provided
    if user_lat is not None and user_lng is not None:
        for uni in all_unis:
            uni.distance = calculate_distance(user_lat, user_lng, uni.latitude, uni.longitude)
        all_unis.sort(key=lambda u: u.distance if u.distance is not None else float('inf'))
    else:
        for uni in all_unis:
            uni.distance = None

    # 3. Manually paginate the sorted list
    total = len(all_unis)
    pages = math.ceil(total / 12) if total > 0 else 1
    if page < 1: page = 1
    if page > pages: page = pages
    
    start = (page - 1) * 12
    end = start + 12
    paged_universities = all_unis[start:end]
    pagination = CustomPagination(page, pages, paged_universities)

    # 4. Only grab map markers for the visible universities
    map_markers = [
        {'name': uni.name, 'lat': uni.latitude, 'lng': uni.longitude} 
        for uni in paged_universities if uni.latitude and uni.longitude
    ]

    return render_template('Homepage_loggedin.html', 
                           universities=paged_universities, 
                           pagination=pagination,
                           map_markers=map_markers,
                           search=search,
                           tuition=tuition,
                           program=program,
                           user_lat=user_lat if user_lat else '',
                           user_lng=user_lng if user_lng else '')

@app.route('/profile')
def profile_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile_user.html', user=user)

# ==========================================
# UNIVERSITY MANAGEMENT (ADMIN)
# ==========================================

@app.route('/delete_university/<int:uni_id>', methods=['POST'])
def delete_university(uni_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
    
    uni_to_delete = University.query.get_or_404(uni_id)
    db.session.delete(uni_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_university/<int:uni_id>', methods=['GET', 'POST'])
def edit_university(uni_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
        
    uni_to_edit = University.query.get_or_404(uni_id)
    if request.method == 'POST':
        uni_to_edit.name = request.form.get('name')
        uni_to_edit.location = request.form.get('location')
        uni_to_edit.tuition = request.form.get('tuition')
        uni_to_edit.acceptance_rate = request.form.get('acceptance_rate')
        uni_to_edit.programs = request.form.get('programs')
        uni_to_edit.image_url = request.form.get('image_url')
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('Editpage.html', uni=uni_to_edit)

# ==========================================
# USER MANAGEMENT (ADMIN)
# ==========================================

@app.route('/admin')
def admin_menu():
    if not session.get('is_admin'):
        flash("Admin access required.")
        return redirect(url_for('dashboard'))
    all_users = User.query.all()
    return render_template('profile_admin_menu.html', users=all_users)

@app.route('/admin/user/<int:user_id>')
def admin_view_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    target_user = User.query.get_or_404(user_id)
    return render_template('profile_admin_view.html', user=target_user)

@app.route('/admin/update/<int:user_id>', methods=['POST'])
def admin_update_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    target_user = User.query.get_or_404(user_id)
    target_user.username = request.form.get('username')
    target_user.email = request.form.get('email')
    target_user.age = request.form.get('age')
    db.session.commit()
    return redirect(url_for('admin_menu'))

@app.route('/admin/delete/<int:user_id>')
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    target_user = User.query.get_or_404(user_id)
    db.session.delete(target_user)
    db.session.commit()
    return redirect(url_for('admin_menu'))

# ==========================================
# APPLICATION START
# ==========================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)