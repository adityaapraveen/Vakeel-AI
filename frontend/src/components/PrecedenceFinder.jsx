import React, { useState } from 'react';
import axios from 'axios';
import SplitText from '../assets/SplitText';
import './PrecedenceFinder.css';

const PrecedenceFinder = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleQuerySubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setResponse(null); 

        try {
            const res = await axios.post('http://localhost:8080/query/legal', { query });

            if (Array.isArray(res.data.answer)) {
                setResponse(res.data.answer.length > 0 ? res.data.answer : []);
            } else {
                setResponse(res.data.answer ? [{ text: res.data.answer }] : []);
            }
        } catch (error) {
            console.error("Error fetching precedents:", error);
            setError("Sorry, something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <SplitText text="Find Legal Precedence" className="Heading" />
            <form onSubmit={handleQuerySubmit}>
                <textarea
                    placeholder="Enter legal query..."
                    rows="5"
                    cols="50"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <div>
                    <button className="btn2" type="submit" disabled={loading || !query.trim()}>
                        <span className="spn2">
                            {loading ? 'Loading...' : 'Submit'}
                        </span>
                    </button> 
                </div>
            </form>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {response !== null && (
                <div className="response">
                    <h3>Response:</h3>
                    {response.length > 0 ? (
                        <ul>
                            {response.map((item, index) => (
                                <li key={index}>{item.text}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>No relevant documents found.</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default PrecedenceFinder;
