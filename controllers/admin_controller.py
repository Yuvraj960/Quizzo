from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import get_db_connection
import json

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_login_required():
    return 'user_id' in session and session.get('role') == 'admin'

@admin.before_request
def check_admin():
    if not admin_login_required():
        return redirect(url_for('auth.login'))

@admin.route('/dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()
    subjects_data = []
    for subject in subjects:
        subject_id = subject['id']
        cur.execute("SELECT * FROM chapters WHERE subject_id = ?", (subject_id,))
        chapters = cur.fetchall()
        chapter_data = []
        for chapter in chapters:
            chapter_id = chapter['id']
            cur.execute("SELECT COUNT(*) as quiz_count FROM quizzes WHERE chapter_id = ?", (chapter_id,))
            quiz_count = cur.fetchone()['quiz_count']
            chapter_data.append({
                'id': chapter_id,
                'name': chapter['name'],
                'quiz_count': quiz_count
            })
        subjects_data.append({
            'id': subject_id,
            'name': subject['name'],
            'chapters': chapter_data
        })
    conn.close()
    return render_template('admin_dashboard.html', subjects_data=subjects_data)

@admin.route('/subjects', methods=['GET', 'POST'])
def admin_subjects():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        cur.execute("SELECT id FROM subjects WHERE LOWER(name) = LOWER(?)", (name,))
        existing = cur.fetchone()
        if existing:
            flash("A subject with that name already exists!", "danger")
            conn.close()
            return redirect(url_for('admin.admin_subjects'))

        cur.execute('INSERT INTO subjects (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        flash("Subject created!", "success")
        conn.close()
        return redirect(url_for('admin.admin_subjects'))

    cur.execute('SELECT id, name, description FROM subjects')
    subjects = cur.fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

@admin.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cur.execute('UPDATE subjects SET name = ?, description = ? WHERE id = ?', (name, description, subject_id))
        conn.commit()
        conn.close()
        flash("Subject updated successfully!", "success")
        return redirect(url_for('admin.subjects'))

    cur.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,))
    subject = cur.fetchone()
    conn.close()
    return render_template('edit_subject.html', subject=subject)

@admin.route('/subjects/update/<int:subject_id>', methods=['POST'])
def update_subject(subject_id):
    name = request.form['name']
    description = request.form['description']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM subjects WHERE LOWER(name) = LOWER(?) AND id != ?", (name, subject_id))
    row = cur.fetchone()
    if row:
        flash("Another subject with that name already exists!", "danger")
        conn.close()
        return redirect(url_for('admin.edit_subject', subject_id=subject_id))

    cur.execute('''
        UPDATE subjects SET name = ?, description = ?
        WHERE id = ?
    ''', (name, description, subject_id))
    conn.commit()
    conn.close()
    
    flash("Subject updated successfully!", "success")
    return redirect(url_for('admin.admin_subjects'))

