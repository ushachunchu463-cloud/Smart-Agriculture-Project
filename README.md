# 🌾 Smart Agriculture Web System

**"Smart Agriculture Monitoring System with Multilingual Support, Soil Analysis, Crop Recommendation, Disease Detection & Government Schemes"**

A complete MCA Final Year Project built with Python Flask, Deep Learning, and Bootstrap.

---

## 📋 Project Features

| Module | Description |
|--------|-------------|
| 👤 Farmer Login/Register | Secure authentication with state & district selection |
| 🌍 Multilingual | Full website in English, Hindi (हिंदी), Telugu (తెలుగు) |
| 🌱 Soil Analysis | Upload soil image → AI detects soil type & features |
| 🌾 Crop Recommendation | Season + Location + Soil → Best crops with market prices |
| 🔬 Disease Detection | Upload leaf image → AI detects disease + treatment |
| 🏛️ Govt Schemes | 10+ Central & State schemes with filter & search |
| 📞 Help & Contact | FAQ + Contact form + Helpline numbers |
| ⚙️ Admin Panel | Manage farmers, add schemes, view messages |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 2.3
- **Database:** SQLite (easy setup) → upgrade to MySQL for production
- **Deep Learning:** TensorFlow/Keras (CNN for soil & disease)
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication:** Flask-Login
- **Multilingual:** Session-based i18n system

---

## 🚀 Setup & Installation

### Step 1 - Install Python
Download Python 3.10+ from https://python.org

### Step 2 - Create Virtual Environment
```bash
cd smart_agriculture
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3 - Install Dependencies
```bash
pip install flask flask-sqlalchemy flask-login werkzeug pillow numpy scikit-learn pandas requests
```

> **Note:** TensorFlow is optional for now. The system uses simulated AI responses.
> To add real AI: `pip install tensorflow`

### Step 4 - Run Setup (First Time Only)
```bash
python setup.py
```

### Step 5 - Start the Application
```bash
python app.py
```

### Step 6 - Open in Browser
```
http://localhost:5000
```

**Demo Login:**
- Email: `admin@farm.com`
- Password: `password123`

---

## 📂 Project Structure

```
smart_agriculture/
│
├── app.py                  ← Main Flask application (all routes + logic)
├── setup.py                ← Database setup & demo data script
├── requirements.txt        ← Python dependencies
│
├── templates/              ← HTML templates
│   ├── base.html           ← Navigation + footer layout
│   ├── login.html          ← Farmer login page
│   ├── register.html       ← Farmer registration page
│   ├── select_language.html← Language selection (EN/HI/TE)
│   ├── home.html           ← Dashboard/home page
│   ├── crop_ideas.html     ← Soil upload + crop recommendations
│   ├── disease_prediction.html ← Disease detection page
│   ├── schemes.html        ← Government schemes list
│   ← scheme_detail.html   ← Individual scheme details
│   ├── help.html           ← Help, FAQ & contact
│   ├── profile.html        ← Farmer profile & history
│   └── admin.html          ← Admin panel
│
├── static/
│   └── uploads/            ← Uploaded soil/leaf images stored here
│
└── smart_agriculture.db    ← SQLite database (auto-created)
```

---

## 🤖 How to Add Real AI Models (Optional)

### Soil Classification Model
```python
# In app.py, replace classify_soil() function:
import tensorflow as tf
import numpy as np
from PIL import Image

def classify_soil(image_path):
    model = tf.keras.models.load_model('models/soil_classifier.h5')
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    soil_classes = ['Red Soil', 'Black Soil', 'Loamy Soil', 'Sandy Soil', 'Clay Soil', 'Alluvial Soil']
    return soil_classes[np.argmax(prediction)]
```

### Disease Detection Model
```python
# In app.py, replace detect_plant_disease() function:
def detect_plant_disease(image_path):
    model = tf.keras.models.load_model('models/disease_detector.h5')
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    disease_classes = list(DISEASES.keys())
    return disease_classes[np.argmax(prediction)]
```

### Recommended Datasets
| Purpose | Dataset | Source |
|---------|---------|--------|
| Soil Classification | Soil Types Dataset | Kaggle |
| Disease Detection | PlantVillage Dataset | Kaggle (54,000+ images) |
| Crop Recommendation | Crop Recommendation Dataset | Kaggle |

---

## 🗃️ Database Schema

```
Farmer          - id, name, phone, email, password, state, district, language
SoilAnalysis    - id, farmer_id, soil_type, state, district, season, image_path, result
DiseaseDetection- id, farmer_id, image_path, disease_name, treatment
GovernmentScheme- id, name, name_hi, name_te, scheme_type, category, description, benefit...
ContactMessage  - id, farmer_id, name, email, message, reply
```

---

## 🌱 Government Schemes Included

**Central Government (7 schemes):**
- PM Kisan Samman Nidhi (₹6000/year)
- PM Fasal Bima Yojana (Crop Insurance)
- Kisan Credit Card (4% interest loan)
- Soil Health Card Scheme
- PM Krishi Sinchai Yojana
- PM Kisan Mandhan Yojana (Pension)
- eNAM National Agriculture Market
- Paramparagat Krishi Vikas Yojana

**State Government (Telangana):**
- Rythu Bandhu (₹10,000/acre/season)
- Rythu Bima (₹5 lakh insurance)

---

## 📊 Expected Output Screenshots

1. **Login Page** — Beautiful green-themed login with farmer branding
2. **Language Selection** — Choose English/Hindi/Telugu with flag cards
3. **Home Dashboard** — Stats, quick tip, menu cards, useful links
4. **Soil Analysis** — Upload image → Soil type + features + health score + crop recommendations
5. **Disease Detection** — Upload leaf → Disease name + confidence % + treatment + organic options
6. **Schemes Page** — Filterable list of all government schemes with details
7. **Profile Page** — Farmer info + analysis history

---

## 🎯 How to Run for Demonstration / Viva

1. Start the server: `python app.py`
2. Register a new farmer account with your state/district
3. Select Telugu or Hindi language — show website changes completely
4. Go to Crop Ideas → Select Telangana/Warangal/Kharif → Upload any soil image
5. Show the soil analysis result and crop recommendations
6. Go to Disease Prediction → Upload any leaf image → Show disease result
7. Go to Government Schemes → Show filtering by state/category
8. Click any scheme → Show detailed page with how to apply
9. Go to Help & Contact → Show FAQ section
10. Visit Admin Panel at /admin → Show farmer management

---

## 📅 Project Timeline (for documentation)

| Phase | Duration | Activities |
|-------|----------|------------|
| Planning | Week 1-2 | Requirements, wireframes, DB design |
| Development | Week 3-8 | Backend + Frontend + AI integration |
| Testing | Week 9-10 | Unit testing, bug fixing |
| Documentation | Week 11-12 | Report writing, presentation |

---

## 👨‍💻 Built With

- **Python Flask** — Web framework
- **SQLite/SQLAlchemy** — Database
- **Bootstrap 5** — Frontend UI framework
- **TensorFlow/Keras** — Deep Learning (CNN models)
- **Pillow** — Image processing

---

*MCA Final Year Project | Smart Agriculture System*
