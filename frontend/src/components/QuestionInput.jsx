import React, { useState } from 'react';
import axios from 'axios';
import SplitText from '../assets/SplitText';
import './QuestionInput.css';

const QuestionInput = () => {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState(null); // Initially null to hide the response section
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleQuestionSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setAnswer(null); // Reset answer on new query

        try {
            const response = await axios.post("http://localhost:8080/query/legal", {
                query: question
            });

            console.log("Received response:", response.data);

            if (Array.isArray(response.data.answer)) {
                setAnswer(response.data.answer.length > 0 ? response.data.answer : []); 
            } else {
                setAnswer(response.data.answer ? [{ text: response.data.answer, score: "N/A" }] : []);
            }
        } catch (error) {
            console.error("Error fetching response:", error.response ? error.response.data : error);
            setError("Sorry, something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <SplitText text="Ask Your Query Here" className="Heading" />
            <form onSubmit={handleQuestionSubmit}>
                <textarea
                    placeholder="Type your question here..."
                    rows="5"
                    cols="50"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                />
                <div>
                    <button disabled={loading || !question.trim()}>
                        <a href="#" className="btn2">
                            <span className="spn2">
                                {loading ? 'Loading...' : 'Submit'}
                            </span>
                        </a>
                    </button>
                </div>
            </form>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {/* Conditionally render response section only when an answer exists */}
            {answer !== null && (
                <div className="response">
                    <h3>Response:</h3>
                    {answer.length > 0 ? (
                        answer.map((item, index) => (
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

export default QuestionInput;
