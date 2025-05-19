from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import hashlib
import secrets
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
CORS(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Create teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teamname TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        current_round INTEGER DEFAULT 1,
        round1_completed TIMESTAMP,
        round2_completed TIMESTAMP,
        round3_completed TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create clues table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER,
        clue1 TEXT,
        round1_answer TEXT,
        clue2 TEXT,
        round2_answer TEXT,
        clue3 TEXT,
        round3_answer TEXT,
        FOREIGN KEY (team_id) REFERENCES teams (id)
    )
    ''')
    
    # Create admin user if it doesn't exist
    cursor.execute('SELECT * FROM teams WHERE username = ?', ('admin',))
    admin = cursor.fetchone()
    
    if not admin:
        # Hash the admin password
        hashed_password = hashlib.sha256('admin@123'.encode()).hexdigest()
        cursor.execute(
            'INSERT INTO teams (teamname, username, password, current_round) VALUES (?, ?, ?, ?)',
            ('Admin', 'admin', hashed_password, 0)
        )
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT id, teamname, current_round FROM teams WHERE username = ? AND password = ?', 
                      (username, hashed_password))
        team = cursor.fetchone()
        conn.close()
        
        if team:
            session['user_id'] = team[0]
            session['teamname'] = team[1]
            session['current_round'] = team[2]
            session['username'] = username
            
            if username == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('team_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('username') != 'admin':
        flash('Unauthorized access. Please login as admin.', 'error')
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/admin/upload', methods=['POST'])
def upload_file():
    if session.get('username') != 'admin':
        flash('Unauthorized access. Please login as admin.', 'error')
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('admin_dashboard'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read the Excel file
            df = pd.read_excel(filepath)
            
            # Check if required columns exist
            required_columns = ['teamname', 'username', 'password', 'clue1', 'round1_answer', 
                               'clue2', 'round2_answer', 'clue3', 'round3_answer']
            for column in required_columns:
                if column not in df.columns:
                    flash(f'Missing required column: {column}', 'error')
                    return redirect(url_for('admin_dashboard'))
            
            # Process data and insert into database
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                # Hash the password
                hashed_password = hashlib.sha256(str(row['password']).encode()).hexdigest()
                
                # Insert team data
                cursor.execute(
                    'INSERT OR REPLACE INTO teams (teamname, username, password, current_round) VALUES (?, ?, ?, ?)',
                    (row['teamname'], row['username'], hashed_password, 1)
                )
                
                # Get the team_id
                cursor.execute('SELECT id FROM teams WHERE username = ?', (row['username'],))
                team_id = cursor.fetchone()[0]
                
                # Insert clue data
                cursor.execute(
                    '''INSERT OR REPLACE INTO clues 
                    (team_id, clue1, round1_answer, clue2, round2_answer, clue3, round3_answer) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (team_id, row['clue1'], row['round1_answer'], row['clue2'], 
                     row['round2_answer'], row['clue3'], row['round3_answer'])
                )
            
            conn.commit()
            conn.close()
            
            flash('Teams data uploaded successfully!', 'success')
            
            # Remove the file after processing
            os.remove(filepath)
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            
        return redirect(url_for('admin_dashboard'))
    
    flash('Invalid file type. Please upload an Excel file (.xlsx)', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/leaderboard')
def leaderboard():
    if session.get('username') != 'admin':
        flash('Unauthorized access. Please login as admin.', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Get all teams except admin, sorted by round completion
    cursor.execute('''
    SELECT id, teamname, current_round, round1_completed, round2_completed, round3_completed 
    FROM teams 
    WHERE username != 'admin'
    ORDER BY 
        current_round DESC, 
        round3_completed ASC,
        round2_completed ASC,
        round1_completed ASC
    ''')
    teams = cursor.fetchall()
    conn.close()
    
    # Find the leading team
    leader = None
    for team in teams:
        if team[2] == 4:  # Team has completed all rounds
            leader = team
            break
    
    return render_template('leaderboard.html', teams=teams, leader=leader)

@app.route('/team/dashboard')
def team_dashboard():
    if 'user_id' not in session or session.get('username') == 'admin':
        flash('Please login to continue.', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    current_round = session['current_round']
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Get team's clues
    cursor.execute('''
    SELECT clue1, clue2, clue3
    FROM clues 
    WHERE team_id = ?
    ''', (user_id,))
    clues = cursor.fetchone()
    conn.close()
    
    if not clues:
        flash('No clues found for your team.', 'error')
        return redirect(url_for('logout'))
    
    # Determine which clue to show based on current round
    current_clue = None
    if current_round == 1:
        current_clue = clues[0]
    elif current_round == 2:
        current_clue = clues[1]
    elif current_round == 3:
        current_clue = clues[2]
    elif current_round == 4:
        # Team has completed all rounds
        return render_template('escaped.html')
    
    return render_template('team_dashboard.html', current_round=current_round, clue=current_clue)

@app.route('/team/submit_answer', methods=['POST'])
def submit_answer():
    if 'user_id' not in session or session.get('username') == 'admin':
        flash('Please login to continue.', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    current_round = session['current_round']
    answer = request.form['answer'].strip()
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Get the correct answer for the current round
    if current_round == 1:
        cursor.execute('SELECT round1_answer FROM clues WHERE team_id = ?', (user_id,))
    elif current_round == 2:
        cursor.execute('SELECT round2_answer FROM clues WHERE team_id = ?', (user_id,))
    elif current_round == 3:
        cursor.execute('SELECT round3_answer FROM clues WHERE team_id = ?', (user_id,))
    else:
        conn.close()
        return redirect(url_for('team_dashboard'))
    
    correct_answer = cursor.fetchone()[0]
    
    # Check if the answer is correct
    if answer.lower() == correct_answer.lower():
        # Update the team's current round and completion timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if current_round == 1:
            cursor.execute(
                'UPDATE teams SET current_round = ?, round1_completed = ? WHERE id = ?', 
                (current_round + 1, timestamp, user_id)
            )
        elif current_round == 2:
            cursor.execute(
                'UPDATE teams SET current_round = ?, round2_completed = ? WHERE id = ?', 
                (current_round + 1, timestamp, user_id)
            )
        elif current_round == 3:
            cursor.execute(
                'UPDATE teams SET current_round = ?, round3_completed = ? WHERE id = ?', 
                (current_round + 1, timestamp, user_id)
            )
        
        conn.commit()
        session['current_round'] = current_round + 1
        flash('Correct answer! Moving to the next round.', 'success')
    else:
        flash('Incorrect answer. Please try again.', 'error')
    
    conn.close()
    return redirect(url_for('team_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)