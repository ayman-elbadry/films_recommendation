from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import pandas as pd

from tmdb_service import search_poster, get_movie_details
from routers.recommendations_router import movies_df  # Reuse the loaded DataFrame

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("/search")
async def search_movies(q: str = "", limit: int = 12):
    """
    Search for movies by title (case-insensitive substring match).
    Returns the top 'limit' matches with their posters.
    """
    if not q or len(q) < 2:
        return []
    
    if movies_df is None or movies_df.empty:
        raise HTTPException(status_code=500, detail="Movies data not loaded")

    # Case-insensitive search
    mask = movies_df["title"].str.contains(q, case=False, na=False)
    matches = movies_df[mask].head(limit)
    
    results = []
    for _, row in matches.iterrows():
        movie_id = int(row["movieId"])
        title = str(row["title"])
        
        poster_url = await search_poster(movie_id, title)
        
        results.append({
            "movieId": movie_id,
            "title": title,
            "genres": str(row["genres"]),
            "poster_url": poster_url
        })
        
    return results

@router.get("/{movie_id}/details")
async def get_single_movie_details(movie_id: int):
    """
    Get full details for a single movie including TMDB enriched data
    like synopsis, runtime, and cast.
    """
    if movies_df is None or movies_df.empty:
        raise HTTPException(status_code=500, detail="Movies data not loaded")
        
    row = movies_df[movies_df["movieId"] == movie_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Movie not found in local database")
        
    r = row.iloc[0]
    title = str(r["title"])
    genres = str(r["genres"])
    
    # Base local info + poster
    poster_url = await search_poster(movie_id, title)
    
    response = {
        "movieId": movie_id,
        "title": title,
        "genres": genres,
        "poster_url": poster_url,
    }
    
    # Enrichment
    enriched_data = await get_movie_details(movie_id, title)
    if enriched_data and "error" not in enriched_data:
        response.update(enriched_data)
    else:
        # Fallback empty fields if TMDB fails
        response.update({
            "overview": "No synopsis available.",
            "release_date": "",
            "cast": [],
            "tagline": ""
        })
        
    return response