@admin.route('/subjects/<int:subject_id>/delete', methods=['POST'])
def delete_subject(subject_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
    conn.commit()
    conn.close()
    flash("Subject deleted!", "info")
    return redirect(url_for('admin.admin_subjects'))

@admin.route('/chapters/<int:subject_id>', methods=['GET', 'POST'])
def admin_chapters(subject_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        cur.execute("SELECT id FROM chapters WHERE subject_id = ? AND LOWER(name) = LOWER(?)", (subject_id, name))
        existing = cur.fetchone()
        if existing:
            flash("A chapter with that name already exists in this subject!", "danger")
            conn.close()
            return redirect(url_for('admin.admin_chapters', subject_id=subject_id))

        cur.execute(
            'INSERT INTO chapters (subject_id, name, description) VALUES (?, ?, ?)', 
            (subject_id, name, description)
        )
        conn.commit()
        flash("Chapter created!", "success")
        conn.close()
        return redirect(url_for('admin.admin_chapters', subject_id=subject_id))
    cur.execute('SELECT name FROM subjects WHERE id = ?', (subject_id,))
    subject_name = cur.fetchone()
    cur.execute('SELECT id, name, description FROM chapters WHERE subject_id = ?', (subject_id,))
    chapters = cur.fetchall()
    conn.close()
    return render_template('chapters.html', subject_id=subject_id, subject_name=subject_name['name'] if subject_name else "", chapters=chapters)

@admin.route('/chapters/edit/<int:chapter_id>')
def edit_chapter(chapter_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,))
    chapter = cur.fetchone()
    conn.close()
    return render_template('edit_chapter.html', chapter=chapter)

@admin.route('/chapters/update/<int:chapter_id>', methods=['POST'])
def update_chapter(chapter_id):
    conn = get_db_connection()
    cur = conn.cursor()

    name = request.form['name']
    description = request.form['description']

    cur.execute("SELECT subject_id FROM chapters WHERE id = ?", (chapter_id,))
    current_chapter = cur.fetchone()
    if not current_chapter:
        flash("No such chapter found!", "danger")
        conn.close()
        return redirect(url_for('admin.admin_dashboard'))

    subject_id = current_chapter['subject_id']

    cur.execute("""
        SELECT id FROM chapters
        WHERE subject_id = ?
          AND LOWER(name) = LOWER(?)
          AND id != ?
    """, (subject_id, name, chapter_id))
    existing = cur.fetchone()
    if existing:
        flash("Another chapter in this subject already has that name!", "danger")
        conn.close()
        return redirect(url_for('admin.edit_chapter', chapter_id=chapter_id))

    cur.execute('''
        UPDATE chapters
        SET name = ?, description = ?
        WHERE id = ?
    ''', (name, description, chapter_id))
    conn.commit()
    conn.close()

    flash("Chapter updated successfully!", "success")
    return redirect(url_for('admin.admin_chapters', subject_id=subject_id))

@admin.route('/chapters/<int:chapter_id>/delete', methods=['POST'])
def delete_chapter(chapter_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM chapters WHERE id = ?', (chapter_id,))
    conn.commit()
    conn.close()
    flash("Chapter deleted!", "info")
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/quizzes/<int:chapter_id>', methods=['GET', 'POST'])
def admin_quizzes(chapter_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remarks = request.form['remarks']

        cur.execute("SELECT id FROM quizzes WHERE chapter_id = ? AND LOWER(remarks) = LOWER(?)", (chapter_id, remarks))
        existing = cur.fetchone()
        if existing:
            flash("A quiz with that name already exists in this chapter!", "danger")
            conn.close()
            return redirect(url_for('admin.admin_quizzes', chapter_id=chapter_id))

        cur.execute('''
            INSERT INTO quizzes (chapter_id, date_of_quiz, time_duration, remarks)
            VALUES (?, ?, ?, ?)
        ''', (chapter_id, date_of_quiz, time_duration, remarks))
        conn.commit()
        flash("Quiz created!", "success")
        conn.close()
        return redirect(url_for('admin.admin_quizzes', chapter_id=chapter_id))

    cur.execute('SELECT id, date_of_quiz, time_duration, remarks FROM quizzes WHERE chapter_id = ?', (chapter_id,))
    quizzes = cur.fetchall()
    conn.close()
    return render_template('quizzes.html', chapter_id=chapter_id, quizzes=quizzes)

@admin.route('/quizzes/edit/<int:quiz_id>')
def edit_quiz(quiz_id):
    """ Renders the quiz edit form """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM quizzes WHERE id = ?', (quiz_id,))
    quiz = cur.fetchone()
    conn.close()
    return render_template('edit_quiz.html', quiz=quiz)

@admin.route('/quizzes/update/<int:quiz_id>', methods=['POST'])
def update_quiz(quiz_id):
    date_of_quiz = request.form['date_of_quiz']
    time_duration = request.form['time_duration']
    remarks = request.form['remarks']  # used as quiz name

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT chapter_id FROM quizzes WHERE id = ?", (quiz_id,))
    quiz_row = cur.fetchone()
    if not quiz_row:
        flash("No such quiz found!", "danger")
        conn.close()
        return redirect(url_for('admin.admin_dashboard'))

    chapter_id = quiz_row['chapter_id']

    cur.execute("""
        SELECT id FROM quizzes
        WHERE chapter_id = ?
          AND LOWER(remarks) = LOWER(?)
          AND id != ?
    """, (chapter_id, remarks, quiz_id))
    existing = cur.fetchone()
    if existing:
        flash("A quiz with that name already exists in this chapter!", "danger")
        conn.close()
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))

    cur.execute('''
        UPDATE quizzes 
        SET date_of_quiz = ?, time_duration = ?, remarks = ?
        WHERE id = ?
    ''', (date_of_quiz, time_duration, remarks, quiz_id))
    conn.commit()

    conn.close()
    flash("Quiz updated successfully!", "success")
    return redirect(url_for('admin.admin_quizzes', chapter_id=chapter_id))

@admin.route('/quizzes/<int:quiz_id>/delete', methods=['POST'])
def delete_quiz(quiz_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
    conn.commit()
    conn.close()
    flash("Quiz deleted!", "info")
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/quiz_dashboard')
def quiz_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()
    subjects_data = []
    for subject in subjects:
        subject_id = subject['id']
        cur.execute("SELECT * FROM chapters WHERE subject_id = ?", (subject_id,))
        chapters = cur.fetchall()
        chapter_list = []
        for chapter in chapters:
            chapter_id = chapter['id']
            cur.execute("SELECT * FROM quizzes WHERE chapter_id = ?", (chapter_id,))
            quizzes = cur.fetchall()
            quiz_list = []
            for quiz in quizzes:
                quiz_id = quiz['id']
                cur.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
                questions = cur.fetchall()
                quiz_list.append({
                    'id': quiz_id,
                    'quiz_name': quiz['remarks'],
                    'chapter_name': chapter['name'],
                    'questions': questions
                })
            chapter_list.append({
                'id': chapter_id,
                'name': chapter['name'],
                'quizzes': quiz_list
            })
        subjects_data.append({
            'id': subject_id,
            'name': subject['name'],
            'chapters': chapter_list
        })

    cur.execute("SELECT chapters.*, subjects.name as subject_name FROM chapters JOIN subjects ON chapters.subject_id = subjects.id")
    all_chapters = cur.fetchall()
    conn.close()
    return render_template('admin_quiz_dashboard.html', subjects_data=subjects_data, all_chapters=all_chapters)

@admin.route('/questions/<int:quiz_id>', methods=['GET', 'POST'])
def admin_questions(quiz_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        question_title = request.form['question_title']
        question_text = request.form['question_text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form['correct_option']

        cur.execute("SELECT id FROM questions WHERE quiz_id = ? AND LOWER(question_title) = LOWER(?)", (quiz_id, question_title))
        existing = cur.fetchone()
        if existing:
            flash("A question with that title already exists in this quiz!", "danger")
            conn.close()
            return redirect(url_for('admin.admin_questions', quiz_id=quiz_id))

        cur.execute('''
            INSERT INTO questions (quiz_id, question_title, question_text, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_id, question_title, question_text, option1, option2, option3, option4, correct_option))
        conn.commit()
        flash("Question added!", "success")
        conn.close()
        return redirect(url_for('admin.admin_questions', quiz_id=quiz_id))

    cur.execute('SELECT id, question_title, question_text, option1, option2, option3, option4, correct_option FROM questions WHERE quiz_id = ?', (quiz_id,))
    questions = cur.fetchall()
    conn.close()
    return render_template('questions.html', quiz_id=quiz_id, questions=questions)

@admin.route('/questions/edit/<int:question_id>')
def edit_question(question_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
    question = cur.fetchone()
    conn.close()
    return render_template('edit_question.html', question=question)

@admin.route('/questions/update/<int:question_id>', methods=['POST'])
def update_question(question_id):
    question_title = request.form['question_title']
    question_text = request.form['question_text']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']
    correct_option = int(request.form['correct_option'])

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT quiz_id FROM questions WHERE id = ?", (question_id,))
    row = cur.fetchone()
    if not row:
        flash("No such question found!", "danger")
        conn.close()
        return redirect(url_for('admin.quiz_dashboard'))
    quiz_id = row['quiz_id']

    cur.execute("""
        SELECT id FROM questions
        WHERE quiz_id = ?
          AND LOWER(question_title) = LOWER(?)
          AND id != ?
    """, (quiz_id, question_title, question_id))
    existing = cur.fetchone()
    if existing:
        flash("A question with that title already exists in this quiz!", "danger")
        conn.close()
        return redirect(url_for('admin.edit_question', question_id=question_id))

    cur.execute('''
        UPDATE questions
        SET question_title = ?,
            question_text = ?,
            option1 = ?,
            option2 = ?,
            option3 = ?,
            option4 = ?,
            correct_option = ?
        WHERE id = ?
    ''', (question_title, question_text, option1, option2, option3, option4, correct_option, question_id))
    conn.commit()

    conn.close()
    flash("Question updated successfully!", "success")
    return redirect(url_for('admin.admin_questions', quiz_id=quiz_id))

@admin.route('/questions/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    flash("Question deleted!", "info")
    return redirect(url_for('admin.quiz_dashboard'))

@admin.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE name LIKE ? OR description LIKE ?", ('%' + query + '%', '%' + query + '%'))
    subjects = cur.fetchall()
    cur.execute("SELECT * FROM chapters WHERE name LIKE ? OR description LIKE ?", ('%' + query + '%', '%' + query + '%'))
    chapters = cur.fetchall()
    cur.execute("SELECT * FROM quizzes WHERE remarks LIKE ? OR date_of_quiz LIKE ?", ('%' + query + '%', '%' + query + '%'))
    quizzes = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE username LIKE ? OR full_name LIKE ?", ('%' + query + '%', '%' + query + '%'))
    users = cur.fetchall()
    conn.close()
    return render_template('admin_search_results.html', query=query, subjects=subjects, chapters=chapters, quizzes=quizzes, users=users)

@admin.route('/summary')
def admin_summary():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT subjects.name AS subject, SUM(scores.total_scored) AS total_score
        FROM scores
        JOIN quizzes ON scores.quiz_id = quizzes.id
        JOIN chapters ON quizzes.chapter_id = chapters.id
        JOIN subjects ON chapters.subject_id = subjects.id
        GROUP BY subjects.id
    """)
    subject_scores = cur.fetchall()
    subjects = [row['subject'] for row in subject_scores]
    total_scores = [row['total_score'] for row in subject_scores]

    cur.execute("""
        SELECT subjects.name AS subject, COUNT(scores.id) AS attempts
        FROM scores
        JOIN quizzes ON scores.quiz_id = quizzes.id
        JOIN chapters ON quizzes.chapter_id = chapters.id
        JOIN subjects ON chapters.subject_id = subjects.id
        GROUP BY subjects.id
    """)
    subject_attempts = cur.fetchall()
    subjects_attempt = [row['subject'] for row in subject_attempts]
    attempts = [row['attempts'] for row in subject_attempts]

    cur.execute("""
        SELECT subjects.name AS subject, AVG(scores.total_scored) AS avg_score
        FROM scores
        JOIN quizzes ON scores.quiz_id = quizzes.id
        JOIN chapters ON quizzes.chapter_id = chapters.id
        JOIN subjects ON chapters.subject_id = subjects.id
        GROUP BY subjects.id
    """)
    subject_avg = cur.fetchall()
    subjects_avg = [row['subject'] for row in subject_avg]
    avg_scores = [row['avg_score'] for row in subject_avg]

    conn.close()
    return render_template('admin_summary.html',
                           subjects=json.dumps(subjects),
                           total_scores=json.dumps(total_scores),
                           subjects_attempt=json.dumps(subjects_attempt),
                           attempts=json.dumps(attempts),
                           subjects_avg=json.dumps(subjects_avg),
                           avg_scores=json.dumps(avg_scores))
