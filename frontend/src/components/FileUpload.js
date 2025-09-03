import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onFileUpload, loading }) => {
  const [uploadError, setUploadError] = useState(null);

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



  const { getInputProps, isDragActive } = useDropzone({
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
        className={`border-2 border-dashed border-gray-300 rounded-lg p-16 text-center transition-colors ${
          isDragActive ? 'border-green-600 bg-green-50' : 'hover:border-green-400'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        onDrop={onDrop}
        onDragOver={(e) => e.preventDefault()}
        onDragEnter={(e) => e.preventDefault()}
      >
        <input {...getInputProps()} disabled={loading} style={{display: 'none'}} />
        
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
                  Drag & drop your CV here, or click the button below to browse<br/>
                  Supports PDF, DOC, DOCX, and TXT files (max 10MB)
                </p>
                <button 
                  onClick={() => document.querySelector('input[type="file"]').click()}
                  className="text-white transition-colors text-3xl font-bold cursor-pointer" 
                  style={{backgroundColor: '#166945', color: 'white', padding: '24px 48px', borderRadius: '50px', boxShadow: 'none', border: 'none'}}
                >
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


    </div>
  );
};

export default FileUpload;
