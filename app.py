
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer, default=1)

    # Academic Performance
    semester_gpa = db.Column(db.Float, default=0.0)  # Out of 10
    previous_gpa = db.Column(db.Float, default=0.0)

    # Attendance
    attendance_percentage = db.Column(db.Float, default=0.0)

    # Sports (0-100 score)
    sports_score = db.Column(db.Float, default=0.0)
    sports_achievements = db.Column(db.String(500), default="")

    # Extra Curricular Activities
    nss_participation = db.Column(db.Boolean, default=False)
    ncc_participation = db.Column(db.Boolean, default=False)
    events_participated = db.Column(db.Integer, default=0)
    events_won = db.Column(db.Integer, default=0)
    certified_courses = db.Column(db.Integer, default=0)

    # Core Competition / Course Related
    core_competition_score = db.Column(db.Float, default=0.0)
    projects_completed = db.Column(db.Integer, default=0)
    internships = db.Column(db.Integer, default=0)

    # Gamification
    total_score = db.Column(db.Float, default=0.0)
    rank = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(50), default="Bronze")
    level = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== SCORING ALGORITHM ====================

def calculate_performance_score(student):
    """
    Weighted scoring system for overall student performance
    """
    # Weights
    WEIGHTS = {
        'academic': 0.35,
        'attendance': 0.15,
        'sports': 0.10,
        'extracurricular': 0.15,
        'core_competition': 0.15,
        'improvement': 0.10
    }

    # 1. Academic Score (0-100)
    academic_score = (student.semester_gpa / 10.0) * 100

    # 2. Attendance Score (already percentage)
    attendance_score = student.attendance_percentage

    # 3. Sports Score (0-100)
    sports_score = min(student.sports_score, 100)

    # 4. Extra Curricular Score (0-100)
    ec_score = 0
    if student.nss_participation: ec_score += 15
    if student.ncc_participation: ec_score += 15
    ec_score += min(student.events_participated * 5, 30)
    ec_score += min(student.events_won * 10, 20)
    ec_score += min(student.certified_courses * 5, 20)
    ec_score = min(ec_score, 100)

    # 5. Core Competition Score (0-100)
    cc_score = min(student.core_competition_score, 100)
    cc_score += min(student.projects_completed * 10, 30)
    cc_score += min(student.internships * 15, 20)
    cc_score = min(cc_score, 100)

    # 6. Improvement Score (based on GPA trend)
    improvement = 0
    if student.previous_gpa > 0:
        diff = student.semester_gpa - student.previous_gpa
        improvement = max(0, (diff / student.previous_gpa) * 100) if student.previous_gpa > 0 else 0
    improvement = min(improvement, 100)

    # Calculate weighted total
    total = (
        academic_score * WEIGHTS['academic'] +
        attendance_score * WEIGHTS['attendance'] +
        sports_score * WEIGHTS['sports'] +
        ec_score * WEIGHTS['extracurricular'] +
        cc_score * WEIGHTS['core_competition'] +
        improvement * WEIGHTS['improvement']
    )

    return round(total, 2)

def assign_badge_and_level(score):
    """Gamification: Assign badges and levels based on score"""
    if score >= 90:
        return "Platinum", 5
    elif score >= 80:
        return "Gold", 4
    elif score >= 70:
        return "Silver", 3
    elif score >= 60:
        return "Bronze", 2
    else:
        return "Rookie", 1

def get_category_badges(student):
    """Return category-specific achievement badges"""
    badges = []

    if student.semester_gpa >= 9.0:
        badges.append({"name": "Academic Excellence", "icon": "🎓", "color": "#FFD700"})
    elif student.semester_gpa >= 8.0:
        badges.append({"name": "Scholar", "icon": "📚", "color": "#C0C0C0"})

    if student.attendance_percentage >= 95:
        badges.append({"name": "Perfect Attendance", "icon": "⭐", "color": "#FF6B6B"})
    elif student.attendance_percentage >= 85:
        badges.append({"name": "Regular", "icon": "📅", "color": "#4ECDC4"})

    if student.sports_score >= 80:
        badges.append({"name": "Sports Star", "icon": "🏆", "color": "#FFD700"})
    elif student.sports_score >= 60:
        badges.append({"name": "Athlete", "icon": "⚽", "color": "#95E1D3"})

    if student.nss_participation or student.ncc_participation:
        badges.append({"name": "National Service", "icon": "🇮🇳", "color": "#FF7675"})

    if student.events_won >= 3:
        badges.append({"name": "Event Champion", "icon": "🥇", "color": "#FFD700"})
    elif student.events_participated >= 5:
        badges.append({"name": "Active Participant", "icon": "🎯", "color": "#74B9FF"})

    if student.certified_courses >= 3:
        badges.append({"name": "Certified Pro", "icon": "📜", "color": "#A29BFE"})

    if student.projects_completed >= 3:
        badges.append({"name": "Project Master", "icon": "💻", "color": "#FD79A8"})
    elif student.internships >= 1:
        badges.append({"name": "Industry Ready", "icon": "🚀", "color": "#FDCB6E"})

    return badges

