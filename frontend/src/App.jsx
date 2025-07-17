import React, { useState, useRef, useEffect } from 'react';
import { Scale, FileText, Search, MessageCircle, Send, Bot, User, Home, ChevronRight, Loader2, Copy, Check, BookOpen, Gavel, Users, Award, TrendingUp } from 'lucide-react';

// Main App Component
const App = () => {
  const [currentView, setCurrentView] = useState('home');
  const [chatHistory, setChatHistory] = useState([]);

  const addMessageToHistory = (message, response, type) => {
    setChatHistory(prev => [...prev, { message, response, type, timestamp: new Date() }]);
  };

  const clearHistory = () => {
    setChatHistory([]);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'ipc':
        return <IPCFinder onAddMessage={addMessageToHistory} />;
      case 'precedence':
        return <PrecedenceFinder onAddMessage={addMessageToHistory} />;
      case 'document':
        return <DocumentCreator onAddMessage={addMessageToHistory} />;
      case 'history':
        return <ChatHistory history={chatHistory} onClear={clearHistory} />;
      default:
        return <HomePage onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <Header currentView={currentView} onNavigate={setCurrentView} />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {renderCurrentView()}
      </main>
    </div>
  );
};

// Header Component
const Header = ({ currentView, onNavigate }) => {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'ipc', label: 'IPC Finder', icon: Scale },
    { id: 'precedence', label: 'Precedence', icon: Search },
    { id: 'document', label: 'Documents', icon: FileText },
    { id: 'history', label: 'Chat History', icon: MessageCircle },
  ];

  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Scale className="w-8 h-8 text-blue-400" />
            <h1 className="text-xl font-bold text-white">LegalBot</h1>
          </div>
          <nav className="flex space-x-1">
            {navItems.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => onNavigate(id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};

// Enhanced Home Component
const HomePage = ({ onNavigate }) => {
  const features = [
    {
      id: 'ipc',
      title: 'IPC Section Finder',
      description: 'Find relevant Indian Penal Code sections for your legal queries with AI-powered search',
      icon: Scale,
      color: 'bg-blue-500',
      stats: '2000+ Sections'
    },
    {
      id: 'precedence',
      title: 'Precedence Finder',
      description: 'Search for legal precedents and case laws from Supreme Court and High Courts',
      icon: Search,
      color: 'bg-green-500',
      stats: '50,000+ Cases'
    },
    {
      id: 'document',
      title: 'Document Creator',
      description: 'Generate legal documents, contracts, and agreements with AI assistance',
      icon: FileText,
      color: 'bg-purple-500',
      stats: '100+ Templates'
    },
  ];

  const stats = [
    { icon: BookOpen, label: 'Legal Sections', value: '2000+' },
    { icon: Gavel, label: 'Case Laws', value: '50,000+' },
    { icon: Users, label: 'Legal Professionals', value: '1000+' },
    { icon: Award, label: 'Success Rate', value: '98%' },
  ];

  return (
    <div className="text-center">
      <div className="mb-16">
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
          Welcome to <span className="text-blue-400">LegalBot</span>
        </h1>
        <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
          Your comprehensive AI-powered legal assistant for Indian law research, case analysis, and document creation. 
          Streamline your legal research with cutting-edge artificial intelligence.
        </p>
        <div className="flex justify-center space-x-4">
          <button 
            onClick={() => onNavigate('ipc')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors"
          >
            Get Started
          </button>
          <button className="border border-gray-600 hover:border-gray-500 text-gray-300 px-8 py-3 rounded-lg font-medium transition-colors">
            Learn More
          </button>
        </div>
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
        {stats.map(({ icon: Icon, label, value }, index) => (
          <div key={index} className="bg-gray-800 rounded-lg p-6 text-center">
            <Icon className="w-8 h-8 text-blue-400 mx-auto mb-3" />
            <div className="text-2xl font-bold text-white mb-1">{value}</div>
            <div className="text-gray-400 text-sm">{label}</div>
          </div>
        ))}
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {features.map(({ id, title, description, icon: Icon, color, stats }) => (
          <div
            key={id}
            onClick={() => onNavigate(id)}
            className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 transition-all cursor-pointer group transform hover:scale-105"
          >
            <div className={`w-12 h-12 ${color} rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-300 mb-4 text-sm leading-relaxed">{description}</p>
            <div className="text-blue-400 text-sm font-medium mb-3">{stats}</div>
            <div className="flex items-center justify-center text-blue-400 group-hover:text-blue-300">
              <span className="text-sm font-medium">Get Started</span>
              <ChevronRight className="w-4 h-4 ml-1" />
            </div>
          </div>
        ))}
      </div>

      {/* Why Choose LegalBot Section */}
      <div className="bg-gray-800 rounded-lg p-8 text-left">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Why Choose LegalBot?</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <TrendingUp className="w-5 h-5 text-green-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">AI-Powered Research</h3>
                <p className="text-gray-300 text-sm">Advanced natural language processing for precise legal research</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Scale className="w-5 h-5 text-blue-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">Comprehensive Database</h3>
                <p className="text-gray-300 text-sm">Access to extensive Indian legal databases and case laws</p>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <FileText className="w-5 h-5 text-purple-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">Document Generation</h3>
                <p className="text-gray-300 text-sm">Create professional legal documents in minutes</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Award className="w-5 h-5 text-yellow-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">Trusted by Professionals</h3>
                <p className="text-gray-300 text-sm">Used by lawyers, judges, and legal researchers nationwide</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Chat Interface Component
const ChatInterface = ({ title, onSubmit, loading, children }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [children]);

  const handleSubmit = () => {
    if (input.trim() && !loading) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg h-[700px] flex flex-col">
      <div className="border-b border-gray-700 p-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <Bot className="w-5 h-5 mr-2 text-blue-400" />
          {title}
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {children}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-700 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your legal query..."
            className="flex-1 bg-gray-700 text-white placeholder-gray-400 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg px-4 py-2 flex items-center space-x-2 transition-colors"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

// Updated Message Components - User messages on right, Bot messages on left
const UserMessage = ({ message }) => (
  <div className="flex items-start space-x-3 justify-end">
    <div className="bg-blue-600 rounded-lg rounded-tr-none p-3 max-w-xs lg:max-w-md">
      <p className="text-white">{message}</p>
    </div>
    <div className="bg-blue-600 rounded-full p-2 flex-shrink-0">
      <User className="w-4 h-4 text-white" />
    </div>
  </div>
);

// Enhanced Bot Message Component with better formatting
const BotMessage = ({ message, citations, documents }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text');
    }
  };

  // Enhanced formatting for legal precedents
  const formatLegalText = (text) => {
    // Split text into sections and format case citations
    const sections = text.split(/\*\*/).filter(section => section.trim());
    
    return sections.map((section, index) => {
      if (section.includes('State of') || section.includes('v.') || section.includes('SCC') || section.includes('AIR')) {
        return (
          <div key={index} className="mb-4 p-3 bg-gray-800 rounded-lg border-l-4 border-blue-400">
            <div className="font-semibold text-blue-300 mb-2 flex items-center">
              <Gavel className="w-4 h-4 mr-2" />
              Case Citation
            </div>
            <p className="text-gray-100 leading-relaxed">{section.trim()}</p>
          </div>
        );
      } else if (section.includes('Answer:')) {
        return (
          <div key={index} className="mb-4">
            <div className="font-semibold text-green-300 mb-2 flex items-center">
              <BookOpen className="w-4 h-4 mr-2" />
              Legal Analysis
            </div>
          </div>
        );
      } else if (section.includes('Reasoning:')) {
        return (
          <div key={index} className="mb-4 p-3 bg-gray-800 rounded-lg border-l-4 border-green-400">
            <div className="font-semibold text-green-300 mb-2 flex items-center">
              <Scale className="w-4 h-4 mr-2" />
              Legal Reasoning
            </div>
            <p className="text-gray-100 leading-relaxed">{section.replace('Reasoning:', '').trim()}</p>
          </div>
        );
      }
      return (
        <p key={index} className="text-gray-100 leading-relaxed mb-3">
          {section.trim()}
        </p>
      );
    });
  };

  return (
    <div className="flex items-start space-x-3 justify-start">
      <div className="bg-gray-600 rounded-full p-2 flex-shrink-0">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="flex-1 max-w-4xl">
        <div className="bg-gray-700 rounded-lg rounded-tl-none p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="prose prose-invert max-w-none">
                {formatLegalText(message)}
              </div>
            </div>
            <button
              onClick={copyToClipboard}
              className="ml-2 p-1 hover:bg-gray-600 rounded transition-colors flex-shrink-0"
              title="Copy response"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <Copy className="w-4 h-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>
        
        {citations && citations.length > 0 && (
          <div className="mt-3 p-3 bg-gray-800 rounded-lg border border-gray-600">
            <h4 className="text-sm font-semibold text-blue-300 mb-2 flex items-center">
              <BookOpen className="w-4 h-4 mr-2" />
              Legal Citations
            </h4>
            <div className="flex flex-wrap gap-2">
              {citations.map((citation, index) => (
                <span key={index} className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                  {citation}
                </span>
              ))}
            </div>
          </div>
        )}

        {documents && documents.length > 0 && (
          <div className="mt-3 space-y-2">
            <h4 className="text-sm font-semibold text-purple-300 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              Referenced Documents
            </h4>
            {documents.map((doc, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-3 border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">{doc.filename}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">
                      Relevance: {doc.score ? (doc.score * 100).toFixed(1) : 'N/A'}%
                    </span>
                    <div className="w-12 bg-gray-700 rounded-full h-1">
                      <div 
                        className="bg-blue-400 h-1 rounded-full"
                        style={{ width: `${doc.score ? doc.score * 100 : 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-400 line-clamp-3">{doc.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// IPC Finder Component
const IPCFinder = ({ onAddMessage }) => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'Hello! I can help you find relevant IPC sections for your legal queries. What would you like to know?' }
  ]);
  const [loading, setLoading] = useState(false);

  const extractCitations = (text) => {
    const patterns = [
      /Section\s+\d+/gi,
      /IPC\s+\d+/gi,
      /Chapter\s+[IVX]+/gi,
    ];
    
    const citations = [];
    patterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        citations.push(...matches.map(match => match.trim()));
      }
    });
    
    return [...new Set(citations)];
  };

  const handleSubmit = async (query) => {
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8080/query/ipc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      
      if (data.answer) {
        const citations = extractCitations(data.answer);
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: data.answer,
          citations: citations,
          documents: data.retrieved_docs || []
        }]);
        onAddMessage(query, data.answer, 'IPC');
      } else {
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: 'I apologize, but I couldn\'t find relevant IPC sections for your query. Please try rephrasing your question.'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: 'Sorry, there was an error processing your request. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatInterface title="IPC Section Finder" onSubmit={handleSubmit} loading={loading}>
      {messages.map((message, index) => (
        <div key={index}>
          {message.type === 'user' ? (
            <UserMessage message={message.content} />
          ) : (
            <BotMessage 
              message={message.content} 
              citations={message.citations}
              documents={message.documents}
            />
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-center space-x-2 text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Searching IPC sections...</span>
        </div>
      )}
    </ChatInterface>
  );
};

// Enhanced Precedence Finder Component
const PrecedenceFinder = ({ onAddMessage }) => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'I can help you find legal precedents and case laws. What legal matter would you like to research?' }
  ]);
  const [loading, setLoading] = useState(false);

  const extractCitations = (text) => {
    const patterns = [
      /AIR\s+\d{4}\s+[A-Z]{2,4}\s+\d+/gi,
      /\(\d{4}\)\s+\d+\s+SCC\s+\d+/gi,
      /\d{4}\s+SCC\s+\([^)]+\)\s+\d+/gi,
      /\d{4}\s+\(\d+\)\s+SCC\s+\d+/gi,
    ];
    
    const citations = [];
    patterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        citations.push(...matches.map(match => match.trim()));
      }
    });
    
    return [...new Set(citations)];
  };

  const handleSubmit = async (query) => {
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8080/query/legal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      
      if (data.answer) {
        const citations = extractCitations(data.answer);
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: data.answer,
          citations: citations,
          documents: data.retrieved_docs || []
        }]);
        onAddMessage(query, data.answer, 'Precedence');
      } else {
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: 'I couldn\'t find relevant precedents for your query. Please try rephrasing your question.'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: 'Sorry, there was an error processing your request. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatInterface title="Precedence Finder" onSubmit={handleSubmit} loading={loading}>
      {messages.map((message, index) => (
        <div key={index}>
          {message.type === 'user' ? (
            <UserMessage message={message.content} />
          ) : (
            <BotMessage 
              message={message.content} 
              citations={message.citations}
              documents={message.documents}
            />
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-center space-x-2 text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Searching legal precedents...</span>
        </div>
      )}
    </ChatInterface>
  );
};

// Document Creator Component
const DocumentCreator = ({ onAddMessage }) => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'I can help you create legal documents and contracts. What type of document would you like to generate?' }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (query) => {
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8080/generate_contract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });

      const data = await response.json();
      
      if (data.contract) {
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: data.contract
        }]);
        onAddMessage(query, data.contract, 'Document');
      } else {
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: 'I couldn\'t generate a document for your request. Please provide more specific details.'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: 'Sorry, there was an error generating the document. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatInterface title="Legal Document Creator" onSubmit={handleSubmit} loading={loading}>
      {messages.map((message, index) => (
        <div key={index}>
          {message.type === 'user' ? (
            <UserMessage message={message.content} />
          ) : (
            <BotMessage message={message.content} />
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-center space-x-2 text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Generating document...</span>
        </div>
      )}
    </ChatInterface>
  );
};

// Chat History Component
const ChatHistory = ({ history, onClear }) => {
  const getTypeColor = (type) => {
    switch (type) {
      case 'IPC': return 'bg-blue-500';
      case 'Precedence': return 'bg-green-500';
      case 'Document': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Chat History</h2>
        {history.length > 0 && (
          <button
            onClick={onClear}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Clear History
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No chat history yet. Start a conversation to see your queries here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded text-xs text-white ${getTypeColor(item.type)}`}>
                  {item.type}
                </span>
                <span className="text-gray-400 text-sm">
                  {item.timestamp.toLocaleString()}
                </span>
              </div>
              <div className="mb-2">
                <p className="text-gray-300 font-medium">Query:</p>
                <p className="text-gray-100">{item.message}</p>
              </div>
              <div>
                <p className="text-gray-300 font-medium">Response:</p>
                <p className="text-gray-100 whitespace-pre-wrap">{item.response}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;