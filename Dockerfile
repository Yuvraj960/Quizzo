# ---- Base Image ----
FROM python:3.10-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Copy requirements ----
COPY requirements.txt .

# ---- Install dependencies ----
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ---- Copy code ----
COPY . .

# ---- Expose the port your app runs on ----
EXPOSE 5000

# ---- Set environment variables ----
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# ---- Run the app ----
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
