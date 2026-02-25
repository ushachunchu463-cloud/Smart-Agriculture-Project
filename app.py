from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartagri2024secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///smart_agriculture.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─────────────────────────────────────────────
# DATABASE MODELS
# ─────────────────────────────────────────────

class Farmer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SoilAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    soil_type = db.Column(db.String(50))
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    season = db.Column(db.String(20))
    image_path = db.Column(db.String(200))
    result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DiseaseDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    image_path = db.Column(db.String(200))
    disease_name = db.Column(db.String(100))
    treatment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GovernmentScheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_hi = db.Column(db.String(200))
    name_te = db.Column(db.String(200))
    scheme_type = db.Column(db.String(20))  # central / state
    category = db.Column(db.String(50))
    state = db.Column(db.String(50), default='All')
    description = db.Column(db.Text)
    description_hi = db.Column(db.Text)
    description_te = db.Column(db.Text)
    benefit = db.Column(db.String(300))
    eligibility = db.Column(db.Text)
    how_to_apply = db.Column(db.Text)
    documents = db.Column(db.Text)
    official_link = db.Column(db.String(300))
    last_date = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)
    reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return Farmer.query.get(int(user_id))

# ─────────────────────────────────────────────
# TRANSLATIONS
# ─────────────────────────────────────────────

TRANSLATIONS = {
    'en': {
        'home': 'Home', 'crop_ideas': 'Crop Ideas', 'disease_prediction': 'Disease Prediction',
        'schemes': 'Government Schemes', 'help': 'Help & Contact', 'profile': 'Profile',
        'logout': 'Logout', 'welcome': 'Welcome', 'login': 'Login', 'register': 'Register',
        'select_language': 'Select Your Language', 'continue': 'Continue',
        'upload_soil': 'Upload Soil Image', 'select_state': 'Select State',
        'select_district': 'Select District', 'select_season': 'Select Season',
        'analyze': 'Analyze Soil', 'soil_type': 'Soil Type', 'soil_features': 'Soil Features',
        'recommended_crops': 'Recommended Crops', 'vegetables': 'Vegetables',
        'fruits': 'Fruits', 'flowers': 'Flowers', 'indoor_plants': 'Indoor Plants',
        'market_demand': 'Market Demand', 'high': 'High', 'medium': 'Medium', 'low': 'Low',
        'upload_leaf': 'Upload Crop/Leaf Image', 'detect_disease': 'Detect Disease',
        'disease_name': 'Disease Name', 'treatment': 'Suggested Treatment',
        'prevention': 'Prevention Tips', 'all_schemes': 'All Schemes',
        'central_govt': 'Central Government', 'state_govt': 'State Government',
        'benefits': 'Benefits', 'eligibility': 'Eligibility', 'apply_now': 'Apply Now',
        'view_details': 'View Details', 'search_schemes': 'Search Schemes...',
        'contact_us': 'Contact Us', 'your_name': 'Your Name', 'your_email': 'Your Email',
        'your_message': 'Your Message', 'send_message': 'Send Message',
        'faq': 'Frequently Asked Questions', 'name': 'Name', 'phone': 'Phone',
        'email': 'Email', 'password': 'Password', 'state': 'State', 'district': 'District',
        'submit': 'Submit', 'kharif': 'Kharif (June-October)', 'rabi': 'Rabi (November-March)',
        'zaid': 'Zaid (April-June)', 'health_score': 'Soil Health Score',
        'confidence': 'Confidence', 'cause': 'Cause', 'organic_option': 'Organic Option',
        'dashboard': 'Dashboard', 'recent_analysis': 'Recent Analysis',
        'total_analyses': 'Total Analyses', 'quick_tip': 'Quick Tip of the Day',
    },
    'hi': {
        'home': 'होम', 'crop_ideas': 'फसल विचार', 'disease_prediction': 'रोग पहचान',
        'schemes': 'सरकारी योजनाएं', 'help': 'सहायता और संपर्क', 'profile': 'प्रोफाइल',
        'logout': 'लॉगआउट', 'welcome': 'स्वागत', 'login': 'लॉगिन', 'register': 'पंजीकरण',
        'select_language': 'अपनी भाषा चुनें', 'continue': 'जारी रखें',
        'upload_soil': 'मिट्टी की तस्वीर अपलोड करें', 'select_state': 'राज्य चुनें',
        'select_district': 'जिला चुनें', 'select_season': 'मौसम चुनें',
        'analyze': 'मिट्टी का विश्लेषण करें', 'soil_type': 'मिट्टी का प्रकार',
        'soil_features': 'मिट्टी की विशेषताएं', 'recommended_crops': 'अनुशंसित फसलें',
        'vegetables': 'सब्जियां', 'fruits': 'फल', 'flowers': 'फूल',
        'indoor_plants': 'इनडोर पौधे', 'market_demand': 'बाजार मांग',
        'high': 'उच्च', 'medium': 'मध्यम', 'low': 'कम',
        'upload_leaf': 'फसल/पत्ती की तस्वीर अपलोड करें', 'detect_disease': 'रोग पहचानें',
        'disease_name': 'रोग का नाम', 'treatment': 'सुझाया गया उपचार',
        'prevention': 'रोकथाम के सुझाव', 'all_schemes': 'सभी योजनाएं',
        'central_govt': 'केंद्र सरकार', 'state_govt': 'राज्य सरकार',
        'benefits': 'लाभ', 'eligibility': 'पात्रता', 'apply_now': 'अभी आवेदन करें',
        'view_details': 'विवरण देखें', 'search_schemes': 'योजनाएं खोजें...',
        'contact_us': 'संपर्क करें', 'your_name': 'आपका नाम', 'your_email': 'आपका ईमेल',
        'your_message': 'आपका संदेश', 'send_message': 'संदेश भेजें',
        'faq': 'अक्सर पूछे जाने वाले प्रश्न', 'name': 'नाम', 'phone': 'फोन',
        'email': 'ईमेल', 'password': 'पासवर्ड', 'state': 'राज्य', 'district': 'जिला',
        'submit': 'जमा करें', 'kharif': 'खरीफ (जून-अक्टूबर)', 'rabi': 'रबी (नवंबर-मार्च)',
        'zaid': 'जायद (अप्रैल-जून)', 'health_score': 'मिट्टी स्वास्थ्य स्कोर',
        'confidence': 'विश्वास', 'cause': 'कारण', 'organic_option': 'जैविक विकल्प',
        'dashboard': 'डैशबोर्ड', 'recent_analysis': 'हाल का विश्लेषण',
        'total_analyses': 'कुल विश्लेषण', 'quick_tip': 'आज की त्वरित टिप',
    },
    'te': {
        'home': 'హోమ్', 'crop_ideas': 'పంట ఆలోచనలు', 'disease_prediction': 'వ్యాధి నిర్ధారణ',
        'schemes': 'ప్రభుత్వ పథకాలు', 'help': 'సహాయం మరియు సంప్రదింపు', 'profile': 'ప్రొఫైల్',
        'logout': 'లాగ్అవుట్', 'welcome': 'స్వాగతం', 'login': 'లాగిన్', 'register': 'నమోదు',
        'select_language': 'మీ భాష ఎంచుకోండి', 'continue': 'కొనసాగించు',
        'upload_soil': 'మట్టి చిత్రం అప్లోడ్ చేయండి', 'select_state': 'రాష్ట్రం ఎంచుకోండి',
        'select_district': 'జిల్లా ఎంచుకోండి', 'select_season': 'సీజన్ ఎంచుకోండి',
        'analyze': 'మట్టిని విశ్లేషించండి', 'soil_type': 'మట్టి రకం',
        'soil_features': 'మట్టి లక్షణాలు', 'recommended_crops': 'సిఫార్సు చేసిన పంటలు',
        'vegetables': 'కూరగాయలు', 'fruits': 'పండ్లు', 'flowers': 'పూలు',
        'indoor_plants': 'ఇండోర్ మొక్కలు', 'market_demand': 'మార్కెట్ డిమాండ్',
        'high': 'అధిక', 'medium': 'మధ్యస్థ', 'low': 'తక్కువ',
        'upload_leaf': 'పంట/ఆకు చిత్రం అప్లోడ్ చేయండి', 'detect_disease': 'వ్యాధిని గుర్తించండి',
        'disease_name': 'వ్యాధి పేరు', 'treatment': 'సూచించిన చికిత్స',
        'prevention': 'నివారణ చిట్కాలు', 'all_schemes': 'అన్ని పథకాలు',
        'central_govt': 'కేంద్ర ప్రభుత్వం', 'state_govt': 'రాష్ట్ర ప్రభుత్వం',
        'benefits': 'ప్రయోజనాలు', 'eligibility': 'అర్హత', 'apply_now': 'ఇప్పుడు దరఖాస్తు చేయండి',
        'view_details': 'వివరాలు చూడండి', 'search_schemes': 'పథకాలు వెతకండి...',
        'contact_us': 'మమ్మల్ని సంప్రదించండి', 'your_name': 'మీ పేరు', 'your_email': 'మీ ఇమెయిల్',
        'your_message': 'మీ సందేశం', 'send_message': 'సందేశం పంపండి',
        'faq': 'తరచుగా అడిగే ప్రశ్నలు', 'name': 'పేరు', 'phone': 'ఫోన్',
        'email': 'ఇమెయిల్', 'password': 'పాస్వర్డ్', 'state': 'రాష్ట్రం', 'district': 'జిల్లా',
        'submit': 'సమర్పించండి', 'kharif': 'ఖరీఫ్ (జూన్-అక్టోబర్)', 'rabi': 'రబీ (నవంబర్-మార్చి)',
        'zaid': 'జైద్ (ఏప్రిల్-జూన్)', 'health_score': 'మట్టి ఆరోగ్య స్కోర్',
        'confidence': 'నమ్మకం', 'cause': 'కారణం', 'organic_option': 'సేంద్రీయ వికల్పం',
        'dashboard': 'డాష్బోర్డ్', 'recent_analysis': 'ఇటీవలి విశ్లేషణ',
        'total_analyses': 'మొత్తం విశ్లేషణలు', 'quick_tip': 'నేటి త్వరిత చిట్కా',
    }
}

