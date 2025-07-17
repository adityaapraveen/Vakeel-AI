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

    // Helper function to format text with proper line breaks and bold formatting
    const formatText = (text) => {
        if (!text) return '';
        
        return text
            .split('\n')
            .map((line, lineIndex) => (
                <span key={lineIndex}>
                    {formatTextWithBold(line)}
                    <br />
                </span>
            ));
    };

    // Helper function to convert **text** to bold
    const formatTextWithBold = (text) => {
        if (!text) return '';
        
        const parts = text.split(/(\*\*.*?\*\*)/g);
        
        return parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                // Remove the ** and make it bold
                const boldText = part.slice(2, -2);
                return <strong key={index}>{boldText}</strong>;
            }
            return part;
        });
    };

    // Helper function to detect if text contains structured content
    const renderFormattedContent = (text) => {
        if (!text) return null;

        // Split by double line breaks to identify paragraphs
        const paragraphs = text.split('\n\n');
        
        return paragraphs.map((paragraph, index) => {
            // Check if paragraph looks like a heading (short line followed by content)
            const lines = paragraph.split('\n');
            const isHeading = lines[0].length < 100 && lines[0].match(/^[A-Z]/) && lines.length > 1;
            
            if (isHeading) {
                return (
                    <div key={index} className="response-section">
                        <h4 className="response-heading">{formatTextWithBold(lines[0])}</h4>
                        <div className="response-content">
                            {lines.slice(1).map((line, lineIndex) => (
                                <p key={lineIndex}>{formatTextWithBold(line)}</p>
                            ))}
                        </div>
                    </div>
                );
            } else {
                // Regular paragraph
                return (
                    <div key={index} className="response-paragraph">
                        {formatText(paragraph)}
                    </div>
                );
            }
        });
    };

    return (
        <div>
            <SplitText />
            <form onSubmit={handleQuerySubmit}>
                <input
                    type="text"
                    value={query}
                    placeholder="Enter your legal query..."
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
                        <div className="response-container">
                            {response.map((item, index) => (
                                <div key={index} className="response-item">
                                    {renderFormattedContent(item.text)}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p>No relevant documents found.</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default PrecedenceFinder;