import React, { useState } from 'react';
import axiosInstance from '../axios';  // Import axiosInstance here

const QuestionInput = () => {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);

    const handleQuestionSubmit = async (event) => {
        event.preventDefault();  // Prevent default form submit behavior
        setLoading(true);

        try {
            // Use axiosInstance for the POST request to the Flask API
            const response = await axiosInstance.post('/ask', { question: question });
            setAnswer(response.data.answer || 'No answer found');
        } catch (error) {
            console.error("Error fetching response:", error);
            setAnswer("Sorry, something went wrong.");
        }

        setLoading(false);
    };

    return (
        <div>
            <form onSubmit={handleQuestionSubmit}>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a question"
                    required
                />
                <button type="submit" disabled={loading}>Ask</button>
            </form>
            {loading ? <p>Loading...</p> : <p>{answer}</p>}
        </div>
    );
};

export default QuestionInput;
