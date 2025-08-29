import requests

API_URL = "https://api.waifu.pics/sfw/waifu"  # 免费动漫图API

def get_random_anime_pic() -> str:
    """
    Fetch a random anime image URL from the public API.
    Returns:
        str: The URL of the anime image.
    Raises:
        Exception: If the API request fails.
    """
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("url", "")
    except Exception as e:
        raise Exception(f"Failed to fetch anime picture: {e}")
