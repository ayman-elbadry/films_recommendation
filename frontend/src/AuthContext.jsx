import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const userId = localStorage.getItem('userId');
        const username = localStorage.getItem('username');
        const hasOnboarded = localStorage.getItem('hasOnboarded');
        if (token && userId) {
            setUser({ token, userId: Number(userId), username, hasOnboarded: hasOnboarded === 'true' });
        }
        setLoading(false);
    }, []);

    const loginUser = (data) => {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);
        setUser({ token: data.access_token, userId: data.user_id, username: data.username, hasOnboarded: false });
    };

    const completeOnboarding = () => {
        localStorage.setItem('hasOnboarded', 'true');
        setUser(prev => ({ ...prev, hasOnboarded: true }));
    };

    const logout = () => {
        localStorage.clear();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, loginUser, completeOnboarding, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
