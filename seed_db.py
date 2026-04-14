from app import app, db, University, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Drop old tables and create the new ones (including User)
    db.drop_all() 
    db.create_all()
    
    # 2. Create the Admin User
    admin_user = User(
        username="admin",
        email="admin@universityfinder.com",
        age=99,
        password_hash=generate_password_hash("admin123"), # Default password
        is_admin=True
    )
    db.session.add(admin_user)
    
    # 3. Create the Universities
    uni1 = University(
        name="Leyte Normal University",
        location="Tacloban City, Leyte",
        tuition="Free / year",
        acceptance_rate="High",
        programs="Education, Arts, Sciences",
        image_url="https://gumlet.assettype.com/sunstar/2023-11/d994499b-a9b1-482a-9f92-d10c003289e7/received_1712202899278583.jpeg?auto=format%2Ccompress&fit=max&w=1200",
        latitude=11.2454,
        longitude=125.0044
    )

    uni2 = University(
        name="UP Visayas Tacloban",
        location="Magsaysay Blvd, Tacloban",
        tuition="Free / year",
        acceptance_rate="15.2%",
        programs="Management, Biology, CS",
        image_url="https://tse4.mm.bing.net/th/id/OIP.youb4p1QCviekRnzNfRbgQHaDo?rs=1&pid=ImgDetMain&o=7&rm=3",
        latitude=11.2440,
        longitude=125.0010
    )

    uni3 = University(
        name="Eastern Visayas State U",
        location="Salazar St, Tacloban City",
        tuition="Free / year",
        acceptance_rate="Moderate",
        programs="Engineering, IT, Arch",
        image_url="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgcHkwcCKlIqADcMeK6Jn2zcMSwE_WsdAu0qjczJ3OYx-D521Ob-e9zeObBPYKcmA2wp8Lf6OxdBQNFPVfffXKwNgNDHVJ-11KszOaqKNcWxDzYLCH1wo4d4bzgBixL2D-W0UYfJ56AAkipkI9VnewqFx9qcf30gNblzpLb8sntC-5CD4kJQnRWBMazPg/w640-h336/EVSU%20ranks%20as%202nd%20top%20university%20in%20Eastern%20Visayas,%2041st%20in%20the%20Philippines.jpg",
        latitude=11.2430,
        longitude=124.9982
    )

    db.session.add(uni1)
    db.session.add(uni2)
    db.session.add(uni3)

    db.session.commit()

    print("SUCCESS: Database built! Admin account created (User: admin, Pass: admin123).")