import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchMovies } from '../api';
import Navbar from '../components/Navbar';
import MovieDetailsModal from '../components/MovieDetailsModal';
import './Search.css';

export default function SearchPage() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';

    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedMovieId, setSelectedMovieId] = useState(null);

    useEffect(() => {
        if (!query) {
            setResults([]);
            return;
        }

        setLoading(true);
        setError('');

        searchMovies(query)
            .then(res => {
                setResults(res.data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.response?.data?.detail || 'Failed to search movies');
                setLoading(false);
            });
    }, [query]);

    return (
        <div className="search-container">
            <Navbar />

            <main className="search-main">
                <div className="search-header">
                    <h1>Search Results</h1>
                    <p>Showing matches for "{query}"</p>
                </div>

                {error && <div className="search-error">{error}</div>}

                {loading ? (
                    <div className="search-loading">
                        <div className="spinner" />
                        <p>Searching database...</p>
                    </div>
                ) : (
                    <>
                        {results.length === 0 && query ? (
                            <div className="no-results">No movies found matching "{query}".</div>
                        ) : (
                            <div className="search-grid">
                                {results.map((movie) => (
                                    <div
                                        key={movie.movieId}
                                        className="search-card"
                                        onClick={() => setSelectedMovieId(movie.movieId)}
                                    >
                                        <div className="search-poster">
                                            {movie.poster_url ? (
                                                <img
                                                    src={movie.poster_url}
                                                    alt={movie.title}
                                                    className="search-poster-img"
                                                />
                                            ) : (
                                                <span className="search-emoji">🎬</span>
                                            )}
                                        </div>
                                        <div className="search-body">
                                            <h3 className="search-title">{movie.title}</h3>
                                            <p className="search-genres">{movie.genres.replace(/\|/g, ' • ')}</p>
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
                    onSuccessHover={() => { }}
                />
            )}
        </div>
    );
}
