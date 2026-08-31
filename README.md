# 🎓 Student Performance & Gamification System

A complete web application that connects an HTML frontend to a Python (Flask) backend to track, predict, and gamify student performance across multiple dimensions.

## ✨ Features

### 📊 Performance Tracking
- **Academic Performance** (GPA) - 35% weight
- **Attendance** - 15% weight
- **Sports Performance** - 10% weight
- **Extra Curricular Activities** (NSS, NCC, Events, Certified Courses) - 15% weight
- **Core Competition & Projects** (Internships, Technical Projects) - 15% weight
- **Improvement Trend** (GPA growth) - 10% weight

### 🏆 Gamification
- **Dynamic Ranking System** - Auto-calculated based on weighted scores
- **Badge System** - Platinum, Gold, Silver, Bronze, Rookie
- **Level System** - Levels 1-5 based on overall score
- **Achievement Badges** - Category-specific badges (Academic Excellence, Sports Star, etc.)
- **Leaderboard** - Visual podium and ranked list
- **Progress Bars** - Visual score representation

### 🤖 Predictions & Insights
- **Attendance Warnings** - Alerts for low attendance
- **GPA Trend Analysis** - Tracks improvement/decline
- **Potential Score Prediction** - Shows achievable score with improvements
- **Personalized Suggestions** - Recommendations for weak areas

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

## 📁 Project Structure
```
student_performance_system/
├── app.py                  # Main Flask backend
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html         # Dashboard with stats & rankings
│   ├── add_student.html   # Student registration form
│   ├── student_detail.html # Profile with charts & predictions
│   └── rankings.html      # Full leaderboard page
└── static/                # CSS/JS assets (optional)
```

## 🎯 Scoring Algorithm

The system uses a weighted scoring algorithm:

| Category | Weight | Max Score |
|----------|--------|-----------|
| Academic (GPA) | 35% | 100 |
| Attendance | 15% | 100 |
| Sports | 10% | 100 |
| Extra Curricular | 15% | 100 |
| Core Competition | 15% | 100 |
| Improvement | 10% | 100 |

**Total Score = Σ(Category Score × Weight)**

### Badge Thresholds
- **Platinum** (Lvl 5): 90-100
- **Gold** (Lvl 4): 80-89
- **Silver** (Lvl 3): 70-79
- **Bronze** (Lvl 2): 60-69
- **Rookie** (Lvl 1): Below 60

## 🛠️ Tech Stack
- **Backend**: Python, Flask, SQLAlchemy (SQLite)
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Database**: SQLite (auto-created)

## 📋 Sample Data
The system comes with 5 pre-loaded sample students to demonstrate functionality.

## 🔮 Future Enhancements
- Machine Learning prediction models
- Department-wise leaderboards
- Export reports to PDF/Excel
- Admin authentication
- Real-time notifications