def t(key):
    lang = session.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

app.jinja_env.globals['t'] = t
app.jinja_env.globals['current_year'] = datetime.utcnow().year

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

STATES_DISTRICTS = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Kurnool", "Nellore", "Tirupati", "Anantapur"],
    "Telangana": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Khammam", "Mahbubnagar", "Nalgonda"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Kolhapur"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi", "Dharwad", "Vijayapura"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Trichy", "Tirunelveli", "Vellore"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Allahabad", "Meerut", "Ghaziabad"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Bhilwara"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Rewa"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar"],
}

SOIL_DATA = {
    "Red Soil": {
        "features": {
            "en": "Low in Nitrogen & Phosphorus, High Iron content, slightly acidic pH (5.5-6.5), good drainage, needs organic compost",
            "hi": "नाइट्रोजन और फास्फोरस में कम, उच्च आयरन सामग्री, थोड़ा अम्लीय pH (5.5-6.5), अच्छी जल निकासी, जैविक खाद की जरूरत",
            "te": "నైట్రోజన్ & ఫాస్పరస్ తక్కువ, అధిక ఇనుము, pH 5.5-6.5, మంచి నీటి పారుదల, సేంద్రీయ ఎరువు అవసరం"
        },
        "health_score": 6.5,
        "crops": {
            "vegetables": [
                {"name": "Tomato", "demand": "high", "price": "₹25/kg"},
                {"name": "Brinjal", "demand": "medium", "price": "₹18/kg"},
                {"name": "Chilli", "demand": "high", "price": "₹40/kg"},
                {"name": "Groundnut", "demand": "high", "price": "₹55/kg"},
            ],
            "fruits": [
                {"name": "Mango", "demand": "high", "price": "₹60/kg"},
                {"name": "Papaya", "demand": "medium", "price": "₹22/kg"},
                {"name": "Guava", "demand": "medium", "price": "₹30/kg"},
            ],
            "flowers": [
                {"name": "Marigold", "demand": "high", "price": "₹20/kg"},
                {"name": "Rose", "demand": "high", "price": "₹80/kg"},
            ],
            "indoor": [
                {"name": "Aloe Vera", "demand": "medium", "price": "₹50/plant"},
                {"name": "Money Plant", "demand": "low", "price": "₹30/plant"},
            ]
        }
    },
    "Black Soil": {
        "features": {
            "en": "Rich in Calcium, Magnesium & Iron, low in Nitrogen & Phosphorus, high water retention, good for cotton & soybean, pH 7.5-8.5",
            "hi": "कैल्शियम, मैग्नीशियम और आयरन में समृद्ध, नाइट्रोजन और फास्फोरस में कम, उच्च जल धारण, कपास के लिए अच्छा",
            "te": "కాల్షియం, మెగ్నీషియం & ఇనుముతో సమృద్ధి, నైట్రోజన్ తక్కువ, నీటి నిలుపుదల అధికం, పత్తికి అనుకూలం"
        },
        "health_score": 7.8,
        "crops": {
            "vegetables": [
                {"name": "Onion", "demand": "high", "price": "₹30/kg"},
                {"name": "Garlic", "demand": "high", "price": "₹80/kg"},
                {"name": "Soybean", "demand": "high", "price": "₹45/kg"},
            ],
            "fruits": [
                {"name": "Banana", "demand": "high", "price": "₹35/dozen"},
                {"name": "Orange", "demand": "medium", "price": "₹40/kg"},
                {"name": "Sweet Lime", "demand": "medium", "price": "₹35/kg"},
            ],
            "flowers": [
                {"name": "Jasmine", "demand": "high", "price": "₹200/kg"},
                {"name": "Chrysanthemum", "demand": "medium", "price": "₹40/kg"},
            ],
            "indoor": [
                {"name": "Peace Lily", "demand": "medium", "price": "₹120/plant"},
                {"name": "Snake Plant", "demand": "high", "price": "₹80/plant"},
            ]
        }
    },
    "Loamy Soil": {
        "features": {
            "en": "Best soil type! Balanced mixture of sand, silt and clay, rich in nutrients, excellent water retention and drainage, pH 6.0-7.0",
            "hi": "सबसे अच्छी मिट्टी! रेत, गाद और मिट्टी का संतुलित मिश्रण, पोषक तत्वों से भरपूर, उत्कृष्ट जल धारण",
            "te": "అత్యుత్తమ మట్టి! ఇసుక, సిల్ట్ & క్లే సమతుల్య మిశ్రమం, పోషకాలతో సమృద్ధి, pH 6.0-7.0"
        },
        "health_score": 9.2,
        "crops": {
            "vegetables": [
                {"name": "Wheat", "demand": "high", "price": "₹22/kg"},
                {"name": "Potato", "demand": "high", "price": "₹20/kg"},
                {"name": "Cabbage", "demand": "medium", "price": "₹15/kg"},
                {"name": "Pea", "demand": "high", "price": "₹45/kg"},
            ],
            "fruits": [
                {"name": "Apple", "demand": "high", "price": "₹120/kg"},
                {"name": "Strawberry", "demand": "high", "price": "₹200/kg"},
                {"name": "Peach", "demand": "medium", "price": "₹80/kg"},
            ],
            "flowers": [
                {"name": "Sunflower", "demand": "high", "price": "₹25/kg"},
                {"name": "Dahlia", "demand": "medium", "price": "₹60/kg"},
                {"name": "Lily", "demand": "high", "price": "₹150/dozen"},
            ],
            "indoor": [
                {"name": "Pothos", "demand": "high", "price": "₹60/plant"},
                {"name": "ZZ Plant", "demand": "medium", "price": "₹150/plant"},
            ]
        }
    },
    "Sandy Soil": {
        "features": {
            "en": "Low nutrient retention, fast draining, low pH (5.0-6.0), needs frequent watering & fertilization, good for root vegetables",
            "hi": "कम पोषक तत्व धारण, तेजी से जल निकासी, कम pH (5.0-6.0), बार-बार सिंचाई और उर्वरक की जरूरत",
            "te": "తక్కువ పోషక నిలుపుదల, వేగంగా నీరు వెళ్ళిపోతుంది, pH 5.0-6.0, తరచుగా నీరు & ఎరువు అవసరం"
        },
        "health_score": 5.0,
        "crops": {
            "vegetables": [
                {"name": "Carrot", "demand": "medium", "price": "₹25/kg"},
                {"name": "Radish", "demand": "low", "price": "₹15/kg"},
                {"name": "Watermelon", "demand": "high", "price": "₹15/kg"},
                {"name": "Pumpkin", "demand": "medium", "price": "₹20/kg"},
            ],
            "fruits": [
                {"name": "Watermelon", "demand": "high", "price": "₹15/kg"},
                {"name": "Muskmelon", "demand": "medium", "price": "₹20/kg"},
            ],
            "flowers": [
                {"name": "Lavender", "demand": "medium", "price": "₹300/kg"},
                {"name": "Portulaca", "demand": "low", "price": "₹30/plant"},
            ],
            "indoor": [
                {"name": "Cactus", "demand": "medium", "price": "₹40/plant"},
                {"name": "Succulents", "demand": "high", "price": "₹50/plant"},
            ]
        }
    },
    "Clay Soil": {
        "features": {
            "en": "High nutrient content, poor drainage, heavy and sticky when wet, needs organic matter to improve structure, pH 6.0-7.5",
            "hi": "उच्च पोषक तत्व, खराब जल निकासी, गीला होने पर भारी और चिपचिपा, संरचना में सुधार के लिए जैविक पदार्थ की जरूरत",
            "te": "అధిక పోషకాలు, నీటి పారుదల తక్కువ, తడిగా ఉన్నప్పుడు భారంగా ఉంటుంది, సేంద్రీయ పదార్థం అవసరం"
        },
        "health_score": 6.8,
        "crops": {
            "vegetables": [
                {"name": "Rice", "demand": "high", "price": "₹35/kg"},
                {"name": "Broccoli", "demand": "medium", "price": "₹40/kg"},
                {"name": "Lettuce", "demand": "medium", "price": "₹30/kg"},
            ],
            "fruits": [
                {"name": "Plum", "demand": "medium", "price": "₹70/kg"},
                {"name": "Cherry", "demand": "high", "price": "₹300/kg"},
            ],
            "flowers": [
                {"name": "Iris", "demand": "medium", "price": "₹100/dozen"},
                {"name": "Aster", "demand": "low", "price": "₹40/kg"},
            ],
            "indoor": [
                {"name": "Fern", "demand": "medium", "price": "₹80/plant"},
                {"name": "Rubber Plant", "demand": "high", "price": "₹200/plant"},
            ]
        }
    },
    "Alluvial Soil": {
        "features": {
            "en": "Most fertile soil! Rich in potash, phosphoric acid & lime, excellent for agriculture, found near river banks, pH 7.0-8.0",
            "hi": "सबसे उपजाऊ मिट्टी! पोटाश, फॉस्फोरिक एसिड और चूने से भरपूर, कृषि के लिए उत्कृष्ट, नदी किनारों के पास पाई जाती है",
            "te": "అత్యంత సారవంతమైన మట్టి! పొటాష్, ఫాస్ఫోరిక్ ఆమ్లం & సున్నంతో సమృద్ధి, నదీ తీరాల దగ్గర"
        },
        "health_score": 9.5,
        "crops": {
            "vegetables": [
                {"name": "Sugarcane", "demand": "high", "price": "₹3.5/kg"},
                {"name": "Jute", "demand": "medium", "price": "₹42/kg"},
                {"name": "Maize", "demand": "high", "price": "₹20/kg"},
                {"name": "Mustard", "demand": "high", "price": "₹55/kg"},
            ],
            "fruits": [
                {"name": "Litchi", "demand": "high", "price": "₹80/kg"},
                {"name": "Mango", "demand": "high", "price": "₹60/kg"},
                {"name": "Jackfruit", "demand": "medium", "price": "₹25/kg"},
            ],
            "flowers": [
                {"name": "Tuberose", "demand": "high", "price": "₹60/kg"},
                {"name": "Gladiolus", "demand": "medium", "price": "₹80/dozen"},
            ],
            "indoor": [
                {"name": "Bamboo Plant", "demand": "high", "price": "₹100/plant"},
                {"name": "Peace Lily", "demand": "medium", "price": "₹120/plant"},
            ]
        }
    }
}

