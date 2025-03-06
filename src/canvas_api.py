import requests
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd

class CanvasAPI:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.params = {"access_token": api_key}
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=self.params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return None

    def get_courses(self) -> List[Tuple[int, str]]:
        """Fetch available courses"""
        data = self._make_request("/courses")
        if data:
            return [(course['id'], course['name']) 
                    for course in data 
                    if 'name' in course]
        return []

    def get_discussion_topics(self, course_id: int) -> List[Tuple[int, str]]:
        """Fetch discussion topics for a course"""
        data = self._make_request(f"/courses/{course_id}/discussion_topics")
        if data:
            return [(topic['id'], topic['title']) 
                    for topic in data]
        return []

    def get_discussion_data(self, course_id: int, topic_id: int) -> Optional[Dict]:
        """Fetch discussion posts and participants"""
        return self._make_request(
            f"/courses/{course_id}/discussion_topics/{topic_id}/view"
        ) 