from locust import HttpUser, task, between
import random
import json
from datetime import datetime, timedelta

class ShortLinkUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"
    short_codes = []

    @task(3)
    def create_short_link(self):
        url = f"https://example{random.randint(1, 1000)}.com"
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        response = self.client.post(
            "/links/shorten",
            json={
                "original_url": url,
                "expires_at": expires_at
            }
        )
        
        if response.status_code == 200:
            short_code = response.json()["short_code"]
            self.short_codes.append(short_code)

    @task(5)
    def redirect_to_original(self):
        if self.short_codes:
            short_code = random.choice(self.short_codes)
            self.client.get(f"/links/{short_code}", allow_redirects=False)

    @task(1)
    def get_link_stats(self):
        if self.short_codes:
            short_code = random.choice(self.short_codes)
            self.client.get(f"/links/{short_code}/stats")

    @task(1)
    def search_links(self):
        self.client.get("/links/search?original_url=example.com") 