DISEASES = {
    "Tomato Late Blight": {
        "cause": "Fungal - Phytophthora infestans",
        "treatment": {
            "en": "Apply Copper Fungicide (Bordeaux mixture) every 7 days. Remove infected leaves immediately. Ensure good air circulation.",
            "hi": "हर 7 दिनों में कॉपर फंगीसाइड (बोर्डो मिश्रण) लगाएं। संक्रमित पत्तियों को तुरंत हटाएं।",
            "te": "ప్రతి 7 రోజులకు కాపర్ ఫంగీసైడ్ (బోర్డో మిశ్రమం) వేయండి. సోకిన ఆకులను వెంటనే తొలగించండి."
        },
        "organic": "Neem oil spray (5ml per litre water) every 5 days",
        "prevention": "Avoid overwatering, improve drainage, rotate crops annually",
        "confidence": 94
    },
    "Rice Blast": {
        "cause": "Fungal - Magnaporthe oryzae",
        "treatment": {
            "en": "Apply Tricyclazole or Carbendazim fungicide. Drain water from field for 3-4 days. Use resistant varieties.",
            "hi": "ट्राइसाइक्लाजोल या कार्बेंडाजिम कवकनाशी लगाएं। 3-4 दिनों के लिए खेत से पानी निकालें।",
            "te": "ట్రైసైక్లజోల్ లేదా కార్బెండాజిమ్ ఫంగీసైడ్ వేయండి. 3-4 రోజులు పొలం నుండి నీరు తీసివేయండి."
        },
        "organic": "Silicon-based spray, Trichoderma viride bio-fungicide",
        "prevention": "Avoid excess nitrogen, maintain proper spacing, use certified seeds",
        "confidence": 91
    },
    "Powdery Mildew": {
        "cause": "Fungal - Erysiphe cichoracearum",
        "treatment": {
            "en": "Apply Sulphur-based fungicide or Dinocap. Spray Wettable Sulphur 0.2% solution. Remove badly infected plants.",
            "hi": "सल्फर-आधारित कवकनाशी लगाएं। वेटेबल सल्फर 0.2% घोल स्प्रे करें। बुरी तरह संक्रमित पौधों को हटाएं।",
            "te": "సల్ఫర్ ఆధారిత ఫంగీసైడ్ వేయండి. వెట్టబుల్ సల్ఫర్ 0.2% ద్రావణం పిచికారీ చేయండి."
        },
        "organic": "Baking soda spray (1 tbsp per litre water), diluted milk spray",
        "prevention": "Ensure good air circulation, avoid overhead watering, plant resistant varieties",
        "confidence": 88
    },
    "Leaf Rust": {
        "cause": "Fungal - Puccinia species",
        "treatment": {
            "en": "Apply Mancozeb or Propiconazole fungicide. Start treatment at first sign of infection. Spray in the morning.",
            "hi": "मैन्कोजेब या प्रोपिकोनाजोल कवकनाशी लगाएं। संक्रमण के पहले संकेत पर उपचार शुरू करें।",
            "te": "మాంకోజెబ్ లేదా ప్రొపికోనజోల్ ఫంగీసైడ్ వేయండి. సోకిన మొదటి సంకేతంలోనే చికిత్స ప్రారంభించండి."
        },
        "organic": "Garlic extract spray, Compost tea application",
        "prevention": "Use rust-resistant varieties, remove crop debris, avoid dense planting",
        "confidence": 86
    },
    "Bacterial Wilt": {
        "cause": "Bacterial - Ralstonia solanacearum",
        "treatment": {
            "en": "No effective chemical cure. Remove and destroy infected plants. Apply Bleaching powder to soil. Use resistant varieties for next crop.",
            "hi": "कोई प्रभावी रासायनिक उपचार नहीं। संक्रमित पौधों को हटाएं और नष्ट करें। मिट्टी पर ब्लीचिंग पाउडर लगाएं।",
            "te": "ప్రభావవంతమైన రసాయన చికిత్స లేదు. సోకిన మొక్కలను తొలగించి నాశనం చేయండి. మట్టికి బ్లీచింగ్ పౌడర్ వేయండి."
        },
        "organic": "Trichoderma harzianum soil treatment, Pseudomonas fluorescens spray",
        "prevention": "Crop rotation, avoid waterlogging, use disease-free seeds and transplants",
        "confidence": 89
    }
}

