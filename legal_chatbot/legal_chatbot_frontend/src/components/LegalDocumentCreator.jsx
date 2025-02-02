import React, { useState } from 'react';
import SplitText from '../assets/SplitText';
import './LegalDocumentCreator.css';

const LegalDocumentCreator = () => {
    const [question, setQuestion] = useState("");
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        setResponse(null); 

        try {
            const res = await fetch('http://localhost:8080/generate_contract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question }),
            });

            const data = await res.json();
            
            if (data.contract) {
                // Split the contract into bullet points if it's formatted appropriately
                const bulletPoints = data.contract.split('\n').map((line, index) => ({
                    key: index,
                    text: line.trim(),
                }));
                setResponse(bulletPoints);
            } else {
                setResponse([]);
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

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {response !== null && (
                <div className="response">
                    <h3>Response:</h3>
                    {response.length > 0 ? (
                        <ul>
                            {response.map(item => (
                                <li key={item.key}>{item.text}</li>
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

export default LegalDocumentCreator;
