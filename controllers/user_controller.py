from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import get_db_connection
from datetime import datetime, timedelta
import json

user = Blueprint('user', __name__, url_prefix='/user')

def user_login_required():
    return 'user_id' in session and session.get('role') == 'user'

@user.before_request
def check_user():
    if not user_login_required():
        return redirect(url_for('auth.login'))

@user.route('/dashboard')
def user_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    today_str = datetime.now().strftime('%Y-%m-%d')
    cur.execute('''
        SELECT q.id AS quiz_id,
               q.date_of_quiz,
               q.time_duration,
               c.name AS chapter_name,
               s.name AS subject_name,
               (SELECT COUNT(*) FROM questions WHERE questions.quiz_id = q.id) as question_count
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE q.date_of_quiz >= ?
        ORDER BY q.date_of_quiz ASC
    ''', (today_str, ))
    
    upcoming_quizzes = cur.fetchall()
    conn.close()

    return render_template('user_dashboard.html', upcoming_quizzes=upcoming_quizzes)

@user.route('/quiz/<int:quiz_id>/view')
def view_quiz(quiz_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT q.id as quiz_id,
               s.name as subject_name,
               c.name as chapter_name,
               (SELECT COUNT(*) FROM questions WHERE questions.quiz_id = q.id) as question_count,
               q.date_of_quiz,
               q.time_duration
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE q.id = ?
    ''', (quiz_id,))
    quiz_info = cur.fetchone()
    conn.close()

    if not quiz_info:
        flash("Quiz not found!", "warning")
        return redirect(url_for('user.user_dashboard'))

    return render_template('view_quiz.html', quiz=quiz_info)

@user.route('/quiz/<int:quiz_id>/attempt', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT q.id, q.time_duration, 
               c.name AS chapter_name,
               s.name AS subject_name
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE q.id = ?
    ''', (quiz_id,))
    quiz_data = cur.fetchone()

    if not quiz_data:
        flash("Quiz not found!", "warning")
        conn.close()
        return redirect(url_for('user.user_dashboard'))

    hours, mins = quiz_data['time_duration'].split(':')
    total_minutes = int(hours) * 60 + int(mins)

    cur.execute('''
        SELECT id, question_title, question_text, option1, option2, option3, option4, correct_option
        FROM questions
        WHERE quiz_id = ?
        ORDER BY id
    ''', (quiz_id,))
    rows = cur.fetchall()
    questions = [dict(r) for r in rows]
    question_count = len(questions)
    conn.close()

    if request.method == 'POST':
        user_answers = request.form
        score = 0
        for q in questions:
            qid = str(q['id'])
            correct = q['correct_option']
            if qid in user_answers and user_answers[qid].isdigit():
                user_choice = int(user_answers[qid])
                if user_choice == correct:
                    score += 1

        conn2 = get_db_connection()
        c2 = conn2.cursor()
        c2.execute('''
            INSERT INTO scores (quiz_id, user_id, time_stamp_of_attempt, total_scored)
            VALUES (?, ?, ?, ?)
        ''', (quiz_id, session['user_id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), score))
        conn2.commit()
        conn2.close()

        flash(f"You scored {score} out of {question_count}.", "success")
        return redirect(url_for('user.user_scores'))
    else:
        return render_template(
            'attempt_quiz.html',
            quiz_id=quiz_id,
            quiz_data=quiz_data,
            total_minutes=total_minutes,
            questions=questions,
            question_count=question_count
        )

@user.route('/scores')
def user_scores():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT scores.quiz_id,
               (SELECT COUNT(*) FROM questions WHERE questions.quiz_id = scores.quiz_id) as question_count,
               scores.time_stamp_of_attempt,
               scores.total_scored,
               subjects.name AS subject_name,
               chapters.name AS chapter_name
        FROM scores
        JOIN quizzes ON scores.quiz_id = quizzes.id
        JOIN chapters ON quizzes.chapter_id = chapters.id
        JOIN subjects ON chapters.subject_id = subjects.id
        WHERE scores.user_id = ?
        ORDER BY scores.time_stamp_of_attempt DESC
    ''', (session['user_id'],))
    
    user_scores_data = cur.fetchall()
    conn.close()

    return render_template('scores.html', scores=user_scores_data)

@user.route('/search', methods=['GET'])
def user_search():
    query = request.args.get('query', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT q.id as quiz_id,
               s.name as subject_name,
               c.name as chapter_name,
               q.date_of_quiz,
               q.time_duration,
               (SELECT COUNT(*) FROM questions WHERE questions.quiz_id = q.id) as question_count
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE s.name LIKE ? OR q.date_of_quiz LIKE ?
        ORDER BY q.date_of_quiz
    ''', (f'%{query}%', f'%{query}%'))

    results = cur.fetchall()
    conn.close()

    return render_template('user_search_results.html', query=query, results=results)

@user.route('/summary')
def user_summary():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT subjects.name as subject_name,
               COUNT(quizzes.id) as quiz_count
        FROM quizzes
        JOIN chapters ON quizzes.chapter_id = chapters.id
        JOIN subjects ON chapters.subject_id = subjects.id
        GROUP BY subjects.id
    ''')
    subject_quiz_counts = cur.fetchall()
    bar_labels = [row['subject_name'] for row in subject_quiz_counts]
    bar_data = [row['quiz_count'] for row in subject_quiz_counts]

    cur.execute('''
        SELECT strftime('%d', time_stamp_of_attempt) AS day_number,
               COUNT(*) as attempts
        FROM scores
        WHERE user_id = ? AND strftime('%Y-%m', time_stamp_of_attempt) = strftime('%Y-%m', 'now')
        GROUP BY day_number
    ''', (session['user_id'],))
    daily_attempts = {str(row['day_number']).zfill(2): row['attempts'] for row in cur.fetchall()}

    conn.close()
    today = datetime.today()
    days_in_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).day

    pie_labels = []
    pie_data = []

    for day in range(1, days_in_month + 1):
        day_str = str(day).zfill(2)
        pie_labels.append(f"Day {day}")
        pie_data.append(daily_attempts.get(day_str, 0))

    return render_template('user_summary.html',
                           bar_labels=json.dumps(bar_labels),
                           bar_data=json.dumps(bar_data),
                           pie_labels=json.dumps(pie_labels),
                           pie_data=json.dumps(pie_data))
