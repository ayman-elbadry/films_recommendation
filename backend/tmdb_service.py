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
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# TMDB API key — set via environment variable or replace with your own
# Get your free key at: https://www.themoviedb.org/settings/api
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

# In-memory cache: movieId -> poster_url
_poster_cache: dict[int, str | None] = {}
# In-memory cache: movieId -> tmdb_id
_tmdb_id_cache: dict[int, int | None] = {}
# In-memory cache: movieId -> full_details_dict
_details_cache: dict[int, dict | None] = {}


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
    if movie_id in _poster_cache and movie_id in _tmdb_id_cache:
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
                first_result = results[0]
                tmdb_id = first_result.get("id")
                _tmdb_id_cache[movie_id] = tmdb_id

                poster_path = first_result.get("poster_path")
                if poster_path:
                    url = f"{TMDB_IMAGE_BASE}/{size}{poster_path}"
                    _poster_cache[movie_id] = url
                    return url

        # No poster found
        _tmdb_id_cache[movie_id] = _tmdb_id_cache.get(movie_id, None) 
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


async def get_movie_details(movie_id: int, title: str) -> dict | None:
    """
    Fetch comprehensive movie details from TMDB (Synopsis, Cast, etc.).
    Relies on search_poster to resolve the TMDB ID first if not cached.
    """
    if not TMDB_API_KEY:
        return {"error": "Missing TMDB API Key"}

    if movie_id in _details_cache:
        return _details_cache[movie_id]

    # Ensure we have the TMDB ID by calling the search
    if movie_id not in _tmdb_id_cache:
        await search_poster(movie_id, title)
    
    tmdb_id = _tmdb_id_cache.get(movie_id)
    if not tmdb_id:
        _details_cache[movie_id] = None
        return None

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            params = {
                "api_key": TMDB_API_KEY,
                "append_to_response": "credits", # gets the cast
            }
            resp = await client.get(f"{TMDB_BASE_URL}/movie/{tmdb_id}", params=params)
            resp.raise_for_status()
            data = resp.json()

            # Format the output nicely
            cast_list = data.get("credits", {}).get("cast", [])
            top_cast = [c["name"] for c in cast_list[:5]] # Take top 5 actors
            
            details = {
                "tmdb_id": tmdb_id,
                "overview": data.get("overview", "No synopsis available."),
                "release_date": data.get("release_date", ""),
                "runtime": data.get("runtime", 0),
                "vote_average": data.get("vote_average", 0.0),
                "cast": top_cast,
                "tagline": data.get("tagline", "")
            }
            
            _details_cache[movie_id] = details
            return details

    except Exception as e:
        print(f"[TMDB] Error fetching full details for '{title}' (ID {tmdb_id}): {e}")
        return None
