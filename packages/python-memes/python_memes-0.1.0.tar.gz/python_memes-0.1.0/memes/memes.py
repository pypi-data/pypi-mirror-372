import requests

class MemeFetcher:
    API_URL = "https://meme-api.com/gimme"

    def __init__(self, subreddit: str | None = None):
        self.subreddit = subreddit

    def get_meme(self) -> dict:
        url = self.API_URL
        if self.subreddit:
            url = f"{url}/{self.subreddit}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                "title": data.get("title"),
                "subreddit": data.get("subreddit"),
                "url": data.get("url"),
            }

        except requests.exceptions.Timeout:
            return {"error": "Meme API request timed out."}

        except requests.exceptions.ConnectionError:
            return {"error": "Could not connect to Meme API."}

        except requests.exceptions.HTTPError as e:
            return {"error": f"Meme API returned HTTP error: {e.response.status_code}"}

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
