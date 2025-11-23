# FastCrate

A modern, opinionated FastAPI boilerplate for building high-performance APIs with best practices out of the box.




## .env Requirments
HUBSPOT_CLIENT_ID = 
HUBSPOT_CLIENT_SECRET = 
HUBSPOT_REDIRECT_URI = 
GROQ_API_KEY =
MODEL_NAME = openai/gpt-oss-20b
HUBSPOT_BASE_URL = https://api.hubapi.com
API_BASE_URL =  
EMAIL_SMTP_SERVER= 
EMAIL_SMTP_PORT = 
EMAIL_USERNAME = 
EMAIL_PASSWORD = 
MONGO_URI = 
MONGO_DB = 
REDIS_HOST = 
REDIS_PORT = 
REDIS_USERNAME =
REDIS_PASSWORD = 
VECTOR_DB_URL = 
VECTOR_DB_API = 
QDRANT_COLLECTION = 
REDIS_URL=
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
EMBEDING_MODEL = all-MiniLM-L6-v2



## 🚀 Quick Start

```bash
git clone https://github.com/mubashirsidiki/FastCrate.git
cd FastCrate

# Install uv if not already installed
pip install uv

# Install dependencies
uv sync

# To add a new package
uv add package_name
# Example: uv add pandas

# Run the app
uv run python main.py
```

> ⚠️ **Note**: If OneDrive causes issues, use:
> ```bash
> uv sync --link-mode=copy
> ```

## 🧪 Testing the Application

### Interactive API Documentation
First, visit the FastAPI interactive documentation:
- **URL**: http://localhost:8000/docs

### Health Check Endpoint
Test if the application is running properly:
- **Method**: GET
- **Endpoint**: `/api/v1/healthcheck`
- **Description**: Health Check

## 📊 Logger Service

Access the built-in logger service to view application logs:

- **URL**: http://localhost:8000/api/v1/logs

> 💡 **Tip**: If after clicking the "Fetch Logs" button you see nothing, try switching to incognito mode in your browser.

## Runnig celery
- **command**: uv run celery -A modules.celery.celery_ini worker --loglevel=info --concurrency=1 --pool=solo

## Running flower
- **command**: uv run celery -A modules.celery.celery_ini flower

## The Flow of Backend in detailed can be found here
- **Link**: https://drive.google.com/file/d/1Unuw3HK6Qlbk6sIVYawtEykcq1ZzzVD-/view?usp=sharing

