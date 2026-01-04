# FocusFlow - Focus Learning & Time Management System

## 📚 Project Overview
FocusFlow is a comprehensive Flask-based web application designed to help users improve learning efficiency and develop productive study habits. The system combines task management with focus timer functionality using the Pomodoro technique, providing a complete solution for effective time management and learning optimization.

## ✨ Core Features

### 👤 User Management System
- User registration and authentication with secure password hashing
- Profile management with personal information and avatar upload
- Multi-language support (English/Chinese)
- Daily check-in system with streak tracking

### 📝 Advanced Task Management
- Create, edit, and organize learning tasks with priorities
- Set due dates and track completion status
- Task categorization and filtering capabilities
- Visual task progress indicators

### ⏱️ Intelligent Focus Timer
- Pomodoro technique implementation with customizable intervals
- Focus session tracking and statistics
- Break management with automatic transitions
- Task association for focused work sessions

### 📊 Learning Analytics Dashboard
- Visual statistics for focus time and task completion
- Daily, weekly, and monthly progress tracking
- Learning streak visualization
- Personalized insights and recommendations

### 🎨 User Experience Features
- Responsive design for desktop and mobile devices
- Dark/light theme support
- Intuitive navigation and clean interface
- Real-time notifications and feedback

## 🛠️ Technology Stack

### Backend Development
- **Python 3.12** - Core programming language
- **Flask 3.1.2** - Lightweight web framework
- **SQLite3** - Embedded database for data persistence
- **Flask-Bcrypt** - Secure password hashing
- **Werkzeug** - WSGI utilities and development server

### Frontend Development
- **HTML5** - Semantic markup structure
- **CSS3** - Responsive styling and animations
- **JavaScript ES6+** - Interactive functionality
- **Bootstrap** - UI components and grid system
- **Chart.js** - Data visualization for statistics

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation Steps

1. **Navigate to Project Directory**
   ```bash
   cd focusflow
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python setup.py
   ```

5. **Launch Application**
   ```bash
   # Development server
   flask run
   
   # Alternative: Direct Python execution
   python app.py
   ```

6. **Access Application**
   Open your browser and navigate to: `http://127.0.0.1:5000`

## 📁 Project Structure
```
focusflow/
├── app.py                 # Main Flask application with routes
├── config.py             # Application configuration settings
├── models.py             # Data models and database schema
├── database.py           # Database connection utilities
├── setup.py              # Database initialization script
├── wsgi.py               # WSGI entry point for production
├── requirements.txt      # Python dependencies
├── schema.sql            # Database table definitions
├── focusflow.db          # SQLite database file (auto-generated)
│
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   ├── focus_timer.js # Pomodoro timer functionality
│   │   └── main.js       # Common JavaScript utilities
│   └── uploads/
│       └── avatars/      # User profile pictures
│
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── dashboard.html    # User dashboard
│   ├── login.html        # Authentication page
│   ├── register.html     # User registration
│   ├── profile.html      # Profile management
│   ├── tasks.html        # Task management interface
│   ├── focus.html        # Focus timer interface
│   ├── stats.html        # Statistics dashboard
│   └── forgot_password.html # Password recovery
│
└── utils/                # Utility modules
    ├── auth.py           # Authentication helpers
    └── helpers.py        # Common utility functions
```

## 🔧 Development Guide

### Database Operations
The application uses SQLite with the following main tables:
- `users` - User account information
- `tasks` - Learning tasks and assignments
- `focus_sessions` - Focus time tracking
- `checkins` - Daily check-in records

### Adding New Features
1. Define new routes in `app.py`
2. Create corresponding template in `templates/`
3. Add necessary database modifications in `models.py`
4. Update static assets if needed

### Testing the Application
```bash
# Run the development server
flask run --debug

# Test database operations
python -c "from app import init_db; init_db()"
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors**
- Ensure `focusflow.db` file exists and has proper permissions
- Run `python setup.py` to recreate database if needed

**Dependency Installation Issues**
- Update pip: `pip install --upgrade pip`
- Verify Python version compatibility

**Application Startup Problems**
- Check if port 5000 is available
- Verify all dependencies are installed correctly
- Check console for specific error messages

**File Upload Issues**
- Ensure `static/uploads/avatars` directory exists
- Verify file size limits (5MB maximum)
- Check allowed file types: PNG, JPG, JPEG, GIF, WebP

## 📝 Usage Guide

### Getting Started
1. Register a new account or login with existing credentials
2. Set up your profile with personal information
3. Create your first learning task in the task management section

### Daily Workflow
1. **Morning Check-in**: Start your day by checking in on the dashboard
2. **Task Planning**: Review and organize your daily tasks
3. **Focus Sessions**: Use the focus timer for productive work periods
4. **Progress Tracking**: Monitor your statistics and adjust goals

### Advanced Features
- **Task Prioritization**: Use high/medium/low priorities to organize work
- **Focus Session Customization**: Adjust timer durations to match your workflow
- **Multi-language Support**: Switch between English and Chinese interfaces
- **Profile Customization**: Upload avatars and personalize your account

## 🤝 Contributing
We welcome contributions to improve FocusFlow! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with detailed description

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support
For technical support or feature requests, please contact the development team or create an issue in the project repository.

---
*Last Updated: 1/6/2025*