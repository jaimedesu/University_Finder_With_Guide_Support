import random
from app import app, db, University

# A collection of 10 high-quality, generic university/campus images from Unsplash
CAMPUS_IMAGES = [
    "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=800&q=80", # Classic brick building
    "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800&q=80", # Library/Study area
    "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=800&q=80", # Campus path
    "https://images.unsplash.com/photo-1562774053-701939374585?w=800&q=80", # Modern college building
    "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&q=80", # Students walking
    "https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=800&q=80", # University sign area
    "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=800&q=80", # Students on grass
    "https://images.unsplash.com/photo-1532649593139-1bc21d3e8c07?w=800&q=80", # Beautiful architecture
    "https://images.unsplash.com/photo-1607237138185-eedd9c632b0b?w=800&q=80", # Campus quad
    "https://images.unsplash.com/photo-1576495199011-eb94736d05d6?w=800&q=80"  # Aerial campus view
]

print("Starting database image update...")

with app.app_context():
    # Grab every university in the database
    universities = University.query.all()
    
    # Loop through them and assign a random image from our list
    for uni in universities:
        uni.image_url = random.choice(CAMPUS_IMAGES)
    
    # Save the changes to the database
    db.session.commit()
    
    print(f"SUCCESS! Updated images for {len(universities)} universities.")