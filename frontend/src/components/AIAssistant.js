import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { chatWithAdvisor } from '../services/api';

const AIAssistant = ({ jobMatches, cvData, analysis }) => {
  const [promptText, setPromptText] = useState('');
  const [chatResponse, setChatResponse] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);

  const handleSendPrompt = async () => {
    if (!promptText.trim()) return;
    
    setChatLoading(true);
    setChatError(null);
    
    // Add user message to chat history
    const userMessage = { role: 'user', content: promptText.trim() };
    const updatedHistory = [...chatHistory, userMessage];
    setChatHistory(updatedHistory);
    
    try {
      const response = await chatWithAdvisor(promptText.trim(), updatedHistory, jobMatches, cvData, analysis);
      setChatResponse(response.response);
      
      // Add assistant response to chat history
      const assistantMessage = { role: 'assistant', content: response.response };
      setChatHistory([...updatedHistory, assistantMessage]);
      
      setPromptText('');
    } catch (error) {
      setChatError(error.message || 'Failed to get response from AI assistant');
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white border border-gray-200 rounded-lg" style={{paddingLeft: '24px', paddingRight: '24px', paddingTop: '24px', paddingBottom: '24px'}}>
        <br/>
        <h4 className="text-gray-800 mb-4" style={{fontSize: '24px', fontWeight: 'bold'}}>AI Career Assistant</h4>
        <p className="text-gray-600 mb-6">
          Ask me anything about your job matches, career advice, or how to improve your CV based on the opportunities available.
        </p>

        {/* Chat History */}
        {chatHistory.length > 0 && (
          <div className="mb-6" style={{paddingLeft: '48px', paddingRight: '48px'}}>
            {chatHistory.map((message, index) => (
              <div key={index} className="mb-4">
                {message.role === 'user' ? (
                  <div 
                    className="w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white text-gray-800 text-right"
                    style={{
                      resize: 'none', 
                      padding: '16px 24px 16px 24px',
                      border: '2px solid #16a34a',
                      height: '48px',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <p className="text-sm">{message.content}</p>
                  </div>
                ) : (
                  <div className="text-left">
                    <ReactMarkdown
                      components={{
                        h1: ({children}) => <h1 className="text-lg font-bold mb-2 text-gray-800">{children}</h1>,
                        h2: ({children}) => <h2 className="text-base font-bold mb-2 text-gray-800">{children}</h2>,
                        h3: ({children}) => <h3 className="text-sm font-bold mb-1 text-gray-800">{children}</h3>,
                        p: ({children}) => <p className="mb-2 text-gray-700 leading-relaxed">{children}</p>,
                        ul: ({children}) => <ul className="mb-2 ml-4 list-disc text-gray-700">{children}</ul>,
                        ol: ({children}) => <ol className="mb-2 ml-4 list-decimal text-gray-700">{children}</ol>,
                        li: ({children}) => <li className="mb-1">{children}</li>,
                        strong: ({children}) => <strong className="font-semibold text-gray-800">{children}</strong>,
                        em: ({children}) => <em className="italic text-gray-700">{children}</em>
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}



        {/* Error Display */}
        {chatError && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            <strong>Error:</strong> {chatError}
          </div>
        )}

        {/* Input Area */}
        <div className="border border-gray-300 rounded-lg p-4" style={{paddingLeft: '48px', paddingRight: '48px'}}>
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendPrompt();
              }
            }}
            placeholder="Ask questions about your job matches, career advice, or how to improve your CV... (Press Enter to send)"
            className="w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            style={{resize: 'none', padding: '16px 24px 16px 24px'}}
            rows={1}
            disabled={chatLoading}
          />
          
          {chatLoading && (
            <div className="flex items-center space-x-2 mt-3">
              <div className="spinner"></div>
              <span className="text-gray-600">AI is thinking...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
