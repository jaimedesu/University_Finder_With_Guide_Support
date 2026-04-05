from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy # ✨ NEW: We imported the database tool!

app = Flask(__name__)

# ✨ NEW: Tell Flask where to save the database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ✨ NEW: Create the blueprint for our Universities table
class University(db.Model):
    id = db.Column(db.Integer, primary_key=True) # A unique ID number for every uni
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    tuition = db.Column(db.String(50), nullable=False)
    acceptance_rate = db.Column(db.String(50), nullable=False)
    programs = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

@app.route('/')
def home():
    # 1. Ask the database for every single university it has
    all_universities = University.query.all()
    
    # 2. Hand that list over to Homepage.html 
    return render_template('Homepage.html', universities=all_universities)

# 2. We allow BOTH GET (viewing the page) and POST (submitting the form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user clicked the "SIGN IN" submit button...
    if request.method == 'POST':
        # Grab the data using the "name" attributes we added to the HTML
        username = request.form.get('username')
        password = request.form.get('password')
        
        # We can print this to the terminal just to prove Python caught it!
        print(f"SUCCESS: {username} just tried to log in with password: {password}")
        
        # Send them straight to the logged-in dashboard!
        return redirect(url_for('dashboard'))
        
    # If they just clicked the link to view the page normally (GET request)
    return render_template('Loginpage.html')

@app.route('/register')
def register():
    return render_template('Registerpage.html')

@app.route('/dashboard')
def dashboard():
    return render_template('Homepage_loggedin.html')

if __name__ == "__main__":
    app.run(debug=True)