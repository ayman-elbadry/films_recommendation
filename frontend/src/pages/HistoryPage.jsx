import { useState, useEffect } from 'react';
import { getMyRatings, updateRating, deleteRating } from '../api';
import Navbar from '../components/Navbar';
import MovieDetailsModal from '../components/MovieDetailsModal';
import './History.css';

export default function HistoryPage() {
    const [ratings, setRatings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedMovieId, setSelectedMovieId] = useState(null);

    const fetchHistory = () => {
        setLoading(true);
        getMyRatings()
            .then(res => {
                setRatings(res.data);
                setLoading(false);
            })
            .catch(err => {
                setError('Failed to load rating history');
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleUpdate = async (movieId, currentRating) => {
        const newRating = prompt("Enter new rating (1-5):", currentRating);
        if (!newRating) return;
        const parsed = parseFloat(newRating);
        if (isNaN(parsed) || parsed < 0.5 || parsed > 5.0) {
            alert("Rating must be a number between 0.5 and 5.0");
            return;
        }

        try {
            await updateRating(movieId, parsed);
            fetchHistory(); // refresh
        } catch (err) {
            alert("Failed to update rating");
        }
    };

    const handleDelete = async (movieId) => {
        if (!window.confirm("Are you sure you want to delete this rating?")) return;

        try {
            await deleteRating(movieId);
            setRatings(ratings.filter(r => r.movie_id !== movieId));
        } catch (err) {
            alert("Failed to delete rating");
        }
    };

    return (
        <div className="history-container">
            <Navbar />

            <main className="history-main">
                <div className="history-header">
                    <h1>Your Rating History</h1>
                    <p>Movies you've reviewed in the past</p>
                </div>

                {error && <div className="history-error">{error}</div>}

                {loading ? (
                    <div className="history-loading">
                        <div className="spinner" />
                        <p>Loading your reviews...</p>
                    </div>
                ) : (
                    <>
                        {ratings.length === 0 ? (
                            <div className="no-history">You haven't rated any movies yet.</div>
                        ) : (
                            <div className="history-list">
                                {ratings.map((r) => (
                                    <div key={r.movie_id} className="history-item">
                                        <div
                                            className="history-poster clickable"
                                            onClick={() => setSelectedMovieId(r.movie_id)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            {r.poster_url ? (
                                                <img src={r.poster_url} alt={r.title} />
                                            ) : (
                                                <div className="history-poster-placeholder">🎬</div>
                                            )}
                                        </div>

                                        <div className="history-details">
                                            <h3>{r.title}</h3>
                                            <div className="history-stars">
                                                {'★'.repeat(Math.round(r.rating))}
                                                <span className="history-score">({r.rating}/5)</span>
                                            </div>
                                            <div className="history-date">
                                                {new Date(r.timestamp).toLocaleDateString()}
                                            </div>
                                        </div>

                                        <div className="history-actions">
                                            <button
                                                className="btn-update"
                                                onClick={() => handleUpdate(r.movie_id, r.rating)}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                className="btn-delete"
                                                onClick={() => handleDelete(r.movie_id)}
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                )}
            </main>

            {selectedMovieId && (
                <MovieDetailsModal
                    movieId={selectedMovieId}
                    onClose={() => setSelectedMovieId(null)}
                    onSuccessHover={fetchHistory}
                />
            )}
        </div>
    );
}
