from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime, timedelta
import functools

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add datetime to template context
@app.context_processor
def inject_datetime():
    return {'now': datetime.now(), 'timedelta': timedelta}

# Helper function to parse datetime from various formats
def parse_datetime(dt_string):
    if not dt_string:
        return None
    if isinstance(dt_string, datetime):
        return dt_string
    
    # Try different datetime formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_string, fmt)
        except ValueError:
            continue
    
    # If no format matches, return current time as fallback
    return datetime.now()

# Add custom template filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags"""
    if text is None:
        return ''
    return text.replace('\n', '<br>\n')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'rar'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database initialization
def init_db():
    conn = sqlite3.connect('assignment_management.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('student', 'teacher')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            deadline TIMESTAMP NOT NULL,
            max_marks INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            attachment_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Create submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            submission_text TEXT,
            file_path TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            marks INTEGER,
            feedback TEXT,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id),
            FOREIGN KEY (student_id) REFERENCES users (id),
            UNIQUE(assignment_id, student_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Decorator for login required
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for teacher access
def teacher_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'teacher':
            flash('Teacher access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('assignment_management.db')
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        if session['user_type'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            flash('Login successful!', 'success')
            
            if user['user_type'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                                   (username, email)).fetchone()
        conn.close()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   (username, email, password_hash, user_type))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/teacher/dashboard')
@login_required
@teacher_required
def teacher_dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get assignments created by this teacher
    assignments = conn.execute('''
        SELECT a.*, COUNT(s.id) as submission_count
        FROM assignments a
        LEFT JOIN submissions s ON a.id = s.assignment_id
        WHERE a.teacher_id = ?
        GROUP BY a.id
        ORDER BY a.created_at DESC
    ''', (user_id,)).fetchall()
    
    # Convert datetime strings to datetime objects
    assignments_list = []
    for assignment in assignments:
        assignment_dict = dict(assignment)
        # Convert deadline to datetime object
        assignment_dict['deadline'] = parse_datetime(assignment_dict['deadline'])
        # Convert created_at to datetime object
        assignment_dict['created_at'] = parse_datetime(assignment_dict['created_at'])
        assignments_list.append(assignment_dict)
    
    # Get statistics
    total_assignments = len(assignments_list)
    total_submissions = conn.execute('''
        SELECT COUNT(*) FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE a.teacher_id = ?
    ''', (user_id,)).fetchone()[0]
    
    pending_submissions = conn.execute('''
        SELECT COUNT(*) FROM assignments a
        LEFT JOIN submissions s ON a.id = s.assignment_id
        WHERE a.teacher_id = ? AND s.id IS NULL AND a.deadline > datetime('now')
    ''', (user_id,)).fetchone()[0]
    
    overdue_assignments = conn.execute('''
        SELECT COUNT(*) FROM assignments a
        LEFT JOIN submissions s ON a.id = s.assignment_id
        WHERE a.teacher_id = ? AND s.id IS NULL AND a.deadline < datetime('now')
    ''', (user_id,)).fetchone()[0]
    
    conn.close()
    
    return render_template('teacher_dashboard.html', 
                         assignments=assignments_list,
                         total_assignments=total_assignments,
                         total_submissions=total_submissions,
                         pending_submissions=pending_submissions,
                         overdue_assignments=overdue_assignments)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get all assignments
    assignments = conn.execute('''
        SELECT a.*, s.submitted_at, s.marks, s.file_path as submission_file
        FROM assignments a
        LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = ?
        ORDER BY a.deadline ASC
    ''', (user_id,)).fetchall()
    
    # Convert datetime strings to datetime objects
    assignments_list = []
    for assignment in assignments:
        assignment_dict = dict(assignment)
        # Convert deadline to datetime object
        assignment_dict['deadline'] = parse_datetime(assignment_dict['deadline'])
        # Convert submitted_at to datetime object
        assignment_dict['submitted_at'] = parse_datetime(assignment_dict['submitted_at'])
        assignments_list.append(assignment_dict)
    
    # Calculate statistics
    total_assignments = len(assignments_list)
    submitted_assignments = len([a for a in assignments_list if a['submitted_at']])
    pending_assignments = len([a for a in assignments_list if not a['submitted_at'] and a['deadline'] > datetime.now()])
    overdue_assignments = len([a for a in assignments_list if not a['submitted_at'] and a['deadline'] < datetime.now()])
    
    conn.close()
    
    return render_template('student_dashboard.html',
                         assignments=assignments_list,
                         total_assignments=total_assignments,
                         submitted_assignments=submitted_assignments,
                         pending_assignments=pending_assignments,
                         overdue_assignments=overdue_assignments)

@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assignment():
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        description = request.form['description']
        deadline = request.form['deadline']
        max_marks = request.form['max_marks']
        
        # Handle file upload
        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(attachment_path)
        
        # Create assignment
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO assignments (title, subject, description, deadline, max_marks, teacher_id, attachment_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, subject, description, deadline, max_marks, session['user_id'], attachment_path))
        conn.commit()
        conn.close()
        
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('create_assignment.html')

@app.route('/edit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assignment(assignment_id):
    conn = get_db_connection()
    
    # Get assignment and verify ownership
    assignment = conn.execute('SELECT * FROM assignments WHERE id = ? AND teacher_id = ?',
                            (assignment_id, session['user_id'])).fetchone()
    
    if not assignment:
        conn.close()
        flash('Assignment not found', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        description = request.form['description']
        deadline = request.form['deadline']
        max_marks = request.form['max_marks']
        
        conn.execute('''
            UPDATE assignments 
            SET title = ?, subject = ?, description = ?, deadline = ?, max_marks = ?
            WHERE id = ?
        ''', (title, subject, description, deadline, max_marks, assignment_id))
        conn.commit()
        conn.close()
        
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    conn.close()
    return render_template('edit_assignment.html', assignment=assignment)

@app.route('/delete_assignment/<int:assignment_id>')
@login_required
@teacher_required
def delete_assignment(assignment_id):
    conn = get_db_connection()
    
    # Verify ownership
    assignment = conn.execute('SELECT * FROM assignments WHERE id = ? AND teacher_id = ?',
                            (assignment_id, session['user_id'])).fetchone()
    
    if assignment:
        # Delete associated submissions first
        conn.execute('DELETE FROM submissions WHERE assignment_id = ?', (assignment_id,))
        
        # Delete assignment
        conn.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
        conn.commit()
        flash('Assignment deleted successfully!', 'success')
    else:
        flash('Assignment not found', 'error')
    
    conn.close()
    return redirect(url_for('teacher_dashboard'))

@app.route('/view_assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    conn = get_db_connection()
    
    # Get assignment details
    assignment = conn.execute('''
        SELECT a.*, u.username as teacher_name
        FROM assignments a
        JOIN users u ON a.teacher_id = u.id
        WHERE a.id = ?
    ''', (assignment_id,)).fetchone()
    
    if not assignment:
        conn.close()
        flash('Assignment not found', 'error')
        return redirect(url_for('home'))
    
    # Convert assignment datetime strings to datetime objects
    assignment_dict = dict(assignment)
    assignment_dict['deadline'] = parse_datetime(assignment_dict['deadline'])
    assignment_dict['created_at'] = parse_datetime(assignment_dict['created_at'])
    
    # Get submissions if teacher
    submissions = None
    if session['user_type'] == 'teacher':
        submissions_raw = conn.execute('''
            SELECT s.*, u.username as student_name
            FROM submissions s
            JOIN users u ON s.student_id = u.id
            WHERE s.assignment_id = ?
            ORDER BY s.submitted_at DESC
        ''', (assignment_id,)).fetchall()
        
        # Convert submission datetime strings to datetime objects
        submissions_list = []
        for submission in submissions_raw:
            submission_dict = dict(submission)
            submission_dict['submitted_at'] = parse_datetime(submission_dict['submitted_at'])
            submissions_list.append(submission_dict)
        submissions = submissions_list
    else:
        # Get student's submission
        submission_raw = conn.execute('''
            SELECT * FROM submissions
            WHERE assignment_id = ? AND student_id = ?
        ''', (assignment_id, session['user_id'])).fetchone()
        
        if submission_raw:
            submission_dict = dict(submission_raw)
            submission_dict['submitted_at'] = parse_datetime(submission_dict['submitted_at'])
            submissions = submission_dict
    
    conn.close()
    
    return render_template('view_assignment.html', 
                         assignment=assignment_dict, 
                         submissions=submissions)

@app.route('/submit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    conn = get_db_connection()
    
    # Get assignment details
    assignment = conn.execute('SELECT * FROM assignments WHERE id = ?', (assignment_id,)).fetchone()
    
    if not assignment:
        conn.close()
        flash('Assignment not found', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Check if deadline has passed
    if assignment['deadline'] < datetime.now():
        flash('Assignment deadline has passed. Late submissions are not allowed.', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Check if already submitted
    existing_submission = conn.execute('''
        SELECT * FROM submissions WHERE assignment_id = ? AND student_id = ?
    ''', (assignment_id, session['user_id'])).fetchone()
    
    if existing_submission:
        conn.close()
        flash('You have already submitted this assignment', 'info')
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    if request.method == 'POST':
        submission_text = request.form.get('submission_text', '')
        file_path = None
        
        # Handle file upload
        if 'submission_file' in request.files:
            file = request.files['submission_file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
        
        # Create submission
        conn.execute('''
            INSERT INTO submissions (assignment_id, student_id, submission_text, file_path)
            VALUES (?, ?, ?, ?)
        ''', (assignment_id, session['user_id'], submission_text, file_path))
        conn.commit()
        conn.close()
        
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    conn.close()
    return render_template('submit_assignment.html', assignment=assignment)

@app.route('/grade_submission/<int:submission_id>', methods=['POST'])
@login_required
@teacher_required
def grade_submission(submission_id):
    conn = get_db_connection()
    
    # Verify teacher owns this assignment
    submission = conn.execute('''
        SELECT s.*, a.teacher_id
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.id = ? AND a.teacher_id = ?
    ''', (submission_id, session['user_id'])).fetchone()
    
    if submission:
        marks = request.form['marks']
        feedback = request.form.get('feedback', '')
        
        conn.execute('''
            UPDATE submissions SET marks = ?, feedback = ?
            WHERE id = ?
        ''', (marks, feedback, submission_id))
        conn.commit()
        flash('Submission graded successfully!', 'success')
    else:
        flash('Submission not found', 'error')
    
    conn.close()
    return redirect(request.referrer or url_for('teacher_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
