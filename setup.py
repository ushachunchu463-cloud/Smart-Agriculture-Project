#!/usr/bin/env python3
"""
Smart Agriculture System - Setup & Demo Data Script
Run this ONCE to create the database and add demo farmer account
"""

from app import app, db, Farmer, seed_schemes
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created")

    # Seed government schemes
    seed_schemes()
    print("✅ Government schemes seeded")

    # Create demo farmer account
    if not Farmer.query.filter_by(email='admin@farm.com').first():
        demo = Farmer(
            name='Demo Farmer',
            phone='9876543210',
            email='admin@farm.com',
            password=generate_password_hash('password123'),
            state='Telangana',
            district='Warangal',
            language='en'
        )
        db.session.add(demo)
        db.session.commit()
        print("✅ Demo account created: admin@farm.com / password123")
    else:
        print("ℹ️  Demo account already exists")

    print("\n🌾 Setup complete! Run: python app.py")
    print("🌐 Then open: http://localhost:5000")
    print("👤 Login: admin@farm.com | password123")
