# 🎯 Quizzo - Quiz Management System

**Quizzo** is a full-stack **Flask + SQLite** application designed for managing subjects, chapters, quizzes, and user attempts in a structured and user-friendly way. It supports two roles:

* **👨‍🏫 Admin** – Manage quiz content, users, and reports.
* **🧑‍🎓 User** – Register, take quizzes, and view progress.

---

## 🚀 Features Overview

### 🛡️ Admin Capabilities

* **CRUD Operations** for:

  * 📚 **Subjects** – Add descriptions and organize chapters.
  * 📖 **Chapters** – Belong to subjects.
  * 📝 **Quizzes** – Include date, duration, and remarks (used as name).
  * ❓ **Questions** – Add question text, options, and correct answer.
* **Dashboards**:

  * 📊 Summary of subjects, chapters, and quiz statuses.
  * ⚙️ Direct Edit/Delete controls for fast management.
* **Quiz Dashboard**:

  * 🗂 View and manage quizzes per subject/chapter.
  * ➕ Add/Edit/Remove questions directly.
* 🔍 **Smart Search** across:

  * Subjects, chapters, quizzes, users.
* 📈 **Summary Reports**:

  * Track user performance, attempt history, and scores.
* 🌐 **REST API**:

  * JSON endpoints for users, subjects, quizzes, and scores.

### 👥 User Functionality

* ✅ **Register & Login**
* 🧪 **Take Quizzes**:

  * Step-by-step (1-question-at-a-time) interface.
  * ⏱ Timer enabled for timed assessments.
* 📄 **View Scores**:

  * See detailed history of previous quiz attempts with timestamps and performance.
* 🔍 **Search** subjects or available quizzes.
* 📊 **Quiz Attempt Summary**:

  * Track participation per subject and month-wise performance.

---

## 🧰 Tech Stack

| Layer      | Technology                     |
| ---------- | ------------------------------ |
| Backend    | Python 3 + Flask               |
| Frontend   | HTML, CSS, Bootstrap, Jinja2   |
| Database   | SQLite3                        |
| JS Utility | Vanilla JS (Timer, Validation) |
| APIs       | RESTful Flask endpoints        |

---

## ⚙️ Getting Started

### 🔧 Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/Yuvraj960/Quizzo.git
   cd Quizzo
   ```

2. **Create & activate virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # For Windows
   # or
   source venv/bin/activate  # For macOS/Linux
   ```

3. **Install required packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**

   ```bash
   python db_init.py
   ```

   > This creates the `quiz_app.sqlite3` database and a **default admin**:
   > **Email**: `admin@quiz.com`
   > **Password**: `admin123`

---

## ▶️ Running the App

Start the Flask server:

```bash
python app.py
```

Then visit: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)


### Through Docker

```bash
docker pull yuvraj96/quizzo:latest
docker run -d -p 5000:5000 yuvraj96/quizzo:latest
```

- The app starts by default at **http://127.0.0.1:5000/**.

---

## 🗂 Project Structure

```
Quizzo/
├── app.py               # Main application entry point
├── db_init.py           # Initializes SQLite database
├── static/              # CSS, JS, Bootstrap files
├── templates/           # HTML templates using Jinja2
├── requirements.txt     # Project dependencies
├── quiz_app.sqlite3     # SQLite DB (auto-created)
└── README.md            # Project documentation
```

---

## 🧪 Sample Admin Flow

1. Log in as admin (`admin@quiz.com` / `admin123`)
2. Add a subject → add chapters → create quizzes under each chapter
3. Add questions to each quiz
4. Monitor user attempts and view reports

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repo 🍴
2. Create a branch: `feature/your-feature-name`
3. Make your changes and commit 🚀
4. Submit a pull request 📥

### Contribution Ideas

* Add charts/graphs to analytics
* Export reports to CSV or PDF
* Enhance frontend UI/UX
* Add email notifications for quiz results
* Role-based access enhancement

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙋 Support & Contact

For issues, suggestions, or feature requests:

* Open an [issue](https://github.com/Yuvraj960/Quizzo/issues)
* Or contact the author via GitHub [@Yuvraj960](https://github.com/Yuvraj960)

---

Give ⭐️ to support the project if you find it useful!

---

Let me know if you want me to also generate a `CONTRIBUTING.md`, `.gitignore`, or installation screenshots section!
