from articles import ArticlesService
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uvicorn

# Singleton instance
articles_service = ArticlesService()

app = FastAPI(title="Nexuscale Articles API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        'https://nexuscale.ai',
        "https://www.nexuscale.ai",
        "https://articles.nexuscale.ai"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/articles", response_model=List[Dict[str, Any]])
def get_articles():
    """Get all articles"""
    try:
        return articles_service.get_all_articles()
    except HTTPException as e:
        raise e


@app.get("/articles/{article_id}", response_model=Dict[str, Any])
def get_article(article_id: str):
    """Get article by ID"""
    try:
        return articles_service.get_article_by_id(article_id)
    except HTTPException as e:
        raise e


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7000, reload=True)