QUICK_TIPS = {
    'en': [
        "💧 Water your crops in the early morning to reduce evaporation.",
        "🌱 Add compost to improve soil fertility naturally.",
        "🦟 Use neem oil spray as an organic pest repellent.",
        "📱 Take photos of your crops weekly to track growth.",
        "🌡️ Check weather forecasts before applying pesticides.",
    ],
    'hi': [
        "💧 वाष्पीकरण कम करने के लिए सुबह जल्दी फसलों को पानी दें।",
        "🌱 मिट्टी की उर्वरता प्राकृतिक रूप से सुधारने के लिए खाद डालें।",
        "🦟 नीम तेल स्प्रे को जैविक कीट विकर्षक के रूप में उपयोग करें।",
        "📱 विकास को ट्रैक करने के लिए साप्ताहिक फसलों की तस्वीरें लें।",
        "🌡️ कीटनाशक लगाने से पहले मौसम का पूर्वानुमान जांचें।",
    ],
    'te': [
        "💧 బాష్పీభవనం తగ్గించడానికి ఉదయాన్నే పంటలకు నీరు పెట్టండి.",
        "🌱 మట్టి సారతను సహజంగా మెరుగుపరచడానికి కంపోస్ట్ జోడించండి.",
        "🦟 సేంద్రీయ పురుగు నివారకంగా వేప నూనె స్ప్రే వాడండి.",
        "📱 పెరుగుదలను ట్రాక్ చేయడానికి వారానికోసారి పంట ఫోటోలు తీయండి.",
        "🌡️ పురుగుమందులు వేయడానికి ముందు వాతావరణ సూచనలు చెక్ చేయండి.",
    ]
}

