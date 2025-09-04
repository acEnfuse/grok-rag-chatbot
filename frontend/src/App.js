import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import JobMatches from './components/JobMatches';
import AIAssistant from './components/AIAssistant';
import { uploadCVAndMatch } from './services/api';

function App() {
  // Scroll to top when component mounts (page loads)
  useEffect(() => {
    // Disable browser scroll restoration
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
    
    // Scroll to top immediately
    window.scrollTo(0, 0);
    
    // Also scroll to top after a small delay to ensure it works
    const timeoutId = setTimeout(() => {
      window.scrollTo(0, 0);
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, []);
  const [jobMatches, setJobMatches] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('job-matches'); // Default to job matches tab

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await uploadCVAndMatch(formData);
      
      setJobMatches(response.matches);
      setCvData(response.cv_summary);
      setAnalysis(response.analysis);
      
      // Switch to job matches tab after successful upload
      setActiveTab('job-matches');
      
    } catch (err) {
      setError(err.message || 'An error occurred while processing your CV');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="min-h-screen bg-green-50">
      {/* Fixed Header with HRSD Logo */}
      <div style={{position: 'fixed', top: '0', left: '0', right: '0', zIndex: 9999, backgroundColor: 'white', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingLeft: '60px', paddingRight: '90px'}}>
        <img src="/hrsd_logo.svg" alt="HRSD Logo" className="hrsd-logo" style={{marginLeft: '20px'}} />
        <div style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: '#6B7280'}}>
          <span>Powered by</span>
          <img src="/Groq_logo.svg" alt="Groq" style={{height: '24px', width: 'auto'}} />
        </div>
      </div>

      {/* Hero Section */}
      <section className="bg-green-800 text-white" style={{height: '23vh', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '100px'}}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center">
            <h1 className="text-8xl font-bold mb-4">Job Search</h1>
            <h2 className="text-2xl font-semibold">Find Your Next Career Opportunity in Saudi Arabia</h2>
          </div>
        </div>
      </section>

      {/* Toggle Button */}
      {jobMatches && (
        <div className="w-full bg-white py-8 flex justify-center">
          <button
            onClick={() => setActiveTab(activeTab === 'job-matches' ? 'ai-assistant' : 'job-matches')}
            className="text-white transition-colors text-3xl font-bold cursor-pointer" 
            style={{backgroundColor: '#166945', color: 'white', padding: '24px 48px', borderRadius: '50px', boxShadow: 'none', border: 'none', marginTop: '32px'}}
          >
            {activeTab === 'job-matches' ? 'AI Assistant' : 'Job Matches'}
          </button>
        </div>
      )}

      {/* Main Content */}
      <main className="bg-green-50 py-0 min-h-screen">
        {error && (
          <div className="max-w-7xl mx-auto px-6">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-8 max-w-4xl mx-auto">
              {error}
            </div>
          </div>
        )}

        {!jobMatches ? (
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center max-w-4xl mx-auto">
              <div className="mb-16">
                <FileUpload 
                  onFileUpload={handleFileUpload}
                  loading={loading}
                />
              </div>
            </div>
          </div>
        ) : (
          <>

            <div className="max-w-6xl mx-auto px-6">

              {/* Tab Content */}
              {activeTab === 'job-matches' && (
                <div className="grid lg:grid-cols-3 gap-8 mb-16">
                  <div className="lg:col-span-2">
                    <JobMatches 
                      matches={jobMatches}
                      cvData={cvData}
                    />
                    <br/>
                  </div>
                  
                  <div>
                    <div className="mb-6">
                      <div style={{backgroundColor: '#10412A', height: '4px', width: '100%'}}></div>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-6" style={{paddingLeft: '24px', paddingRight: '24px'}}>
                      <h4 className="text-gray-800 mb-4" style={{fontSize: '24px', fontWeight: 'bold'}}>AI Analysis</h4>
                      <div className="prose max-w-none">
                        <div className="text-gray-700" style={{fontSize: '16px', fontFamily: 'inherit', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                          {analysis}
                        </div>
                      </div>
                      <br/>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'ai-assistant' && (
                <AIAssistant 
                  jobMatches={jobMatches}
                  cvData={cvData}
                  analysis={analysis}
                />
              )}
            </div>
          </>
        )}
      </main>


    </div>
  );
}

export default App;
