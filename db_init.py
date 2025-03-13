import sqlite3

DATABASE = 'quiz_app.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT,
            qualification TEXT,
            dob TEXT,
            role TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id INTEGER NOT NULL,
            date_of_quiz TEXT,
            time_duration TEXT,
            remarks TEXT,
            FOREIGN KEY(chapter_id) REFERENCES chapters(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_title TEXT NOT NULL,
            question_text TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT,
            option4 TEXT,
            correct_option INTEGER NOT NULL,
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            time_stamp_of_attempt TEXT,
            total_scored INTEGER,
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    c.execute('SELECT * FROM users WHERE role = "admin"')
    admin_record = c.fetchone()
    if not admin_record:
        c.execute('''
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', ("admin@quiz.com", "admin123", "Quiz Master", "admin"))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
