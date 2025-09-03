import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import JobMatches from './components/JobMatches';
import { uploadCVAndMatch } from './services/api';

function App() {
  const [jobMatches, setJobMatches] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      
    } catch (err) {
      setError(err.message || 'An error occurred while processing your CV');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="min-h-screen bg-green-50">
      {/* Header with HRSD Logo */}
      <header className="bg-white relative" style={{backgroundColor: 'white', height: '150px !important', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 90px'}}>
        <img src="/hrsd_logo.svg" alt="HRSD Logo" className="hrsd-logo" style={{marginLeft: '40px'}} />
        <div style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: '#6B7280'}}>
          <span>Powered by</span>
          <img src="/Groq_logo.svg" alt="Groq" style={{height: '24px', width: 'auto'}} />
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-green-800 text-white" style={{height: '23vh', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center">
            <h1 className="text-8xl font-bold mb-4">Job Search</h1>
            <h2 className="text-2xl font-semibold">Find Your Next Career Opportunity in Saudi Arabia</h2>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="bg-green-50 py-0 min-h-screen">
        <div className="max-w-7xl mx-auto px-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-8 max-w-4xl mx-auto">
              {error}
            </div>
          )}

          {!jobMatches ? (
            <div className="text-center max-w-4xl mx-auto">

              
              <div className="mb-16">
                <FileUpload 
                  onFileUpload={handleFileUpload}
                  loading={loading}
                />
              </div>
            </div>
          ) : (
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-12">
                <h3 className="text-3xl font-bold text-gray-800 mb-4">
                  Your Job Matches
                </h3>
                <p className="text-lg text-gray-600">
                  Found {jobMatches.length} matching opportunities
                </p>
              </div>

              <div className="grid lg:grid-cols-3 gap-8 mb-16">
                <div className="lg:col-span-2">
                  <JobMatches 
                    matches={jobMatches}
                    cvData={cvData}
                  />
                </div>
                
                <div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold mb-4 text-gray-800">AI Analysis</h4>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700">
                        {analysis}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>


    </div>
  );
}

export default App;
