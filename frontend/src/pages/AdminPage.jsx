import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { retrainModel } from '../api';
import './Admin.css';

export default function AdminPage() {
    const [adminKey, setAdminKey] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRetrain = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        setError('');

        try {
            const res = await retrainModel(adminKey);
            setMessage(res.data.message || 'Model successfully retrained!');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to retrain model. Check your admin key.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="admin-container">
            <div className="admin-content">
                <button className="back-btn" onClick={() => navigate('/home')}>
                    ← Back to Home
                </button>

                <div className="admin-header">
                    <h1>🔐 Admin Dashboard</h1>
                    <p>Manage the ML Recommendation System.</p>
                </div>

                <div className="admin-card">
                    <h2>Force Model Retraining</h2>
                    <p className="admin-desc">
                        Trigger the SVD model to retrain using the latest ratings. This process takes a few seconds and updates the model in real-time.
                    </p>

                    <form onSubmit={handleRetrain} className="admin-form">
                        <input
                            type="password"
                            placeholder="Enter Admin Secret Key"
                            value={adminKey}
                            onChange={(e) => setAdminKey(e.target.value)}
                            required
                        />
                        <button type="submit" className="retrain-btn" disabled={loading || !adminKey}>
                            {loading ? 'Retraining...' : 'Trigger Retrain Now'}
                        </button>
                    </form>

                    {message && <div className="admin-success">{message}</div>}
                    {error && <div className="admin-error">{error}</div>}
                </div>
            </div>
        </div>
    );
}
