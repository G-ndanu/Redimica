# 🩺 Redimica – Doctor-Patient Engagement System (DPES)

A web-based doctor-patient engagement platform designed to streamline virtual care through symptom tracking, real-time messaging, and video consultations using Google Meet.

---

## 📌 Features

- Patient health journal for symptom tracking  
- Real-time messaging system (doctor ↔ patient) with file sharing  
- Google Meet integration for virtual consultations  
- Role-based dashboards for doctors and patients  
- Doctor feedback and consultation history  
- Profile management for patients and doctors  
- Responsive design for mobile and desktop use

---

## 🧱 Tech Stack

| Layer        | Technology               |
|--------------|---------------------------|
| Frontend     | HTML, CSS, JavaScript     |
| Backend      | Django, Django Channels   |
| Real-time    | WebSockets via Channels   |
| Database     | MySQL                     |
| Hosting      | Google Cloud Platform     |
| Virtual Meet | Google Meet API           |
| Secrets Mgmt | python-decouple + `.env`  |

---

## ⚙️ Installation Guide

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/redimica.git
cd redimica
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
.env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup `.env` File

Create a `.env` file in the project root and add:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Server

```bash
python manage.py runserver
```

---

## 🔐 Google Meet Integration

1. Set up a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Google Calendar API**
3. Download `credentials.json` and store it securely in your project
4. Use `google-auth-oauthlib` to authenticate users and generate Meet links

---

## 📁 Project Structure

```bash
redimica/
├── backend/ 
|   ├── backend/       # Django project
│   ├── core/   
|   ├── .env             # Main Django app
│   ├── manage.py
|   └── requirements.txt
├── frontend/              # HTML/CSS/JS UI
├── venv/                  # Virtual environment
├── .gitignore
└── README.md
```

---

## ✍️ Author

- **Grace Ndanu** – [GitHub Profile](https://github.com/G-ndanu)

---

## 📄 License

MIT license