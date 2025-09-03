import React, { useState } from 'react';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your HRSD career advisor. How can I help you with your job search today?",
      sender: 'ai',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      // Simulate AI response (replace with actual API call)
      setTimeout(() => {
        const aiMessage = {
          id: Date.now() + 1,
          text: "I understand you're looking for career guidance. To provide the best assistance, please upload your CV first so I can analyze your skills and experience. Then I can give you personalized job recommendations and career advice.",
          sender: 'ai',
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setLoading(false);
      }, 1500);
      
    } catch (error) {
      console.error('Error sending message:', error);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4 text-green-800">
        Career Advisor Chat
      </h3>

      <div className="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto mb-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-green-800 text-white'
                    : 'bg-white text-gray-800 border'
                }`}
              >
                <p className="text-sm">{message.text}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-green-100' : 'text-gray-500'
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 border px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="spinner w-4 h-4"></div>
                  <span className="text-sm">AI is typing...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSendMessage} className="flex space-x-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask about job opportunities, career advice, or skills development..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={!inputMessage.trim() || loading}
          className="bg-green-800 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
