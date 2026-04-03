# Assignment Management System

A comprehensive web application for managing assignments between teachers and students. Built with Flask (Python), HTML, CSS, JavaScript, and SQLite database.

## Features

### For Teachers
- ✅ Create new assignments with title, subject, description, deadline, and marks
- ✅ Edit existing assignments
- ✅ Delete assignments
- ✅ Upload assignment attachments
- ✅ View all student submissions
- ✅ Grade assignments with feedback
- ✅ Track submission statistics

### For Students
- ✅ View all available assignments
- ✅ Submit assignments with text and/or file attachments
- ✅ Track submission status
- ✅ View grades and feedback
- ✅ See deadline warnings

### General Features
- 🔐 Secure user authentication (login/signup)
- 🔒 Password hashing with Werkzeug
- 📱 Responsive design for all devices
- 🎨 Modern UI with Bootstrap 5
- 📊 Dashboard with statistics
- 🔍 Search and filter functionality
- 📁 File upload support (PDF, DOC, Images, ZIP)
- ⏰ Deadline tracking
- 💬 Flash messages for notifications

## Project Structure

```
Assignment.11/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── assignment_management.db # SQLite database (created automatically)
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── home.html           # Home page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── teacher_dashboard.html    # Teacher dashboard
│   ├── student_dashboard.html    # Student dashboard
│   ├── create_assignment.html     # Create assignment form
│   ├── edit_assignment.html       # Edit assignment form
│   ├── view_assignment.html       # View assignment details
│   └── submit_assignment.html     # Submit assignment form
├── static/                  # Static files
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   ├── js/
│   │   └── script.js       # Custom JavaScript
│   └── uploads/            # File upload directory
└── database/               # Database files (if needed)
```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `user_type` - 'student' or 'teacher'
- `created_at` - Registration timestamp

### Assignments Table
- `id` - Primary key
- `title` - Assignment title
- `subject` - Subject name
- `description` - Assignment description
- `deadline` - Submission deadline
- `max_marks` - Maximum marks
- `teacher_id` - Foreign key to users table
- `attachment_path` - Path to attachment file
- `created_at` - Creation timestamp

### Submissions Table
- `id` - Primary key
- `assignment_id` - Foreign key to assignments table
- `student_id` - Foreign key to users table
- `submission_text` - Text submission content
- `file_path` - Path to submitted file
- `submitted_at` - Submission timestamp
- `marks` - Assigned marks
- `feedback` - Teacher feedback

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project
```bash
# If using git
git clone <repository-url>
cd Assignment.11

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage Guide

### First Time Setup
1. Run the application using `python app.py`
2. The database will be created automatically
3. Register as a teacher or student
4. Login and start using the system

### Teacher Workflow
1. **Login** as a teacher
2. **Create Assignment** from the dashboard
3. **Set Details** - title, subject, description, deadline, marks
4. **Upload Attachment** (optional)
5. **Monitor Submissions** from the dashboard
6. **Grade Submissions** with marks and feedback

### Student Workflow
1. **Login** as a student
2. **View Assignments** on the dashboard
3. **Submit Assignment** before deadline
4. **Upload File** and/or add text
5. **Check Status** and view grades

## Default Credentials (for testing)

You can create your own accounts, but here are some examples:

**Teacher Account:**
- Username: `teacher1`
- Email: `teacher@example.com`
- Password: `teacher123`
- Role: Teacher

**Student Account:**
- Username: `student1`
- Email: `student@example.com`
- Password: `student123`
- Role: Student

## File Upload Support

The system supports the following file types:
- Documents: `.txt`, `.pdf`, `.doc`, `.docx`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`
- Archives: `.zip`, `.rar`

Maximum file size: 16MB

## Security Features

- Password hashing with Werkzeug
- Session management
- File upload validation
- SQL injection protection
- XSS protection
- CSRF protection

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   ```bash
   # Kill the process using port 5000
   # On Windows:
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # On macOS/Linux:
   lsof -ti:5000 | xargs kill -9
   ```

2. **Database locked error**
   - Make sure only one instance of the app is running
   - Restart the application

3. **File upload not working**
   - Check if the `static/uploads` directory exists
   - Ensure proper write permissions

4. **Template not found error**
   - Verify all template files are in the `templates/` directory
   - Check file names and spelling

### Debug Mode

The application runs in debug mode by default. For production:
```python
# In app.py, change the last line to:
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue on the repository

## Future Enhancements

- Email notifications for deadlines
- Bulk assignment operations
- Advanced grading rubrics
- Plagiarism detection
- Mobile app version
- Integration with learning management systems
- Real-time chat between teachers and students
- Assignment templates
- Analytics and reporting dashboard

---

**Happy Learning! 🎓**
