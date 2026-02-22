"""
TMDB API service for fetching movie posters.
Uses in-memory cache to avoid repeated API calls.

TMDB provides a free API. To get your own key:
1. Create a free account at https://www.themoviedb.org/signup
2. Go to Settings > API > Create > Developer
3. Copy your API Key (v3 auth) and paste it below
"""

import re
import os
import httpx

# TMDB API key — set via environment variable or replace with your own
# Get your free key at: https://www.themoviedb.org/settings/api
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

# In-memory cache: movieId -> poster_url
_poster_cache: dict[int, str | None] = {}


def _parse_title_year(title: str) -> tuple[str, str | None]:
    """
    Parse MovieLens title format: "Movie Name, The (YEAR)" -> ("The Movie Name", "YEAR")
    Also handles: "Movie Name (YEAR)" -> ("Movie Name", "YEAR")
    """
    match = re.match(r"^(.+?)\s*\((\d{4})\)\s*$", title)
    if match:
        name = match.group(1).strip()
        year = match.group(2)
        # Handle MovieLens "Name, The" -> "The Name" format
        comma_match = re.match(r"^(.+),\s*(The|A|An|Le|La|Les|Der|Das|Die|El|Il)$", name, re.IGNORECASE)
        if comma_match:
            name = f"{comma_match.group(2)} {comma_match.group(1)}"
        return name, year
    return title.strip(), None


async def search_poster(movie_id: int, title: str, size: str = "w500") -> str | None:
    """
    Search TMDB for a movie poster by title. Returns the full poster URL.
    Results are cached in memory.
    """
    if not TMDB_API_KEY:
        return None

    # Check cache first
    if movie_id in _poster_cache:
        return _poster_cache[movie_id]

    name, year = _parse_title_year(title)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params = {
                "api_key": TMDB_API_KEY,
                "query": name,
                "include_adult": "false",
            }
            if year:
                params["year"] = year

            resp = await client.get(f"{TMDB_BASE_URL}/search/movie", params=params)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if results:
                poster_path = results[0].get("poster_path")
                if poster_path:
                    url = f"{TMDB_IMAGE_BASE}/{size}{poster_path}"
                    _poster_cache[movie_id] = url
                    return url

        # No poster found
        _poster_cache[movie_id] = None
        return None

    except Exception as e:
        print(f"[TMDB] Error searching poster for '{title}': {e}")
        return None


async def get_posters_batch(movies: list[dict], size: str = "w500") -> dict[int, str | None]:
    """
    Fetch posters for a list of movies. Each movie dict must have 'movieId' and 'title'.
    Returns a dict mapping movieId -> poster_url.
    """
    result = {}
    for movie in movies:
        mid = movie["movieId"]
        title = movie["title"]
        poster_url = await search_poster(mid, title, size)
        result[mid] = poster_url
    return result
