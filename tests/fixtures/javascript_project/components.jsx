/**
 * React component examples for testing.
 */

import React, { useState, useEffect } from 'react';

// Functional component with hooks
function UserProfile({ userId, onUpdate }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUser(userId);
    }, [userId]);
    
    const fetchUser = async (id) => {
        setLoading(true);
        const data = await fetch(`/api/users/${id}`).then(r => r.json());
        setUser(data);
        setLoading(false);
    };
    
    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;
    
    return (
        <div className="user-profile">
            <h1>{user.name}</h1>
            <p>{user.email}</p>
        </div>
    );
}

// Component with multiple hooks
export default function Dashboard({ initialData }) {
    const [data, setData] = useState(initialData);
    const [filter, setFilter] = useState('all');
    
    useEffect(() => {
        // Fetch data on mount
        loadDashboardData();
    }, []);
    
    const loadDashboardData = async () => {
        const response = await fetch('/api/dashboard');
        setData(await response.json());
    };
    
    const handleFilterChange = (newFilter) => {
        setFilter(newFilter);
    };
    
    return (
        <div className="dashboard">
            <UserProfile userId={data.currentUser} />
        </div>
    );
}

// Class component (legacy)
class LegacyComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            count: 0
        };
    }
    
    incrementCount() {
        this.setState({ count: this.state.count + 1 });
    }
    
    render() {
        return <button onClick={() => this.incrementCount()}>Count: {this.state.count}</button>;
    }
}

export { UserProfile, LegacyComponent };
