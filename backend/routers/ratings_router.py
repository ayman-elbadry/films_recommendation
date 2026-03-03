"""
Ratings router: submit single or batch ratings.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth import get_current_user
from storage import add_rating, add_ratings_batch, get_ratings_for_user, update_rating, delete_rating
from routers.recommendations_router import movies_df
from tmdb_service import search_poster
from fastapi import HTTPException, status

router = APIRouter(prefix="/ratings", tags=["Ratings"])


# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------
class SingleRating(BaseModel):
    movie_id: int
    rating: float = Field(ge=0.5, le=5.0)


class BatchRatingsRequest(BaseModel):
    ratings: list[SingleRating]


class RatingResponse(BaseModel):
    message: str


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.post("", response_model=RatingResponse)
def submit_rating(body: SingleRating, user: dict = Depends(get_current_user)):
    """Submit a single movie rating for the authenticated user."""
    add_rating(user_id=user["id"], movie_id=body.movie_id, rating=body.rating)
    return RatingResponse(message="Rating saved successfully")


@router.post("/batch", response_model=RatingResponse)
def submit_batch_ratings(body: BatchRatingsRequest, user: dict = Depends(get_current_user)):
    """Submit multiple ratings at once (used during cold-start onboarding)."""
    if len(body.ratings) < 3:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must rate at least 3 movies",
        )
    add_ratings_batch(
        user_id=user["id"],
        rating_list=[r.model_dump() for r in body.ratings],
    )
    return RatingResponse(message=f"{len(body.ratings)} ratings saved successfully")


@router.get("")
async def get_my_ratings(user: dict = Depends(get_current_user)):
    """Get all ratings submitted by the authenticated user, enriched with poster_url and title."""
    user_ratings = get_ratings_for_user(user["id"])
    
    # Enrich with movie data
    enriched_ratings = []
    for r in user_ratings:
        mid = r["movie_id"]
        row = movies_df[movies_df["movieId"] == mid]
        if not row.empty:
            title = str(row.iloc[0]["title"])
            poster = await search_poster(mid, title)
            r["title"] = title
            r["poster_url"] = poster
            enriched_ratings.append(r)
            
    # Sort by newest first
    enriched_ratings.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return enriched_ratings


@router.put("/{movie_id}", response_model=RatingResponse)
def update_existing_rating(movie_id: int, body: SingleRating, user: dict = Depends(get_current_user)):
    """Update a previously submitted rating."""
    success = update_rating(user_id=user["id"], movie_id=movie_id, new_rating=body.rating)
    if not success:
        raise HTTPException(status_code=404, detail="Rating not found")
    return RatingResponse(message="Rating updated successfully")


@router.delete("/{movie_id}", response_model=RatingResponse)
def delete_existing_rating(movie_id: int, user: dict = Depends(get_current_user)):
    """Delete a previously submitted rating."""
    success = delete_rating(user_id=user["id"], movie_id=movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rating not found")
    return RatingResponse(message="Rating deleted successfully")
