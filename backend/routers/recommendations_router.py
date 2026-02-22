"""
Recommendation router: hybrid Content-Based + Collaborative Filtering.

Hybrid Logic:
1. Find a movie the user recently liked (rated >= 4.0)
2. Use TF-IDF + Cosine Similarity on genres to find Top 30 similar movies
3. Use the pre-trained SVD model to predict ratings for those 30 movies
4. Return the Top 10 sorted by predicted SVD score
"""

import os
import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from svd_model import SVDModel  # noqa: F401 — needed for pickle to resolve the class
from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_current_user
from storage import get_ratings_for_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# ------------------------------------------------------------------
# Load data and model at module level (once on import / startup)
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent  # backend/
DATA_ROOT = BASE_DIR.parent             # project root (where CSVs live)
MODEL_PATH = BASE_DIR / "models" / "svd_model.pkl"

# Load movies
_movies_path = DATA_ROOT / "movies.csv"
if _movies_path.exists():
    movies_df = pd.read_csv(_movies_path)
    # Preprocess genres: replace '|' with space for TF-IDF
    movies_df["genres_clean"] = movies_df["genres"].fillna("").str.replace("|", " ", regex=False)
    print(f"[ML] Loaded {len(movies_df)} movies from {_movies_path}")
else:
    movies_df = pd.DataFrame(columns=["movieId", "title", "genres", "genres_clean"])
    print(f"[ML] WARNING: movies.csv not found at {_movies_path}")

# Build TF-IDF matrix on genres
_tfidf = TfidfVectorizer(stop_words="english")
_tfidf_matrix = _tfidf.fit_transform(movies_df["genres_clean"])
print(f"[ML] TF-IDF matrix shape: {_tfidf_matrix.shape}")

# Load SVD model
svd_model = None
if MODEL_PATH.exists():
    with open(MODEL_PATH, "rb") as f:
        svd_model = pickle.load(f)
    print(f"[ML] SVD model loaded from {MODEL_PATH}")
else:
    print(f"[ML] WARNING: SVD model not found at {MODEL_PATH}. Run train_model.py first!")

# Precompute popular movies (by average rating count from the original ratings CSV)
_ratings_path = DATA_ROOT / "ratings.csv"
_popular_movie_ids = []
if _ratings_path.exists():
    # Read just enough to compute popularity
    _ratings_sample = pd.read_csv(_ratings_path, usecols=["movieId", "rating"], nrows=1_000_000)
    _popularity = (
        _ratings_sample.groupby("movieId")
        .agg(count=("rating", "count"), mean=("rating", "mean"))
        .reset_index()
    )
    # Filter: at least 100 ratings, sort by mean rating
    _popular = _popularity[_popularity["count"] >= 100].sort_values("mean", ascending=False)
    _popular_movie_ids = _popular["movieId"].head(50).tolist()
    print(f"[ML] Precomputed {len(_popular_movie_ids)} popular movies")
else:
    print(f"[ML] WARNING: ratings.csv not found at {_ratings_path}")


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def _get_content_similar_movies(movie_id: int, top_n: int = 30) -> list[int]:
    """Find top_n movies similar to movie_id based on TF-IDF genre similarity."""
    idx_matches = movies_df[movies_df["movieId"] == movie_id].index
    if len(idx_matches) == 0:
        return []

    idx = idx_matches[0]
    sim_scores = cosine_similarity(_tfidf_matrix[idx], _tfidf_matrix).flatten()
    # Get top_n+1 (skip self)
    similar_indices = sim_scores.argsort()[::-1][1 : top_n + 1]
    return movies_df.iloc[similar_indices]["movieId"].tolist()


def _predict_svd_ratings(user_id: int, movie_ids: list[int]) -> list[dict]:
    """Use SVD model to predict ratings for a list of movies."""
    results = []
    for mid in movie_ids:
        movie_row = movies_df[movies_df["movieId"] == mid]
        if movie_row.empty:
            continue

        if svd_model is not None:
            predicted_rating = svd_model.predict(user_id, mid)
        else:
            predicted_rating = 3.0  # fallback if no model

        row = movie_row.iloc[0]
        results.append({
            "movieId": int(mid),
            "title": str(row["title"]),
            "genres": str(row["genres"]),
            "predicted_rating": round(predicted_rating, 2),
        })
    return results


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.get("/popular")
def get_popular_movies(limit: int = 10):
    """
    Return popular movies for the cold-start onboarding screen.
    These are high-rated movies with many ratings.
    """
    selected_ids = _popular_movie_ids[:limit]
    results = []
    for mid in selected_ids:
        row = movies_df[movies_df["movieId"] == mid]
        if not row.empty:
            r = row.iloc[0]
            results.append({
                "movieId": int(r["movieId"]),
                "title": str(r["title"]),
                "genres": str(r["genres"]),
            })
    return results


@router.get("")
def get_recommendations(user: dict = Depends(get_current_user)):
    """
    Hybrid recommendation endpoint:
    1. Find a movie the user recently liked (rating >= 4.0)
    2. Content-based: TF-IDF genre similarity → Top 30
    3. Collaborative: SVD predicted ratings for those 30
    4. Return Top 10 sorted by predicted SVD score
    """
    user_id = user["id"]
    user_ratings = get_ratings_for_user(user_id)

    if not user_ratings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ratings found. Please rate some movies first (cold start).",
        )

    # Step 1: Find a movie the user recently liked
    liked = [r for r in user_ratings if r["rating"] >= 4.0]
    if not liked:
        # Fallback: use highest-rated movie
        liked = sorted(user_ratings, key=lambda x: x["rating"], reverse=True)

    seed_movie_id = liked[-1]["movie_id"]  # most recently liked

    # Step 2: Content-based — find 30 similar movies by genre
    similar_ids = _get_content_similar_movies(seed_movie_id, top_n=30)

    if not similar_ids:
        # Fallback: use popular movies
        similar_ids = _popular_movie_ids[:30]

    # Remove movies the user has already rated
    rated_ids = {r["movie_id"] for r in user_ratings}
    similar_ids = [mid for mid in similar_ids if mid not in rated_ids]

    # Step 3: Collaborative — predict SVD ratings
    predictions = _predict_svd_ratings(user_id, similar_ids)

    # Step 4: Sort by predicted rating, return top 10
    predictions.sort(key=lambda x: x["predicted_rating"], reverse=True)
    top_10 = predictions[:10]

    return {
        "user_id": user_id,
        "seed_movie_id": seed_movie_id,
        "recommendations": top_10,
    }
