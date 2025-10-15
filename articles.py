import redis
import requests
import json
import os
from typing import List, Dict, Any
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
API_TOKEN = os.getenv("BLOG_API_TOKEN")
BLOGS_API_URL = os.getenv("BLOGS_API_URL")

class ArticlesService:
    def __init__(self):
        # Configs
        self.API_TOKEN = API_TOKEN
        self.API_URL = BLOGS_API_URL
        self.CACHE_TTL = 60 * 10  # 10 minutes

        # Redis connection
        self.redis_client = redis.StrictRedis(
        host="127.0.0.1",
        port=6379,
        db=0,
        decode_responses=True
        )

    def get_all_articles(self) -> List[Dict[str, Any]]:
        """Fetch all articles with caching"""
        cache_key = "articles"
        
        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            response = requests.get(
                f"{self.API_URL}/api/articles?populate=*",
                headers={"Authorization": f"Bearer {self.API_TOKEN}"}
            )
            response.raise_for_status()
            data = response.json()["data"]
            
            # Cache the result
            self.redis_client.setex(cache_key, self.CACHE_TTL, json.dumps(data))
            return data
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")
    
    def get_article_by_id(self, article_id: str) -> Dict[str, Any]:
        """Fetch single article by ID with caching"""
        cache_key = f"article:{article_id}"
        
        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            response = requests.get(
                f"{self.API_URL}/api/articles/{article_id}?populate=*",
                headers={"Authorization": f"Bearer {self.API_TOKEN}"}
            )
            response.raise_for_status()
            data = response.json()["data"]
            
            # Cache the result
            # self.redis_client.setex(cache_key, self.CACHE_TTL, json.dumps(data))
            return data
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch article {article_id}: {str(e)}")