def predict_performance(student):
    """Simple prediction model for performance improvement"""
    predictions = []

    # Attendance warning
    if student.attendance_percentage < 75:
        predictions.append({
            "type": "warning",
            "message": "Low attendance may affect academic performance. Target: >85%",
            "impact": "High"
        })

    # GPA trend
    if student.previous_gpa > 0:
        trend = student.semester_gpa - student.previous_gpa
        if trend < 0:
            predictions.append({
                "type": "warning",
                "message": f"GPA declining by {abs(trend):.2f} points. Focus on weak subjects.",
                "impact": "High"
            })
        elif trend > 0.5:
            predictions.append({
                "type": "success",
                "message": f"Excellent improvement! GPA up by {trend:.2f} points. Keep it up!",
                "impact": "Positive"
            })

    # Suggestions based on weak areas
    if student.sports_score < 40:
        predictions.append({
            "type": "info",
            "message": "Consider joining sports clubs to improve overall fitness score.",
            "impact": "Medium"
        })

    if student.certified_courses == 0:
        predictions.append({
            "type": "info",
            "message": "Adding certified courses can boost your ranking by 10-15%.",
            "impact": "Medium"
        })

    if student.events_participated < 3:
        predictions.append({
            "type": "info",
            "message": "Participate in more events to improve extracurricular score.",
            "impact": "Low"
        })

    # Overall prediction
    current = calculate_performance_score(student)
    potential = current
    if student.attendance_percentage < 85:
        potential += 5
    if student.certified_courses < 2:
        potential += 3
    if student.events_participated < 3:
        potential += 2

    predictions.append({
        "type": "prediction",
        "message": f"Current Score: {current:.1f} | Predicted Potential: {min(potential, 100):.1f}",
        "impact": "Analysis"
    })

    return predictions

def update_all_rankings():
    """Recalculate all student rankings"""
    students = Student.query.all()

    # Calculate scores
    for student in students:
        student.total_score = calculate_performance_score(student)
        student.badge, student.level = assign_badge_and_level(student.total_score)

    db.session.commit()

    # Sort and assign ranks
    students_sorted = sorted(students, key=lambda x: x.total_score, reverse=True)
    for idx, student in enumerate(students_sorted, 1):
        student.rank = idx

    db.session.commit()

# ==================== ROUTES ====================

@app.route('/')
def dashboard():
    students = Student.query.order_by(Student.rank).all()
    top_performers = Student.query.order_by(Student.total_score.desc()).limit(5).all()

    stats = {
        'total_students': Student.query.count(),
        'avg_score': round(db.session.query(db.func.avg(Student.total_score)).scalar() or 0, 2),
        'platinum_count': Student.query.filter(Student.badge == 'Platinum').count(),
        'gold_count': Student.query.filter(Student.badge == 'Gold').count(),
        'attendance_avg': round(db.session.query(db.func.avg(Student.attendance_percentage)).scalar() or 0, 1)
    }

    return render_template('index.html', students=students, top_performers=top_performers, stats=stats)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            roll_number=request.form['roll_number'],
            department=request.form['department'],
            year=int(request.form['year']),
            semester_gpa=float(request.form['semester_gpa']),
            previous_gpa=float(request.form.get('previous_gpa', 0)),
            attendance_percentage=float(request.form['attendance_percentage']),
            sports_score=float(request.form.get('sports_score', 0)),
            sports_achievements=request.form.get('sports_achievements', ''),
            nss_participation='nss_participation' in request.form,
            ncc_participation='ncc_participation' in request.form,
            events_participated=int(request.form.get('events_participated', 0)),
            events_won=int(request.form.get('events_won', 0)),
            certified_courses=int(request.form.get('certified_courses', 0)),
            core_competition_score=float(request.form.get('core_competition_score', 0)),
            projects_completed=int(request.form.get('projects_completed', 0)),
            internships=int(request.form.get('internships', 0))
        )

        db.session.add(student)
        db.session.commit()
        update_all_rankings()

        return redirect(url_for('dashboard'))

    return render_template('add_student.html')

