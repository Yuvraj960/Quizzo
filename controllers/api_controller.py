from flask import Blueprint, jsonify, session, redirect, url_for
from models.db import get_db_connection

api = Blueprint('api', __name__, url_prefix='/admin/api')

def admin_login_required():
    return 'user_id' in session and session.get('role') == 'admin'

@api.before_request
def check_admin_api():
    if not admin_login_required():
        return redirect(url_for('auth.login'))

@api.route('/users', methods=['GET'])
def api_get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, full_name, qualification, dob, role
        FROM users
    """)
    rows = cur.fetchall()
    conn.close()

    users_list = []
    for r in rows:
        users_list.append({
            'id': r['id'],
            'username': r['username'],
            'full_name': r['full_name'],
            'qualification': r['qualification'],
            'dob': r['dob'],
            'role': r['role']
        })

    return jsonify(users_list)

@api.route('/subjects', methods=['GET'])
def api_get_subjects():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM subjects")
    rows = cur.fetchall()
    conn.close()

    subjects_list = []
    for r in rows:
        subjects_list.append({
            'id': r['id'],
            'name': r['name'],
            'description': r['description']
        })

    return jsonify(subjects_list)

@api.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
def api_get_chapters(subject_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM chapters WHERE subject_id = ?", (subject_id,))
    rows = cur.fetchall()
    conn.close()

    chapters_list = []
    for r in rows:
        chapters_list.append({
            'id': r['id'],
            'name': r['name'],
            'description': r['description']
        })

    return jsonify(chapters_list)

@api.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
def api_get_quizzes(chapter_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date_of_quiz, time_duration, remarks FROM quizzes WHERE chapter_id = ?", (chapter_id,))
    rows = cur.fetchall()
    conn.close()

    quizzes_list = []
    for r in rows:
        quizzes_list.append({
            'id': r['id'],
            'date_of_quiz': r['date_of_quiz'],
            'time_duration': r['time_duration'],
            'remarks': r['remarks']
        })

    return jsonify(quizzes_list)

@api.route('/scores', methods=['GET'])
def api_get_scores():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, quiz_id, user_id, time_stamp_of_attempt, total_scored FROM scores")
    rows = cur.fetchall()
    conn.close()

    scores_list = []
    for r in rows:
        scores_list.append({
            'id': r['id'],
            'quiz_id': r['quiz_id'],
            'user_id': r['user_id'],
            'time_stamp': r['time_stamp_of_attempt'],
            'score': r['total_scored']
        })

    return jsonify(scores_list)
