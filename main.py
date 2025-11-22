from articles import ArticlesService
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
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
        "https://articles.nexuscale.ai",
        "https://blogs.nexuscale.ai",
        "https://new-nexuscale-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/articles")
def get_articles(
    page: Optional[int] = Query(None, ge=1, description="Page number (starts at 1)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page (max 100)")
):
    """
    Get articles - with or without pagination

    - If no query params: returns ALL articles (legacy behavior)
    - If page is provided: returns paginated results with metadata

    Examples:
    - /articles - returns all articles
    - /articles?page=1 - returns first page (default page size)
    - /articles?page=2&page_size=10 - returns page 2 with 10 items
    """
    try:
        # If page is specified, return paginated results
        if page is not None:
            return articles_service.get_articles_paginated(page=page, page_size=page_size)

        # Otherwise, return all articles (legacy behavior)
        return articles_service.get_all_articles()
    except HTTPException as e:
        raise e


@app.get("/articles/slug/{slug}", response_model=Dict[str, Any])
def get_article_by_slug(slug: str):
    """Get article by slug"""
    try:
        return articles_service.get_article_by_slug(slug)
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
