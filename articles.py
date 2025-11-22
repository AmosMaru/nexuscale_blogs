import redis
import requests
from requests.adapters import HTTPAdapter
from requests import Session
import json
import os
from typing import List, Dict, Any
from fastapi import HTTPException
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()  # Load environment variables from .env file
API_TOKEN = os.getenv("BLOG_API_TOKEN")
BLOGS_API_URL = os.getenv("BLOGS_API_URL")

class ArticlesService:
    def __init__(self):
        # Configs
        self.API_TOKEN = API_TOKEN
        self.API_URL = BLOGS_API_URL
        self.CACHE_TTL = 60 * 30  # 30 minutes
        self.PAGE_SIZE = 15  # Articles per page
        self.MAX_WORKERS = 5  # Concurrent requests

        # Redis connection - configurable for production
        self.redis_client = redis.StrictRedis(
            host=os.getenv("REDIS_HOST", "127.0.0.1"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            decode_responses=True
        )

        # HTTP Session with connection pooling for better performance
        self.session = Session()
        adapter = HTTPAdapter(
            pool_connections=int(os.getenv("HTTP_POOL_CONNECTIONS", "10")),
            pool_maxsize=int(os.getenv("HTTP_POOL_MAXSIZE", "20")),
            max_retries=3
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def _fetch_page(self, page: int) -> Dict[str, Any]:
        """Fetch a single page of articles"""
        try:
            response = self.session.get(
                f"{self.API_URL}/api/articles?populate=*&sort[0]=publishedAt:desc&pagination[page]={page}&pagination[pageSize]={self.PAGE_SIZE}",
                headers={"Authorization": f"Bearer {self.API_TOKEN}"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch page {page}: {str(e)}")

    def get_all_articles(self) -> List[Dict[str, Any]]:
        """Fetch all articles with caching and parallel pagination"""
        cache_key = "articles"

        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        try:
            # First request to get total count
            first_response = self._fetch_page(1)
            all_articles = first_response["data"]

            pagination = first_response.get("meta", {}).get("pagination", {})
            total_pages = pagination.get("pageCount", 1)

            # If there are more pages, fetch them concurrently
            if total_pages > 1:
                with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                    # Submit tasks for remaining pages
                    future_to_page = {
                        executor.submit(self._fetch_page, page): page
                        for page in range(2, total_pages + 1)
                    }

                    # Collect results as they complete
                    for future in as_completed(future_to_page):
                        page_data = future.result()
                        all_articles.extend(page_data["data"])

            # Cache the result
            self.redis_client.setex(cache_key, self.CACHE_TTL, json.dumps(all_articles))
            return all_articles

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")
    
    def get_articles_paginated(self, page: int = 1, page_size: int = None) -> Dict[str, Any]:
        """Fetch articles with pagination - returns data and metadata"""
        if page_size is None:
            page_size = self.PAGE_SIZE

        cache_key = f"articles:page:{page}:size:{page_size}"

        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        try:
            response = self.session.get(
                f"{self.API_URL}/api/articles?populate=*&sort[0]=publishedAt:desc&pagination[page]={page}&pagination[pageSize]={page_size}",
                headers={"Authorization": f"Bearer {self.API_TOKEN}"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Cache the result
            self.redis_client.setex(cache_key, self.CACHE_TTL, json.dumps(result))
            return result
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch page {page}: {str(e)}")

    def get_article_by_id(self, article_id: str) -> Dict[str, Any]:
        """Fetch single article by ID with caching"""
        cache_key = f"article:{article_id}"

        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        try:
            response = self.session.get(
                f"{self.API_URL}/api/articles/{article_id}?populate=*",
                headers={"Authorization": f"Bearer {self.API_TOKEN}"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()["data"]

            # Cache the result
            self.redis_client.setex(cache_key, self.CACHE_TTL, json.dumps(data))
            return data
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch article {article_id}: {str(e)}")

    def get_article_by_slug(self, slug: str) -> Dict[str, Any]:
        """Fetch single article by slug with caching"""
        cache_key = f"article:slug:{slug}"

        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        try:
            # Use Strapi's filter syntax to query by slug
            params = {
                "filters[slug][$eq]": slug,
                "populate": "*"
            }

            response = self.session.get(
                f"{self.API_URL}/api/articles",
                params=params,
                headers={"Authorization": f"Bearer {self.API_TOKEN}"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Strapi returns an array of results, get the first one
            if result.get("data") and len(result["data"]) > 0:
                data = result["data"][0]
                # Cache the result
                self.redis_client.setex(cache_key, self.CACHE_TTL, json.dumps(data))
                return data
            else:
                raise HTTPException(status_code=404, detail=f"Article with slug '{slug}' not found")

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch article by slug '{slug}': {str(e)}")

