import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRecommendations, submitRating } from '../api';
import { useAuth } from '../AuthContext';
import './Home.css';

export default function HomePage() {
    const [recommendations, setRecommendations] = useState([]);
    const [seedMovieId, setSeedMovieId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [ratingModal, setRatingModal] = useState(null);
    const [userRating, setUserRating] = useState(0);
    const [submittingRating, setSubmittingRating] = useState(false);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const fetchRecommendations = () => {
        setLoading(true);
        setError('');
        getRecommendations()
            .then(res => {
                setRecommendations(res.data.recommendations);
                setSeedMovieId(res.data.seed_movie_id);
                setLoading(false);
            })
            .catch(err => {
                setError(err.response?.data?.detail || 'Failed to load recommendations');
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchRecommendations();
    }, []);

    const handleRate = async () => {
        if (!ratingModal || userRating === 0) return;
        setSubmittingRating(true);
        try {
            await submitRating(ratingModal.movieId, userRating);
            setRatingModal(null);
            setUserRating(0);
            fetchRecommendations(); // Refresh after rating
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to submit rating');
        } finally {
            setSubmittingRating(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="home-container">
            {/* Navbar */}
            <nav className="navbar">
                <div className="nav-brand">
                    <span className="nav-icon">🎬</span>
                    <span className="nav-title">MovieRec</span>
                </div>
                <div className="nav-right">
                    <span className="nav-user">👤 {user?.username}</span>
                    <button className="nav-logout" onClick={handleLogout}>Logout</button>
                </div>
            </nav>

            {/* Main Content */}
            <main className="home-main">
                <div className="home-header">
                    <h1>Your Recommendations</h1>
                    <p>Personalized picks based on your taste — powered by AI</p>
                    {seedMovieId && (
                        <span className="seed-badge">
                            Based on movies you loved
                        </span>
                    )}
                </div>

                {error && <div className="home-error">{error}</div>}

                {loading ? (
                    <div className="home-loading">
                        <div className="spinner" />
                        <p>Generating recommendations...</p>
                    </div>
                ) : (
                    <div className="rec-grid">
                        {recommendations.map((movie, idx) => (
                            <div
                                key={movie.movieId}
                                className="rec-card"
                                onClick={() => { setRatingModal(movie); setUserRating(0); }}
                            >
                                <div className="rec-rank">#{idx + 1}</div>
                                <div className="rec-poster">
                                    <span className="rec-emoji">🎬</span>
                                </div>
                                <div className="rec-body">
                                    <h3 className="rec-title">{movie.title}</h3>
                                    <p className="rec-genres">{movie.genres.replace(/\|/g, ' • ')}</p>
                                    <div className="rec-score">
                                        <span className="score-star">★</span>
                                        <span className="score-value">{movie.predicted_rating}</span>
                                        <span className="score-label">predicted</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                <button className="refresh-btn" onClick={fetchRecommendations} disabled={loading}>
                    🔄 Refresh Recommendations
                </button>
            </main>

            {/* Rating Modal */}
            {ratingModal && (
                <div className="modal-overlay" onClick={() => setRatingModal(null)}>
                    <div className="modal-card" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setRatingModal(null)}>✕</button>
                        <h2>Rate this Movie</h2>
                        <h3>{ratingModal.title}</h3>
                        <p className="modal-genres">{ratingModal.genres.replace(/\|/g, ' • ')}</p>
                        <div className="modal-stars">
                            {[1, 2, 3, 4, 5].map(s => (
                                <button
                                    key={s}
                                    className={`modal-star ${s <= userRating ? 'active' : ''}`}
                                    onClick={() => setUserRating(s)}
                                >
                                    ★
                                </button>
                            ))}
                        </div>
                        {userRating > 0 && <p className="modal-rating-text">{userRating}/5 stars</p>}
                        <button
                            className="modal-submit"
                            onClick={handleRate}
                            disabled={userRating === 0 || submittingRating}
                        >
                            {submittingRating ? 'Submitting...' : 'Submit Rating'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
