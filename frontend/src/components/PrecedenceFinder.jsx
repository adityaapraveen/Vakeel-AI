import React, { useState } from 'react';
import axios from 'axios';
import SplitText from '../assets/SplitText';
import './PrecedenceFinder.css';

const PrecedenceFinder = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState(null);
    const [retrievedDocs, setRetrievedDocs] = useState([]);
    const [usedDocs, setUsedDocs] = useState([]);
    const [unusedDocs, setUnusedDocs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleQuerySubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setResponse(null);
        setRetrievedDocs([]);
        setUsedDocs([]);
        setUnusedDocs([]);

        try {
            const res = await axios.post('http://localhost:8080/query/legal', { query });
            const { answer, retrieved_docs, used_docs, unused_docs } = res.data;

            if (Array.isArray(answer)) {
                setResponse(answer.length > 0 ? answer : []);
            } else {
                setResponse(answer ? [{ text: answer }] : []);
            }

            const sortedRetrieved = (retrieved_docs || []).sort((a, b) => b.score - a.score);
            const sortedUsed = (used_docs || []).sort((a, b) => b.score - a.score);
            const sortedUnused = (unused_docs || []).sort((a, b) => b.score - a.score);

            setRetrievedDocs(sortedRetrieved);
            setUsedDocs(sortedUsed);
            setUnusedDocs(sortedUnused);

        } catch (error) {
            console.error("Error fetching precedents:", error);
            setError("Sorry, something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

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

    const formatTextWithBold = (text) => {
        if (!text) return '';
        const parts = text.split(/(\*\*.*?\*\*)/g);
        return parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                const boldText = part.slice(2, -2);
                return <strong key={index}>{boldText}</strong>;
            }
            return part;
        });
    };

    const extractCitations = (text) => {
        if (!text) return [];
        
        const citations = [];
        
        // Common Indian legal citation patterns
        const patterns = [
            // AIR patterns: AIR 1999 SC 123, AIR 2000 Del 456
            /AIR\s+(\d{4})\s+([A-Z]{2,4})\s+(\d+)/gi,
            // SCC patterns: (1999) 4 SCC 123, 1999 SCC (Crl.) 456
            /\((\d{4})\)\s+(\d+)\s+SCC\s+(\d+)/gi,
            /(\d{4})\s+SCC\s+\([^)]+\)\s+(\d+)/gi,
            // Other patterns: 1999 (2) SCC 123
            /(\d{4})\s+\((\d+)\)\s+SCC\s+(\d+)/gi,
            // Supreme Court patterns: SC 1999, HC 2000
            /\b(\d{4})\s+(\d+)\s+(SC|HC)\s+(\d+)/gi,
            // Criminal Law Journal: Crl LJ 1999 123
            /Crl\s+LJ\s+(\d{4})\s+(\d+)/gi,
            // All India Reporter variations
            /A\.I\.R\.\s+(\d{4})\s+([A-Z]{2,4})\s+(\d+)/gi
        ];
        
        patterns.forEach(pattern => {
            const matches = text.match(pattern);
            if (matches) {
                matches.forEach(match => {
                    if (!citations.includes(match.trim())) {
                        citations.push(match.trim());
                    }
                });
            }
        });
        
        return citations;
    };

    const extractCaseName = (text) => {
        if (!text) return '';
        
        // Look for case name patterns: "Name v. Name" or "Name vs Name"
        const caseNamePatterns = [
            /([A-Z][a-zA-Z\s&.]+)\s+v\.?\s+([A-Z][a-zA-Z\s&.]+)/,
            /([A-Z][a-zA-Z\s&.]+)\s+vs\.?\s+([A-Z][a-zA-Z\s&.]+)/,
            /State\s+of\s+[A-Z][a-zA-Z\s]+\s+v\.?\s+[A-Z][a-zA-Z\s.]+/,
            /[A-Z][a-zA-Z\s.]+\s+v\.?\s+Union\s+of\s+India/
        ];
        
        for (const pattern of caseNamePatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[0].trim();
            }
        }
        
        return '';
    };

    const renderFormattedContent = (text) => {
        if (!text) return null;
        const paragraphs = text.split('\n\n');

        return paragraphs.map((paragraph, index) => {
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

                            {usedDocs.length > 0 && (
                                <div className="retrieved-section">
                                    <h4>📌 Used Documents:</h4>
                                    <div className="documents-container">
                                        {usedDocs.map((doc, index) => {
                                            const citations = extractCitations(doc.text);
                                            const caseName = extractCaseName(doc.text);
                                            
                                            return (
                                                <div key={index} className="document-card">
                                                    <div className="document-header">
                                                        <div className="document-title">
                                                            <h5>📄 {doc.filename}</h5>
                                                            {caseName && (
                                                                <div className="case-name">{caseName}</div>
                                                            )}
                                                        </div>
                                                        <span className="relevance-score">
                                                            Relevance: {doc.score ? doc.score.toFixed(3) : 'N/A'}
                                                        </span>
                                                    </div>
                                                    
                                                    {citations.length > 0 && (
                                                        <div className="citations-section">
                                                            <h6>📖 Legal Citations:</h6>
                                                            <div className="citations-container">
                                                                {citations.map((citation, citIndex) => (
                                                                    <span key={citIndex} className="citation-badge">
                                                                        {citation}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                    
                                                    <div className="document-content">
                                                        <div className="document-text">
                                                            {formatText(doc.text)}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* {unusedDocs.length > 0 && (
                                <div className="retrieved-section">
                                    <h4>📁 Unused Documents:</h4>
                                    <div className="documents-container">
                                        {unusedDocs.map((doc, index) => {
                                            const citations = extractCitations(doc.text);
                                            const caseName = extractCaseName(doc.text);
                                            
                                            return (
                                                <div key={index} className="document-card unused">
                                                    <div className="document-header">
                                                        <div className="document-title">
                                                            <h5>📄 {doc.filename}</h5>
                                                            {caseName && (
                                                                <div className="case-name">{caseName}</div>
                                                            )}
                                                        </div>
                                                        <span className="relevance-score">
                                                            Relevance: {doc.score ? doc.score.toFixed(3) : 'N/A'}
                                                        </span>
                                                    </div>
                                                    
                                                    {citations.length > 0 && (
                                                        <div className="citations-section">
                                                            <h6>📖 Legal Citations:</h6>
                                                            <div className="citations-container">
                                                                {citations.map((citation, citIndex) => (
                                                                    <span key={citIndex} className="citation-badge">
                                                                        {citation}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                    
                                                    <div className="document-content">
                                                        <div className="document-text">
                                                            {formatText(doc.text)}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )} */}

                            {retrievedDocs.length > 0 && (
                                <div className="retrieved-section">
                                    <h4>📚 All Retrieved Documents:</h4>
                                    <div className="documents-container">
                                        {retrievedDocs.map((doc, index) => {
                                            const citations = extractCitations(doc.text);
                                            const caseName = extractCaseName(doc.text);
                                            
                                            return (
                                                <div key={index} className="document-card">
                                                    <div className="document-header">
                                                        <div className="document-title">
                                                            <h5>📄 {doc.filename}</h5>
                                                            {caseName && (
                                                                <div className="case-name">{caseName}</div>
                                                            )}
                                                        </div>
                                                        <span className="relevance-score">
                                                            Relevance: {doc.score ? doc.score.toFixed(2) : 'N/A'}
                                                        </span>
                                                    </div>
                                                    
                                                    {citations.length > 0 && (
                                                        <div className="citations-section">
                                                            <h6>📖 Legal Citations:</h6>
                                                            <div className="citations-container">
                                                                {citations.map((citation, citIndex) => (
                                                                    <span key={citIndex} className="citation-badge">
                                                                        {citation}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                    
                                                    <div className="document-content">
                                                        <div className="document-text">
                                                            {formatText(doc.text)}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
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