"""
Ratings router: submit single or batch ratings.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth import get_current_user
from storage import add_rating, add_ratings_batch, get_ratings_for_user

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
def get_my_ratings(user: dict = Depends(get_current_user)):
    """Get all ratings submitted by the authenticated user."""
    return get_ratings_for_user(user["id"])
