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
    all_universities = University.query.all()
    return render_template('Homepage_loggedin.html', universities=all_universities)

@app.route('/add_university', methods=['POST'])
def add_university():
    # 1. Grab all the text the user typed into the form
    new_name = request.form.get('name')
    new_location = request.form.get('location')
    new_tuition = request.form.get('tuition')
    new_acceptance_rate = request.form.get('acceptance_rate')
    new_programs = request.form.get('programs')
    new_image_url = request.form.get('image_url')

    # 2. Package it into a new University Database Object
    new_uni = University(
        name=new_name,
        location=new_location,
        tuition=new_tuition,
        acceptance_rate=new_acceptance_rate,
        programs=new_programs,
        image_url=new_image_url
    )

    # 3. Save it to the database!
    db.session.add(new_uni)
    db.session.commit()

    # 4. Refresh the dashboard so the user immediately sees the new school
    return redirect(url_for('dashboard'))

@app.route('/delete_university/<int:uni_id>', methods=['POST'])
def delete_university(uni_id):
    # 1. Find the specific university in the database by its ID
    uni_to_delete = University.query.get_or_404(uni_id)
    
    # 2. Delete it!
    db.session.delete(uni_to_delete)
    db.session.commit()
    
    # 3. Refresh the dashboard
    return redirect(url_for('dashboard'))

@app.route('/edit_university/<int:uni_id>', methods=['GET', 'POST'])
def edit_university(uni_id):
    # 1. Find the specific university we want to edit
    uni_to_edit = University.query.get_or_404(uni_id)
    
    # 2. If the admin submits the edit form...
    if request.method == 'POST':
        uni_to_edit.name = request.form.get('name')
        uni_to_edit.location = request.form.get('location')
        uni_to_edit.tuition = request.form.get('tuition')
        uni_to_edit.acceptance_rate = request.form.get('acceptance_rate')
        uni_to_edit.programs = request.form.get('programs')
        uni_to_edit.image_url = request.form.get('image_url')
        
        # Save the updated data to the database!
        db.session.commit()
        return redirect(url_for('dashboard'))
        
    # 3. If they just clicked the "Edit" button, show them the form with the current data
    return render_template('Editpage.html', uni=uni_to_edit)

if __name__ == "__main__":
    app.run(debug=True)