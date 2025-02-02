import React, { useState } from 'react';
import SplitText from '../assets/SplitText';
import './LegalDocumentCreator.css';

const LegalDocumentCreator = () => {
    const [question, setQuestion] = useState("");
    const [response, setResponse] = useState(null); // Set to null initially to hide response
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        setResponse(null); // Reset response on new query

        try {
            const res = await fetch('http://localhost:8080/generate_contract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question }),
            });

            const data = await res.json();
            
            // Check if the response contains a contract
            if (data.contract) {
                setResponse([{ text: data.contract }]); // Wrap response in an array for consistency
            } else {
                setResponse([]); // Empty array means no document found
            }
        } catch (error) {
            console.error("Error fetching response:", error);
            setError("An error occurred. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="legal-document-creator">
            <SplitText text="Create Your Legal Document Here" className="Heading" />
            <textarea
                placeholder="Type your question here..."
                rows="5"
                cols="50"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
            />

            <button onClick={handleSubmit} disabled={loading || !question.trim()}>
                <a href="#" className="btn2">
                    <span className="spn2">{loading ? 'Loading...' : 'Submit'}</span>
                </a>
            </button>

            {/* Display Error Message if an error occurs */}
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {/* Conditionally render response section only when an answer exists */}
            {response !== null && (
                <div className="response">
                    <h3>Response:</h3>
                    {response.length > 0 ? (
                        response.map((item, index) => (
                            <div key={index}>
                                <p><strong>Text:</strong> {item.text}</p>
                            </div>
                        ))
                    ) : (
                        <p>No relevant documents found.</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default LegalDocumentCreator;
