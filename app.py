import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key is required for session tracking and flash messages
# You can set a real key in an environment variable named SECRET_KEY
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

# User table for login
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # True for admin accounts

# ==========================================
# PUBLIC ROUTES
# ==========================================

@app.route('/')
def home():
    # Show the public homepage with optional search/filter
    search = request.args.get('search', '').strip()
    tuition = request.args.get('tuition', '').strip()
    program = request.args.get('program', '').strip()

    query = University.query

    # Basic search (name, location, or programs)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (University.name.ilike(like)) |
            (University.location.ilike(like)) |
            (University.programs.ilike(like))
        )

    # Filter by program text
    if program:
        query = query.filter(University.programs.ilike(f"%{program}%"))

    all_universities = query.all()

    # Markers for the map (only if lat/long exists)
    map_markers = [
        {
            "name": u.name,
            "lat": u.latitude,
            "lng": u.longitude,
        }
        for u in all_universities
        if u.latitude is not None and u.longitude is not None
    ]

    # Filter by tuition block after loading (simple and readable)
    if tuition:
        def get_amount(value):
            digits = ''.join(ch for ch in value if ch.isdigit())
            return int(digits) if digits else None

        if tuition == 'free':
            all_universities = [u for u in all_universities if 'free' in u.tuition.lower()]
        else:
            filtered = []
            for u in all_universities:
                amount = get_amount(u.tuition)
                if amount is None:
                    continue
                if tuition == 'under_30000' and amount < 30000:
                    filtered.append(u)
                elif tuition == 'between_30000_60000' and 30000 <= amount <= 60000:
                    filtered.append(u)
                elif tuition == 'over_60000' and amount > 60000:
                    filtered.append(u)
            all_universities = filtered
    return render_template(
        'Homepage.html',
        universities=all_universities,
        map_markers=map_markers,
        search=search,
        tuition=tuition,
        program=program
    )

# ==========================================
# AUTHENTICATION ROUTES (Login / Register)
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Read form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Look for the user in the database
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists AND password is correct
        if user and check_password_hash(user.password_hash, password):
            # Save their ID in the session cookie to keep them logged in
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            
            # Send everyone to the dashboard first
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.")
            return redirect(url_for('login'))
            
    return render_template('Loginpage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Read form data
        email = request.form.get('email', '').strip()
        age_raw = request.form.get('age', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Make sure age is a number
        try:
            age = int(age_raw)
        except ValueError:
            flash("Age must be a number.")
            return redirect(url_for('register'))
        
        # Make sure username or email isn't already taken
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash("Username or Email already exists! Please login or use a different one.")
            return redirect(url_for('register'))
            
        # Create new user and hash the password for security
        new_user = User(
            username=username, 
            email=email, 
            age=age, 
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! You can now sign in.")
        return redirect(url_for('login'))
        
    return render_template('Registerpage.html')

@app.route('/logout')
def logout():
    # Erase the user's login cookie
    session.clear()
    return redirect(url_for('home'))

# ==========================================
# USER & DASHBOARD ROUTES
# ==========================================

@app.route('/dashboard')
def dashboard():
    # Only logged-in users can view this page
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))

    # Same search/filter logic as the public page
    search = request.args.get('search', '').strip()
    tuition = request.args.get('tuition', '').strip()
    program = request.args.get('program', '').strip()

    query = University.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            (University.name.ilike(like)) |
            (University.location.ilike(like)) |
            (University.programs.ilike(like))
        )

    if program:
        query = query.filter(University.programs.ilike(f"%{program}%"))

    all_universities = query.all()

    map_markers = [
        {
            "name": u.name,
            "lat": u.latitude,
            "lng": u.longitude,
        }
        for u in all_universities
        if u.latitude is not None and u.longitude is not None
    ]

    if tuition:
        def get_amount(value):
            digits = ''.join(ch for ch in value if ch.isdigit())
            return int(digits) if digits else None

        if tuition == 'free':
            all_universities = [u for u in all_universities if 'free' in u.tuition.lower()]
        else:
            filtered = []
            for u in all_universities:
                amount = get_amount(u.tuition)
                if amount is None:
                    continue
                if tuition == 'under_30000' and amount < 30000:
                    filtered.append(u)
                elif tuition == 'between_30000_60000' and 30000 <= amount <= 60000:
                    filtered.append(u)
                elif tuition == 'over_60000' and amount > 60000:
                    filtered.append(u)
            all_universities = filtered
    return render_template(
        'Homepage_loggedin.html',
        universities=all_universities,
        map_markers=map_markers,
        search=search,
        tuition=tuition,
        program=program
    )

@app.route('/profile')
def profile_user():
    # Show the logged-in user's profile
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Grab the current logged-in user from the database
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        flash("Please log in again.")
        return redirect(url_for('login'))
    return render_template('profile_user.html', user=current_user)

# ==========================================
# ADMIN: USER MANAGEMENT ROUTES
# ==========================================

@app.route('/admin/users')
def admin_menu():
    # Admin-only page
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
        
    all_users = User.query.all()
    return render_template('profile_admin_menu.html', users=all_users)

@app.route('/admin/user/<int:user_id>')
def admin_view_user(user_id):
    # Admin-only page
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
        
    user = User.query.get_or_404(user_id)
    return render_template('profile_admin_view.html', user=user)

@app.route('/admin/user/<int:user_id>/update', methods=['POST'])
def admin_update_user(user_id):
    # Admin-only action
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
        
    user = User.query.get_or_404(user_id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.age = request.form.get('age')
    db.session.commit()
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/user/<int:user_id>/delete')
def admin_delete_user(user_id):
    # Admin-only action
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_menu'))

# ==========================================
# ADMIN: UNIVERSITY MANAGEMENT ROUTES
# ==========================================

@app.route('/add_university', methods=['POST'])
def add_university():
    # Admin-only action
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
    new_uni = University(
        name=request.form.get('name'),
        location=request.form.get('location'),
        tuition=request.form.get('tuition'),
        acceptance_rate=request.form.get('acceptance_rate'),
        programs=request.form.get('programs'),
        image_url=request.form.get('image_url')
    )
    db.session.add(new_uni)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_university/<int:uni_id>', methods=['POST'])
def delete_university(uni_id):
    # Admin-only action
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
        flash("Admins only.")
        return redirect(url_for('dashboard'))
    uni_to_delete = University.query.get_or_404(uni_id)
    db.session.delete(uni_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_university/<int:uni_id>', methods=['GET', 'POST'])
def edit_university(uni_id):
    # Admin-only page/action
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('login'))
    if not session.get('is_admin'):
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

if __name__ == "__main__":
    app.run(debug=True)