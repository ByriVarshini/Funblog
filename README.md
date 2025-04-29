```markdown
# 📝 FunBlog – A Full-Stack Blogging Platform

FunBlog is a modern, responsive blogging web application built with **FastAPI** and **PostgreSQL**. It provides a seamless interface for users to register, log in, create, edit, and delete blog posts. Admins have additional privileges to manage content and users.

## 🚀 Features

- 🔐 **User Authentication**
  - JWT-based secure login and registration
  - Role-based access (User/Admin)

- 📰 **Blog Management**
  - Create, edit, view, and delete posts
  - Markdown support for rich content
  - Post timestamps and author info

- 🎨 **Frontend**
  - Responsive UI built with HTML, CSS, Bootstrap, and JavaScript
  - Clean and modern design
  - Mobile-friendly layout

- 🛠️ **Admin Panel**
  - View, manage, and delete users
  - Moderate posts

- 💾 **Database**
  - PostgreSQL integration for persistent storage
  - SQLAlchemy ORM for database operations

---

## 🏗️ Tech Stack

| Layer        | Technology             |
| ------------ | ---------------------- |
| Backend      | FastAPI, Python        |
| Frontend     | HTML, CSS, Bootstrap, JS |
| Database     | PostgreSQL             |
| Auth         | JWT (JSON Web Token)   |
| ORM          | SQLAlchemy           

---

## 📁 Folder Structure

```
funblog/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   ├── schemas/
│   └── utils/
│
├── static/
├── templates/
├── requirements.txt
├── README.md
└── .env
```

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL installed and running
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/funblog.git
cd funblog
```

### 2. Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file and add:

```ini
DATABASE_URL=postgresql://username:password@localhost:5432/funblog
SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

### 4. Run the App

```bash
uvicorn app.main:app --reload
```


## 💡 Author

**Varshini**  
[GitHub](https://github.com/yourusername)

---

```

Let me know if you'd like the `requirements.txt` generated or need help adding screenshots.
