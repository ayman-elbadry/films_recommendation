import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import './Navbar.css';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim().length >= 2) {
            navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
            setSearchQuery('');
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="nav-brand" onClick={() => navigate('/home')}>
                <span className="nav-icon">🎬</span>
                <span className="nav-title">MovieRec</span>
            </div>

            <form className="nav-search" onSubmit={handleSearch}>
                <input
                    type="text"
                    placeholder="Search movies..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button type="submit">🔍</button>
            </form>

            <div className="nav-links">
                <Link to="/home" className="nav-link">Home</Link>
                <Link to="/history" className="nav-link">My Ratings</Link>
                {user?.username === 'admin' && (
                    <Link to="/admin" className="nav-link admin-link">Admin</Link>
                )}
            </div>

            <div className="nav-right">
                <span className="nav-user">👤 {user?.username}</span>
                <button className="nav-logout" onClick={handleLogout}>Logout</button>
            </div>
        </nav>
    );
}
