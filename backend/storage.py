"""
JSON-based storage helpers for users and ratings.
Thread-safe read/write using a threading lock.
"""

import json
import os
import threading
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"
RATINGS_FILE = DATA_DIR / "new_ratings.json"

_lock = threading.Lock()


def _ensure_files():
    """Create data directory and JSON files if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text("[]", encoding="utf-8")
    if not RATINGS_FILE.exists():
        RATINGS_FILE.write_text("[]", encoding="utf-8")


# --- Users ---

def read_users() -> list[dict]:
    """Read and return the list of users from users.json."""
    _ensure_files()
    with _lock:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def write_users(users: list[dict]):
    """Overwrite users.json with the given list."""
    _ensure_files()
    with _lock:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)


def get_user_by_username(username: str) -> dict | None:
    """Find a user by username. Returns None if not found."""
    users = read_users()
    for user in users:
        if user["username"] == username:
            return user
    return None


def get_next_user_id() -> int:
    """Return the next available user ID."""
    users = read_users()
    if not users:
        return 1
    return max(u["id"] for u in users) + 1


def add_user(username: str, hashed_password: str) -> dict:
    """Create a new user, save to users.json, and return the user dict."""
    users = read_users()
    new_user = {
        "id": get_next_user_id(),
        "username": username,
        "hashed_password": hashed_password,
    }
    users.append(new_user)
    write_users(users)
    return new_user


# --- Ratings ---

def read_ratings() -> list[dict]:
    """Read and return the list of ratings from new_ratings.json."""
    _ensure_files()
    with _lock:
        with open(RATINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def write_ratings(ratings: list[dict]):
    """Overwrite new_ratings.json with the given list."""
    _ensure_files()
    with _lock:
        with open(RATINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(ratings, f, indent=2, ensure_ascii=False)


def add_rating(user_id: int, movie_id: int, rating: float):
    """Append a single rating to new_ratings.json."""
    from datetime import datetime, timezone

    ratings = read_ratings()
    ratings.append({
        "user_id": user_id,
        "movie_id": movie_id,
        "rating": rating,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    write_ratings(ratings)


def add_ratings_batch(user_id: int, rating_list: list[dict]):
    """Append multiple ratings at once (cold-start onboarding)."""
    from datetime import datetime, timezone

    ratings = read_ratings()
    now = datetime.now(timezone.utc).isoformat()
    for r in rating_list:
        ratings.append({
            "user_id": user_id,
            "movie_id": r["movie_id"],
            "rating": r["rating"],
            "timestamp": now,
        })
    write_ratings(ratings)


def get_ratings_for_user(user_id: int) -> list[dict]:
    """Return all ratings submitted by a specific user."""
    return [r for r in read_ratings() if r["user_id"] == user_id]
