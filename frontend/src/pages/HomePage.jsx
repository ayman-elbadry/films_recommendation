import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRecommendations } from '../api';
import Navbar from '../components/Navbar';
import MovieDetailsModal from '../components/MovieDetailsModal';
import './Home.css';

export default function HomePage() {
    const [recommendations, setRecommendations] = useState([]);
    const [seedMovieId, setSeedMovieId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedMovieId, setSelectedMovieId] = useState(null);
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

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="home-container">
            <Navbar />

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
                                onClick={() => setSelectedMovieId(movie.movieId)}
                            >
                                <div className="rec-rank">#{idx + 1}</div>
                                <div className="rec-poster">
                                    {movie.poster_url ? (
                                        <img
                                            src={movie.poster_url}
                                            alt={movie.title}
                                            className="rec-poster-img"
                                        />
                                    ) : (
                                        <span className="rec-emoji">🎬</span>
                                    )}
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

            {selectedMovieId && (
                <MovieDetailsModal
                    movieId={selectedMovieId}
                    onClose={() => setSelectedMovieId(null)}
                    onSuccessHover={fetchRecommendations}
                />
            )}
        </div>
    );
}
