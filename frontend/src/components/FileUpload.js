import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import { chatWithAdvisor } from '../services/api';

const FileUpload = ({ onFileUpload, loading }) => {
  const [uploadError, setUploadError] = useState(null);
  const [promptText, setPromptText] = useState('');
  const [chatResponse, setChatResponse] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setUploadError(null);
    
    if (rejectedFiles.length > 0) {
      setUploadError('Please upload a valid file (PDF, DOC, DOCX, or TXT)');
      return;
    }
    
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const handleSendPrompt = async () => {
    if (!promptText.trim()) return;
    
    setChatLoading(true);
    setChatError(null);
    setChatResponse(null);
    
    try {
      const response = await chatWithAdvisor(promptText.trim());
      setChatResponse(response.response);
      setPromptText('');
    } catch (error) {
      setChatError(error.message || 'Failed to get response from AI assistant');
    } finally {
      setChatLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  return (
    <div className="max-w-2xl mx-auto">
      {uploadError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {uploadError}
        </div>
      )}

      <div
        {...getRootProps()}
        className={`border-2 border-dashed border-gray-300 rounded-lg p-16 text-center transition-colors ${
          isDragActive ? 'border-green-600 bg-green-50' : 'hover:border-green-400'
        } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <input {...getInputProps()} disabled={loading} />
        
        {loading ? (
          <div className="flex flex-col items-center p-8" style={{paddingTop: '40px'}}>
            <div className="spinner mb-6"></div>
            <p className="text-xl font-medium text-gray-600 text-center">
              Processing your CV...
            </p>
            <p className="text-sm text-gray-500 mt-2 text-center">
              This may take a few moments
            </p>
          </div>
        ) : (
          <div>
            {isDragActive ? (
              <p className="text-xl font-medium text-green-600">
                Drop your CV here...
              </p>
            ) : (
              <>
                <br/>
                <p className="text-xs font-medium text-gray-700 mb-4">
                  Upload your CV to discover matching job opportunities in Saudi Arabia<br/>
                  Drag & drop your CV here, or click to browse<br/>
                  Supports PDF, DOC, DOCX, and TXT files (max 10MB)
                </p>
                <button className="text-white transition-colors text-3xl font-bold" style={{backgroundColor: '#166945', color: 'white', padding: '24px 48px', borderRadius: '50px', boxShadow: 'none', border: 'none'}}>
                  Choose File
                </button>
              </>
            )}
          </div>
        )}
      </div>

      <div className="mt-8 text-center">
        <br/>
        <p className="text-sm text-gray-500">
          Your CV data is processed securely and is not stored permanently
        </p>
      </div>

      {/* LLM Prompt Input */}
      <div className="mt-8 max-w-2xl mx-auto">
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <br/>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">Ask the AI Assistant</h3>
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendPrompt();
              }
            }}
            placeholder="Ask questions about your CV, career advice, or job opportunities... (Press Enter to send)"
            className="w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            style={{resize: 'none', padding: '16px 24px 16px 24px'}}
            rows={1}
            disabled={loading}
          />
        </div>
      </div>

      {/* AI Response Section */}
      {(chatResponse || chatError || chatLoading) && (
        <div className="mt-6 max-w-2xl mx-auto">
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-800 mb-4">AI Assistant Response</h4>
            
            {chatLoading && (
              <div className="flex items-center space-x-2">
                <div className="spinner"></div>
                <span className="text-gray-600">Thinking...</span>
              </div>
            )}
            
            {chatError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <strong>Error:</strong> {chatError}
              </div>
            )}
            
                                {chatResponse && (
                      <div className="prose max-w-none">
                        <div className="border border-gray-300 rounded-lg" style={{backgroundColor: 'white', maxHeight: '400px', overflowY: 'auto'}}>
                          <div className="text-sm text-black p-4" style={{paddingLeft: '24px', paddingRight: '24px'}}>
                            <ReactMarkdown
                              components={{
                                h1: ({children}) => <h1 className="text-xl font-bold mb-3 text-gray-800">{children}</h1>,
                                h2: ({children}) => <h2 className="text-lg font-bold mb-2 text-gray-800">{children}</h2>,
                                h3: ({children}) => <h3 className="text-base font-bold mb-2 text-gray-800">{children}</h3>,
                                p: ({children}) => <p className="mb-3 text-gray-700 leading-relaxed">{children}</p>,
                                ul: ({children}) => <ul className="mb-3 ml-4 list-disc text-gray-700">{children}</ul>,
                                ol: ({children}) => <ol className="mb-3 ml-4 list-decimal text-gray-700">{children}</ol>,
                                li: ({children}) => <li className="mb-1">{children}</li>,
                                strong: ({children}) => <strong className="font-semibold text-gray-800">{children}</strong>,
                                em: ({children}) => <em className="italic text-gray-700">{children}</em>
                              }}
                            >
                              {chatResponse}
                            </ReactMarkdown>
                          </div>
                        </div>
                      </div>
                    )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
