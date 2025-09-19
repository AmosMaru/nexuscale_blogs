
# 📰 Simple Articles API

A FastAPI service that fetches articles from a Strapi backend with optional Redis caching.  
It exposes two endpoints:

- `GET /articles` → Fetch all articles  
- `GET /articles/{id}` → Fetch a single article by ID  

---

## 🚀 Features
- FastAPI for API endpoints
- Requests to fetch articles from Strapi
- Redis caching support (optional)
- Environment variables managed via `.env`

---

## 📂 Project Structure
```

.
├── articles_service.py   # Service class for fetching articles
├── main.py               # FastAPI entrypoint
├── requirements.txt      # Dependencies
├── .env                  # Environment variables
└── README.md             # Documentation

````

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone git@github.com:AmosMaru/nexuscale_blogs.git
cd articles-api
````

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
BLOG_API_TOKEN=your_api_token_here
BLOGS_API_URL=https://your-strapi-instance.com
```

---

## 🗄️ Running Redis (Optional Caching)

### Install Redis on Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install redis-server -y
```

Enable and start Redis:

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Install Redis on macOS (using Homebrew)

```bash
brew install redis
brew services start redis
```

### Install Redis on Windows

1. Download from: [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
2. Extract and run `redis-server.exe`.

Test Redis is working:

```bash
redis-cli ping
# PONG
```

---

## ▶️ Running the FastAPI Server

Start the API with **Uvicorn**:

```bash
uvicorn main:app --reload
```

By default, it runs on:

```
http://127.0.0.1:8000
```

---

## 📖 API Endpoints

### Get All Articles

```http
GET /articles
```

### Get Article by ID

```http
GET /articles/{id}
```

---

## 📝 Example Response

```json
[
  {
    "id": 1,
    "attributes": {
      "title": "First Blog Post",
      "content": "This is a test article..."
    }
  }
]
```