# ─────────────────────────────────────────────
# SOIL CLASSIFICATION (rule-based simulation)
# ─────────────────────────────────────────────

import random

def classify_soil(image_path):
    """Simulates CNN soil classification. In production replace with real model."""
    soil_types = list(SOIL_DATA.keys())
    # In production: load TensorFlow model and predict
    # model = tf.keras.models.load_model('models/soil_model.h5')
    # img = preprocess_image(image_path)
    # prediction = model.predict(img)
    return random.choice(soil_types)

def detect_plant_disease(image_path):
    """Simulates CNN disease detection. In production replace with real model."""
    diseases = list(DISEASES.keys())
    return random.choice(diseases)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        farmer = Farmer.query.filter_by(email=email).first()
        if farmer and check_password_hash(farmer.password, password):
            login_user(farmer)
            session['language'] = farmer.language
            if not farmer.language or farmer.language == 'en':
                return redirect(url_for('select_language'))
            return redirect(url_for('home'))
        flash('Invalid email or password!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        state = request.form.get('state')
        district = request.form.get('district')
        if Farmer.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return render_template('register.html', states=list(STATES_DISTRICTS.keys()))
        farmer = Farmer(
            name=name, phone=phone, email=email,
            password=generate_password_hash(password),
            state=state, district=district
        )
        db.session.add(farmer)
        db.session.commit()
        login_user(farmer)
        return redirect(url_for('select_language'))
    return render_template('register.html', states=list(STATES_DISTRICTS.keys()), districts=STATES_DISTRICTS)

@app.route('/select-language', methods=['GET', 'POST'])
@login_required
def select_language():
    if request.method == 'POST':
        lang = request.form.get('language', 'en')
        session['language'] = lang
        current_user.language = lang
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('select_language.html')

@app.route('/home')
@login_required
def home():
    lang = session.get('language', 'en')
    tips = QUICK_TIPS.get(lang, QUICK_TIPS['en'])
    tip = random.choice(tips)
    total_analyses = SoilAnalysis.query.filter_by(farmer_id=current_user.id).count()
    total_detections = DiseaseDetection.query.filter_by(farmer_id=current_user.id).count()
    recent = SoilAnalysis.query.filter_by(farmer_id=current_user.id).order_by(SoilAnalysis.created_at.desc()).first()
    return render_template('home.html', tip=tip, total_analyses=total_analyses,
                           total_detections=total_detections, recent=recent)

@app.route('/crop-ideas', methods=['GET', 'POST'])
@login_required
def crop_ideas():
    result = None
    if request.method == 'POST':
        state = request.form.get('state')
        district = request.form.get('district')
        season = request.form.get('season')
        image = request.files.get('soil_image')
        if image and image.filename:
            filename = secure_filename(f"soil_{current_user.id}_{int(datetime.utcnow().timestamp())}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            soil_type = classify_soil(filepath)
            lang = session.get('language', 'en')
            soil_info = SOIL_DATA[soil_type]
            result = {
                'soil_type': soil_type,
                'features': soil_info['features'].get(lang, soil_info['features']['en']),
                'health_score': soil_info['health_score'],
                'crops': soil_info['crops'],
                'state': state,
                'district': district,
                'season': season,
                'image': filename
            }
            analysis = SoilAnalysis(
                farmer_id=current_user.id,
                soil_type=soil_type,
                state=state, district=district, season=season,
                image_path=filename,
                result=json.dumps(result)
            )
            db.session.add(analysis)
            db.session.commit()
    return render_template('crop_ideas.html', result=result,
                           states=list(STATES_DISTRICTS.keys()), districts=STATES_DISTRICTS)

@app.route('/disease-prediction', methods=['GET', 'POST'])
@login_required
def disease_prediction():
    result = None
    if request.method == 'POST':
        image = request.files.get('leaf_image')
        if image and image.filename:
            filename = secure_filename(f"leaf_{current_user.id}_{int(datetime.utcnow().timestamp())}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            disease_name = detect_plant_disease(filepath)
            lang = session.get('language', 'en')
            disease_info = DISEASES[disease_name]
            result = {
                'disease_name': disease_name,
                'cause': disease_info['cause'],
                'treatment': disease_info['treatment'].get(lang, disease_info['treatment']['en']),
                'organic': disease_info['organic'],
                'prevention': disease_info['prevention'],
                'confidence': disease_info['confidence'],
                'image': filename
            }
            detection = DiseaseDetection(
                farmer_id=current_user.id,
                image_path=filename,
                disease_name=disease_name,
                treatment=result['treatment']
            )
            db.session.add(detection)
            db.session.commit()
    return render_template('disease_prediction.html', result=result)

@app.route('/schemes')
@login_required
def schemes():
    scheme_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    query = GovernmentScheme.query.filter_by(is_active=True)
    if scheme_type != 'all':
        query = query.filter_by(scheme_type=scheme_type)
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(GovernmentScheme.name.contains(search))
    all_schemes = query.all()
    categories = db.session.query(GovernmentScheme.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('schemes.html', schemes=all_schemes, categories=categories,
                           selected_type=scheme_type, selected_category=category, search=search)

@app.route('/schemes/<int:scheme_id>')
@login_required
def scheme_detail(scheme_id):
    scheme = GovernmentScheme.query.get_or_404(scheme_id)
    lang = session.get('language', 'en')
    if lang == 'hi' and scheme.description_hi:
        scheme.display_name = scheme.name_hi or scheme.name
        scheme.display_desc = scheme.description_hi
    elif lang == 'te' and scheme.description_te:
        scheme.display_name = scheme.name_te or scheme.name
        scheme.display_desc = scheme.description_te
    else:
        scheme.display_name = scheme.name
        scheme.display_desc = scheme.description
    return render_template('scheme_detail.html', scheme=scheme)

@app.route('/help', methods=['GET', 'POST'])
@login_required
def help_contact():
    if request.method == 'POST':
        msg = ContactMessage(
            farmer_id=current_user.id,
            name=request.form.get('name'),
            email=request.form.get('email'),
            message=request.form.get('message')
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent successfully! We will respond soon.', 'success')
    return render_template('help.html')

@app.route('/profile')
@login_required
def profile():
    analyses = SoilAnalysis.query.filter_by(farmer_id=current_user.id).order_by(SoilAnalysis.created_at.desc()).limit(5).all()
    detections = DiseaseDetection.query.filter_by(farmer_id=current_user.id).order_by(DiseaseDetection.created_at.desc()).limit(5).all()
    return render_template('profile.html', analyses=analyses, detections=detections)

@app.route('/api/districts/<state>')
def get_districts(state):
    districts = STATES_DISTRICTS.get(state, [])
    return jsonify(districts)

@app.route('/set-language/<lang>')
@login_required
def set_language(lang):
    if lang in ['en', 'hi', 'te']:
        session['language'] = lang
        current_user.language = lang
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# ─────────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────────

@app.route('/admin')
@login_required
def admin():
    farmers = Farmer.query.all()
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    all_schemes = GovernmentScheme.query.all()
    return render_template('admin.html', farmers=farmers, messages=messages, schemes=all_schemes)

@app.route('/admin/add-scheme', methods=['POST'])
@login_required
def add_scheme():
    scheme = GovernmentScheme(
        name=request.form.get('name'),
        scheme_type=request.form.get('scheme_type'),
        category=request.form.get('category'),
        state=request.form.get('state', 'All'),
        description=request.form.get('description'),
        benefit=request.form.get('benefit'),
        eligibility=request.form.get('eligibility'),
        how_to_apply=request.form.get('how_to_apply'),
        documents=request.form.get('documents'),
        official_link=request.form.get('official_link'),
        last_date=request.form.get('last_date')
    )
    db.session.add(scheme)
    db.session.commit()
    flash('Scheme added successfully!', 'success')
    return redirect(url_for('admin'))

def seed_schemes():
    if GovernmentScheme.query.count() == 0:
        schemes_data = [
            {
                "name": "PM Kisan Samman Nidhi",
                "name_hi": "पीएम किसान सम्मान निधि",
                "name_te": "పీఎం కిసాన్ సమ్మాన్ నిధి",
                "scheme_type": "central",
                "category": "Financial Aid",
                "state": "All",
                "description": "Financial support of ₹6000 per year to all farmer families across India. Amount paid in 3 equal instalments of ₹2000 directly to bank accounts.",
                "description_hi": "भारत भर में सभी किसान परिवारों को प्रति वर्ष ₹6000 की वित्तीय सहायता। राशि सीधे बैंक खातों में ₹2000 की 3 समान किश्तों में भुगतान की जाती है।",
                "description_te": "భారతదేశంలోని అన్ని రైతు కుటుంబాలకు సంవత్సరానికి ₹6000 ఆర్థిక సహాయం. మొత్తం నేరుగా బ్యాంక్ ఖాతాలకు ₹2000 చొప్పున 3 సమాన వాయిదాలలో చెల్లించబడుతుంది.",
                "benefit": "₹6,000 per year (3 instalments of ₹2,000)",
                "eligibility": "All land-holding farmer families with cultivable land. Excludes institutional landholders, farmers with government jobs and income tax payers.",
                "how_to_apply": "Visit Common Service Centre or apply online at pmkisan.gov.in. Submit Aadhaar card, bank passbook and land records.",
                "documents": "Aadhaar Card, Bank Passbook, Land Records (Khasra/Khatauni), Mobile Number",
                "official_link": "https://pmkisan.gov.in",
                "last_date": "Ongoing"
            },
            {
                "name": "PM Fasal Bima Yojana",
                "name_hi": "प्रधानमंत्री फसल बीमा योजना",
                "name_te": "ప్రధానమంత్రి ఫసల్ బీమా యోజన",
                "scheme_type": "central",
                "category": "Crop Insurance",
                "state": "All",
                "description": "Comprehensive crop insurance scheme providing financial support to farmers suffering crop loss/damage due to unforeseen events like natural calamities, pests and diseases.",
                "description_hi": "प्राकृतिक आपदाओं, कीटों और बीमारियों जैसी अप्रत्याशित घटनाओं के कारण फसल हानि/क्षति से पीड़ित किसानों को वित्तीय सहायता प्रदान करने वाली व्यापक फसल बीमा योजना।",
                "description_te": "సహజ విపత్తులు, తెగుళ్ళు మరియు వ్యాధుల వంటి అనూహ్య సంఘటనల కారణంగా పంట నష్టం/నష్టం అనుభవిస్తున్న రైతులకు ఆర్థిక మద్దతు అందించే సమగ్ర పంట బీమా పథకం.",
                "benefit": "Up to ₹2 lakh compensation for crop loss. Premium: 2% for Kharif, 1.5% for Rabi crops.",
                "eligibility": "All farmers growing notified crops in notified areas. Both loanee and non-loanee farmers.",
                "how_to_apply": "Apply through nearest bank branch, CSC center or online at pmfby.gov.in before sowing.",
                "documents": "Land records, Bank account details, Aadhaar card, Sowing certificate",
                "official_link": "https://pmfby.gov.in",
                "last_date": "Before each sowing season"
            },
            {
                "name": "Kisan Credit Card (KCC)",
                "name_hi": "किसान क्रेडिट कार्ड",
                "name_te": "కిసాన్ క్రెడిట్ కార్డ్",
                "scheme_type": "central",
                "category": "Loans & Credit",
                "state": "All",
                "description": "Provides farmers with affordable credit for agriculture and allied activities. Interest rate of 4% per annum for loans up to ₹3 lakh with timely repayment.",
                "description_hi": "कृषि और संबद्ध गतिविधियों के लिए किसानों को किफायती ऋण प्रदान करता है। समय पर पुनर्भुगतान के साथ ₹3 लाख तक के ऋण पर 4% प्रति वर्ष की ब्याज दर।",
                "description_te": "వ్యవసాయం మరియు అనుబంధ కార్యకలాపాలకు రైతులకు సాధ్యమైనంత తక్కువ వడ్డీకి రుణం అందిస్తుంది. సకాలంలో చెల్లింపుతో ₹3 లక్షల వరకు రుణాలపై 4% వడ్డీ.",
                "benefit": "Loan up to ₹3 lakh at 4% interest rate per annum",
                "eligibility": "All farmers, sharecroppers, self-help groups and joint liability groups of farmers.",
                "how_to_apply": "Apply at nearest bank branch with land documents. Many banks offer online applications.",
                "documents": "Aadhaar card, Land records, Passport size photo, Bank account details",
                "official_link": "https://www.nabard.org",
                "last_date": "Ongoing"
            },
            {
                "name": "Soil Health Card Scheme",
                "name_hi": "मृदा स्वास्थ्य कार्ड योजना",
                "name_te": "మృదా ఆరోగ్య కార్డ్ పథకం",
                "scheme_type": "central",
                "category": "Soil Testing",
                "state": "All",
                "description": "Free soil testing service for farmers. Soil Health Card provides information on soil nutrient status and recommendations on appropriate dosage of nutrients to be applied.",
                "description_hi": "किसानों के लिए मुफ्त मृदा परीक्षण सेवा। मृदा स्वास्थ्य कार्ड मृदा पोषक तत्व की स्थिति और लागू किए जाने वाले पोषक तत्वों की उचित खुराक पर जानकारी प्रदान करता है।",
                "description_te": "రైతులకు ఉచిత మట్టి పరీక్షా సేవ. మృదా ఆరోగ్య కార్డ్ మట్టి పోషక స్థితిపై సమాచారం మరియు వర్తించాల్సిన పోషకాల సరైన మోతాదుపై సిఫార్సులు అందిస్తుంది.",
                "benefit": "Free soil testing, Personalized fertilizer recommendations, Improved crop yield",
                "eligibility": "All farmers in India",
                "how_to_apply": "Contact nearest agriculture department office or Krishi Vigyan Kendra for soil testing.",
                "documents": "Aadhaar card, Land details",
                "official_link": "https://soilhealth.dac.gov.in",
                "last_date": "Ongoing"
            },
            {
                "name": "PM Krishi Sinchai Yojana",
                "name_hi": "प्रधानमंत्री कृषि सिंचाई योजना",
                "name_te": "ప్రధానమంత్రి కృషి సించాయ్ యోజన",
                "scheme_type": "central",
                "category": "Water & Irrigation",
                "state": "All",
                "description": "Ensures access to protective irrigation to all agricultural farms to produce more crops per drop of water. Focuses on Har Khet Ko Pani and More Crop Per Drop.",
                "description_hi": "पानी की प्रत्येक बूंद पर अधिक फसल उत्पादन के लिए सभी कृषि खेतों को सुरक्षात्मक सिंचाई की पहुंच सुनिश्चित करता है।",
                "description_te": "నీటి ప్రతి చుక్కకు ఎక్కువ పంట ఉత్పత్తి చేయడానికి అన్ని వ్యవసాయ పొలాలకు రక్షిత సేద్యపు నీటి సదుపాయం అందించడం.",
                "benefit": "55% subsidy on drip/sprinkler irrigation systems for small farmers",
                "eligibility": "All farmers. Higher subsidy for small and marginal farmers.",
                "how_to_apply": "Apply through state agriculture department or online portal.",
                "documents": "Land records, Aadhaar card, Bank account details",
                "official_link": "https://pmksy.gov.in",
                "last_date": "Ongoing"
            },
            {
                "name": "PM Kisan Mandhan Yojana",
                "name_hi": "पीएम किसान मानधन योजना",
                "name_te": "పీఎం కిసాన్ మాన్ ధన్ యోజన",
                "scheme_type": "central",
                "category": "Pension",
                "state": "All",
                "description": "Pension scheme for small and marginal farmers. Assured monthly pension of ₹3000 after attaining age of 60 years.",
                "description_hi": "छोटे और सीमांत किसानों के लिए पेंशन योजना। 60 वर्ष की आयु प्राप्त करने के बाद ₹3000 की सुनिश्चित मासिक पेंशन।",
                "description_te": "చిన్న మరియు సన్నకారు రైతులకు పెన్షన్ పథకం. 60 సంవత్సరాల వయస్సు చేరిన తర్వాత నెలకు ₹3000 హామీ పెన్షన్.",
                "benefit": "₹3,000 monthly pension after age 60",
                "eligibility": "Small and marginal farmers aged 18-40 years with cultivable land up to 2 hectares.",
                "how_to_apply": "Apply at nearest CSC center with land documents and Aadhaar.",
                "documents": "Aadhaar card, Land records, Bank passbook, Mobile number",
                "official_link": "https://maandhan.in",
                "last_date": "Ongoing"
            },
            {
                "name": "Rythu Bandhu Scheme",
                "name_hi": "रैतू बंधु योजना",
                "name_te": "రైతు బంధు పథకం",
                "scheme_type": "state",
                "category": "Financial Aid",
                "state": "Telangana",
                "description": "Telangana government's investment support scheme providing financial assistance of ₹10,000 per acre per season to all farmer landowners to meet agricultural investment needs.",
                "description_hi": "तेलंगाना सरकार की निवेश सहायता योजना जो कृषि निवेश की जरूरतों को पूरा करने के लिए सभी किसान भूमि मालिकों को प्रति एकड़ प्रति सीजन ₹10,000 की वित्तीय सहायता प्रदान करती है।",
                "description_te": "వ్యవసాయ పెట్టుబడి అవసరాలను తీర్చడానికి అన్ని రైతు భూమి యజమానులకు సీజన్‌కు ఎకరాకు ₹10,000 ఆర్థిక సహాయం అందించే తెలంగాణ ప్రభుత్వ పెట్టుబడి మద్దతు పథకం.",
                "benefit": "₹10,000 per acre per season (Kharif & Rabi)",
                "eligibility": "All farmer landowners in Telangana. Both small and large farmers.",
                "how_to_apply": "Automatic enrollment based on land records. Visit nearest agriculture office if not enrolled.",
                "documents": "Passbook/Pattadar Passbook, Aadhaar card, Bank account linked to Aadhaar",
                "official_link": "https://rythubandhu.telangana.gov.in",
                "last_date": "Each season"
            },
            {
                "name": "Rythu Bima",
                "name_hi": "रैतू बीमा",
                "name_te": "రైతు బీమా",
                "scheme_type": "state",
                "category": "Crop Insurance",
                "state": "Telangana",
                "description": "Life insurance scheme for farmers in Telangana. Provides ₹5 lakh insurance coverage to farmer families in case of farmer's death due to any reason.",
                "description_hi": "तेलंगाना में किसानों के लिए जीवन बीमा योजना। किसी भी कारण से किसान की मृत्यु होने पर किसान परिवारों को ₹5 लाख बीमा कवरेज प्रदान करती है।",
                "description_te": "తెలంగాణలో రైతులకు జీవిత బీమా పథకం. ఏదైనా కారణంతో రైతు మరణించినప్పుడు రైతు కుటుంబాలకు ₹5 లక్షల బీమా కవరేజ్ అందిస్తుంది.",
                "benefit": "₹5 lakh life insurance coverage",
                "eligibility": "All farmers between 18-59 years of age who are Rythu Bandhu beneficiaries in Telangana.",
                "how_to_apply": "Automatic enrollment for Rythu Bandhu beneficiaries. Premium paid by state government.",
                "documents": "Rythu Bandhu passbook, Aadhaar card",
                "official_link": "https://rythubandhu.telangana.gov.in",
                "last_date": "Ongoing"
            },
            {
                "name": "eNAM - National Agriculture Market",
                "name_hi": "eNAM - राष्ट्रीय कृषि बाजार",
                "name_te": "eNAM - జాతీయ వ్యవసాయ మార్కెట్",
                "scheme_type": "central",
                "category": "Market Access",
                "state": "All",
                "description": "Online trading platform for agricultural commodities. Farmers can sell their produce online to get best market price across India without middlemen.",
                "description_hi": "कृषि वस्तुओं के लिए ऑनलाइन ट्रेडिंग प्लेटफॉर्म। किसान बिचौलियों के बिना पूरे भारत में सर्वोत्तम बाजार मूल्य पाने के लिए अपनी उपज ऑनलाइन बेच सकते हैं।",
                "description_te": "వ్యవసాయ వస్తువుల కోసం ఆన్‌లైన్ వ్యాపార వేదిక. రైతులు దళారులు లేకుండా భారతదేశం అంతటా అత్యుత్తమ మార్కెట్ ధర పొందేందుకు తమ ఉత్పత్తులను ఆన్‌లైన్‌లో విక్రయించవచ్చు.",
                "benefit": "Better price realization, transparent trading, reduced middlemen",
                "eligibility": "All farmers with produce to sell",
                "how_to_apply": "Register at enam.gov.in or visit nearest APMC market.",
                "documents": "Aadhaar card, Bank account details, Mobile number",
                "official_link": "https://enam.gov.in",
                "last_date": "Ongoing"
            },
            {
                "name": "Paramparagat Krishi Vikas Yojana",
                "name_hi": "परम्परागत कृषि विकास योजना",
                "name_te": "పరంపరాగత కృషి వికాస యోజన",
                "scheme_type": "central",
                "category": "Organic Farming",
                "state": "All",
                "description": "Promotes organic farming through cluster based approach. Provides financial assistance for organic farming, certification and marketing of organic produce.",
                "description_hi": "क्लस्टर आधारित दृष्टिकोण के माध्यम से जैविक खेती को बढ़ावा देता है। जैविक खेती, प्रमाणीकरण और जैविक उत्पाद के विपणन के लिए वित्तीय सहायता प्रदान करता है।",
                "description_te": "క్లస్టర్ ఆధారిత విధానం ద్వారా సేంద్రీయ వ్యవసాయాన్ని ప్రోత్సహిస్తుంది. సేంద్రీయ వ్యవసాయం, ధృవీకరణ మరియు సేంద్రీయ ఉత్పత్తుల మార్కెటింగ్‌కు ఆర్థిక సహాయం అందిస్తుంది.",
                "benefit": "₹50,000 per hectare for 3 years, organic certification support",
                "eligibility": "Farmers willing to adopt organic farming practices. Group of minimum 50 farmers.",
                "how_to_apply": "Contact nearest Krishi Vigyan Kendra or agriculture department.",
                "documents": "Aadhaar card, Land records, Group formation certificate",
                "official_link": "https://pgsindia-ncof.gov.in",
                "last_date": "Ongoing"
            },
        ]
        for s in schemes_data:
            scheme = GovernmentScheme(**s)
            db.session.add(scheme)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_schemes()

if __name__ == '__main__':
    app.run(debug=False)