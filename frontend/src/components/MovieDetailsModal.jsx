import { useState, useEffect } from 'react';
import { getMovieDetails, submitRating } from '../api';
import './MovieDetailsModal.css';

export default function MovieDetailsModal({ movieId, onClose, onSuccessHover }) {
    const [details, setDetails] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [userRating, setUserRating] = useState(0);
    const [submittingRating, setSubmittingRating] = useState(false);

    useEffect(() => {
        setLoading(true);
        getMovieDetails(movieId)
            .then(res => {
                setDetails(res.data);
                setLoading(false);
            })
            .catch(err => {
                setError('Failed to load movie details');
                setLoading(false);
            });
    }, [movieId]);

    const handleRate = async () => {
        if (userRating === 0 || !details) return;
        setSubmittingRating(true);
        try {
            await submitRating(details.movieId, userRating);
            // Optionally notify parent that rating occurred
            if (onSuccessHover) onSuccessHover();
            onClose();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to submit rating');
        } finally {
            setSubmittingRating(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-details-card" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>✕</button>

                {loading ? (
                    <div className="modal-loading">
                        <div className="spinner" />
                        <p>Loading details...</p>
                    </div>
                ) : error ? (
                    <div className="modal-error">{error}</div>
                ) : details ? (
                    <div className="modal-content-split">

                        <div className="modal-left">
                            {details.poster_url ? (
                                <img src={details.poster_url} alt={details.title} className="modal-main-poster" />
                            ) : (
                                <div className="modal-poster-placeholder">🎬</div>
                            )}

                            <div className="modal-rate-section">
                                <h3>Rate this Movie</h3>
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
                                <button
                                    className="modal-submit"
                                    onClick={handleRate}
                                    disabled={userRating === 0 || submittingRating}
                                >
                                    {submittingRating ? 'Submitting...' : 'Submit Rating'}
                                </button>
                            </div>
                        </div>

                        <div className="modal-right">
                            <h2 className="modal-full-title">
                                {details.title}
                                {details.release_date && <span className="modal-year"> ({details.release_date.split('-')[0]})</span>}
                            </h2>
                            <p className="modal-full-genres">{details.genres?.replace(/\|/g, ' • ')}</p>

                            {details.tagline && <p className="modal-tagline">"{details.tagline}"</p>}

                            <div className="modal-stats">
                                {details.vote_average > 0 && <span>⭐️ TMDB: {details.vote_average}/10</span>}
                                {details.runtime > 0 && <span>⏱ {details.runtime} min</span>}
                            </div>

                            <div className="modal-overview-section">
                                <h3>Synopsis</h3>
                                <p className="modal-overview">{details.overview}</p>
                            </div>

                            {details.cast && details.cast.length > 0 && (
                                <div className="modal-cast-section">
                                    <h3>Starring</h3>
                                    <div className="modal-cast-list">
                                        {details.cast.map((actor, i) => (
                                            <span key={i} className="modal-actor">{actor}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                    </div>
                ) : null}
            </div>
        </div>
    );
}
