# FocusFlow - Focus Learning & Time Management System

## 📚 Project Overview
FocusFlow is a Flask-based focus learning and time management system designed to help users improve learning efficiency and develop good study habits. By combining the Pomodoro technique with task management functionality, FocusFlow provides a comprehensive solution for enhancing learning productivity.

## ✨ Key Features

### 👤 User Account System
- Registration, login, and password reset functionality
- Personal profile management (edit information, change password)
- Learning preference settings

### 📝 Task Management
- Create, edit, and delete learning tasks
- Set task priority and due dates
- Task categorization and organization
- Task completion status tracking

### ⏱️ Focus Mode
- Pomodoro technique timer implementation
- Customizable focus and break durations
- Focus session recording and statistics
- Visual distraction minimization during focus sessions

### 📊 Statistics & Analytics
- Learning data visualization
- Daily/weekly/monthly focus time statistics
- Task completion rate analysis
- Personalized learning recommendations
- Continuous learning streak tracking

### 🌐 Internationalization Support
- Bilingual interface (English/Chinese)
- Multi-language content translation

### 🎨 User Experience Optimization
- Responsive design for various screen sizes
- Dark/light mode theme switching
- Intuitive and user-friendly interface

## 🛠️ Technology Stack

### Backend
- Python 3.12
- Flask 3.1.2 - Web framework
- SQLite3 - Lightweight database
- Flask-CORS 6.0.1 - Cross-origin resource sharing

### Frontend
- HTML5, CSS3, JavaScript ES6+
- Bootstrap 5 - Responsive UI framework
- Font Awesome - Icon library
- Chart.js - Data visualization

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Browser support: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Installation Steps

#### 1. Clone the project (or use existing files)

#### 2. Create and activate virtual environment
If you are using Windows, enter the command prompt in the terminal:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
```

If you are using macOS or Linux, enter the command prompt in the terminal:
```bash
# macOS/Linux
source .venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Initialize database
```bash
cd focusflow
python setup.py
```

#### 5. Compile translation files (optional)
```bash
# To update or add new translations
pybabel compile -d translations
```

#### 6. Run the application
```bash
# Development mode
flask run

# Or using WSGI entry point
python wsgi.py
```

The application will start at http://127.0.0.1:5000

## 📋 User Guide

### First-time Usage
1. Visit http://127.0.0.1:5000 to open the application
2. Click "Register" to create a new account
3. Log in using your registered credentials

### Core Features Usage

#### Task Management
1. Click "Task Management" in the left navigation bar
2. Click "Add New Task" to create a learning task
3. Fill in task title, description, priority, etc.
4. Click "Save" to complete task creation
5. Edit or delete tasks from the task list

#### Focus Mode
1. Click "Focus Mode" in the left navigation bar
2. Select a task to focus on (optional)
3. Set focus duration and break duration
4. Click "Start" to begin the focus timer
5. Automatically switches to break mode after focus session

#### Statistics & Analytics
1. Click "Statistics & Analytics" in the left navigation bar
2. View learning statistics and visual charts
3. Select different time periods for statistics
4. Read personalized learning recommendations

#### Personal Center
1. Click "Personal Center" in the left navigation bar
2. Edit personal information and learning goals
3. Change account password
4. Set language preferences and theme mode

## 📁 Project Structure
```
focusflow/
├── app.py                 # Main application entry and route definitions
├── config.py              # Application configuration
├── models.py              # Data model definitions
├── database.py            # Database operations
├── schema.sql             # Database table structure
├── setup.py               # Project initialization script
├── wsgi.py                # WSGI server entry point
├── static/                # Static resource files
│   ├── css/               # Stylesheets
│   │   └── style.css      # Main stylesheet
│   ├── js/                # JavaScript scripts
│   │   ├── focus_timer.js # Focus timer implementation
│   │   └── main.js        # Common script functions
│   └── sounds/            # Audio files (notification sounds)
├── templates/             # HTML template files
│   ├── base.html          # Base template
│   ├── dashboard.html     # User dashboard
│   ├── focus_session.html # Focus mode page
│   ├── forgot_password.html # Forgot password page
│   ├── login.html         # Login page
│   ├── profile.html       # Personal center page
│   ├── register.html      # Registration page
│   ├── stats.html         # Statistics page
│   └── tasks.html         # Task management page
├── translations/          # Multi-language translation files
│   └── zh/                # Chinese translations
│       └── LC_MESSAGES/   # Message catalog
│           └── messages.po # Translation file
└── utils/                 # Utility functions
    ├── auth.py            # Authentication functions
    └── helpers.py         # Helper functions
```

## 🔧 Testing Guide

### Functional Testing

#### 1. User Authentication Testing
- **Registration Test**: Visit `/register` page, fill in registration info and submit, verify successful registration and auto-login
- **Login Test**: Visit `/login` page, use valid/invalid credentials, verify login logic
- **Password Reset**: Visit `/forgot_password` page, test password reset flow

#### 2. Task Management Testing
- **Create Tasks**: Create tasks with different priorities and due dates on `/tasks` page
- **Edit Tasks**: Modify existing task information, verify updates
- **Delete Tasks**: Delete tasks and confirm removal from list
- **Task Status**: Mark tasks as complete/incomplete, check status changes

#### 3. Focus Mode Testing
- **Timer Function**: Set different durations, test timer accuracy
- **Pause/Resume**: Test pause and resume timer functionality
- **Task Association**: Select tasks for focus, verify focus time correctly associated
- **Break Mode**: Test automatic switch to break mode after focus session

#### 4. Statistics Testing
- **Data Display**: View statistics for different time periods on `/stats` page
- **Chart Display**: Verify various charts correctly display learning data

### Performance Testing
- Simulate multiple concurrent user operations
- Test page loading speed with large task datasets
- Verify stability during long focus mode sessions

### Development Environment Test Commands

```bash
# Run unit tests (if implemented)
python -m unittest discover

# Code quality check
flake8 .

# Static type checking (if using type annotations)
mypy .
```

## 🚧 Troubleshooting

### 1. Database Connection Error
- Ensure `python setup.py` has been run to initialize database
- Check database file permissions

### 2. Dependency Installation Failure
- Update pip to latest version: `pip install --upgrade pip`
- Verify Python version compatibility

### 3. Application Won't Start
- Check if port is occupied, use `flask run --port=5001` to change port
- Check console error messages for troubleshooting

### 4. Language Display Issues
- Ensure translation files are properly compiled: `pybabel compile -d translations`
- Check browser language settings

## 📜 License
MIT License

## 🤝 Contributing
We welcome issues and pull requests to improve the FocusFlow project.

## 📞 Contact
For any questions or suggestions, please contact the project maintainer.

---
Last Updated: 12/26/2025