@app.route('/student/<int:id>')
def student_detail(id):
    student = Student.query.get_or_404(id)
    badges = get_category_badges(student)
    predictions = predict_performance(student)

    # Calculate individual category scores for chart
    category_scores = {
        'Academic': round((student.semester_gpa / 10) * 100, 1),
        'Attendance': round(student.attendance_percentage, 1),
        'Sports': round(student.sports_score, 1),
        'Extra Curricular': round(min(
            (15 if student.nss_participation else 0) +
            (15 if student.ncc_participation else 0) +
            min(student.events_participated * 5, 30) +
            min(student.events_won * 10, 20) +
            min(student.certified_courses * 5, 20), 100
        ), 1),
        'Core Competition': round(min(student.core_competition_score + 
            min(student.projects_completed * 10, 30) +
            min(student.internships * 15, 20), 100), 1)
    }

    return render_template('student_detail.html', student=student, badges=badges, 
                          predictions=predictions, category_scores=category_scores)

@app.route('/rankings')
def rankings():
    students = Student.query.order_by(Student.rank).all()
    return render_template('rankings.html', students=students)

@app.route('/api/students')
def api_students():
    students = Student.query.order_by(Student.rank).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'roll_number': s.roll_number,
        'department': s.department,
        'total_score': s.total_score,
        'rank': s.rank,
        'badge': s.badge,
        'level': s.level,
        'semester_gpa': s.semester_gpa,
        'attendance_percentage': s.attendance_percentage
    } for s in students])

@app.route('/api/leaderboard')
def api_leaderboard():
    top = Student.query.order_by(Student.total_score.desc()).limit(10).all()
    return jsonify([{
        'name': s.name,
        'score': s.total_score,
        'badge': s.badge,
        'department': s.department
    } for s in top])

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    update_all_rankings()
    return redirect(url_for('dashboard'))

# ==================== INITIALIZATION ====================

with app.app_context():
    db.create_all()

    # Add sample data if empty
    if Student.query.count() == 0:
        sample_students = [
            Student(name="Arun Kumar", roll_number="CS2024001", department="Computer Science", year=3,
                   semester_gpa=9.2, previous_gpa=8.8, attendance_percentage=94,
                   sports_score=85, sports_achievements="Inter-college Basketball Winner",
                   nss_participation=True, ncc_participation=False,
                   events_participated=8, events_won=4, certified_courses=4,
                   core_competition_score=88, projects_completed=5, internships=2),

            Student(name="Priya Sharma", roll_number="EC2024002", department="Electronics", year=2,
                   semester_gpa=8.5, previous_gpa=8.0, attendance_percentage=91,
                   sports_score=60, sports_achievements="College Badminton Team",
                   nss_participation=False, ncc_participation=True,
                   events_participated=5, events_won=2, certified_courses=3,
                   core_competition_score=75, projects_completed=3, internships=1),

            Student(name="Rahul Verma", roll_number="ME2024003", department="Mechanical", year=4,
                   semester_gpa=7.8, previous_gpa=7.5, attendance_percentage=82,
                   sports_score=95, sports_achievements="State Level Football Player",
                   nss_participation=True, ncc_participation=True,
                   events_participated=10, events_won=6, certified_courses=2,
                   core_competition_score=70, projects_completed=4, internships=1),

            Student(name="Sneha Patel", roll_number="CS2024004", department="Computer Science", year=2,
                   semester_gpa=9.5, previous_gpa=9.0, attendance_percentage=98,
                   sports_score=45, sports_achievements="",
                   nss_participation=False, ncc_participation=False,
                   events_participated=6, events_won=3, certified_courses=5,
                   core_competition_score=92, projects_completed=6, internships=2),

            Student(name="Vikram Rao", roll_number="CV2024005", department="Civil", year=3,
                   semester_gpa=6.5, previous_gpa=7.0, attendance_percentage=68,
                   sports_score=70, sports_achievements="Athletics Participant",
                   nss_participation=True, ncc_participation=False,
                   events_participated=3, events_won=0, certified_courses=1,
                   core_competition_score=55, projects_completed=2, internships=0),
        ]

        for s in sample_students:
            db.session.add(s)
        db.session.commit()
        update_all_rankings()
        print("Sample data added!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
