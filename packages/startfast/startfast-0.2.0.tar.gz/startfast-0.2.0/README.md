<div align="center">

# ⚡ StartFast

**The production-ready FastAPI project structure that senior developers spend 4+ hours building from scratch.**

*Skip the boilerplate. Ship the features.*

[![PyPI version](https://badge.fury.io/py/startfast.svg)](https://badge.fury.io/py/startfast)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

```bash
pip install startfast
startfast my-api
# ✅ Production FastAPI project ready in 30 seconds
```

</div>

---

## 🎯 Why StartFast?

Every FastAPI project starts the same way: authentication, database setup, Docker configuration, testing framework, project structure. **You've built this 10 times already.**

StartFast gives you the **professional project structure** instantly, so you can focus on your actual business logic.

```bash
# Instead of 4 hours of setup...
startfast my-api

# You get production-ready:
✅ Async FastAPI with proper structure
✅ PostgreSQL + SQLAlchemy (async)  
✅ JWT authentication + user management
✅ Docker + docker-compose
✅ pytest + coverage
✅ API documentation
```

---

## ⚡ Quick Start

### Get Started in 30 Seconds

```bash
# Install
pip install startfast

# Create project
startfast my-api

# Start developing
cd my-api
uvicorn app.main:app --reload
```

That's it. Your API is live at `http://localhost:8000/docs`

### Customize When Needed

```bash
# SQLite for quick prototyping
startfast my-app --db sqlite

```

---

## 🏗️ What You Get

**Professional project structure** following FastAPI best practices:

```plaintext
my-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Environment configuration
│   │   └── security.py      # JWT auth + password hashing
│   ├── api/v1/              # API routes
│   ├── models/              # Database models  
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
├── tests/                   # pytest test suite
├── Dockerfile               # Production container
├── docker-compose.yml       # Local development
└── requirements.txt         # Dependencies
```

**Everything configured correctly:**

- Async database connections
- Password hashing with bcrypt
- JWT token authentication
- Request/response validation
- Error handling middleware
- Health check endpoints
- CORS configuration
- Environment-based config

---

## 🚀 Core Commands

```bash
# Standard full-featured API
startfast my-api

# Quick prototype (SQLite + minimal features)
startfast my-app --minimal

```

### Database Options

```bash
--db postgres    # Production (default)
--db sqlite      # Development/prototyping  
--db mysql       # Enterprise compatibility
--db mongo       # Document store
```

### Authentication Options

```bash
--auth jwt       # JWT tokens (default)
--auth oauth2    # OAuth2 with scopes
--auth api-key   # Simple API keys
--auth none      # No authentication
```

---

## 💡 Perfect For

- **🚀 Startups**: Get your MVP API running in minutes
- **🏢 Enterprise**: Consistent, scalable project structure
- **🧪 Prototyping**: Quick experiments with production-ready foundation
- **📚 Learning**: Study well-structured FastAPI projects
- **⚡ Hackathons**: Skip setup, focus on features

---

## 🛠️ Installation

```bash
pip install startfast
```

**Requirements:** Python 3.8+

---

## 🤝 Contributing

StartFast is built by developers who got tired of recreating the same project structure.

```bash
git clone https://github.com/Incognitol07/startfast.git
cd startfast
pip install -e ".[dev]"
```

Found a better way to structure something? **PRs welcome!**

---

## 📄 License

MIT License - use it however you want.

---

<div align="center">

**Stop rebuilding. Start shipping.**

[![Star on GitHub](https://img.shields.io/github/stars/Incognitol07/startfast?style=social)](https://github.com/Incognitol07/startfast)

Made by developers who value their time ⚡

</div>
