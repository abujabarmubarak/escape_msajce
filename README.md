# Escape from College

A web application for managing a college escape room event. Teams progress through three rounds of clues, with an admin interface to track progress and manage teams.

## Features

- **Admin Interface**
  - Secure login with fixed credentials
  - Excel file upload for team data
  - Real-time leaderboard
  - Team progress tracking

- **Team Interface**
  - Secure login system
  - Progressive clue reveal
  - Answer submission and validation
  - Visual progress tracking

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (using the sqlite3 module)
- **Data Processing**: Pandas for Excel file handling
- **Frontend**: HTML, CSS, JavaScript
- **Security**: Session management, password hashing

## Project Structure

```
/
├── app.py              # Main Flask application
├── db.sqlite3          # SQLite database
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── leaderboard.html
│   ├── team_dashboard.html
│   └── escaped.html
├── static/             # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── script.js
│       └── confetti.js
└── uploads/            # Temporary directory for Excel uploads
    └── .gitignore
```

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application at `http://localhost:5000`

## Admin Login

- Username: `admin`
- Password: `admin@123`

## Excel File Format

The uploaded Excel file must contain the following columns:
- teamname
- username
- password
- clue1
- round1_answer
- clue2
- round2_answer
- clue3
- round3_answer

## License

This project is for educational purposes.