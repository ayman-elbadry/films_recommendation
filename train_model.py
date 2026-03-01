"""
Train an SVD model on the MovieLens ratings dataset.

Usage:
    python train_model.py

Outputs:
    models/svd_model.pkl — serialized SVD model
"""

import os
import pickle
import time
from pathlib import Path

import pandas as pd
from svd_model import SVDModel

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
RATINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "ratings.csv")
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "svd_model.pkl"

# SVD hyper-parameters
N_FACTORS = 50
N_EPOCHS = 20
LR = 0.005
REG = 0.02
SAMPLE_SIZE = 500_000


def main():
    print("=" * 60)
    print("  SVD Model Training Pipeline")
    print("=" * 60)

    # Load data
    print("\n[1/3] Loading ratings data...")
    df = pd.read_csv(RATINGS_FILE, usecols=["userId", "movieId", "rating"])
    print(f"  Total ratings: {len(df):,}")

    # Sample for faster training
    if len(df) > SAMPLE_SIZE:
        print(f"  Sampling {SAMPLE_SIZE:,} ratings for training...")
        df = df.sample(n=SAMPLE_SIZE, random_state=42)

    # Train SVD
    print("\n[2/3] Training SVD model...")
    start = time.time()
    model = SVDModel(n_factors=N_FACTORS, n_epochs=N_EPOCHS, lr=LR, reg=REG)
    model.fit(
        user_ids=df["userId"].values,
        item_ids=df["movieId"].values,
        ratings=df["rating"].values,
    )
    elapsed = time.time() - start
    print(f"  Training completed in {elapsed:.1f}s")

    # Save model
    print("\n[3/3] Saving model...")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
    print(f"  Model saved to {MODEL_PATH} ({size_mb:.1f} MB)")

    # Quick test
    print("\n[TEST] Sample prediction:")
    test_pred = model.predict(1, 1)
    print(f"  User 1, Movie 1  -> Predicted rating: {test_pred:.2f}")

    print("\n" + "=" * 60)
    print("  Done! Model ready for the recommendation API.")
    print("=" * 60)


if __name__ == "__main__":
    main()
