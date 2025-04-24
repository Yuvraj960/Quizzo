from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('user.user_dashboard'))
    return render_template('index.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('user.user_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, password, role FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('user.user_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO users (username, password, full_name, qualification, dob, role)
                VALUES (?, ?, ?, ?, ?, "user")
            ''', (username, password, full_name, qualification, dob))
            conn.commit()
            flash("Registration successful! You can now login.", "success")
            return redirect(url_for('auth.login'))
        except Exception:
            flash("Username already exists. Please choose another.", "warning")
            return redirect(url_for('auth.register'))
        finally:
            conn.close()
    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))
