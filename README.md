---
title: Backend Reco Films
emoji: 🎥
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
# 🎬 Movie Recommendation System

A full-stack **hybrid movie recommendation system** combining **Content-Based Filtering** (TF-IDF on genres) and **Collaborative Filtering** (SVD with SGD) to deliver personalized movie suggestions. Built with **FastAPI** and **React + Vite**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Machine Learning Models](#machine-learning-models)
- [Notebooks](#notebooks)
- [Screenshots](#screenshots)
- [Authors](#authors)

---

## Overview

This application provides personalized movie recommendations using a **hybrid approach**:

1. **Cold Start (Onboarding)** — New users rate a selection of popular movies to bootstrap their profile.
2. **Content-Based Filtering** — Uses **TF-IDF vectorization** on movie genres and **cosine similarity** to find movies similar to ones the user enjoyed.
3. **Collaborative Filtering** — A custom **SVD model** (Stochastic Gradient Descent) predicts ratings for candidate movies based on learned latent factors.
4. **Hybrid Ranking** — Content-based candidates are re-ranked by SVD predicted scores to produce the final Top-10 recommendations.

### Key Features

- 🔐 **JWT Authentication** — Secure user registration and login with bcrypt password hashing
- 🎯 **Hybrid Recommendations** — Combines content-based and collaborative filtering
- 🧊 **Cold-Start Handling** — Onboarding flow with popular movies for new users
- 📊 **Exploratory Data Analysis** — Jupyter notebooks with 18 visualizations
- ⚡ **Real-time API** — FastAPI backend with auto-reload for development
- 🎨 **Modern UI** — React SPA with protected routes and responsive design

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                      │
│         (Vite · React Router · Axios · CSS)             │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌──────┐ │
│  │  Login   │  │ Register  │  │ Onboarding │  │ Home │ │
│  └──────────┘  └───────────┘  └────────────┘  └──────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (Axios)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│            (Uvicorn · JWT · JSON Storage)                │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────┐  │
│  │ Auth Router│  │Ratings     │  │Recommendations    │  │
│  │ /auth/*    │  │Router      │  │Router             │  │
│  │            │  │/ratings/*  │  │/recommendations/* │  │
│  └────────────┘  └────────────┘  └───────────────────┘  │
│                                          │              │
│                          ┌───────────────┴──────────┐   │
│                          ▼                          ▼   │
│                  ┌──────────────┐          ┌──────────┐ │
│                  │ TF-IDF +     │          │ SVD Model│ │
│                  │ Cosine Sim.  │          │ (SGD)    │ │
│                  │ (Content)    │          │ (Collab) │ │
│                  └──────────────┘          └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **PyJWT** | JWT token encoding/decoding |
| **Passlib + bcrypt** | Password hashing |
| **Pandas** | Data manipulation |
| **NumPy / SciPy** | Numerical computation |
| **Scikit-learn** | TF-IDF vectorization & cosine similarity |
| **Joblib / Pickle** | Model serialization |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI framework |
| **Vite 7** | Build tool & dev server |
| **React Router v7** | Client-side routing |
| **Axios** | HTTP client |
| **CSS** | Styling |

### Data
| File | Description |
|---|---|
| `movies.csv` | Movie metadata (ID, title, genres) — ~62K movies |
| `ratings.csv` | User-movie ratings — ~27M ratings (MovieLens) |

---

## Project Structure

```
Recommendation-system-movie/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── auth.py                 # JWT & password utilities
│   ├── storage.py              # JSON-based user & ratings storage
│   ├── svd_model.py            # SVD model class (SGD-based)
│   ├── train_model.py          # Model training script
│   ├── requirements.txt        # Python dependencies
│   ├── data/
│   │   ├── users.json          # Registered users
│   │   └── new_ratings.json    # User ratings (from the app)
│   ├── models/
│   │   └── svd_model.pkl       # Trained SVD model (generated)
│   └── routers/
│       ├── auth_router.py      # /auth/register, /auth/login
│       ├── ratings_router.py   # /ratings (CRUD)
│       └── recommendations_router.py  # /recommendations
│
├── frontend/
│   ├── index.html              # HTML entry point
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   └── src/
│       ├── main.jsx            # React entry point
│       ├── App.jsx             # Router & route guards
│       ├── AuthContext.jsx     # Auth context provider
│       ├── api.js              # Axios instance configuration
│       ├── index.css           # Global styles
│       └── pages/
│           ├── LoginPage.jsx       # Login form
│           ├── RegisterPage.jsx    # Registration form
│           ├── OnboardingPage.jsx  # Cold-start movie rating
│           ├── HomePage.jsx        # Recommendations display
│           ├── Auth.css            # Auth pages styling
│           ├── Onboarding.css      # Onboarding page styling
│           └── Home.css            # Home page styling
│
├── notebooks/
│   ├── 01_EDA_Dataset.ipynb        # Exploratory Data Analysis
│   ├── 02_Model_Evaluation.ipynb   # Model training & evaluation
│   └── figures/                    # Generated visualizations (18 plots)
│
├── movies.csv                  # Movie dataset
├── ratings.csv                 # Ratings dataset (not tracked by Git)
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** & **npm**
- **MovieLens dataset** (`ratings.csv` and `movies.csv` in the project root)

### 1. Clone the Repository

```bash
git clone https://github.com/ayman-elbadry/films_recommendation.git
cd films_recommendation
```

### 2. Backend Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Train the SVD model (required on first run)
python train_model.py

# Start the API server
python -m uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**. \
Interactive docs at **http://localhost:8000/docs** (Swagger UI).

### 3. Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Start the dev server
npm run dev
```

The app will be available at **http://localhost:5173**.

### 4. Dataset

This project uses the [MovieLens 25M dataset](https://grouplens.org/datasets/movielens/25m/). Place the following files at the project root:

- `movies.csv` — Movie metadata (included)
- `ratings.csv` — User ratings (~678 MB, **not tracked by Git**)

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive a JWT token |

### Ratings

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/ratings` | Submit a single movie rating | 🔐 JWT |
| `POST` | `/ratings/batch` | Submit multiple ratings (onboarding) | 🔐 JWT |
| `GET` | `/ratings` | Get current user's ratings | 🔐 JWT |

### Recommendations

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/recommendations` | Get personalized hybrid recommendations | 🔐 JWT |
| `GET` | `/recommendations/popular` | Get popular movies (cold-start) | ❌ |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |

---

## Machine Learning Models

### 1. Content-Based Filtering (TF-IDF)

- **Vectorization**: TF-IDF on cleaned movie genres (e.g., `Action Adventure Sci-Fi`)
- **Similarity**: Cosine similarity between genre vectors
- **Output**: Top 30 most similar movies to a user's liked movie

### 2. Collaborative Filtering (SVD via SGD)

A custom implementation of **Singular Value Decomposition** using **Stochastic Gradient Descent**:

- **Latent factors**: 50 dimensions
- **Training**: 20 epochs on 500K sampled ratings
- **Learning rate**: 0.005 with L2 regularization (λ = 0.02)
- **Prediction**: `r̂ = μ + bᵤ + bᵢ + pᵤᵀ · qᵢ`

Where:
- `μ` = global mean rating
- `bᵤ` = user bias
- `bᵢ` = item bias
- `pᵤ` = user latent factor vector
- `qᵢ` = item latent factor vector

### 3. Hybrid Pipeline

```
User's liked movie (rating ≥ 4.0)
        │
        ▼
   TF-IDF Cosine Similarity → Top 30 similar movies
        │
        ▼
   SVD Predicted Ratings for those 30 movies
        │
        ▼
   Sort by predicted score → Top 10 recommendations
```

---

## Notebooks

The `notebooks/` directory contains detailed analysis:

### 📊 01 — Exploratory Data Analysis
- Rating distribution
- Genre frequency & co-occurrence
- User activity patterns
- Movie popularity analysis
- Temporal trends
- Sparsity matrix visualization

### 📈 02 — Model Evaluation
- SVD convergence (RMSE over epochs)
- Prediction error analysis
- Model comparison (SVD vs. baseline)
- TF-IDF similarity heatmap
- Latent factor PCA visualization
- Bias distributions

> All 18 generated figures are saved in `notebooks/figures/`.

---

## Authors

- **Ayman El Badry** — [GitHub](https://github.com/ayman-elbadry)

---

## License

This project is for educational purposes.

---

<p align="center">
  Made with ❤️ using FastAPI & React
</p>