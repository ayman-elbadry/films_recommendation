import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPopularMovies, submitBatchRatings } from '../api';
import { useAuth } from '../AuthContext';
import './Onboarding.css';

const STAR_VALUES = [1, 2, 3, 4, 5];

function StarRating({ value, onChange }) {
    const [hover, setHover] = useState(0);

    return (
        <div className="star-rating">
            {STAR_VALUES.map((star) => (
                <button
                    key={star}
                    type="button"
                    className={`star ${star <= (hover || value) ? 'active' : ''}`}
                    onMouseEnter={() => setHover(star)}
                    onMouseLeave={() => setHover(0)}
                    onClick={() => onChange(star)}
                >
                    ★
                </button>
            ))}
        </div>
    );
}

export default function OnboardingPage() {
    const [movies, setMovies] = useState([]);
    const [ratings, setRatings] = useState({});
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { completeOnboarding } = useAuth();

    useEffect(() => {
        getPopularMovies(10)
            .then(res => {
                setMovies(res.data);
                setLoading(false);
            })
            .catch(() => {
                setError('Failed to load movies');
                setLoading(false);
            });
    }, []);

    const ratedCount = Object.keys(ratings).length;
    const canSubmit = ratedCount >= 3;

    const handleSubmit = async () => {
        setSubmitting(true);
        setError('');
        try {
            const ratingList = Object.entries(ratings).map(([movie_id, rating]) => ({
                movie_id: Number(movie_id),
                rating,
            }));
            await submitBatchRatings(ratingList);
            completeOnboarding();
            navigate('/home');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to submit ratings');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="onboarding-container">
                <div className="onboarding-loading">
                    <div className="spinner" />
                    <p>Loading movies...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="onboarding-container">
            <div className="onboarding-content">
                <div className="onboarding-header">
                    <h1>🎬 Let's Get Started!</h1>
                    <p>Rate at least <strong>3 movies</strong> so we can learn your taste</p>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${Math.min((ratedCount / 3) * 100, 100)}%` }}
                        />
                    </div>
                    <span className="progress-text">
                        {ratedCount}/3 rated {ratedCount >= 3 && '✓'}
                    </span>
                </div>

                {error && <div className="onboarding-error">{error}</div>}

                <div className="movies-grid">
                    {movies.map((movie) => (
                        <div
                            key={movie.movieId}
                            className={`movie-card ${ratings[movie.movieId] ? 'rated' : ''}`}
                        >
                            <div className="movie-poster">
                                {movie.poster_url ? (
                                    <img
                                        src={movie.poster_url}
                                        alt={movie.title}
                                        className="poster-img"
                                    />
                                ) : (
                                    <span className="poster-emoji">🎞️</span>
                                )}
                            </div>
                            <div className="movie-info">
                                <h3>{movie.title}</h3>
                                <p className="movie-genres">{movie.genres.replace(/\|/g, ' • ')}</p>
                                <StarRating
                                    value={ratings[movie.movieId] || 0}
                                    onChange={(val) =>
                                        setRatings((prev) => ({ ...prev, [movie.movieId]: val }))
                                    }
                                />
                            </div>
                        </div>
                    ))}
                </div>

                <button
                    className="submit-btn"
                    onClick={handleSubmit}
                    disabled={!canSubmit || submitting}
                >
                    {submitting
                        ? 'Submitting...'
                        : canSubmit
                            ? `Continue with ${ratedCount} ratings →`
                            : `Rate ${3 - ratedCount} more movie${3 - ratedCount > 1 ? 's' : ''}`}
                </button>
            </div>
        </div>
    );
}
